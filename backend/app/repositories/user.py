from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Репозиторий для работы с таблицей users.

    Содержит методы специфичные для пользователей:
    поиск по email для логина и проверка существования
    для регистрации.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        """
        Найти пользователя по email адресу.

        Используется при логине для последующей проверки пароля.

        Parameters
        ----------
        email : str
            Email адрес пользователя.

        Returns
        -------
        User | None
            Объект пользователя если найден, иначе None.
        """
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        """
        Проверить существование пользователя по email.

        Используется при регистрации чтобы не допустить дубликатов.
        Загружает только id вместо всего объекта для экономии ресурсов.

        Parameters
        ----------
        email : str
            Email адрес для проверки.

        Returns
        -------
        bool
            True если пользователь с таким email уже существует.
        """
        result = await self.session.execute(
            select(User.id).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None