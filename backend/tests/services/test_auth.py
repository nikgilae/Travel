import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.auth import AuthService
from app.core.exceptions import AlreadyExistsException, UnauthorizedException
from app.core.security import hash_password


class TestAuthService:

    def setup_method(self):
        """Создать моки перед каждым тестом."""
        self.mock_session = AsyncMock()
        self.service = AuthService(self.mock_session)
        self.service.user_repo = AsyncMock()

    async def test_register_success(self):
        """Успешная регистрация — создаёт пользователя и возвращает токен."""
        self.service.user_repo.exists_by_email.return_value = False
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.email = "new@test.com"
        self.service.user_repo.create.return_value = mock_user

        user, token = await self.service.register("new@test.com", "Password123")

        assert user.email == "new@test.com"
        assert token is not None
        assert len(token) > 0
        self.service.user_repo.create.assert_called_once()
        self.mock_session.commit.assert_called_once()

    async def test_register_email_already_exists(self):
        """Регистрация с занятым email — выбрасывает AlreadyExistsException."""
        self.service.user_repo.exists_by_email.return_value = True

        with pytest.raises(AlreadyExistsException):
            await self.service.register("existing@test.com", "Password123")

        self.service.user_repo.create.assert_not_called()
        
    async def test_login_success(self):
        """Успешный логин — возвращает пользователя и токен."""
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.hashed_password = hash_password("Password123")
        self.service.user_repo.get_by_email.return_value = mock_user

        user, token = await self.service.login("user@test.com", "Password123")

        assert user is mock_user
        assert token is not None

    async def test_login_wrong_password(self):
        """Неверный пароль — выбрасывает UnauthorizedException."""
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.hashed_password = hash_password("CorrectPass123")
        self.service.user_repo.get_by_email.return_value = mock_user

        with pytest.raises(UnauthorizedException):
            await self.service.login("user@test.com", "WrongPass123")

    async def test_login_user_not_found(self):
        """Несуществующий email — выбрасывает то же исключение что и неверный пароль."""
        self.service.user_repo.get_by_email.return_value = None

        with pytest.raises(UnauthorizedException):
            await self.service.login("nobody@test.com", "Password123")