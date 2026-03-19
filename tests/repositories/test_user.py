from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository
from app.core.security import hash_password
import uuid


class TestUserRepository:

    async def test_create_user(self, db_session: AsyncSession):
        """Создание пользователя — проверяем что серверные поля заполняются."""
        repo = UserRepository(db_session)
        user = await repo.create(
            email="newuser@test.com",
            hashed_password=hash_password("Pass123"),
        )

        assert user.id is not None
        assert user.email == "newuser@test.com"
        assert user.created_at is not None
        assert user.updated_at is not None

    async def test_get_by_email(self, db_session: AsyncSession):
        """Поиск пользователя по email — должен найти существующего."""
        repo = UserRepository(db_session)
        await repo.create(
            email="find@test.com",
            hashed_password=hash_password("Pass123"),
        )
        await db_session.commit()

        found = await repo.get_by_email("find@test.com")

        assert found is not None
        assert found.email == "find@test.com"

    async def test_get_by_email_not_found(self, db_session: AsyncSession):
        """Поиск по несуществующему email — должен вернуть None."""
        repo = UserRepository(db_session)

        found = await repo.get_by_email("nobody@nowhere.com")

        assert found is None
    async def test_exists_by_email_true(self, db_session: AsyncSession):
        """exists_by_email возвращает True для существующего email."""
        repo = UserRepository(db_session)
        await repo.create(
            email="exists@test.com",
            hashed_password=hash_password("Pass123"),
        )
        await db_session.commit()

        result = await repo.exists_by_email("exists@test.com")

        assert result is True

    async def test_exists_by_email_false(self, db_session: AsyncSession):
        """exists_by_email возвращает False для несуществующего email."""
        repo = UserRepository(db_session)

        result = await repo.exists_by_email("nobody@nowhere.com")

        assert result is False

    async def test_delete_user(self, db_session: AsyncSession):
        """Удаление пользователя — после удаления не находится по ID."""
        repo = UserRepository(db_session)
        user = await repo.create(
            email="delete@test.com",
            hashed_password=hash_password("Pass123"),
        )
        await db_session.commit()

        result = await repo.delete(user.id)
        await db_session.commit()

        assert result is True
        found = await repo.get_by_id(user.id)
        assert found is None
    