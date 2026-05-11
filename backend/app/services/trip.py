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
        
        
    async def finalize_route(
        self,
        trip_id: uuid.UUID,
        user_id: uuid.UUID,
        day_number: int, # <--- НОВЫЙ ПАРАМЕТР
        selected_poi_ids: list[uuid.UUID]
    ) -> Trip:
        """
        Финализирует маршрут (FR 2.10) для конкретного дня с умной логистической сортировкой.
        """
        import math
        from sqlalchemy import select
        from app.core.exceptions import NotFoundException
        from app.models.trip import TripPOI
        from app.models.poi import POI

        # 1. Проверяем, что поездка существует и принадлежит юзеру
        trip = await self.trip_repo.get_by_user_and_id(trip_id, user_id)
        if not trip:
            raise NotFoundException("Trip not found")

        if not selected_poi_ids:
            sorted_ids = []
        else:
            # 2. Загружаем координаты выбранных мест
            result_pois = await self.session.execute(
                select(POI).where(POI.id.in_(selected_poi_ids))
            )
            pois_data = result_pois.scalars().all()
            poi_map = {poi.id: poi for poi in pois_data}

            # 3. Функция расстояния (Гаверсинус)
            def calc_distance(id1: uuid.UUID, id2: uuid.UUID) -> float:
                p1, p2 = poi_map.get(id1), poi_map.get(id2)
                if not p1 or not p2 or p1.lat is None or p1.lon is None or p2.lat is None or p2.lon is None:
                    return float('inf')
                
                R = 6371.0 
                lat1, lon1 = math.radians(p1.lat), math.radians(p1.lon)
                lat2, lon2 = math.radians(p2.lat), math.radians(p2.lon)
                
                a = math.sin((lat2 - lat1) / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2)**2
                return R * (2 * math.asin(math.sqrt(a)))

            # 4. Алгоритм "Ближайшего соседа"
            current_id = selected_poi_ids[0]
            unvisited = set(selected_poi_ids[1:])
            sorted_ids = [current_id]

            while unvisited:
                next_id = min(unvisited, key=lambda x: calc_distance(current_id, x))
                sorted_ids.append(next_id)
                unvisited.remove(next_id)
                current_id = next_id

        # 5. Получаем все места пула ТОЛЬКО ДЛЯ ЭТОГО ДНЯ
        result_tp = await self.session.execute(
            select(TripPOI).where(
                TripPOI.trip_id == trip_id,
                TripPOI.day_number == day_number # <--- ФИЛЬТР ПО ДНЮ
            )
        )
        trip_pois = result_tp.scalars().all()

        # 6. Применяем новые порядковые номера
        for tp in trip_pois:
            if tp.poi_id in sorted_ids:
                tp.is_selected = True
                tp.sequence_order = float(sorted_ids.index(tp.poi_id) + 1)
            else:
                tp.is_selected = False
                tp.sequence_order = None

        await self.session.commit()

        # 7. Возвращаем обновленную поездку
        return await self.trip_repo.get_with_details(trip_id)

    async def auto_finalize_main_pois(
        self, 
        trip_id: uuid.UUID, 
        user_id: uuid.UUID,
        day_number: int # <--- НОВЫЙ ПАРАМЕТР
    ) -> Trip:
        """
        Автоматически финализирует маршрут на указанный день, 
        выбирая только 'main' POI.
        """
        from sqlalchemy import select
        from app.models.trip import TripPOI

        # 1. Находим 'main' места только для текущего дня
        result = await self.session.execute(
            select(TripPOI.poi_id).where(
                TripPOI.trip_id == trip_id,
                TripPOI.poi_status == "main",
                TripPOI.day_number == day_number # <--- ФИЛЬТР ПО ДНЮ
            )
        )
        main_poi_ids = result.scalars().all()

        # 2. Передаем day_number дальше в finalize_route
        return await self.finalize_route(trip_id, user_id, day_number, main_poi_ids)
    
    # app/services/trip.py

# app/services/trip.py

    async def remove_poi_from_day(self, trip_id: uuid.UUID, user_id: uuid.UUID, poi_id: uuid.UUID) -> None:
        """
        Удаляет место из активного маршрута пользователя.
        """
        # 1. Используем trip_repo вместо несуществующего self.get
        trip = await self.trip_repo.get_by_user_and_id(trip_id, user_id)
        if not trip:
            raise NotFoundException("Trip not found or access denied")

        from sqlalchemy import update
        from app.models.trip import TripPOI 

        # 2. Используем self.session вместо self.db
        stmt = (
            update(TripPOI)
            .where(TripPOI.trip_id == trip_id)
            .where(TripPOI.poi_id == poi_id)
            .values(
                is_selected=False,
                poi_status="additional",
                sequence_order=None
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()