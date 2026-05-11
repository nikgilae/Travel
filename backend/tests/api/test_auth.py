from httpx import AsyncClient


class TestAuthAPI:

    async def test_register_success(self, client: AsyncClient):
        """Успешная регистрация — возвращает токен и user_id."""
        response = await client.post("/auth/register", json={
            "email": "newuser@test.com",
            "password": "Password123",
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
            "password": "Password123",
        })

        response = await client.post("/auth/register", json={
            "email": "duplicate@test.com",
            "password": "Password123",
        })

        assert response.status_code == 409
        assert response.json()["error_code"] == "ALREADY_EXISTS"
        
    async def test_login_success(self, client: AsyncClient):
        """Успешный логин — возвращает токен."""
        await client.post("/auth/register", json={
            "email": "login@test.com",
            "password": "Password123",
        })

        response = await client.post("/auth/login", json={
            "email": "login@test.com",
            "password": "Password123",
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user_id" in data

    async def test_login_wrong_password(self, client: AsyncClient):
        """Неверный пароль — возвращает 401."""
        await client.post("/auth/register", json={
            "email": "wrongpass@test.com",
            "password": "Password123",
        })

        response = await client.post("/auth/login", json={
            "email": "wrongpass@test.com",
            "password": "WrongPass123",
        })

        assert response.status_code == 401
        assert response.json()["error_code"] == "UNAUTHORIZED"

    async def test_register_invalid_email(self, client: AsyncClient):
        """Невалидный email — возвращает 422 с error_code."""
        response = await client.post("/auth/register", json={
            "email": "notanemail",
            "password": "Password123",
        })

        assert response.status_code == 422
        assert response.json()["error_code"] == "VALIDATION_FAILED"