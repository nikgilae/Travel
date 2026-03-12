# Репозитории для работы с таблицами trips и trip_pois.
# TripRepository — CRUD операции с поездками пользователя.
# TripPOIRepository — управление местами внутри маршрута:
# добавление, удаление, изменение порядка через Float sequence_order.

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.trip import Trip, TripPOI
from app.models.poi import POI
from app.models.geography import Country, City
from app.repositories.base import BaseRepository


class TripRepository(BaseRepository[Trip]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Trip, session)

    async def get_by_user_id(self, user_id: UUID) -> list[Trip]:
        # Все поездки конкретного пользователя.
        # Используется на главной странице — список поездок.
        result = await self.session.execute(
            select(Trip).where(Trip.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_with_details(self, trip_id: UUID) -> Trip | None:
        # Загружаем поездку со всеми связанными данными за один запрос:
        # страна, город, и список мест маршрута вместе с POI.
        # Используется на странице конкретной поездки.
        result = await self.session.execute(
            select(Trip)
            .where(Trip.id == trip_id)
            .options(
                # Загружаем страну и город — нужны для отображения заголовка.
                joinedload(Trip.country),
                joinedload(Trip.city),
                # Цепочка: TripPOI → POI.
                # Загружаем места маршрута сразу с данными POI.
                joinedload(Trip.pois).joinedload(TripPOI.poi),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_id(
        self,
        trip_id: UUID,
        user_id: UUID,
    ) -> Trip | None:
        # Получаем поездку только если она принадлежит этому пользователю.
        # Используется перед любым изменением поездки — защита от того
        # чтобы один пользователь не мог изменить поездку другого.
        result = await self.session.execute(
            select(Trip).where(
                Trip.id == trip_id,
                Trip.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()


class TripPOIRepository(BaseRepository[TripPOI]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(TripPOI, session)

    async def get_by_trip(self, trip_id: UUID) -> list[TripPOI]:
        # Все места маршрута отсортированные по порядку.
        # ORDER BY sequence_order — места идут в правильном порядке:
        # 1.0, 1.5, 2.0, 3.0 и т.д.
        result = await self.session.execute(
            select(TripPOI)
            .where(TripPOI.trip_id == trip_id)
            .order_by(TripPOI.sequence_order)
            .options(joinedload(TripPOI.poi))
        )
        return list(result.scalars().all())

    async def get_last_sequence_order(self, trip_id: UUID) -> float:
        # Получаем максимальный sequence_order в маршруте.
        # Нужно чтобы добавить новое место в конец маршрута:
        # новый sequence_order = последний + 1.0
        # Если маршрут пустой — возвращаем 0.0, первое место получит 1.0.
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
        # Проверяем существует ли уже это место в маршруте.
        # Используется перед добавлением — чтобы не дублировать места.
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
        # Удаление конкретного места из маршрута.
        # У TripPOI нет отдельного id — составной PK из trip_id + poi_id.
        # Поэтому нельзя использовать базовый delete(id) из BaseRepository —
        # нужен специальный метод с двумя параметрами.
        instance = await self.get_by_trip_and_poi(trip_id, poi_id)
        if not instance:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True