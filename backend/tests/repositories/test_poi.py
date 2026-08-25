from sqlalchemy.ext.asyncio import AsyncSession

from app.models.poi import EMBEDDING_DIM
from app.repositories.geography import CityRepository
from app.repositories.poi import POIRepository

QUERY_VECTOR = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
CLOSE_VECTOR = QUERY_VECTOR  # совпадает с запросом — расстояние 0
FAR_VECTOR = [-1.0] + [0.0] * (EMBEDDING_DIM - 1)  # противоположный — расстояние 2


async def _create_poi(db_session, city_id, name, embedding=None):
    repo = POIRepository(db_session)
    poi = await repo.create(
        name=name,
        description="Описание",
        information=None,
        geom=None,
        is_indoor=False,
        city_id=city_id,
    )
    poi.embedding = embedding
    await db_session.commit()
    return poi


class TestGetRelevantForTrip:

    async def test_orders_by_cosine_distance(
        self, db_session: AsyncSession, test_city
    ):
        close = await _create_poi(db_session, test_city.id, "Близкое", CLOSE_VECTOR)
        far = await _create_poi(db_session, test_city.id, "Далёкое", FAR_VECTOR)

        repo = POIRepository(db_session)
        result = await repo.get_relevant_for_trip(test_city.id, QUERY_VECTOR, limit=2)

        assert [poi.id for poi in result] == [close.id, far.id]

    async def test_filters_by_city(
        self, db_session: AsyncSession, test_city, test_country
    ):
        other_city = await CityRepository(db_session).create(
            country_id=test_country.id,
            name="Другой город",
            content="Другой город",
        )
        await db_session.commit()

        in_city = await _create_poi(db_session, test_city.id, "В городе", CLOSE_VECTOR)
        await _create_poi(db_session, other_city.id, "В другом городе", CLOSE_VECTOR)

        repo = POIRepository(db_session)
        result = await repo.get_relevant_for_trip(test_city.id, QUERY_VECTOR, limit=5)

        assert [poi.id for poi in result] == [in_city.id]

    async def test_graceful_degradation_pads_with_random_without_embedding(
        self, db_session: AsyncSession, test_city
    ):
        with_embedding = await _create_poi(db_session, test_city.id, "С embedding", CLOSE_VECTOR)
        without_embedding_ids = {
            (await _create_poi(db_session, test_city.id, f"Без embedding {i}")).id
            for i in range(3)
        }

        repo = POIRepository(db_session)
        result = await repo.get_relevant_for_trip(test_city.id, QUERY_VECTOR, limit=3)

        result_ids = [poi.id for poi in result]
        assert len(result_ids) == 3
        assert result_ids[0] == with_embedding.id  # с embedding всегда первый — точное совпадение
        assert set(result_ids[1:]) <= without_embedding_ids

    async def test_limit_respected_when_plenty_available(
        self, db_session: AsyncSession, test_city
    ):
        for i in range(5):
            await _create_poi(db_session, test_city.id, f"POI {i}", CLOSE_VECTOR)

        repo = POIRepository(db_session)
        result = await repo.get_relevant_for_trip(test_city.id, QUERY_VECTOR, limit=2)

        assert len(result) == 2
