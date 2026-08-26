"""
Обогащение текста POI через Google Place Details (Итерация 4, RAG-POI-PLAN.md).

Приоритет источников (см. app.services.poi_description.build_ai_description):
editorial_summary Google → саммари отзывов → текущий шаблон по категории.

Идемпотентный: без --force пропускает POI с уже заполненным ai_description.
Батчи по городу — commit после каждого города, чтобы частичный сбой не терял
уже обогащённое по предыдущим городам. Параллелизм вызовов к Google ограничен
семафором (--concurrency), запросов может быть тысячи — не десятки, как у
enrich_city_from_google. Когда текст реально меняется (источник не
category_fallback) — embedding обнуляется, чтобы существующий
backfill_poi_embeddings.py (без правок) пересчитал его на новом тексте.

Run: uv run python -m scripts.enrich_poi_descriptions [--force] [--concurrency N]
"""

import argparse
import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.database import AsyncSessionLocal
from app.core.maps import GoogleMapsClient
from app.models.geography import City
from app.models.poi import POI
from app.services.poi_description import build_ai_description

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_CONCURRENCY = 5


async def _enrich_one(client: GoogleMapsClient, poi: POI, semaphore: asyncio.Semaphore) -> None:
    """Обогатить один POI. Не поднимает исключение — сбой не должен ронять весь батч."""
    try:
        async with semaphore:
            place_details = await client.get_place_details(poi.google_place_id)

        text, source = await build_ai_description(place_details, poi.description or "")

        poi.ai_description = text
        poi.ai_description_source = source
        if source != "category_fallback":
            poi.embedding = None
    except Exception as e:
        logger.warning("Не удалось обогатить POI %s: %s: %s", poi.id, type(e).__name__, e)


async def enrich(
    session: AsyncSession, force: bool = False, concurrency: int = DEFAULT_CONCURRENCY
) -> None:
    """Основная логика обогащения. Принимает сессию — тестируется без AsyncSessionLocal."""
    if not settings.GOOGLE_MAPS_ENABLED:
        logger.warning("GOOGLE_MAPS_ENABLED=false — обогащение пропущено")
        return

    client = GoogleMapsClient()
    semaphore = asyncio.Semaphore(concurrency)

    city_ids = (await session.execute(select(City.id))).scalars().all()

    total_enriched = 0
    total_skipped_no_place_id = 0

    for city_id in city_ids:
        query = select(POI).where(POI.city_id == city_id)
        if not force:
            query = query.where(POI.ai_description.is_(None))
        pois = (await session.execute(query)).scalars().all()

        if not pois:
            continue

        targets = [poi for poi in pois if poi.google_place_id]
        total_skipped_no_place_id += len(pois) - len(targets)

        await asyncio.gather(*[_enrich_one(client, poi, semaphore) for poi in targets])

        await session.commit()
        total_enriched += len(targets)
        logger.info(
            "city %s: обогащено %d POI (из %d кандидатов)",
            city_id, len(targets), len(pois),
        )

    logger.info(
        "Готово: обогащено %d POI, пропущено (нет google_place_id) %d",
        total_enriched, total_skipped_no_place_id,
    )


async def main(force: bool = False, concurrency: int = DEFAULT_CONCURRENCY) -> None:
    async with AsyncSessionLocal() as session:
        await enrich(session, force=force, concurrency=concurrency)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Пересчитать все POI, включая уже обогащённые",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help="Максимум параллельных запросов к Google Place Details",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(force=args.force, concurrency=args.concurrency))
