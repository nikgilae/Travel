from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.trip import TripRepository


class TestTripRepository:

    async def test_create_trip(
        self,
        db_session: AsyncSession,
        test_user,
        test_country,
        test_city,
    ):
        """Создание поездки — проверяем что серверные поля заполняются."""
        repo = TripRepository(db_session)
        trip = await repo.create(
            user_id=test_user.id,
            country_id=test_country.id,
            city_id=test_city.id,
            purpose="leisure",
            budget="medium",
            group_size=2,
            other_information=None,
            start_date=None,
            end_date=None,
        )

        assert trip.id is not None
        assert trip.user_id == test_user.id
        assert trip.purpose == "leisure"
        assert trip.created_at is not None
        
    async def test_get_by_user_id(
        self,
        db_session: AsyncSession,
        test_user,
        test_country,
        test_city,
    ):
        """Получение поездок пользователя — возвращает только его поездки."""
        repo = TripRepository(db_session)
        await repo.create(
            user_id=test_user.id,
            country_id=test_country.id,
            city_id=test_city.id,
            purpose="leisure",
            budget="medium",
            group_size=1,
            other_information=None,
            start_date=None,
            end_date=None,
        )
        await db_session.commit()

        trips = await repo.get_by_user_id(test_user.id)

        assert len(trips) == 1
        assert trips[0].user_id == test_user.id

    async def test_get_by_user_and_id_wrong_user(
        self,
        db_session: AsyncSession,
        test_user,
        test_country,
        test_city,
    ):
        """Запрос чужой поездки — возвращает None."""
        import uuid
        repo = TripRepository(db_session)
        trip = await repo.create(
            user_id=test_user.id,
            country_id=test_country.id,
            city_id=test_city.id,
            purpose="leisure",
            budget="medium",
            group_size=1,
            other_information=None,
            start_date=None,
            end_date=None,
        )
        await db_session.commit()

        found = await repo.get_by_user_and_id(trip.id, uuid.uuid4())

        assert found is None