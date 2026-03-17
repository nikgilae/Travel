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

    Содержит стандартные CRUD операции из BaseRepository
    и пространственный запрос get_nearby через PostGIS функцию
    ST_DWithin для поиска мест в заданном радиусе.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(POI, session)

    async def get_with_rules(self, poi_id: UUID) -> POI | None:
        """
        Получить POI вместе с его правилами за один запрос.

        Использует цепочку joinedload: POI -> POIRule -> Rule
        чтобы избежать N+1 запросов при отображении карточки места.

        Parameters
        ----------
        poi_id : UUID
            UUID точки интереса.

        Returns
        -------
        POI | None
            Объект POI с заполненными rules и вложенными rule,
            иначе None если не найден.
        """
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
        """
        Найти POI в заданном радиусе от координат пользователя.

        Использует PostGIS функции для точного расчёта расстояний
        с учётом кривизны Земли через тип geography.
        Запрос использует пространственный индекс GIST автоматически.

        Parameters
        ----------
        lat : float
            Широта пользователя (от -90 до +90).
        lon : float
            Долгота пользователя (от -180 до +180).
        radius_meters : float
            Радиус поиска в метрах.

        Returns
        -------
        list[POI]
            Список POI находящихся в радиусе от указанных координат.

        Notes
        -----
        ST_MakePoint принимает (lon, lat) — сначала долгота,
        потом широта. Это стандарт PostGIS (порядок X, Y).
        ST_GeogFromWKB конвертирует geometry в geography для
        точного расчёта расстояний на сфере.
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

        Используется когда нужно получить конкретный набор мест,
        например все POI из маршрута пользователя.

        Parameters
        ----------
        ids : list[UUID]
            Список UUID точек интереса.

        Returns
        -------
        list[POI]
            Список найденных POI. Порядок не гарантирован.
        """
        result = await self.session.execute(
            select(POI).where(POI.id.in_(ids))
        )
        return list(result.scalars().all())