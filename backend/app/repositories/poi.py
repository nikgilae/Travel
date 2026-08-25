import random
from uuid import UUID

from geoalchemy2.functions import ST_DWithin, ST_GeogFromWKB, ST_MakePoint, ST_SetSRID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.poi import POI
from app.models.rule import POIRule
from app.repositories.base import BaseRepository


class POIRepository(BaseRepository[POI]):
    """
    Репозиторий для работы с таблицей pois.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(POI, session)

    async def get_by_city(self, city_id: UUID) -> list[POI]:
        """
        Получить все POI для конкретного города.
        """
        result = await self.session.execute(
            select(self.model).where(self.model.city_id == city_id)
        )
        return list(result.scalars().all())

    async def get_with_rules(self, poi_id: UUID) -> POI | None:
        """
        Получить POI вместе с его правилами за один запрос.
        """
        result = await self.session.execute(
            select(POI)
            .where(POI.id == poi_id)
            .options(
                joinedload(POI.rules).joinedload(POIRule.rule)
            )
        )
        return result.unique().scalar_one_or_none()

    async def get_nearby(
        self,
        lat: float,
        lon: float,
        radius_meters: float,
    ) -> list[POI]:
        """
        Найти POI в заданном радиусе от координат пользователя.
        """
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
        """
        Загрузить несколько POI по списку UUID за один запрос.
        """
        result = await self.session.execute(
            select(POI).where(POI.id.in_(ids))
        )
        return list(result.scalars().all())

    async def get_relevant_for_trip(
        self, city_id: UUID, query_embedding: list[float], limit: int
    ) -> list[POI]:
        """
        Top-k POI города по косинусной близости к query_embedding.

        Graceful degradation: если POI с embedding в городе меньше limit,
        дозаполняет остаток случайной выборкой из POI без embedding — тот же
        random.sample, что раньше применялся к городу целиком.
        """
        result = await self.session.execute(
            select(POI)
            .where(POI.city_id == city_id, POI.embedding.isnot(None))
            .order_by(POI.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        relevant = list(result.scalars().all())

        if len(relevant) < limit:
            missing = limit - len(relevant)
            result = await self.session.execute(
                select(POI).where(POI.city_id == city_id, POI.embedding.is_(None))
            )
            without_embedding = list(result.scalars().all())
            relevant += random.sample(without_embedding, min(missing, len(without_embedding)))

        return relevant