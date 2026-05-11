from httpx import AsyncClient


class TestTripsAPI:

    async def test_create_trip_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_country,
        test_city,
    ):
        """Успешное создание поездки — возвращает 201 с trip_id."""
        response = await client.post(
            "/trips",
            json={
                "country_id": str(test_country.id),
                "city_id": str(test_city.id),
                "purpose": "leisure",
                "budget": "medium",
                "group_size": 2,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["purpose"] == "leisure"
        assert data["budget"] == "medium"
        assert data["group_size"] == 2

    async def test_create_trip_unauthorized(
        self,
        client: AsyncClient,
        test_country,
        test_city,
    ):
        """Создание поездки без токена — возвращает 401."""
        response = await client.post(
            "/trips",
            json={
                "country_id": str(test_country.id),
                "city_id": str(test_city.id),
                "purpose": "leisure",
                "budget": "medium",
                "group_size": 1,
            },
        )

        assert response.status_code == 401
        
    async def test_get_trips_empty(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Получение списка поездок — пустой список если поездок нет."""
        response = await client.get("/trips", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_trips_after_create(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_country,
        test_city,
    ):
        """После создания поездки — список содержит одну поездку."""
        await client.post(
            "/trips",
            json={
                "country_id": str(test_country.id),
                "city_id": str(test_city.id),
                "purpose": "leisure",
                "budget": "medium",
                "group_size": 1,
            },
            headers=auth_headers,
        )

        response = await client.get("/trips", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["purpose"] == "leisure"

    async def test_get_trip_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Запрос несуществующей поездки — возвращает 404."""
        import uuid
        response = await client.get(
            f"/trips/{uuid.uuid4()}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["error_code"] == "RESOURCE_NOT_FOUND"
        
    async def test_update_trip(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_country,
        test_city,
    ):
        """Partial update поездки — обновляются только переданные поля."""
        create_resp = await client.post(
            "/trips",
            json={
                "country_id": str(test_country.id),
                "city_id": str(test_city.id),
                "purpose": "leisure",
                "budget": "medium",
                "group_size": 1,
            },
            headers=auth_headers,
        )
        trip_id = create_resp.json()["id"]

        response = await client.put(
            f"/trips/{trip_id}",
            json={"budget": "high", "group_size": 3},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["budget"] == "high"
        assert data["group_size"] == 3
        assert data["purpose"] == "leisure"  # не изменилось

    async def test_delete_trip(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_country,
        test_city,
    ):
        """Удаление поездки — после удаления возвращает 404."""
        create_resp = await client.post(
            "/trips",
            json={
                "country_id": str(test_country.id),
                "city_id": str(test_city.id),
                "purpose": "leisure",
                "budget": "medium",
                "group_size": 1,
            },
            headers=auth_headers,
        )
        trip_id = create_resp.json()["id"]

        delete_resp = await client.delete(
            f"/trips/{trip_id}",
            headers=auth_headers,
        )
        assert delete_resp.status_code == 204

        get_resp = await client.get(
            f"/trips/{trip_id}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 404