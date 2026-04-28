import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID

from app.core.exceptions import NotFoundException
from app.models.poi import POI
from app.repositories.poi import POIRepository
from app.repositories.rule import POIRuleRepository
import logging
from sqlalchemy import select
from app.core.maps import GoogleMapsClient

logger = logging.getLogger(__name__)


class POIService:
    """
    Сервис управления точками интереса.

    Содержит логику создания POI, поиска в радиусе
    и получения POI с правилами.

    Parameters
    ----------
    session : AsyncSession
        Асинхронная сессия БД.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.poi_repo = POIRepository(session)
        self.poi_rule_repo = POIRuleRepository(session)

    async def create(
        self,
        name: str,
        description: str | None,
        information: str | None,
        lat: float | None,
        lon: float | None,
        is_indoor: bool,
        city_id: uuid.UUID,
        
    ) -> POI:
        """
        Создать новую точку интереса.

        Если переданы координаты lat/lon — формирует геометрию
        PostGIS через ST_MakePoint для пространственных запросов.

        Parameters
        ----------
        name : str
            Название места.
        description : str or None
            Краткое описание.
        information : str or None
            Подробная информация.
        lat : float or None
            Широта. Если None — geom не заполняется.
        lon : float or None
            Долгота. Если None — geom не заполняется.
        is_indoor : bool
            True если место внутри здания.

        Returns
        -------
        POI
            Созданный объект POI.
        """
        geom = None
        if lat is not None and lon is not None:
            geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326)

        poi = await self.poi_repo.create(
            name=name,
            description=description,
            information=information,
            geom=geom,
            is_indoor=is_indoor,
            city_id=city_id,
        )
        await self.session.commit()
        return poi

    async def get_all(self) -> list[POI]:
        """
        Получить все POI.

        Returns
        -------
        list[POI]
            Список всех точек интереса.
        """
        return await self.poi_repo.get_all()

    async def get_by_id(self, poi_id: uuid.UUID) -> POI:
        """
        Получить POI по ID.

        Parameters
        ----------
        poi_id : uuid.UUID
            UUID точки интереса.

        Returns
        -------
        POI
            Объект POI.

        Raises
        ------
        NotFoundException
            Если POI не найден.
        """
        poi = await self.poi_repo.get_by_id(poi_id)
        if not poi:
            raise NotFoundException("POI not found")
        return poi

    async def get_with_rules(self, poi_id: uuid.UUID) -> POI:
        """
        Получить POI с правилами посещения.

        Parameters
        ----------
        poi_id : uuid.UUID
            UUID точки интереса.

        Returns
        -------
        POI
            Объект POI с заполненными rules.

        Raises
        ------
        NotFoundException
            Если POI не найден.
        """
        poi = await self.poi_repo.get_with_rules(poi_id)
        if not poi:
            raise NotFoundException("POI not found")
        return poi

    async def get_nearby(
        self,
        lat: float,
        lon: float,
        radius_meters: float,
    ) -> list[POI]:
        """
        Найти POI в заданном радиусе от координат.

        Parameters
        ----------
        lat : float
            Широта пользователя.
        lon : float
            Долгота пользователя.
        radius_meters : float
            Радиус поиска в метрах.

        Returns
        -------
        list[POI]
            Список POI в радиусе.
        """
        return await self.poi_repo.get_nearby(lat, lon, radius_meters)
    
    async def enrich_city_from_google(self, city_id: uuid.UUID, city_name: str) -> int:
        """
        Автоматически наполняет базу местами для заданного города через Google Maps.
        """
        client = GoogleMapsClient()
        
        # Разные типы запросов, чтобы собрать разнообразный пул мест
        search_queries = [
            f"Главные достопримечательности {city_name}",
            f"Интересные необычные места {city_name}",
            f"Лучшие рестораны и кафе {city_name}",
            f"Парки и природа {city_name}"
            f"Музеи {city_name}"
            f"Экстримальные места{city_name}"
            f"Пешие маршруты {city_name}"
        ]

        added_count = 0

        for query in search_queries:
            places = await client.search_places(query)
            
            for place in places:
                name = place.get("name")
                lat = place.get("coordinates", {}).get("lat")
                lon = place.get("coordinates", {}).get("lng")
                
                if not name or not lat or not lon:
                    continue

                # Проверяем, нет ли уже такого места в базе (простейшая защита от дублей)
                # В идеале нужно искать через репозиторий, но для скорости напишем прямо тут
                existing = await self.session.execute(
                    select(self.poi_repo.model).where(
                        self.poi_repo.model.name == name,
                        self.poi_repo.model.city_id == city_id
                    )
                )
                if existing.scalar_one_or_none():
                    continue # Такое место уже есть, пропускаем

                # Создаем новое место (используем твой метод create, который генерит PostGIS точку)
                await self.create(
                    name=name,
                    description=place.get("description", "Интересное место"),
                    information=place.get("information", ""),
                    lat=lat,
                    lon=lon,
                    is_indoor=place.get("is_indoor", False),
                    city_id=city_id
                )
                added_count += 1

        return added_count