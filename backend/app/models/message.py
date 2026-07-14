import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Message(Base):
    """
    ORM модель таблицы messages — «чёрный ящик» переписки с AI.

    Пишется в режиме write-only: сообщения только записываются, ни REST, ни
    WebSocket не гидрируют историю обратно из БД (поведение для пользователя не
    меняется — см. TODO-1). Одна запись = один ход диалога (user / assistant /
    tool). Запись best-effort: её сбой никогда не должен ронять сам чат.

    Attributes
    ----------
    id : uuid.UUID
        Первичный ключ.
    user_id : uuid.UUID
        FK на users.id. Кто участвует в диалоге. CASCADE — удаляется с юзером.
    trip_id : uuid.UUID or None
        FK на trips.id. Привязка к поездке; NULL для общего чата (/chat/general).
        SET NULL — транскрипт переживает удаление поездки.
    role : str
        Роль автора хода: "user", "assistant" или "tool".
    content : str or None
        Текст сообщения. NULLABLE: у ассистентского хода с чистым вызовом
        инструмента текста нет (content=None, есть только tool_calls).
    tool_name : str or None
        Имя инструмента для записей role="tool" (какая функция дала результат).
    tool_calls : list or None
        Сериализованные вызовы инструментов для записей role="assistant"
        (что ассистент решил вызвать). NULL если вызовов не было.
    created_at : datetime
        Время записи. Ставится PostgreSQL через now().
    """

    __tablename__ = "messages"
    __table_args__ = (
        # Индексы под чтение транскриптов: по поездке и по пользователю во времени.
        Index("idx_messages_trip_created", "trip_id", "created_at"),
        Index("idx_messages_user_created", "user_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    trip_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trips.id", ondelete="SET NULL"),
        nullable=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    tool_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tool_calls: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
