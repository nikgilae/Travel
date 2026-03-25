import json
from openai import AsyncOpenAI

from app.config import settings
import httpx
from openai import AsyncOpenAI
from app.config import settings

# Настраиваем кастомный таймаут: 15 секунд на коннект, 60 секунд на ожидание ответа
custom_timeout = httpx.Timeout(60.0, connect=15.0)

client = AsyncOpenAI(
    api_key=settings.AI_API_KEY,
    base_url=settings.AI_BASE_URL,
    timeout=custom_timeout,
)

\


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
) -> dict:
    """
    Сгенерировать персонализированный маршрут через AI.

    Передаёт AI контекст из нашей БД (POI, правила города)
    и параметры пользователя. AI возвращает упорядоченный
    маршрут с советами и оценкой бюджета.

    Parameters
    ----------
    city_name : str
        Название города назначения.
    country_name : str
        Название страны назначения.
    days : int
        Количество дней поездки.
    purpose : str
        Цель поездки: leisure, business, education, other.
    budget : str
        Уровень бюджета: low, medium, high.
    group_size : int
        Количество путешественников.
    interests : list[str]
        Интересы пользователя. Например: ['история', 'еда', 'шопинг'].
    pois : list[dict]
        Список доступных POI из нашей БД.
        Каждый элемент: {id, name, description, is_indoor, rules}.
    city_rules : list[dict]
        Правила города из нашей БД.
        Каждый элемент: {content, is_strict}.
    notes : str or None
        Дополнительные пожелания пользователя.

    Returns
    -------
    dict
        Сгенерированный маршрут в формате:
        {
            "summary": str,
            "total_budget_estimate": str,
            "days": [
                {
                    "day": int,
                    "pois": [
                        {
                            "poi_id": str,
                            "name": str,
                            "start_time": str,
                            "duration_hours": float,
                            "budget_estimate": str,
                            "ai_tip": str,
                        }
                    ]
                }
            ]
        }
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
Составь оптимальный маршрут используя места из списка выше.
Учитывай: время работы мест, логистику между ними, интересы путешественника.

ОТВЕТЬ СТРОГО В JSON ФОРМАТЕ (без markdown, без ```json, только чистый JSON):
{{
    "summary": "краткое описание маршрута 2-3 предложения",
    "total_budget_estimate": "оценка общего бюджета на группу",
    "days": [
        {{
            "day": 1,
            "theme": "тема дня например: История и культура",
            "pois": [
                {{
                    "poi_id": "id из списка выше",
                    "name": "название места",
                    "start_time": "09:00",
                    "duration_hours": 2.5,
                    "budget_estimate": "120 юаней/чел",
                    "ai_tip": "конкретный совет для этого места"
                }}
            ]
        }}
    ]
}}"""

    response = await client.chat.completions.create(
        model=settings.AI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты профессиональный тревел-ассистент. "
                    "Отвечаешь только в формате JSON без лишнего текста. "
                    "Используешь реальные poi_id из предоставленного списка."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=10000,
    )

    raw = response.choices[0].message.content.strip()

    # Очищаем от возможных markdown артефактов
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)