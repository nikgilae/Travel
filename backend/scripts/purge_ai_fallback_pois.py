"""
Убрать из базы места, названные моделью, а не найденные в Google.

Когда включать: сразу после того, как в Google Cloud вернули биллинг и
AI_POI_FALLBACK_ENABLED переведён в false. Тогда города, наполненные моделью
на время простоя, надо очистить, чтобы Google собрал их заново — по-настоящему,
с координатами и google_place_id.

Что делает: удаляет POI с source='ai_fallback' и сбрасывает last_enriched_at
у затронутых городов, иначе кулдаун не пустит обогащение ещё сутки.

Места, уже попавшие в чей-то маршрут, по умолчанию не трогаются: FK у
trip_pois стоит на ON DELETE CASCADE, то есть удаление места молча вырезало бы
его из чужого сохранённого плана. Их сносит явный --force.

На практике это почти все места города (пул маршрута забирает их целиком),
поэтому обычный порядок такой: сначала прогнать без флагов и посмотреть цифру,
затем решить — подождать, пока эти поездки отживут, или пройтись --force.

Run: uv run python -m scripts.purge_ai_fallback_pois [--dry-run] [--force]
"""

import argparse
import asyncio
import logging

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.geography import City
from app.models.poi import POI
from app.models.trip import TripPOI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AI_FALLBACK_SOURCE = "ai_fallback"


async def purge(session: AsyncSession, dry_run: bool = False, force: bool = False) -> int:
    """Удалить места от модели. Возвращает количество удалённых."""
    query = select(POI.id, POI.city_id).where(POI.source == AI_FALLBACK_SOURCE)
    rows = (await session.execute(query)).all()
    if not rows:
        logger.info("Мест с source=%s не найдено — чистить нечего", AI_FALLBACK_SOURCE)
        return 0

    poi_ids = [r.id for r in rows]
    city_ids = {r.city_id for r in rows}

    used = set((await session.execute(
        select(TripPOI.poi_id).where(TripPOI.poi_id.in_(poi_ids))
    )).scalars().all())

    if used and not force:
        logger.info(
            "%d мест уже стоят в чьих-то маршрутах — оставляю их "
            "(снести можно флагом --force)", len(used),
        )
        poi_ids = [pid for pid in poi_ids if pid not in used]

    logger.info(
        "К удалению %d мест в %d городах%s",
        len(poi_ids), len(city_ids), " (dry-run, ничего не меняю)" if dry_run else "",
    )
    if dry_run or not poi_ids:
        return len(poi_ids)

    await session.execute(delete(POI).where(POI.id.in_(poi_ids)))
    # Без сброса кулдауна Google не придёт в эти города ещё сутки, и человек
    # всё это время будет видеть пустой город вместо настоящих мест.
    await session.execute(
        update(City).where(City.id.in_(city_ids)).values(last_enriched_at=None)
    )
    await session.commit()

    logger.info("Удалено %d мест, кулдаун сброшен у %d городов", len(poi_ids), len(city_ids))
    return len(poi_ids)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="только показать, что будет удалено")
    parser.add_argument("--force", action="store_true", help="удалять и те места, что стоят в маршрутах")
    args = parser.parse_args()

    async with AsyncSessionLocal() as session:
        await purge(session, dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    asyncio.run(main())
