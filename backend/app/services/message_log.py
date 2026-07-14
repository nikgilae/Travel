"""Персист диалогов чата — «чёрный ящик» волны 1.

Запись строго best-effort: используется ОТДЕЛЬНАЯ сессия БД (AsyncSessionLocal),
чтобы сбой записи не отравлял сессию самого чата и не ронял пользовательский
поток. Любое исключение логируется и проглатывается — чат продолжает работать.

Режим write-only: только пишем, историю из БД не читаем (гидрация — TODO-1).
"""
import logging
import uuid

from app.core.database import AsyncSessionLocal
from app.repositories.message import MessageRepository

logger = logging.getLogger(__name__)


async def save_messages(
    user_id: uuid.UUID,
    trip_id: uuid.UUID | None,
    entries: list[dict],
) -> None:
    """
    Записать пачку сообщений в таблицу messages. Никогда не бросает исключение.

    Parameters
    ----------
    user_id : uuid.UUID
        Автор/участник диалога.
    trip_id : uuid.UUID or None
        Поездка (NULL для общего чата /chat/general).
    entries : list[dict]
        Каждый dict: {"role", "content"?, "tool_name"?, "tool_calls"?}.
        Отсутствующие ключи трактуются как None.
    """
    if not entries:
        return
    try:
        async with AsyncSessionLocal() as session:
            repo = MessageRepository(session)
            for e in entries:
                await repo.create(
                    user_id=user_id,
                    trip_id=trip_id,
                    role=e["role"],
                    content=e.get("content"),
                    tool_name=e.get("tool_name"),
                    tool_calls=e.get("tool_calls"),
                )
            await session.commit()
    except Exception:
        # best-effort: не роняем чат из-за проблем с записью транскрипта
        logger.exception("save_messages failed (best-effort, чат продолжает работать)")


def extract_delta(chat_history: list[dict], start_index: int) -> list[dict]:
    """
    Выделить новые ходы ассистента/инструментов из истории после process_message.

    Берём только role="assistant" и role="tool" из chat_history[start_index:].
    Ход пользователя (в т.ч. системный промпт, который агент вставляет в index 0
    на первом сообщении) намеренно пропускаем — сырой user_message пишется
    отдельно ДО вызова агента.

    Returns
    -------
    list[dict]
        Записи в формате save_messages.
    """
    entries: list[dict] = []
    for item in chat_history[start_index:]:
        role = item.get("role")
        if role == "assistant":
            entries.append({
                "role": "assistant",
                "content": item.get("content"),
                "tool_calls": item.get("tool_calls"),
            })
        elif role == "tool":
            entries.append({
                "role": "tool",
                "content": item.get("content"),
                "tool_name": item.get("name"),
            })
    return entries
