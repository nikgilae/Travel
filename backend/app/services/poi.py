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
from app.services.embedding import build_poi_text, get_embedding

logger = logging.getLogger(__name__)

# get_embedding сам может занять до ~54с (3 попытки × AI_READ_TIMEOUT_SECONDS=18s)
# при деградации провайдера. _set_embedding вызывается синхронно в create() и,
# особенно, в цикле enrich_city_from_google() — там до 20+ кандидатов подряд,
# то есть без этого потолка один медленный провайдер мог бы держать запрос
# генерации маршрута минутами, хотя формально ничего не "падает" (embedding
# просто nullable и добирается backfill'ом). Тот же принцип и число, что
# RAG_RETRIEVAL_TIMEOUT_SECONDS в trip_ai.py.
EMBEDDING_HOOK_TIMEOUT_SECONDS = 5.0

# Сколько эмбеддингов считаем одновременно в _set_embeddings (обогащение
# города). Окно, а не «все разом»: у провайдера свои лимиты, а выигрыш от
# ширины дальше десятка запросов уже незаметен на фоне их задержки.
EMBEDDING_CONCURRENCY = 8


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

    @staticmethod
    async def _set_embedding(poi: POI) -> None:
        """
        Посчитать и проставить embedding для нового POI.

        Не должно ронять создание POI: при сбое или таймауте embedding-вызова
        (сеть, провайдер) — предупреждение в лог, poi.embedding остаётся None.
        Retrieval (Итерация 2) уже спроектирован с graceful degradation на
        такой случай. Жёсткий потолок EMBEDDING_HOOK_TIMEOUT_SECONDS — иначе
        get_embedding сам может занять до ~54с (3 ретрая), а это вызывается
        синхронно в критическом пути generate() (enrich_city_from_google).
        """
        try:
            poi.embedding = await asyncio.wait_for(
                get_embedding(build_poi_text(poi)), timeout=EMBEDDING_HOOK_TIMEOUT_SECONDS
            )
        except Exception as e:
            logger.warning(
                "Не удалось посчитать embedding для POI %s: %s: %s",
                poi.id, type(e).__name__, e,
            )

    async def _set_embeddings(self, pois: list[POI]) -> None:
        """
        То же, что _set_embedding, но для пачки мест сразу.

        Обогащение свежего города добавляет не «20+ кандидатов», как считалось
        при написании EMBEDDING_HOOK_TIMEOUT_SECONDS, а полторы-две сотни, и
        по одному подряд это десятки секунд чистого ожидания сети. Здесь они
        идут параллельно, окном EMBEDDING_CONCURRENCY, чтобы не устраивать
        провайдеру эмбеддингов залп на двести запросов разом.

        Поведение на отказ не меняется: каждый вызов по-прежнему сам гасит
        свою ошибку и оставляет embedding пустым (его доберёт
        scripts/backfill_poi_embeddings.py), поэтому gather здесь не может
        уронить обогащение целиком.
        """
        if not pois:
            return

        semaphore = asyncio.Semaphore(EMBEDDING_CONCURRENCY)

        async def _one(poi: POI) -> None:
            async with semaphore:
                await self._set_embedding(poi)

        await asyncio.gather(*(_one(poi) for poi in pois))

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
        await self._set_embedding(poi)
        await self.session.commit()
        return poi

    async def create_invented_pois(
        self,
        city_id: uuid.UUID,
        places: list[dict],
    ) -> int:
        """
        Сохранить места, названные AI-моделью (app.services.poi_invention).

        Отличий от обогащения через Google два: у мест нет google_place_id,
        поэтому дедуп идёт по названию внутри города, и каждое помечается
        source='ai_fallback' — по этому признаку их вычищают, когда Places API
        снова заработает.

        Parameters
        ----------
        city_id : uuid.UUID
            Город, которому принадлежат места.
        places : list[dict]
            Разобранный ответ модели: name, description, information,
            lat, lng, is_indoor.

        Returns
        -------
        int
            Сколько мест реально добавлено.
        """
        if not places:
            return 0

        existing = await self.poi_repo.get_by_city(city_id)
        known = {p.name.strip().lower() for p in existing}

        created: list[POI] = []
        for place in places:
            name = place["name"]
            if name.strip().lower() in known:
                continue
            known.add(name.strip().lower())

            geom = None
            if place.get("lat") is not None and place.get("lng") is not None:
                geom = ST_SetSRID(ST_MakePoint(place["lng"], place["lat"]), 4326)

            poi = await self.poi_repo.create(
                name=name,
                description=place.get("description") or "Интересное место",
                information=place.get("information") or "",
                geom=geom,
                is_indoor=place.get("is_indoor", False),
                city_id=city_id,
                source="ai_fallback",
            )
            created.append(poi)

        await self._set_embeddings(created)

        if created:
            await self.session.commit()

        return len(created)

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
        # Используем poi_repo.create() напрямую — commit один в конце.
        # Эмбеддинги считаются не здесь, а одной пачкой после цикла: внутри
        # цикла это был последовательный сетевой вызов на каждое место.
        created: list[POI] = []
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
            poi = await self.poi_repo.create(
                name=name,
                description=place.get("description", "Интересное место"),
                information=place.get("information", ""),
                geom=geom,
                is_indoor=place.get("is_indoor", False),
                city_id=city_id,
                google_place_id=gid,
            )
            created.append(poi)

        await self._set_embeddings(created)

        added_count = len(created)
        if added_count > 0:
            await self.session.commit()

        return added_count