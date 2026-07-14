from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """
    Репозиторий для таблицы messages («чёрный ящик» чата).

    Специфичных методов не нужно — запись идёт через унаследованный create().
    Чтение (гидрация истории) в волне 1 не используется, режим write-only.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Message, session)
