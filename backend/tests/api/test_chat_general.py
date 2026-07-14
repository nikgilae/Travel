from sqlalchemy import select

from app.models.message import Message
from tests.conftest import make_completion


class TestGeneralChat:

    async def test_response_shape_unchanged(self, client, auth_headers, mock_ai):
        """
        CRITICAL регрессия: форма ответа /chat/general НЕ меняется —
        ровно {"reply": <текст>}. Персист транскрипта не должен ломать контракт.
        """
        mock_ai.default = make_completion(content="Советую Токио.")
        resp = await client.post(
            "/chat/general",
            json={"message": "Куда поехать?", "history": []},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert list(data.keys()) == ["reply"]
        assert data["reply"] == "Советую Токио."

    async def test_persists_user_and_assistant(self, client, auth_headers, mock_ai, db_session, test_user):
        """После обмена в messages появляются user+assistant с trip_id=NULL."""
        mock_ai.default = make_completion(content="Ответ.")
        await client.post(
            "/chat/general",
            json={"message": "привет", "history": []},
            headers=auth_headers,
        )
        rows = (await db_session.execute(
            select(Message).where(Message.user_id == test_user.id).order_by(Message.created_at)
        )).scalars().all()
        assert [r.role for r in rows] == ["user", "assistant"]
        assert rows[0].content == "привет"
        assert rows[1].content == "Ответ."
        assert all(r.trip_id is None for r in rows)  # general-чат не привязан к поездке

    async def test_best_effort_persistence_does_not_break_reply(
        self, client, auth_headers, mock_ai, monkeypatch
    ):
        """Сбой записи транскрипта не должен ломать ответ пользователю (best-effort)."""
        import app.services.message_log as ml

        class _BoomSession:
            async def __aenter__(self): raise RuntimeError("db down")
            async def __aexit__(self, *a): return False

        monkeypatch.setattr(ml, "AsyncSessionLocal", lambda: _BoomSession())
        mock_ai.default = make_completion(content="Всё равно отвечаю.")
        resp = await client.post(
            "/chat/general",
            json={"message": "тест", "history": []},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["reply"] == "Всё равно отвечаю."

    async def test_requires_auth(self, client, mock_ai):
        """Без токена — 401, AI не вызывается."""
        resp = await client.post(
            "/chat/general",
            json={"message": "привет", "history": []},
        )
        assert resp.status_code == 401
