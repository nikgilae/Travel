from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.trip import Trip, TripPOI
from app.repositories.base import BaseRepository


class TripRepository(BaseRepository[Trip]):
    """
    Репозиторий для работы с таблицей trips.

    Содержит методы получения поездок пользователя
    и защиту от доступа к чужим поездкам через
    get_by_user_and_id.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Trip, session)

    async def get_by_user_id(self, user_id: UUID) -> list[Trip]:
        """
        Получить все поездки пользователя.

        Используется на главной странице для отображения
        списка поездок.

        Parameters
        ----------
        user_id : UUID
            UUID пользователя.

        Returns
        -------
        list[Trip]
            Список всех поездок пользователя.
        """
        result = await self.session.execute(
            select(Trip).where(Trip.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_with_details(self, trip_id: UUID) -> Trip | None:
        """
        Получить поездку со всеми связанными данными за один запрос.

        Загружает страну, город и список мест маршрута вместе
        с данными POI через цепочку joinedload.

        Parameters
        ----------
        trip_id : UUID
            UUID поездки.

        Returns
        -------
        Trip | None
            Объект поездки с заполненными country, city и pois,
            иначе None если не найдена.
        """
        result = await self.session.execute(
            select(Trip)
            .where(Trip.id == trip_id)
            .options(
                joinedload(Trip.country),
                joinedload(Trip.city),
                joinedload(Trip.pois).joinedload(TripPOI.poi),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_id(
        self,
        trip_id: UUID,
        user_id: UUID,
    ) -> Trip | None:
        """
        Получить поездку только если она принадлежит пользователю.

        Защита от доступа к чужим поездкам: если пользователь
        запрашивает чужую поездку — возвращает None как будто
        она не существует (не раскрывает факт существования).

        Parameters
        ----------
        trip_id : UUID
            UUID поездки.
        user_id : UUID
            UUID пользователя запрашивающего поездку.

        Returns
        -------
        Trip | None
            Объект поездки если принадлежит пользователю,
            иначе None.
        """
        result = await self.session.execute(
            select(Trip).where(
                Trip.id == trip_id,
                Trip.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()


class TripPOIRepository(BaseRepository[TripPOI]):
    """
    Репозиторий для управления местами в маршруте (таблица trip_pois).

    Составной PK (trip_id + poi_id) требует специальных методов
    удаления и проверки существования — базовый delete(id) не применим.
    sequence_order хранится как Float для вставки мест без перенумерации.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(TripPOI, session)

    async def get_by_trip(self, trip_id: UUID) -> list[TripPOI]:
        """
        Получить все места маршрута отсортированные по порядку.

        Parameters
        ----------
        trip_id : UUID
            UUID поездки.

        Returns
        -------
        list[TripPOI]
            Список мест маршрута отсортированных по sequence_order
            с заполненными данными POI.
        """
        result = await self.session.execute(
            select(TripPOI)
            .where(TripPOI.trip_id == trip_id)
            .order_by(TripPOI.sequence_order)
            .options(joinedload(TripPOI.poi))
        )
        return list(result.scalars().all())

    async def get_last_sequence_order(self, trip_id: UUID) -> float:
        """
        Получить максимальный sequence_order в маршруте.

        Используется для добавления нового места в конец маршрута:
        новый order = последний + 1.0.

        Parameters
        ----------
        trip_id : UUID
            UUID поездки.

        Returns
        -------
        float
            Максимальное значение sequence_order,
            или 0.0 если маршрут пустой.
        """
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.max(TripPOI.sequence_order))
            .where(TripPOI.trip_id == trip_id)
        )
        max_order = result.scalar_one_or_none()
        return max_order if max_order is not None else 0.0

    async def get_by_trip_and_poi(
        self,
        trip_id: UUID,
        poi_id: UUID,
    ) -> TripPOI | None:
        """
        Проверить наличие POI в маршруте.

        Используется перед добавлением места чтобы не
        допустить дублирования в маршруте.

        Parameters
        ----------
        trip_id : UUID
            UUID поездки.
        poi_id : UUID
            UUID точки интереса.

        Returns
        -------
        TripPOI | None
            Объект TripPOI если место уже в маршруте, иначе None.
        """
        result = await self.session.execute(
            select(TripPOI).where(
                TripPOI.trip_id == trip_id,
                TripPOI.poi_id == poi_id,
            )
        )
        return result.scalar_one_or_none()

    async def delete_by_trip_and_poi(
        self,
        trip_id: UUID,
        poi_id: UUID,
    ) -> bool:
        """
        Удалить место из маршрута по составному ключу.

        Нельзя использовать базовый delete(id) так как у TripPOI
        нет отдельного поля id — PK составной (trip_id + poi_id).

        Parameters
        ----------
        trip_id : UUID
            UUID поездки.
        poi_id : UUID
            UUID точки интереса для удаления.

        Returns
        -------
        bool
            True если место найдено и удалено,
            False если места нет в маршруте.
        """
        instance = await self.get_by_trip_and_poi(trip_id, poi_id)
        if not instance:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True