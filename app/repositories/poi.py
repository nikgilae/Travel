# Репозиторий для работы с таблицей pois (Points of Interest).
# Содержит стандартные CRUD операции из BaseRepository плюс
# пространственный запрос get_nearby — поиск мест в радиусе
# через PostGIS функцию ST_DWithin.

from uuid import UUID

from geoalchemy2.functions import ST_DWithin, ST_GeogFromWKB, ST_MakePoint, ST_SetSRID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.poi import POI
from app.models.rule import POIRule
from app.repositories.base import BaseRepository


class POIRepository(BaseRepository[POI]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(POI, session)

    async def get_with_rules(self, poi_id: UUID) -> POI | None:
        # Загружаем POI вместе с его правилами за один запрос.
        # joinedload(POI.rules) — подгружает список POIRule.
        # joinedload(POI.rules, POIRule.rule) — цепочка:
        # сразу подгружает и сам Rule внутри каждого POIRule.
        result = await self.session.execute(
            select(POI)
            .where(POI.id == poi_id)
            .options(
                joinedload(POI.rules).joinedload(POIRule.rule)
            )
        )
        return result.scalar_one_or_none()

    async def get_nearby(
        self,
        lat: float,
        lon: float,
        radius_meters: float,
    ) -> list[POI]:
        # Поиск POI в заданном радиусе от координат пользователя.
        # Использует PostGIS функции для работы с геометрией.
        #
        # ST_MakePoint(lon, lat) — создаёт точку из координат.
        #   Важно: сначала долгота (lon), потом широта (lat) — это стандарт PostGIS.
        #
        # ST_SetSRID(..., 4326) — указываем систему координат WGS84
        #   (та же что используется в GPS и Google Maps).
        #
        # ST_GeogFromWKB(...) — конвертируем геометрию в geography тип.
        #   Geography учитывает кривизну Земли — расстояния точнее
        #   чем в плоской геометрии. Критично для больших расстояний.
        #
        # ST_DWithin(a, b, radius) — возвращает True если расстояние
        #   между a и b меньше radius (в метрах для geography типа).
        result = await self.session.execute(
            select(POI).where(
                ST_DWithin(
                    ST_GeogFromWKB(POI.geom),
                    ST_GeogFromWKB(
                        ST_SetSRID(ST_MakePoint(lon, lat), 4326)
                    ),
                    radius_meters,
                )
            )
        )
        return list(result.scalars().all())

    async def get_by_ids(self, ids: list[UUID]) -> list[POI]:
        # Загрузка нескольких POI по списку ID за один запрос.
        # Используется когда нужно получить конкретный набор мест —
        # например все POI из маршрута пользователя.
        # in_() генерирует SQL: WHERE id IN ('uuid1', 'uuid2', ...)
        result = await self.session.execute(
            select(POI).where(POI.id.in_(ids))
        )
        return list(result.scalars().all())