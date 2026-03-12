# Репозиторий для работы с таблицей users.
# Содержит методы специфичные для пользователей:
# поиск по email (логин) и проверка существования (регистрация).

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):

    def __init__(self, session: AsyncSession) -> None:
        # Передаём модель User в родительский класс.
        # Снаружи достаточно передать только сессию.
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        # Используется при логине — ищем пользователя по email
        # для последующей проверки пароля.
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        # Используется при регистрации — проверяем что email не занят.
        # select(User.id) вместо select(User) — загружаем только id,
        # не тянем все поля из БД (быстрее).
        result = await self.session.execute(
            select(User.id).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None