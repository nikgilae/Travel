import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, AlreadyExistsException, ForbiddenException
from app.models.trip import Trip, TripPOI
from app.repositories.trip import TripRepository, TripPOIRepository
from app.repositories.poi import POIRepository
from app.repositories.rule import POIRuleRepository
from app.repositories.geography import CountryRepository, CityRepository


class TripService:
    """
    Сервис управления поездками.

    Оркестрирует репозитории для создания поездок,
    добавления мест в маршрут и генерации contextual warnings.

    Parameters
    ----------
    session : AsyncSession
        Асинхронная сессия БД.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.trip_repo = TripRepository(session)
        self.trip_poi_repo = TripPOIRepository(session)
        self.poi_repo = POIRepository(session)
        self.poi_rule_repo = POIRuleRepository(session)
        self.country_repo = CountryRepository(session)
        self.city_repo = CityRepository(session)

    async def create(
        self,
        user_id: uuid.UUID,
        country_id: uuid.UUID,
        city_id: uuid.UUID,
        purpose: str,
        budget: str,
        group_size: int,
        other_information: list[str] | None,
        start_date,
        end_date,
    ) -> Trip:
        """
        Создать новую поездку для пользователя.

        Проверяет существование страны и города перед созданием.

        Parameters
        ----------
        user_id : uuid.UUID
            UUID владельца поездки.
        country_id : uuid.UUID
            UUID страны назначения.
        city_id : uuid.UUID
            UUID города назначения.
        purpose : str
            Цель поездки.
        budget : str
            Уровень бюджета.
        group_size : int
            Количество путешественников.
        other_information : list[str] or None
            Дополнительные предпочтения.
        start_date : date or None
            Дата начала.
        end_date : date or None
            Дата окончания.

        Returns
        -------
        Trip
            Созданный объект поездки.

        Raises
        ------
        NotFoundException
            Если страна или город не найдены.
        """
        if not await self.country_repo.get_by_id(country_id):
            raise NotFoundException("Country not found")
        if not await self.city_repo.get_by_id(city_id):
            raise NotFoundException("City not found")

        trip = await self.trip_repo.create(
            user_id=user_id,
            country_id=country_id,
            city_id=city_id,
            purpose=purpose,
            budget=budget,
            group_size=group_size,
            other_information=other_information,
            start_date=start_date,
            end_date=end_date,
        )
        await self.session.commit()
        return trip

    async def get_user_trips(self, user_id: uuid.UUID) -> list[Trip]:
        """
        Получить все поездки пользователя.

        Parameters
        ----------
        user_id : uuid.UUID
            UUID пользователя.

        Returns
        -------
        list[Trip]
            Список поездок пользователя.
        """
        return await self.trip_repo.get_by_user_id(user_id)

    async def get_with_details(
        self,
        trip_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Trip:
        """
        Получить поездку с деталями только если принадлежит пользователю.

        Parameters
        ----------
        trip_id : uuid.UUID
            UUID поездки.
        user_id : uuid.UUID
            UUID запрашивающего пользователя.

        Returns
        -------
        Trip
            Объект поездки с заполненными country, city, pois.

        Raises
        ------
        NotFoundException
            Если поездка не найдена или не принадлежит пользователю.
        """
        trip = await self.trip_repo.get_by_user_and_id(trip_id, user_id)
        if not trip:
            raise NotFoundException("Trip not found")
        return await self.trip_repo.get_with_details(trip_id)

    async def update(
        self,
        trip_id: uuid.UUID,
        user_id: uuid.UUID,
        **kwargs,
    ) -> Trip:
        """
        Обновить поездку.

        Обновляет только переданные поля (partial update).
        Проверяет владельца перед обновлением.

        Parameters
        ----------
        trip_id : uuid.UUID
            UUID поездки.
        user_id : uuid.UUID
            UUID пользователя — должен быть владельцем.
        **kwargs
            Поля для обновления. Передаются из TripUpdate схемы
            через model_dump(exclude_unset=True).

        Returns
        -------
        Trip
            Обновлённый объект поездки.

        Raises
        ------
        NotFoundException
            Если поездка не найдена или не принадлежит пользователю.
        """
        trip = await self.trip_repo.get_by_user_and_id(trip_id, user_id)
        if not trip:
            raise NotFoundException("Trip not found")

        updated = await self.trip_repo.update(trip_id, **kwargs)
        await self.session.commit()
        return updated

    async def delete(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """
        Удалить поездку.

        Parameters
        ----------
        trip_id : uuid.UUID
            UUID поездки.
        user_id : uuid.UUID
            UUID пользователя — должен быть владельцем.

        Raises
        ------
        NotFoundException
            Если поездка не найдена или не принадлежит пользователю.
        """
        trip = await self.trip_repo.get_by_user_and_id(trip_id, user_id)
        if not trip:
            raise NotFoundException("Trip not found")

        await self.trip_repo.delete(trip_id)
        await self.session.commit()

    async def add_poi(
        self,
        trip_id: uuid.UUID,
        user_id: uuid.UUID,
        poi_id: uuid.UUID,
        sequence_order: float,
        planned_start_time,
    ) -> tuple[TripPOI, list]:
        """
        Добавить POI в маршрут поездки.

        Ключевой метод Contextual Engine — при добавлении места
        автоматически загружает правила POI и возвращает их
        как contextual_warnings для отображения пользователю.

        Parameters
        ----------
        trip_id : uuid.UUID
            UUID поездки.
        user_id : uuid.UUID
            UUID пользователя — должен быть владельцем поездки.
        poi_id : uuid.UUID
            UUID точки интереса для добавления.
        sequence_order : float
            Порядковый номер в маршруте.
        planned_start_time : datetime or None
            Запланированное время посещения.

        Returns
        -------
        tuple[TripPOI, list]
            Кортеж из объекта TripPOI и списка POIRule с правилами.
            Список правил используется как contextual_warnings в ответе.

        Raises
        ------
        NotFoundException
            Если поездка или POI не найдены.
        AlreadyExistsException
            Если это место уже есть в маршруте.
        """
        trip = await self.trip_repo.get_by_user_and_id(trip_id, user_id)
        if not trip:
            raise NotFoundException("Trip not found")

        poi = await self.poi_repo.get_by_id(poi_id)
        if not poi:
            raise NotFoundException("POI not found")

        existing = await self.trip_poi_repo.get_by_trip_and_poi(trip_id, poi_id)
        if existing:
            raise AlreadyExistsException("POI already in this trip")

        trip_poi = await self.trip_poi_repo.create(
            trip_id=trip_id,
            poi_id=poi_id,
            sequence_order=sequence_order,
            planned_start_time=planned_start_time,
        )
        await self.session.commit()

        # Загружаем правила POI для contextual warnings
        poi_rules = await self.poi_rule_repo.get_by_poi(poi_id)

        return trip_poi, poi_rules

    async def remove_poi(
        self,
        trip_id: uuid.UUID,
        user_id: uuid.UUID,
        poi_id: uuid.UUID,
    ) -> None:
        """
        Удалить POI из маршрута.

        Parameters
        ----------
        trip_id : uuid.UUID
            UUID поездки.
        user_id : uuid.UUID
            UUID пользователя — должен быть владельцем.
        poi_id : uuid.UUID
            UUID точки интереса для удаления.

        Raises
        ------
        NotFoundException
            Если поездка не найдена или POI не в маршруте.
        """
        trip = await self.trip_repo.get_by_user_and_id(trip_id, user_id)
        if not trip:
            raise NotFoundException("Trip not found")

        deleted = await self.trip_poi_repo.delete_by_trip_and_poi(trip_id, poi_id)
        if not deleted:
            raise NotFoundException("POI not found in this trip")

        await self.session.commit()