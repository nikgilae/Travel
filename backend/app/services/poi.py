import asyncio
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
        google_place_id: str | None = None,
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
            google_place_id=google_place_id,
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
        Наполняет базу местами для города через Google Maps.
        Все запросы к API выполняются параллельно, один commit в конце.
        """
        client = GoogleMapsClient()

        search_queries = [
            f"Главные достопримечательности {city_name}",
            f"Исторические места и памятники {city_name}",
            f"Смотровые площадки {city_name}",
            f"Религиозные места храмы церкви {city_name}",
            f"Парки и скверы {city_name}",
            f"Природные достопримечательности {city_name}",
            f"Пляжи и набережные {city_name}",
            f"Активный отдых экскурсии {city_name}",
            f"Музеи {city_name}",
            f"Художественные галереи {city_name}",
            f"Театры и концертные залы {city_name}",
            f"Лучшие рестораны {city_name}",
            f"Кафе и кофейни {city_name}",
            f"Уличная еда рынки {city_name}",
            f"Традиционная кухня ресторан {city_name}",
            f"Бары и пабы {city_name}",
            f"Ночные клубы живая музыка {city_name}",
            f"Сувенирные магазины рынки {city_name}",
            f"Спа и массаж {city_name}",
            f"Зоопарк аквариум аттракционы {city_name}",
        ]

        # Все запросы к Google Maps параллельно
        raw_results = await asyncio.gather(
            *[client.search_places(q) for q in search_queries],
            return_exceptions=True,
        )

        # Дедупликация в памяти по google_place_id до обращения к БД
        seen_place_ids: set[str] = set()
        candidates: list[dict] = []

        for result in raw_results:
            if isinstance(result, Exception):
                logger.warning("Запрос к Google Maps не удался: %s", result)
                continue
            for place in result:
                name = place.get("name")
                lat = place.get("coordinates", {}).get("lat")
                lon = place.get("coordinates", {}).get("lng")
                if not name or not lat or not lon:
                    continue
                gid = place.get("google_place_id")
                if gid:
                    if gid in seen_place_ids:
                        continue
                    seen_place_ids.add(gid)
                candidates.append(place)

        logger.info("Google Maps вернул %d уникальных кандидатов для '%s'", len(candidates), city_name)

        # Проверяем каждый кандидат против БД и добавляем новые
        # Используем poi_repo.create() напрямую — commit один в конце
        added_count = 0
        for place in candidates:
            name = place.get("name")
            lat = place.get("coordinates", {}).get("lat")
            lon = place.get("coordinates", {}).get("lng")
            gid = place.get("google_place_id")

            if gid:
                existing = await self.session.execute(
                    select(self.poi_repo.model).where(
                        self.poi_repo.model.google_place_id == gid
                    )
                )
            else:
                existing = await self.session.execute(
                    select(self.poi_repo.model).where(
                        self.poi_repo.model.name == name,
                        self.poi_repo.model.city_id == city_id
                    )
                )
            if existing.scalar_one_or_none():
                continue

            geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326)
            await self.poi_repo.create(
                name=name,
                description=place.get("description", "Интересное место"),
                information=place.get("information", ""),
                geom=geom,
                is_indoor=place.get("is_indoor", False),
                city_id=city_id,
                google_place_id=gid,
            )
            added_count += 1

        if added_count > 0:
            await self.session.commit()

        return added_count