import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.exc import SQLAlchemyError

import app.main as main_module
from app.main import app
from app.core.database import get_db
from app.core.exceptions import AIGenerationError
from app.services.trip import TripService
from app.services.trip_ai import TripAIService


@pytest_asyncio.fixture
async def error_client(db_session):
    """
    Клиент, который НЕ пробрасывает исключения приложения наружу
    (raise_app_exceptions=False) — нужно, чтобы дойти до generic Exception-handler,
    который живёт в ServerErrorMiddleware и иначе перевыбрасывает ошибку.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


class TestErrorHandlers:

    async def test_generic_exception_returns_500_and_alerts(
        self, error_client, auth_headers, monkeypatch
    ):
        """Необработанная ошибка → 500 INTERNAL_ERROR + алерт в Sentry/Telegram."""
        cap = MagicMock()
        notify = AsyncMock()
        monkeypatch.setattr(main_module, "capture_exception", cap)
        monkeypatch.setattr(main_module, "notify_telegram", notify)

        async def boom(self, *a, **k):
            raise ValueError("unexpected boom")
        monkeypatch.setattr(TripService, "get_user_trips", boom)

        resp = await error_client.get("/trips", headers=auth_headers)

        assert resp.status_code == 500
        assert resp.json()["error_code"] == "INTERNAL_ERROR"
        # ноль «молчаливых» 5xx: фаундер получает сигнал
        cap.assert_called_once()
        notify.assert_awaited_once()

    async def test_sqlalchemy_error_returns_500_and_alerts(
        self, error_client, auth_headers, monkeypatch
    ):
        """Ошибка БД → 500 DATABASE_ERROR + алерт (раньше молчала)."""
        cap = MagicMock()
        notify = AsyncMock()
        monkeypatch.setattr(main_module, "capture_exception", cap)
        monkeypatch.setattr(main_module, "notify_telegram", notify)

        async def boom(self, *a, **k):
            raise SQLAlchemyError("db exploded")
        monkeypatch.setattr(TripService, "get_user_trips", boom)

        resp = await error_client.get("/trips", headers=auth_headers)

        assert resp.status_code == 500
        assert resp.json()["error_code"] == "DATABASE_ERROR"
        cap.assert_called_once()
        notify.assert_awaited_once()

    async def test_known_exceptions_still_work(self, error_client, auth_headers):
        """Регрессия: обычные ошибки (404 на чужой/несуществующий трип) не сломаны."""
        resp = await error_client.get(f"/trips/{uuid.uuid4()}", headers=auth_headers)
        assert resp.status_code == 404
        assert resp.json()["error_code"] == "RESOURCE_NOT_FOUND"

    async def test_ai_generation_error_returns_502_with_retryable_and_alerts_sentry_only(
        self, error_client, auth_headers, monkeypatch
    ):
        """
        П.12 T8: AIGenerationError из TripAIService.generate → 502 с телом
        {error_code, message, detail, retryable}, capture_exception вызван,
        а notify_telegram — НЕТ (сбои AI-провайдера ожидаемы, не должны спамить
        Telegram фаундера — это отличает 502 от настоящих 500).
        """
        cap = MagicMock()
        notify = AsyncMock()
        monkeypatch.setattr(main_module, "capture_exception", cap)
        monkeypatch.setattr(main_module, "notify_telegram", notify)

        async def boom(self, *a, **k):
            raise AIGenerationError("AI недоступен", retryable=False)
        monkeypatch.setattr(TripAIService, "generate", boom)

        resp = await error_client.post(
            f"/trips/{uuid.uuid4()}/generate",
            json={"interests": ["еда"]},
            headers=auth_headers,
        )

        assert resp.status_code == 502
        body = resp.json()
        assert body["error_code"] == "AI_GENERATION_FAILED"
        assert body["message"] == "AI недоступен"
        assert body["detail"] == "AI недоступен"
        assert body["retryable"] is False
        cap.assert_called_once()
        notify.assert_not_awaited()
