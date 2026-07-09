from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestAuthAPI:

    async def test_register_success(self, client: AsyncClient):
        """Успешная регистрация — возвращает токен и user_id."""
        response = await client.post("/auth/register", json={
            "email": "newuser@test.com",
            "password": "Password123!",
        })

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "user_id" in data
        assert data["token_type"] == "bearer"

    async def test_register_duplicate_email(self, client: AsyncClient):
        """Повторная регистрация с тем же email — возвращает 409."""
        await client.post("/auth/register", json={
            "email": "duplicate@test.com",
            "password": "Password123!",
        })

        response = await client.post("/auth/register", json={
            "email": "duplicate@test.com",
            "password": "Password123!",
        })

        assert response.status_code == 409
        assert response.json()["error_code"] == "ALREADY_EXISTS"

    async def test_login_success(self, client: AsyncClient):
        """Успешный логин — возвращает токен."""
        await client.post("/auth/register", json={
            "email": "login@test.com",
            "password": "Password123!",
        })

        response = await client.post("/auth/login", json={
            "email": "login@test.com",
            "password": "Password123!",
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user_id" in data

    async def test_login_wrong_password(self, client: AsyncClient):
        """Неверный пароль — возвращает 401."""
        await client.post("/auth/register", json={
            "email": "wrongpass@test.com",
            "password": "Password123!",
        })

        response = await client.post("/auth/login", json={
            "email": "wrongpass@test.com",
            "password": "WrongPass123!",
        })

        assert response.status_code == 401
        assert response.json()["error_code"] == "UNAUTHORIZED"

    async def test_register_invalid_email(self, client: AsyncClient):
        """Невалидный email — возвращает 422 с error_code."""
        response = await client.post("/auth/register", json={
            "email": "notanemail",
            "password": "Password123!",
        })

        assert response.status_code == 422
        assert response.json()["error_code"] == "VALIDATION_FAILED"

    async def test_login_is_first_login_true_without_trips(self, client: AsyncClient):
        """
        Логин сразу после регистрации — is_first_login = true.

        Доказывает, что флаг не зависит от времени (5 минут),
        а зависит только от отсутствия поездок у пользователя.
        """
        await client.post("/auth/register", json={
            "email": "firstlogin@test.com",
            "password": "Password123!",
        })

        response = await client.post("/auth/login", json={
            "email": "firstlogin@test.com",
            "password": "Password123!",
        })

        assert response.status_code == 200
        assert response.json()["is_first_login"] is True

    async def test_login_is_first_login_false_with_trip(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user,
        test_country,
        test_city,
    ):
        """Пользователь с хотя бы одной поездкой — is_first_login = false."""
        from app.repositories.trip import TripRepository

        trip_repo = TripRepository(db_session)
        await trip_repo.create(
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
        await db_session.commit()

        response = await client.post("/auth/login", json={
            "email": test_user.email,
            "password": "TestPass123",
        })

        assert response.status_code == 200
        assert response.json()["is_first_login"] is False
