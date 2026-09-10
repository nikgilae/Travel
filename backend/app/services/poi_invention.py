"""
Наполнение города местами из памяти AI-модели, когда Google Maps недоступен.

Вынужденная замена, не улучшение. С 09.09.2026 у проекта выключен биллинг в
Google Cloud, Places API отвечает REQUEST_DENIED на каждый запрос, и город,
которого нет в справочнике, остаётся пустым навсегда: человек проходит весь
онбординг и упирается в «мест нет». Здесь модель называет места по своей
памяти, чтобы маршрут всё-таки собрался.

Чем это хуже Google и почему выключается первым же делом после биллинга
(AI_POI_FALLBACK_ENABLED):

- координаты приблизительные, модель помнит их хуже, чем названия;
- нет google_place_id, поэтому карточка места не обогащается и переход в
  карты идёт текстовым поиском по названию;
- модель может назвать место, которое закрылось или переехало.

Что здесь сделано против последнего: промпт прямо запрещает выдумывать и
требует вернуть пустой список, если города модель не знает. Пустой список —
нормальный ответ, а не сбой: он честнее выдуманного маршрута по
несуществующему городу.
"""

import json
import logging

from app.config import settings
from app.services.ai import RETRYABLE_AI_ERRORS, gen_client

logger = logging.getLogger(__name__)

# Столько ждём ответа. Задача фоновая, человек в этот момент идёт по остальным
# шагам онбординга, поэтому потолок щедрее, чем у генерации маршрута.
INVENTION_TIMEOUT_SECONDS = 90.0

MAX_INVENTION_ATTEMPTS = 2


def _build_prompt(city_name: str, country_name: str, count: int) -> str:
    return f"""Ты знаешь города мира как опытный местный гид.

ГОРОД: {city_name}, страна: {country_name}

ЗАДАЧА: перечисли до {count} РЕАЛЬНО СУЩЕСТВУЮЩИХ мест этого города, которые
имеет смысл посетить путешественнику. Разного типа: достопримечательности,
парки и природа, музеи, рестораны и кафе, рынки, бары, места для активного
отдыха.

ЖЁСТКИЕ ПРАВИЛА:
1. Только те места, в существовании которых ты уверен. Ничего не выдумывай.
2. Если ты не знаешь такого города или знаешь о нём слишком мало — верни
   пустой список мест. Пустой ответ лучше выдуманного.
3. Координаты указывай настолько точно, насколько помнишь. Если не помнишь
   координаты места — ставь null, но не выдумывай числа.
4. Название пиши на русском, как его называют путешественники.

ОТВЕТЬ СТРОГО В JSON (без markdown, без ```json):
{{"places":[{{"name":"название места","description":"тип места в двух-трёх словах","information":"одно предложение, чем это место интересно","lat":55.7539,"lng":37.6208,"is_indoor":false}}]}}"""


def _parse(raw: str | None) -> list[dict]:
    """
    Разобрать ответ модели в список мест, отбросив мусор.

    Место без названия бесполезно. Координаты необязательны: место без них
    попадёт в маршрут, но не встанет на карту — это лучше, чем выдуманная
    точка посреди океана.
    """
    if not raw:
        return []

    data = json.loads(raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```"))
    places = data.get("places") or []

    cleaned: list[dict] = []
    seen: set[str] = set()
    for place in places:
        name = (place.get("name") or "").strip()
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())

        lat, lng = place.get("lat"), place.get("lng")
        # Координаты берём только парой и только в допустимых пределах:
        # одна половина или число вне диапазона — признак того, что модель
        # их не помнит, а досочиняет.
        if not (isinstance(lat, (int, float)) and isinstance(lng, (int, float))
                and -90 <= lat <= 90 and -180 <= lng <= 180):
            lat = lng = None

        cleaned.append({
            "name": name,
            "description": (place.get("description") or "Интересное место").strip(),
            "information": (place.get("information") or "").strip(),
            "lat": lat,
            "lng": lng,
            "is_indoor": bool(place.get("is_indoor", False)),
        })

    return cleaned


async def invent_city_pois(city_name: str, country_name: str) -> list[dict]:
    """
    Попросить у модели список мест города.

    Возвращает пустой список, если модель города не знает или ответ не удалось
    разобрать. Наружу ошибки не выпускаются: это фолбэк, и его отказ означает
    ровно то же, что отказ Google — город остался без мест.
    """
    count = settings.AI_POI_FALLBACK_COUNT
    messages = [
        {
            "role": "system",
            "content": (
                "Ты справочник реальных мест мира. Отвечаешь только JSON. "
                "Никогда не выдумываешь несуществующие места: если не знаешь "
                "город, возвращаешь пустой список."
            ),
        },
        {"role": "user", "content": _build_prompt(city_name, country_name, count)},
    ]

    for attempt in range(1, MAX_INVENTION_ATTEMPTS + 1):
        try:
            response = await gen_client.with_options(
                timeout=INVENTION_TIMEOUT_SECONDS
            ).chat.completions.create(
                model=settings.AI_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=4000,
            )
            raw = response.choices[0].message.content if response.choices else None
            places = _parse(raw)
            logger.info(
                "AI назвал %d мест для города '%s' (попытка %d)",
                len(places), city_name, attempt,
            )
            return places
        except RETRYABLE_AI_ERRORS as e:
            logger.warning(
                "AI-фолбэк для '%s': попытка %d/%d не удалась — %s: %s",
                city_name, attempt, MAX_INVENTION_ATTEMPTS, type(e).__name__, e,
            )
        except Exception as e:
            logger.error(
                "AI-фолбэк для '%s' не сработал — %s: %s",
                city_name, type(e).__name__, e,
            )
            return []

    return []
