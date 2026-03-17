import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import AlreadyExistsException, UnauthorizedException
from app.config import settings
from app.models.user import User
from app.repositories.user import UserRepository


class AuthService:
    """
    Сервис аутентификации и регистрации пользователей.

    Оркестрирует UserRepository для решения бизнес-задач:
    регистрация нового пользователя и выдача JWT токена.
    Не знает о HTTP слое — только бизнес-логика.

    Parameters
    ----------
    session : AsyncSession
        Асинхронная сессия БД. Используется для создания
        репозитория и управления транзакциями через commit.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(self, email: str, password: str) -> tuple[User, str]:
        """
        Зарегистрировать нового пользователя.

        Проверяет что email не занят, хэширует пароль,
        создаёт пользователя в БД и возвращает токен.

        Parameters
        ----------
        email : str
            Email адрес нового пользователя.
        password : str
            Открытый пароль — будет захэширован через bcrypt.

        Returns
        -------
        tuple[User, str]
            Кортеж из объекта пользователя и JWT access токена.

        Raises
        ------
        AlreadyExistsException
            Если пользователь с таким email уже существует.
        """
        if await self.user_repo.exists_by_email(email):
            raise AlreadyExistsException("Email already registered")

        hashed = hash_password(password)
        user = await self.user_repo.create(
            email=email,
            hashed_password=hashed,
        )
        await self.session.commit()

        token = create_access_token(user.id)
        return user, token

    async def login(self, email: str, password: str) -> tuple[User, str]:
        """
        Аутентифицировать пользователя и выдать JWT токен.

        Ищет пользователя по email, проверяет пароль,
        возвращает токен при успешной аутентификации.

        Parameters
        ----------
        email : str
            Email адрес пользователя.
        password : str
            Открытый пароль для проверки.

        Returns
        -------
        tuple[User, str]
            Кортеж из объекта пользователя и JWT access токена.

        Raises
        ------
        UnauthorizedException
            Если пользователь не найден или пароль неверный.
            Намеренно одно исключение для обоих случаев —
            не раскрывает существует ли пользователь с таким email.
        """
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UnauthorizedException("Invalid email or password")

        if not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        token = create_access_token(user.id)
        return user, token