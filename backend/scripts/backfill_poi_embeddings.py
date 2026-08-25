"""
Backfill embeddings for existing POI rows.

Идемпотентный: без --force пересчитывает только POI с embedding IS NULL.
Батчи по городу — commit после каждого города, чтобы частичный сбой не терял
уже посчитанное по предыдущим городам.

Run: uv run python -m scripts.backfill_poi_embeddings [--force]
"""

import argparse
import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.geography import City
from app.models.poi import POI
from app.services.embedding import build_poi_text, get_embedding

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def backfill(session: AsyncSession, force: bool = False) -> None:
    """Основная логика backfill'а. Принимает сессию — тестируется без AsyncSessionLocal."""
    city_ids = (await session.execute(select(City.id))).scalars().all()

    total_computed = 0
    total_skipped_empty = 0

    for city_id in city_ids:
        query = select(POI).where(POI.city_id == city_id)
        if not force:
            query = query.where(POI.embedding.is_(None))
        pois = (await session.execute(query)).scalars().all()

        if not pois:
            continue

        computed_in_city = 0
        for poi in pois:
            text = build_poi_text(poi)
            if not text.strip():
                logger.warning("POI %s has no text content — skipping", poi.id)
                total_skipped_empty += 1
                continue
            poi.embedding = await get_embedding(text)
            computed_in_city += 1

        await session.commit()
        total_computed += computed_in_city
        logger.info(
            "city %s: посчитано %d эмбеддингов (из %d кандидатов)",
            city_id, computed_in_city, len(pois),
        )

    logger.info(
        "Готово: посчитано %d эмбеддингов, пропущено (нет текста) %d",
        total_computed, total_skipped_empty,
    )


async def main(force: bool = False) -> None:
    async with AsyncSessionLocal() as session:
        await backfill(session, force=force)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Пересчитать все POI, включая уже имеющие embedding",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(force=args.force))
