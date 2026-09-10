import asyncio
import json
import logging
import uuid
from datetime import date, timedelta

import pytest_asyncio
from httpx import AsyncClient, ASGITransport

import app.services.ai as ai_module
import app.services.trip_ai as trip_ai_module
from app.main import app
from app.core.database import get_db
from app.config import settings as app_settings
from app.repositories.poi import POIRepository
from app.repositories.trip import TripPOIRepository, TripRepository
from tests.conftest import make_completion


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


# ── Генерация маршрута через AI (T8, регрессии коммита 1) ─────────────────────
# Каждый тест здесь отключает Google Maps (needs_enrichment иначе всегда True
# для свежего города — иначе тест реально пойдёт в сеть, см. GOOGLE_MAPS_API_KEY
# в backend/.env) и подменяет app.services.ai.gen_client через mock_gen_ai.

async def _create_trip_with_dates(
    client: AsyncClient, auth_headers: dict, test_country, test_city, days: int = 1,
) -> str:
    """Создать поездку с датами (нужны для /generate) и вернуть её id."""
    start = date(2026, 3, 1)
    end = start + timedelta(days=days - 1)
    resp = await client.post(
        "/trips",
        json={
            "country_id": str(test_country.id),
            "city_id": str(test_city.id),
            "purpose": "leisure",
            "budget": "medium",
            "group_size": 2,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def _create_pois(db_session, test_city, n: int = 2) -> list:
    """Создать n POI в тестовом городе напрямую через репозиторий."""
    repo = POIRepository(db_session)
    pois = [
        await repo.create(
            city_id=test_city.id,
            name=f"Место {i}",
            description="Описание места",
            is_indoor=False,
        )
        for i in range(n)
    ]
    await db_session.commit()
    return pois


def _ai_payload_for_pois(pois: list, day: int = 1) -> str:
    """Валидный ответ AI: первый POI — main, остальные — additional, один день."""
    main, additional = pois[:1], pois[1:]
    return json.dumps({
        "summary": "Прекрасный маршрут",
        "total_budget_estimate": "300$",
        "days": [
            {
                "day": day,
                "theme": "Знакомство с городом",
                "main_pois": [
                    {
                        "poi_id": str(p.id),
                        "name": p.name,
                        "start_time": "10:00",
                        "duration_hours": 2.0,
                        "budget_estimate": "0",
                        "ai_tip": "Идите утром",
                        "activity_level": 3,
                    }
                    for p in main
                ],
                "additional_pois": [
                    {
                        "poi_id": str(p.id),
                        "name": p.name,
                        "start_time": "14:00",
                        "duration_hours": 1.0,
                        "budget_estimate": "0",
                        "ai_tip": "Запасной вариант",
                        "activity_level": 1,
                    }
                    for p in additional
                ],
            }
        ],
    })


@pytest_asyncio.fixture
async def no_google_enrichment(monkeypatch):
    """
    Отключить обогащение через Google Maps на время теста.

    Без этого TripAIService.generate() для свежего test_city (last_enriched_at
    всегда None) реально пойдёт в сеть на все 20 поисковых запросов — этот
    ключ настоящий (см. GOOGLE_MAPS_API_KEY в backend/.env), а сеть в тестах
    запрещена по правилам T8.
    """
    monkeypatch.setattr(app_settings, "GOOGLE_MAPS_ENABLED", False)
    # И AI-фолбэк заодно: с ним пустой тестовый город пошёл бы за местами
    # к модели, а сеть в тестах запрещена по тем же правилам T8.
    monkeypatch.setattr(app_settings, "AI_POI_FALLBACK_ENABLED", False)


@pytest_asyncio.fixture
async def rollback_client(db_session):
    """
    Как `client` из conftest, но override_get_db реплицирует rollback-при-
    исключении из настоящего app.core.database.get_db (там `except Exception:
    await session.rollback(); raise`). Обычный `client` фикс в conftest просто
    yield'ит сессию без отката — этого достаточно почти всем тестам, но не
    для проверки того, что после сбоя генерации сессия остаётся рабочей для
    следующего запроса (T8 п.9, "PendingRollbackError").
    """
    async def override_get_db():
        try:
            yield db_session
        except Exception:
            await db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


class TestTripGenerate:

    async def test_generate_success_saves_pois_and_ai_summary(
        self, client, auth_headers, db_session, test_country, test_city,
        mock_gen_ai, no_google_enrichment,
    ):
        """П.1: валидный JSON → 200, POI сохранены в БД, ai_summary записан."""
        trip_id = await _create_trip_with_dates(client, auth_headers, test_country, test_city, days=1)
        pois = await _create_pois(db_session, test_city, n=2)
        mock_gen_ai.queue = [make_completion(content=_ai_payload_for_pois(pois))]

        resp = await client.post(
            f"/trips/{trip_id}/generate",
            json={"interests": ["история"]},
            headers=auth_headers,
        )

        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["saved_pois_count"] == 2
        assert len(mock_gen_ai.calls) == 1

        rows = await TripPOIRepository(db_session).get_by_trip(uuid.UUID(trip_id))
        assert len(rows) == 2

        trip = await TripRepository(db_session).get_by_id(uuid.UUID(trip_id))
        assert trip.ai_summary == "Прекрасный маршрут"

    async def test_generate_malformed_json_both_attempts_502_leaves_trip_empty(
        self, client, auth_headers, db_session, test_country, test_city,
        mock_gen_ai, no_google_enrichment,
    ):
        """П.3: битый JSON на всех попытках → 502 с retryable, 0 trip_pois, ai_summary=NULL."""
        trip_id = await _create_trip_with_dates(client, auth_headers, test_country, test_city, days=1)
        await _create_pois(db_session, test_city, n=2)
        mock_gen_ai.queue = [
            make_completion(content=f"это не json #{i}")
            for i in range(ai_module.MAX_AI_ATTEMPTS)
        ]

        resp = await client.post(
            f"/trips/{trip_id}/generate",
            json={"interests": ["еда"]},
            headers=auth_headers,
        )

        assert resp.status_code == 502
        body = resp.json()
        assert body["error_code"] == "AI_GENERATION_FAILED"
        assert "retryable" in body
        assert len(mock_gen_ai.calls) == ai_module.MAX_AI_ATTEMPTS

        rows = await TripPOIRepository(db_session).get_by_trip(uuid.UUID(trip_id))
        assert rows == []
        trip = await TripRepository(db_session).get_by_id(uuid.UUID(trip_id))
        assert trip.ai_summary is None

    async def test_generate_empty_days_returns_502_not_200_with_empty_plan(
        self, client, auth_headers, db_session, test_country, test_city,
        mock_gen_ai, no_google_enrichment,
    ):
        """
        П.4 — КЛЮЧЕВАЯ регрессия коммита: {"days": []} через весь HTTP-путь
        должен дать 502, а НЕ 200 с пустым планом.
        """
        trip_id = await _create_trip_with_dates(client, auth_headers, test_country, test_city, days=1)
        await _create_pois(db_session, test_city, n=2)
        empty_payload = json.dumps({
            "summary": "ok", "total_budget_estimate": "0", "days": [],
        })
        mock_gen_ai.queue = [
            make_completion(content=empty_payload),
            make_completion(content=empty_payload),
        ]

        resp = await client.post(
            f"/trips/{trip_id}/generate",
            json={"interests": ["еда"]},
            headers=auth_headers,
        )

        assert resp.status_code == 502
        assert resp.json()["error_code"] == "AI_GENERATION_FAILED"

        rows = await TripPOIRepository(db_session).get_by_trip(uuid.UUID(trip_id))
        assert rows == []

    async def test_generate_unknown_poi_ids_502_and_session_recovers_for_next_request(
        self, rollback_client, auth_headers, db_session, test_country, test_city,
        mock_gen_ai, no_google_enrichment,
    ):
        """
        П.9: все poi_id в ответе AI — несуществующие UUID → 502, 0 trip_pois,
        и следующий запрос в ТОЙ ЖЕ сессии не падает PendingRollbackError
        (проверка отката в get_db).
        """
        trip_id = await _create_trip_with_dates(
            rollback_client, auth_headers, test_country, test_city, days=1,
        )
        await _create_pois(db_session, test_city, n=2)
        payload = json.dumps({
            "summary": "s", "total_budget_estimate": "b",
            "days": [{
                "day": 1, "theme": "t",
                "main_pois": [{
                    "poi_id": str(uuid.uuid4()),
                    "name": "Несуществующее место",
                    "start_time": "10:00", "duration_hours": 1.0,
                    "budget_estimate": "0", "ai_tip": "", "activity_level": 2,
                }],
                "additional_pois": [],
            }],
        })
        mock_gen_ai.queue = [make_completion(content=payload)]

        resp = await rollback_client.post(
            f"/trips/{trip_id}/generate",
            json={"interests": ["еда"]},
            headers=auth_headers,
        )
        assert resp.status_code == 502
        assert resp.json()["error_code"] == "AI_GENERATION_FAILED"

        rows = await TripPOIRepository(db_session).get_by_trip(uuid.UUID(trip_id))
        assert rows == []

        # Сессия не должна быть «отравлена» — следующий запрос обязан пройти.
        next_resp = await rollback_client.get("/trips", headers=auth_headers)
        assert next_resp.status_code == 200

    async def test_generate_repeat_call_with_existing_pois_is_idempotent(
        self, client, auth_headers, db_session, test_country, test_city,
        mock_gen_ai, no_google_enrichment,
    ):
        """
        Повторный /generate на уже наполненной поездке → 200 идемпотентно с
        saved_pois_count=0, план в БД цел (не 502, не задвоился, не потёрся),
        и — ключевое отличие от прежней семантики — AI не вызывался ни разу:
        проверка «план уже есть» стоит ДО обращения к провайдеру.
        """
        trip_id = await _create_trip_with_dates(client, auth_headers, test_country, test_city, days=1)
        pois = await _create_pois(db_session, test_city, n=2)
        payload = _ai_payload_for_pois(pois)

        mock_gen_ai.queue = [make_completion(content=payload)]
        first = await client.post(
            f"/trips/{trip_id}/generate",
            json={"interests": ["еда"]},
            headers=auth_headers,
        )
        assert first.status_code == 200, first.text
        assert first.json()["saved_pois_count"] == 2
        calls_after_first = len(mock_gen_ai.calls)

        mock_gen_ai.queue = [make_completion(content=payload)]
        second = await client.post(
            f"/trips/{trip_id}/generate",
            json={"interests": ["еда"]},
            headers=auth_headers,
        )

        assert second.status_code == 200, second.text
        assert second.json()["saved_pois_count"] == 0
        assert second.json()["proposed_pois_count"] == 0
        # Провайдера не дёргали: ни новых вызовов, ни съеденной очереди.
        assert len(mock_gen_ai.calls) == calls_after_first
        assert len(mock_gen_ai.queue) == 1

        rows = await TripPOIRepository(db_session).get_by_trip(uuid.UUID(trip_id))
        assert len(rows) == 2  # план цел, не задвоился и не потёрся

    async def test_generate_repeat_with_different_ai_selection_does_not_append(
        self, client, auth_headers, db_session, test_country, test_city,
        mock_gen_ai, no_google_enrichment,
    ):
        """
        Дефект живого стека: при temperature=0.7 повтор /generate предлагал
        ДРУГОЙ набор мест, дубли не срабатывали, и план распухал (29 → 40 → 51).
        Теперь повтор коротко замыкается: число мест в БД не меняется,
        AI не вызывается, HTTP 200.
        """
        trip_id = await _create_trip_with_dates(client, auth_headers, test_country, test_city, days=1)
        pois = await _create_pois(db_session, test_city, n=4)

        mock_gen_ai.queue = [make_completion(content=_ai_payload_for_pois(pois[:2]))]
        first = await client.post(
            f"/trips/{trip_id}/generate",
            json={"interests": ["еда"]},
            headers=auth_headers,
        )
        assert first.status_code == 200, first.text
        assert first.json()["saved_pois_count"] == 2
        calls_after_first = len(mock_gen_ai.calls)

        # Второй прогон «предложил бы» два совершенно других места — до фикса
        # они прошли бы мимо проверки дублей и легли в БД четвёртым и пятым.
        mock_gen_ai.queue = [make_completion(content=_ai_payload_for_pois(pois[2:]))]
        second = await client.post(
            f"/trips/{trip_id}/generate",
            json={"interests": ["еда"]},
            headers=auth_headers,
        )

        assert second.status_code == 200, second.text
        assert second.json()["saved_pois_count"] == 0
        assert len(mock_gen_ai.calls) == calls_after_first

        rows = await TripPOIRepository(db_session).get_by_trip(uuid.UUID(trip_id))
        assert len(rows) == 2
        # Пул остался тем, что сохранила первая генерация.
        assert {str(r.poi_id) for r in rows} == {str(p.id) for p in pois[:2]}

    async def test_generate_repeat_logs_skipped_existing_event(
        self, client, auth_headers, db_session, test_country, test_city,
        mock_gen_ai, no_google_enrichment, caplog,
    ):
        """
        Пропущенный повтор должен попадать в event-лог отдельным статусом,
        иначе в приборах волны он смешается с настоящими успехами генерации.
        """
        trip_id = await _create_trip_with_dates(client, auth_headers, test_country, test_city, days=1)
        pois = await _create_pois(db_session, test_city, n=2)
        payload = _ai_payload_for_pois(pois)

        mock_gen_ai.queue = [make_completion(content=payload)]
        first = await client.post(
            f"/trips/{trip_id}/generate",
            json={"interests": ["еда"]},
            headers=auth_headers,
        )
        assert first.status_code == 200, first.text

        with caplog.at_level(logging.INFO, logger="app.core.events"):
            second = await client.post(
                f"/trips/{trip_id}/generate",
                json={"interests": ["еда"]},
                headers=auth_headers,
            )
        assert second.status_code == 200, second.text

        payloads = [
            json.loads(rec.getMessage().split("event ", 1)[1])
            for rec in caplog.records
            if rec.name == "app.core.events"
        ]
        generate_events = [p for p in payloads if p["event"] == "generate"]
        assert generate_events, "событие generate не записалось"
        assert generate_events[-1]["status"] == "skipped_existing"
        assert generate_events[-1]["trip_id"] == trip_id

    async def test_generate_without_dates_returns_400(
        self, client, auth_headers, test_country, test_city,
    ):
        """П.11 (T3b, часть 1): поездка без дат → 400 BAD_REQUEST, AI не вызывается."""
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

        resp = await client.post(
            f"/trips/{trip_id}/generate",
            json={"interests": ["еда"]},
            headers=auth_headers,
        )

        assert resp.status_code == 400
        assert resp.json()["error_code"] == "BAD_REQUEST"

    async def test_generate_does_not_wait_for_city_enrichment(
        self, client, auth_headers, db_session, test_country, test_city,
        mock_gen_ai, monkeypatch,
    ):
        """
        Обогащение города не держит запрос генерации.

        Регрессия на главную поломку прода: раньше обогащение шло синхронно
        внутри /generate (20 запросов в Google + эмбеддинг на каждое новое
        место), и человек с неразогретым городом упирался в обрыв соединения
        на фронте. Здесь обогащение подменено задачей, которая не закончится
        никогда: если генерация начнёт её ждать, тест не повиснет, а упадёт
        по своему таймауту.

        Фикстуры no_google_enrichment тут намеренно нет — проверяем именно
        включённый GOOGLE_MAPS_ENABLED, при котором обогащение положено.
        """
        monkeypatch.setattr(app_settings, "GOOGLE_MAPS_ENABLED", True)

        scheduled = []

        def _fake_schedule(city_id, city_name):
            scheduled.append((city_id, city_name))
            return asyncio.get_running_loop().create_future()  # никогда не завершится

        monkeypatch.setattr(trip_ai_module.city_enrichment, "schedule", _fake_schedule)

        trip_id = await _create_trip_with_dates(client, auth_headers, test_country, test_city, days=1)
        pois = await _create_pois(db_session, test_city, n=2)
        mock_gen_ai.queue = [make_completion(content=_ai_payload_for_pois(pois))]

        resp = await asyncio.wait_for(
            client.post(
                f"/trips/{trip_id}/generate",
                json={"interests": ["история"]},
                headers=auth_headers,
            ),
            timeout=10,
        )

        assert resp.status_code == 200, resp.text
        assert resp.json()["saved_pois_count"] == 2
        # Обогащение при этом всё-таки заведено, просто в фоне.
        assert len(scheduled) == 1
        assert scheduled[0][1] == test_city.name

class TestTripCityName:
    """
    Название города приходит с сервера, а не только из localStorage.

    Иначе на любом устройстве, где не проходил онбординг (а именно ради
    второго устройства человека и просят завести аккаунт), в заголовке
    маршрута оказывается сырой UUID города.
    """

    async def test_trip_details_include_city_and_country_names(
        self, client, auth_headers, test_country, test_city,
    ):
        trip_id = await _create_trip_with_dates(client, auth_headers, test_country, test_city)

        resp = await client.get(f"/trips/{trip_id}", headers=auth_headers)

        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["city_name"] == test_city.name
        assert data["country_name"] == test_country.name

    async def test_trip_list_still_works_without_loaded_relations(
        self, client, auth_headers, test_country, test_city,
    ):
        """
        Список поездок не грузит город и страну.

        Свойства city_name/country_name обязаны на это отвечать None, а не
        уводить сессию в ленивую загрузку (MissingGreenlet и 500 на списке).
        """
        await _create_trip_with_dates(client, auth_headers, test_country, test_city)

        resp = await client.get("/trips", headers=auth_headers)

        assert resp.status_code == 200, resp.text
        assert len(resp.json()) == 1
