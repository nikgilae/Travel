"""
Фоновое обогащение города местами из Google Maps.

До этого модуля обогащение жило внутри запроса `POST /trips/{id}/generate`
(`app/services/trip_ai.py`, шаг 3) и стоило там: 20 поисковых запросов в
Google, затем по одному вызову эмбеддинга на каждое новое место, подряд.
Для города, которого раньше не было в справочнике, это сотни последовательных
сетевых вызовов внутри запроса с потолком AI_GENERATION_BUDGET_SECONDS=30 с,
при том что фронт рвёт соединение на 45 с. То есть первый человек в новом
городе не получал маршрут в принципе, а не «иногда медленно».

Теперь обогащение — отдельная задача со своей сессией БД:

- создание города (`CityService.create`) заводит её сразу, поэтому пока
  человек доходит по онбордингу до дат, бюджета и интересов, места уже
  подтягиваются;
- генерация только ставит задачу и идёт дальше, не дожидаясь результата;
  ждёт она лишь в одном случае — когда генерировать буквально не из чего
  (см. COLD_START_ENRICH_TIMEOUT_SECONDS в trip_ai.py).

Задачи не переживают перезапуск процесса: обогащение идемпотентно (дедуп по
`google_place_id`), а `last_enriched_at` обновляется только после успешного
прохода, поэтому оборванный заход просто повторится при следующем поводе.
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timedelta

from app.config import settings
from app.core.database import AsyncSessionLocal
from app.models.geography import City
from app.repositories.geography import CityRepository, CountryRepository
from app.repositories.poi import POIRepository
from app.services.poi import POIService
from app.services.poi_invention import invent_city_pois

logger = logging.getLogger(__name__)

# Идущие прямо сейчас обогащения, по одному на город. Служит сразу двум целям:
# не запускать второй заход по тому же городу (два человека выбрали Пхукет
# одновременно) и держать сильную ссылку на задачу — asyncio.create_task сам
# по себе от сборщика мусора её не защищает.
_in_flight: dict[uuid.UUID, asyncio.Task] = {}


def is_due(city: City, has_pois: bool = True) -> bool:
    """
    Нужно ли обогащать этот город сейчас.

    Та же проверка кулдауна, что раньше стояла внутри generate(), вынесенная
    в одно место: её теперь спрашивают и создание города, и генерация.

    Достаточно любого из двух источников мест: Google Places или память
    модели. Выключены оба — заходить незачем.

    Пустому городу кулдаун не помеха. Кулдаун защищает от лишних платных
    запросов по городу, где места уже есть. Если мест ноль, то предыдущий
    заход ничего не принёс (сейчас так заканчивается КАЖДЫЙ заход в Google:
    биллинг выключен), и запирать человека на сутки не за что: он в этом
    городе не может получить маршрут вообще.
    """
    if not (settings.GOOGLE_MAPS_ENABLED or settings.AI_POI_FALLBACK_ENABLED):
        return False
    if not has_pois:
        return True
    if city.last_enriched_at is None:
        return True
    cooldown = timedelta(hours=settings.ENRICH_COOLDOWN_HOURS)
    return (datetime.utcnow() - city.last_enriched_at) >= cooldown


def schedule(city_id: uuid.UUID, city_name: str) -> asyncio.Task | None:
    """
    Поставить обогащение города в фон и сразу вернуть управление.

    Возвращает задачу (в том числе уже идущую по этому городу) либо None,
    если оба источника мест выключены (GOOGLE_MAPS_ENABLED и
    AI_POI_FALLBACK_ENABLED). Вызывающему ждать её не обязательно и по
    умолчанию не нужно.
    """
    if not (settings.GOOGLE_MAPS_ENABLED or settings.AI_POI_FALLBACK_ENABLED):
        logger.info(
            "Источники мест выключены (GOOGLE_MAPS_ENABLED=false, "
            "AI_POI_FALLBACK_ENABLED=false) — обогащение города '%s' пропущено",
            city_name,
        )
        return None

    running = _in_flight.get(city_id)
    if running is not None and not running.done():
        logger.info("Обогащение города '%s' уже идёт — второй заход не завожу", city_name)
        return running

    task = asyncio.create_task(_enrich(city_id, city_name))
    _in_flight[city_id] = task
    task.add_done_callback(lambda _: _in_flight.pop(city_id, None))
    return task


async def _enrich(city_id: uuid.UUID, city_name: str) -> int:
    """
    Один заход обогащения в собственной сессии БД.

    Сессия своя, а не пришедшая из запроса: запрос к этому моменту уже
    ответил, и его сессия закрыта. Ошибки наружу не выпускаются — это фоновая
    задача, ронять ей нечего, а её провал уже обработан на стороне генерации
    (город остаётся с тем набором мест, что был).
    """
    started = time.monotonic()
    async with AsyncSessionLocal() as session:
        try:
            poi_service = POIService(session)

            added = 0
            if settings.GOOGLE_MAPS_ENABLED:
                added = await poi_service.enrich_city_from_google(city_id, city_name)
                await CityRepository(session).update(
                    city_id, last_enriched_at=datetime.utcnow()
                )
                await session.commit()

            # Google ничего не дал, а город так и стоит пустой. Пока биллинг
            # в Google Cloud выключен, это происходит с КАЖДЫМ новым городом,
            # и без фолбэка человек проходит весь онбординг ради сообщения
            # «мест нет». Просим места у модели.
            #
            # Условие намеренно про пустой город, а не про added == 0: у города
            # с местами ноль новинок — это нормальный повторный заход, туда
            # подмешивать выдуманные места незачем.
            if settings.AI_POI_FALLBACK_ENABLED and added == 0:
                city = await CityRepository(session).get_by_id(city_id)
                if city and not await POIRepository(session).get_by_city(city_id):
                    added = await _fill_from_ai(poi_service, city, session)

            logger.info(
                "Обогащение города '%s' завершено: +%d мест за %.1f с",
                city_name, added, time.monotonic() - started,
            )
            return added
        except Exception as e:
            await session.rollback()
            logger.warning(
                "Обогащение города '%s' не удалось за %.1f с — %s: %s",
                city_name, time.monotonic() - started, type(e).__name__, e,
            )
            return 0


async def _fill_from_ai(poi_service: POIService, city, session) -> int:
    """
    Наполнить пустой город местами из памяти модели.

    Возврат ноль — обычный исход, а не сбой: модель могла не знать города
    (опечатка, несуществующее название). Тогда город остаётся пустым, и
    человек получает внятное сообщение вместо выдуманного маршрута.
    """
    country = await CountryRepository(session).get_by_id(city.country_id)
    country_name = country.name if country else ""

    logger.info(
        "Город '%s' пуст после Google — спрашиваем места у модели "
        "(AI_POI_FALLBACK_ENABLED=true)", city.name,
    )
    places = await invent_city_pois(city.name, country_name)
    added = await poi_service.create_invented_pois(city.id, places)
    logger.info(
        "AI-фолбэк: городу '%s' добавлено %d мест (source=ai_fallback)",
        city.name, added,
    )
    return added
