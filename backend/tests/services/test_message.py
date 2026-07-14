import uuid

import pytest
from sqlalchemy import select

from app.models.message import Message
from app.repositories.message import MessageRepository
from app.services.message_log import save_messages, extract_delta


class TestMessageRepository:

    async def test_create_persists_message(self, db_session, test_user):
        """MessageRepository.create вставляет запись со всеми полями."""
        repo = MessageRepository(db_session)
        msg = await repo.create(
            user_id=test_user.id,
            trip_id=None,
            role="user",
            content="привет",
            tool_name=None,
            tool_calls=None,
        )
        await db_session.commit()

        assert msg.id is not None
        assert msg.role == "user"
        assert msg.content == "привет"
        assert msg.created_at is not None


class TestSaveMessages:

    async def test_persists_batch(self, db_session, test_user):
        """save_messages пишет пачку user+assistant в БД."""
        await save_messages(test_user.id, None, [
            {"role": "user", "content": "вопрос"},
            {"role": "assistant", "content": "ответ", "tool_calls": None},
        ])
        rows = (await db_session.execute(
            select(Message).where(Message.user_id == test_user.id).order_by(Message.created_at)
        )).scalars().all()
        assert [r.role for r in rows] == ["user", "assistant"]
        assert rows[0].content == "вопрос"
        assert rows[1].content == "ответ"

    async def test_persists_tool_call_fields(self, db_session, test_user):
        """Ход ассистента с tool_calls и ход tool сохраняются корректно."""
        await save_messages(test_user.id, None, [
            {"role": "assistant", "content": None,
             "tool_calls": [{"id": "c1", "function": {"name": "tool_x"}}]},
            {"role": "tool", "content": '{"ok": true}', "tool_name": "tool_x"},
        ])
        rows = (await db_session.execute(
            select(Message).where(Message.user_id == test_user.id).order_by(Message.created_at)
        )).scalars().all()
        assistant, tool = rows
        assert assistant.content is None
        assert assistant.tool_calls == [{"id": "c1", "function": {"name": "tool_x"}}]
        assert tool.role == "tool"
        assert tool.tool_name == "tool_x"

    async def test_empty_entries_is_noop(self, db_session, test_user):
        """Пустой список не создаёт записей и не падает."""
        await save_messages(test_user.id, None, [])
        count = (await db_session.execute(
            select(Message).where(Message.user_id == test_user.id)
        )).scalars().all()
        assert count == []

    async def test_best_effort_never_raises(self, db_session, test_user, monkeypatch):
        """Сбой записи НЕ должен бросать исключение (best-effort)."""
        import app.services.message_log as ml

        class _BoomSession:
            async def __aenter__(self): raise RuntimeError("db down")
            async def __aexit__(self, *a): return False

        monkeypatch.setattr(ml, "AsyncSessionLocal", lambda: _BoomSession())
        # не должно бросить — иначе чат бы упал
        await save_messages(test_user.id, None, [{"role": "user", "content": "x"}])


class TestExtractDelta:

    def test_filters_only_assistant_and_tool(self):
        """Из истории берём только assistant/tool; system и user пропускаем."""
        hist = [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "wrapped"},
            {"role": "assistant", "content": None,
             "tool_calls": [{"id": "c1"}]},
            {"role": "tool", "name": "tool_x", "content": "{}"},
            {"role": "assistant", "content": "final"},
        ]
        delta = extract_delta(hist, 0)
        assert [e["role"] for e in delta] == ["assistant", "tool", "assistant"]
        assert delta[0]["tool_calls"] == [{"id": "c1"}]
        assert delta[1]["tool_name"] == "tool_x"
        assert delta[2]["content"] == "final"

    def test_respects_start_index(self):
        """Берём только новые записи начиная со start_index."""
        hist = [
            {"role": "assistant", "content": "old"},
            {"role": "assistant", "content": "new"},
        ]
        delta = extract_delta(hist, 1)
        assert [e["content"] for e in delta] == ["new"]
