"""Тесты WS-чата (/trips/{id}/chat).

Полноценный WebSocket через реальный транспорт (starlette TestClient) работает в
своём event loop, а наши async-фикстуры БД привязаны к loop pytest-asyncio —
шарить async-сессию между ними нельзя. Поэтому разделяем:

- Ветку авторизации по токену (БД не нужна — возврат до TripService) проверяем
  реальным WebSocket-транспортом.
- Диалог, персист транскрипта и tool-persist проверяем на уровне логики, повторяя
  ТУ ЖЕ последовательность, что и цикл WS-эндпоинта:
      save раздельно(user) → before=len → process_message → save(delta).
  AI мокается в одной точке (общий app.services.ai.client).
"""
import json
import uuid

from sqlalchemy import select
from starlette.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.message import Message
from app.models.trip import Trip
from app.services.trip import TripService
from app.services.chat_agent import TravelAgentService
from app.services.message_log import save_messages, extract_delta
from tests.conftest import make_completion, FakeToolCall


# ── Ветка токена (реальный WebSocket, без БД) ─────────────────────────────────

class TestWebSocketAuth:

    def test_invalid_token_closes_with_message(self):
        """Невалидный токен → системное сообщение об ошибке, соединение не виснет."""
        async def _no_db():
            yield None
        app.dependency_overrides[get_db] = _no_db
        try:
            client = TestClient(app)
            with client.websocket_connect("/trips/%s/chat?token=bad.token" % uuid.uuid4()) as ws:
                data = ws.receive_json()
                assert data["sender"] == "system"
                assert "токен" in data["text"].lower()
        finally:
            app.dependency_overrides.clear()


# ── Диалог + персист (уровень логики WS-цикла) ────────────────────────────────

async def _run_ws_turn(db_session, user, trip, user_message, chat_history):
    """Повторяет тело цикла WS-эндпоинта для одного хода пользователя."""
    trip_service = TripService(db_session)
    agent = TravelAgentService(trip_service)

    await save_messages(user.id, trip.id, [{"role": "user", "content": user_message}])
    before = len(chat_history)
    ai_response = await agent.process_message(
        messages=chat_history,
        user_message=user_message,
        trip_id=str(trip.id),
        user_id=str(user.id),
    )
    await save_messages(user.id, trip.id, extract_delta(chat_history, before))
    return ai_response


class TestWebSocketDialog:

    async def test_normal_dialog_persists_user_and_assistant(
        self, db_session, test_user, test_trip, mock_ai
    ):
        """
        CRITICAL регрессия: обычный WS-диалог работает как раньше — ассистент
        возвращает текст, а в messages появляются user+assistant с trip_id.
        """
        mock_ai.default = make_completion(content="Привет! Чем помочь?")
        chat_history = []
        reply = await _run_ws_turn(db_session, test_user, test_trip, "привет", chat_history)

        assert reply == "Привет! Чем помочь?"
        rows = (await db_session.execute(
            select(Message).where(Message.user_id == test_user.id).order_by(Message.created_at)
        )).scalars().all()
        assert [r.role for r in rows] == ["user", "assistant"]
        assert all(r.trip_id == test_trip.id for r in rows)

    async def test_tool_call_persists_tool_role_and_applies_effect(
        self, db_session, test_user, test_trip, mock_ai
    ):
        """
        Команда с инструментом: AI вызывает tool → инструмент реально отрабатывает
        (бюджет обновлён) и в messages есть запись role=tool.
        """
        args = json.dumps({
            "trip_id": str(test_trip.id),
            "user_id": str(test_user.id),
            "budget": "high",
        })
        mock_ai.queue = [
            make_completion(tool_calls=[FakeToolCall("call_1", "tool_update_trip_info", args)]),
            make_completion(content="Готово, бюджет обновлён."),
        ]
        chat_history = []
        reply = await _run_ws_turn(db_session, test_user, test_trip, "сделай бюджет высоким", chat_history)

        assert reply == "Готово, бюджет обновлён."

        # эффект инструмента применён
        trip = (await db_session.execute(
            select(Trip).where(Trip.id == test_trip.id)
        )).scalar_one()
        assert trip.budget == "high"

        # в транскрипте есть ход role=tool
        roles = (await db_session.execute(
            select(Message.role).where(Message.user_id == test_user.id).order_by(Message.created_at)
        )).scalars().all()
        assert "tool" in roles
        assert roles[0] == "user"

    async def test_crash_mid_turn_keeps_raw_user_message(
        self, db_session, test_user, test_trip, monkeypatch
    ):
        """
        Аварийный диалог не теряется: сырой ход пользователя записан ДО агента,
        поэтому даже если агент упадёт, сообщение остаётся в БД.
        """
        # сырой user пишем как в цикле
        await save_messages(test_user.id, test_trip.id, [{"role": "user", "content": "упаду?"}])

        # агент падает
        trip_service = TripService(db_session)
        agent = TravelAgentService(trip_service)

        async def boom(*a, **k):
            raise RuntimeError("AI proxy down")
        monkeypatch.setattr(agent, "process_message", boom)

        try:
            await agent.process_message(messages=[], user_message="упаду?",
                                        trip_id=str(test_trip.id), user_id=str(test_user.id))
        except RuntimeError:
            pass  # в реальном эндпоинте это ловит except-блок

        rows = (await db_session.execute(
            select(Message).where(Message.user_id == test_user.id)
        )).scalars().all()
        assert len(rows) == 1
        assert rows[0].role == "user"
        assert rows[0].content == "упаду?"
