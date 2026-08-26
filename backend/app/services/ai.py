import asyncio
import json
import logging
import time

import httpx
from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AsyncOpenAI,
    InternalServerError,
)

from app.config import settings
from app.core.exceptions import AIGenerationError

logger = logging.getLogger(__name__)

# Общий клиент — им пользуются чаты (REST /chat/general и WS-агент).
# У диалога свои требования: ответы короткие, а обрыв дороже лишних секунд,
# поэтому здесь щедрый read-таймаут и ретраи SDK (как было до этого коммита).
chat_timeout = httpx.Timeout(60.0, connect=15.0)

client = AsyncOpenAI(
    api_key=settings.AI_API_KEY,
    base_url=settings.AI_BASE_URL,
    timeout=chat_timeout,
    max_retries=2,
)

# Клиент генерации маршрута: тот же пул соединений (with_options переиспользует
# httpx-клиент), но без ретраев SDK и с коротким read-таймаутом. Ретраями и общим
# бюджетом времени управляет generate_trip — иначе один прикладной вызов молча
# стоил бы два-три сетевых таймаута и человек ловил бы таймаут фронта.
generation_timeout = httpx.Timeout(
    settings.AI_READ_TIMEOUT_SECONDS,
    connect=settings.AI_CONNECT_TIMEOUT_SECONDS,
)
gen_client = client.with_options(timeout=generation_timeout, max_retries=0)

# Сколько раз мы сами пробуем получить валидный ответ (ретраев SDK больше нет).
# Четыре, а не два: после срезки connect-таймаута до 3 сек провальный дозвон
# стоит 3 сек, и из 30 сек бюджета две попытки тратили 6, оставляя 24 впустую.
# Реальный ограничитель — гейт ниже: он не начинает попытку, если остатка не
# хватает на полный read-таймаут, так что бюджет по-прежнему жёсткий потолок.
# На здоровом канале цена нулевая: первый же дозвон проходит за 0.1-0.7 сек и
# остальные попытки не случаются. Замер 2026-08-11 (канал давал ~1/3 успешных
# дозвонов): 2 попытки → ~55% успеха, 4 → ~80%. Ошибки, которые повтором не
# лечатся (4xx провайдера, обрезка по max_tokens), обрывают цикл сразу.
MAX_AI_ATTEMPTS = 4

# Сбои, после которых имеет смысл повторить запрос: сеть/таймаут, 5xx провайдера,
# битый или бессмысленный JSON в ответе. Всё остальное (4xx: неверный ключ,
# слишком длинный промпт, обрезка по max_tokens) повтором не лечится — падаем сразу.
RETRYABLE_AI_ERRORS = (
    json.JSONDecodeError,
    APITimeoutError,
    APIConnectionError,
    InternalServerError,
    asyncio.TimeoutError,
)


class _MalformedAIResponse(Exception):
    """Ответ AI пришёл, но его нельзя использовать (пустой / без дней маршрута)."""


class _TruncatedAIResponse(Exception):
    """Модель упёрлась в max_tokens: ответ оборван на полуслове."""


def _calc_max_tokens(days: int, fast: bool) -> int:
    """
    Подобрать max_tokens под длину поездки.

    Замер по живой БД (не-fast промпт, 6-8 мест в день): реальный 9-дневный план —
    62-71 сохранённых POI и ≈19 700 символов JSON, то есть ≈2 300-2 700 символов на
    день; на смеси кириллицы, UUID и ASCII это ~2,5-3 символа на токен → ≈750-1000
    токенов на день. Берём 1100 на день (запас ~30%) плюс 1500 на «шапку» ответа
    (summary, оценка бюджета, обрамление). Потолок 32000 — как было до коммита,
    чтобы не упереться в лимит модели на очень длинных поездках.
    """
    if fast:
        return 4000
    return min(32000, 1500 + 1100 * max(1, days))


def _extract_content(response) -> str | None:
    """Достать текст ответа модели, не падая на пустом choices/message."""
    choices = getattr(response, "choices", None) or []
    if not choices:
        return None
    message = getattr(choices[0], "message", None)
    return getattr(message, "content", None)


def _check_not_truncated(response, max_tokens: int, days: int) -> None:
    """
    Проверить, что модель закончила мысль, а не упёрлась в лимит токенов.

    Обрезанный ответ детерминированно даёт битый JSON: повтор с теми же
    параметрами воспроизведёт ту же обрезку и только сожжёт бюджет времени.

    Raises
    ------
    _TruncatedAIResponse
        finish_reason == "length".
    """
    choices = getattr(response, "choices", None) or []
    if not choices:
        return
    if getattr(choices[0], "finish_reason", None) == "length":
        raise _TruncatedAIResponse(
            f"ответ обрезан по max_tokens={max_tokens} на {days} днях"
        )


def _parse_ai_response(raw_content: str | None, expected_days: int) -> dict:
    """
    Разобрать сырой ответ AI в структуру маршрута.

    Parameters
    ----------
    raw_content : str or None
        Текст ответа модели.
    expected_days : int
        Сколько дней в поездке — ответ на меньшее число дней считаем браком.

    Raises
    ------
    _MalformedAIResponse
        Ответ пустой, не того типа или покрывает не все дни поездки.
    json.JSONDecodeError
        Ответ не является валидным JSON.
    """
    if not raw_content or not raw_content.strip():
        raise _MalformedAIResponse("AI вернул пустой ответ")

    raw = raw_content.strip()

    # Очистка от markdown блока если AI всё же обернул в ```json```
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)

    if not isinstance(result, dict):
        raise _MalformedAIResponse(f"AI вернул JSON неожиданного типа: {type(result).__name__}")

    days = result.get("days")
    if not isinstance(days, list) or not days:
        # Пустой days — это и есть тот самый «успех с пустым планом».
        # Он не должен доезжать до пользователя как успешный результат.
        raise _MalformedAIResponse("AI вернул ответ без дней маршрута (days пуст)")

    if len(days) < expected_days:
        # План на 3 дня для 10-дневной поездки — это тоже брак, а не успех.
        raise _MalformedAIResponse(
            f"AI вернул {len(days)} дн. вместо {expected_days} — маршрут неполный"
        )

    return result


async def generate_trip(
    city_name: str,
    country_name: str,
    days: int,
    purpose: str,
    budget: str,
    group_size: int,
    interests: list[str],
    pois: list[dict],
    city_rules: list[dict],
    notes: str | None = None,
    fast: bool = False,
) -> dict:
    """
    Сгенерировать персонализированный пул мест через AI.

    fast=True — компактный режим для демо: 3 основных + 1 запасное место в день,
    короткие подсказки. Заметно меньше выходных токенов → генерация ~8-10 сек
    вместо ~20+. Управляется настройкой ``settings.DEMO_FAST_GENERATION``.
    """
    budget_map = {
        "low": "эконом (минимальные расходы)",
        "medium": "средний (комфортное путешествие)",
        "high": "премиум (без ограничений)",
    }
    purpose_map = {
        "leisure": "отдых и туризм",
        "business": "деловая поездка",
        "education": "образование",
        "other": "другое",
    }

    pois_text = "\n".join([
        f"- ID: {p['id']} | {p['name']}: {p['description']}"
        + (f" | Правила: {', '.join(r['content'] for r in p['rules'])}" if p.get('rules') else "")
        for p in pois
    ])

    rules_text = "\n".join([
        f"- {'⚠️ ОБЯЗАТЕЛЬНО' if r['is_strict'] else '💡 Рекомендация'}: {r['content']}"
        for r in city_rules
    ])

    prompt = f"""Ты — опытный тревел-ассистент. Составь детальный маршрут путешествия.

ПАРАМЕТРЫ ПОЕЗДКИ:
- Город: {city_name}, {country_name}
- Дней: {days}
- Цель: {purpose_map.get(purpose, purpose)}
- Бюджет: {budget_map.get(budget, budget)}
- Группа: {group_size} чел.
- Интересы: {', '.join(interests)}
{f'- Пожелания: {notes}' if notes else ''}

ДОСТУПНЫЕ МЕСТА (используй их poi_id в ответе):
{pois_text}

ВАЖНЫЕ ПРАВИЛА ГОРОДА:
{rules_text}

ЗАДАЧА:
Сформируй расширенный пул мест (минимум 5 объектов на каждый день).
Для каждого места укажи activity_level (1-5): 1=очень спокойно (кафе, парк), 2=спокойно (прогулка), 3=умеренно (музей, галерея), 4=активно (рынок, много ходьбы), 5=очень активно (горный маршрут, интенсивный тур).
1. Основные (main_pois): 3-4 места, которые идеально подходят под интересы.
   Приоритет — местам, реально соответствующим интересам {', '.join(interests)}.
   Известную достопримечательность города, которая НЕ соответствует ни одному
   из указанных интересов, можно включить в main_pois, но не более ОДНОЙ на
   день, и только если остальные места дня по интересам. Пример: если интересы —
   food/night, а не cultural, можно предложить одну известную достопримечательность
   в день, но остальные 2-3 места должны быть ресторанами/барами/ночными
   локациями, а не музеями/храмами.
2. Дополнительные (additional_pois): 3-4 запасных варианта поблизости или для смены настроения.
Учитывай: время работы мест, логистику между ними, интересы.
Никогда не предлагай одно и то же место дважды в рамках одной поездки. Если у тебя закончились идеи, лучше предложи просто погулять по району

ОТВЕТЬ СТРОГО В JSON ФОРМАТЕ (без markdown, без ```json, только чистый JSON):
{{
    "summary": "краткое описание концепции поездки 2-3 предложения",
    "total_budget_estimate": "оценка общего бюджета на группу",
    "days": [
        {{
            "day": 1,
            "theme": "тема дня например: История и культура",
            "main_pois": [
                {{
                    "poi_id": "id из списка выше",
                    "name": "точное название места из списка",
                    "start_time": "10:00",
                    "duration_hours": 2.5,
                    "budget_estimate": "120 юаней/чел",
                    "ai_tip": "конкретный совет для этого места",
                    "activity_level": 3
                }}
            ],
            "additional_pois": [
                {{
                    "poi_id": "id из списка выше",
                    "name": "точное название места из списка",
                    "start_time": "14:00",
                    "duration_hours": 1.5,
                    "budget_estimate": "0",
                    "ai_tip": "почему стоит рассмотреть это место как запасное",
                    "activity_level": 2
                }}
            ]
        }}
    ]
}}"""

    # ── Быстрый режим для демо ────────────────────────────────────────────────
    # Компактный промпт: ровно 3 основных + 1 запасное место в день и короткие
    # подсказки. Это резко сокращает объём выходного JSON — главный драйвер
    # задержки, — укладывая генерацию в ~8-10 сек. Список входных POI на скорость
    # почти не влияет, поэтому его не трогаем здесь.
    if fast:
        prompt = f"""Ты — опытный тревел-ассистент. Составь маршрут путешествия.

ПАРАМЕТРЫ ПОЕЗДКИ:
- Город: {city_name}, {country_name}
- Дней: {days}
- Цель: {purpose_map.get(purpose, purpose)}
- Бюджет: {budget_map.get(budget, budget)}
- Группа: {group_size} чел.
- Интересы: {', '.join(interests)}
{f'- Пожелания: {notes}' if notes else ''}

ДОСТУПНЫЕ МЕСТА (используй их poi_id в ответе):
{pois_text}

ВАЖНЫЕ ПРАВИЛА ГОРОДА:
{rules_text}

ЗАДАЧА:
На каждый день выбери РОВНО 3 основных места (main_pois) под интересы пользователя
и РОВНО 1 запасное (additional_pois). Приоритет — местам, реально соответствующим
интересам {', '.join(interests)}. Известную достопримечательность города вне этих
интересов можно включить, но не более ОДНОЙ из 3 main_pois на день — остальные
должны соответствовать интересам (например, для food/night — рестораны/бары/
ночные локации, а не музеи/храмы). Учитывай логистику между местами.
ai_tip — очень коротко, максимум 8 слов. budget_estimate — коротко.
Никогда не повторяй одно и то же место в рамках поездки.
Для каждого места укажи activity_level (1-5).

ОТВЕТЬ СТРОГО В JSON (без markdown, без ```json, только чистый JSON):
{{"summary":"1-2 предложения","total_budget_estimate":"оценка на группу","days":[{{"day":1,"theme":"тема дня","main_pois":[{{"poi_id":"id из списка","name":"название","start_time":"10:00","duration_hours":2.5,"budget_estimate":"120 юаней/чел","ai_tip":"короткий совет","activity_level":3}}],"additional_pois":[{{"poi_id":"id из списка","name":"название","start_time":"14:00","duration_hours":1.5,"budget_estimate":"0","ai_tip":"почему запасное","activity_level":2}}]}}]}}"""

    messages = [
        {
            "role": "system",
            "content": (
                "Ты профессиональный тревел-ассистент. "
                "Отвечаешь только в формате JSON без лишнего текста. "
                "Используешь реальные poi_id из предоставленного списка."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    max_tokens = _calc_max_tokens(days, fast)

    async def _attempt() -> dict:
        """Один сетевой заход: запрос → проверка обрезки → разбор JSON."""
        response = await gen_client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=messages,
            temperature=0.6 if fast else 0.7,
            max_tokens=max_tokens,
        )
        _check_not_truncated(response, max_tokens, days)
        return _parse_ai_response(_extract_content(response), expected_days=days)

    # ── Бюджет времени на всю операцию ────────────────────────────────────────
    # Пользователь ждёт синхронно, а фронт рвёт запрос на 45 сек, поэтому бюджет —
    # жёсткий потолок (asyncio.wait_for), а не пожелание: даже зависший провайдер
    # не удержит запрос дольше AI_GENERATION_BUDGET_SECONDS. Вторую попытку
    # начинаем только если остатка хватает на полный read-таймаут.
    started_at = time.perf_counter()
    budget = settings.AI_GENERATION_BUDGET_SECONDS
    last_error: str | None = None

    for attempt in range(1, MAX_AI_ATTEMPTS + 1):
        elapsed = time.perf_counter() - started_at
        remaining = budget - elapsed
        if attempt > 1 and remaining < settings.AI_READ_TIMEOUT_SECONDS:
            logger.error(
                "AI-генерация: бюджет исчерпан после попытки %d/%d "
                "(потрачено %.1f сек из %.1f, остаток %.1f сек < read-таймаута %.1f сек), "
                "повтор не начинаем. Последняя причина: %s",
                attempt - 1, MAX_AI_ATTEMPTS, elapsed, budget,
                remaining, settings.AI_READ_TIMEOUT_SECONDS, last_error,
            )
            break

        try:
            result = await asyncio.wait_for(_attempt(), timeout=max(1.0, remaining))
            if attempt > 1:
                logger.info(
                    "AI-генерация: попытка %d/%d успешна (%.1f сек от старта)",
                    attempt, MAX_AI_ATTEMPTS, time.perf_counter() - started_at,
                )
            return result

        except _TruncatedAIResponse as e:
            # Повтор с теми же параметрами воспроизведёт обрезку — не тратим бюджет.
            logger.error(
                "AI-генерация: %s (попытка %d, %.1f сек от старта)",
                e, attempt, time.perf_counter() - started_at,
            )
            raise AIGenerationError(
                "Маршрут получился слишком длинным для одного ответа — "
                "попробуйте сократить поездку или сгенерировать её по частям.",
                retryable=False,
            ) from e

        except (*RETRYABLE_AI_ERRORS, _MalformedAIResponse) as e:
            last_error = f"{type(e).__name__}: {e}"
            # У JSONDecodeError в .doc лежит сырой ответ — без него причину не понять.
            raw_snippet = str(getattr(e, "doc", ""))[:200]
            logger.warning(
                "AI-генерация: попытка %d/%d провалилась через %.1f сек — %s%s",
                attempt, MAX_AI_ATTEMPTS, time.perf_counter() - started_at, last_error,
                f". Сырой ответ: {raw_snippet}" if raw_snippet else "",
            )
            continue

        except APIError as e:
            # 4xx и прочие ошибки, которые повтором не лечатся (неверный ключ,
            # превышен лимит контекста) — не тратим бюджет впустую и честно
            # говорим клиенту, что кнопка «Попробовать ещё раз» тут не поможет.
            logger.error(
                "AI-генерация: неповторяемая ошибка провайдера через %.1f сек — %s: %s",
                time.perf_counter() - started_at, type(e).__name__, e,
            )
            raise AIGenerationError(
                "Сервис подбора мест ответил ошибкой. Мы уже знаем о проблеме.",
                retryable=False,
            ) from e

    logger.error(
        "AI-генерация: не удалось получить валидный маршрут за %d попыток и %.1f сек. "
        "Последняя причина: %s",
        MAX_AI_ATTEMPTS, time.perf_counter() - started_at, last_error,
    )
    raise AIGenerationError(
        "Сервис подбора мест сейчас не отвечает как надо. Попробуйте ещё раз."
    )
