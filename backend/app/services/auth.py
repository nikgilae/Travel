import secrets
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import AlreadyExistsException, UnauthorizedException
from app.config import settings
from app.models.user import User
from app.repositories.user import UserRepository
from app.repositories.trip import TripRepository


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
        self.trip_repo = TripRepository(session)

    async def register(self, email: str, password: str) -> tuple[User, str, bool]:
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
        tuple[User, str, bool]
            Кортеж из объекта пользователя, JWT access токена и флага is_first_login.
            is_first_login всегда true при регистрации.

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
        return user, token, True

    async def create_guest(self) -> tuple[User, str]:
        """
        Завести гостевой аккаунт и выдать на него токен.

        Человек об этом аккаунте не знает: он нужен, чтобы онбординг работал
        (страны, города и поездки требуют авторизации) до того, как человек
        увидел хоть какую-то ценность. Форма регистрации приходит позже, на
        готовом маршруте — см. claim() ниже.

        Почта техническая и заведомо недоставляемая (домен .invalid
        зарезервирован RFC 2606), чтобы её нельзя было спутать с настоящей
        ни в базе, ни в рассылке. Пароль случайный и никому не известен:
        войти в гостевой аккаунт можно только по выданному токену.

        Returns
        -------
        tuple[User, str]
            Гостевой пользователь и JWT access токен.
        """
        user = await self.user_repo.create(
            email=f"guest-{uuid.uuid4()}@guest.invalid",
            hashed_password=hash_password(secrets.token_urlsafe(32)),
            is_guest=True,
        )
        await self.session.commit()

        return user, create_access_token(user.id)

    async def claim(self, user: User, email: str, password: str) -> tuple[User, str]:
        """
        Превратить гостевой аккаунт в настоящий, не теряя поездок.

        Поездки уже привязаны к user.id, поэтому здесь только дописываются
        почта и пароль. Никакого переноса данных между аккаунтами нет, и это
        главная причина, по которой гостевой аккаунт лучше по-настоящему
        анонимных сессий: переносить нечего, значит нечему и потеряться.

        Parameters
        ----------
        user : User
            Текущий (гостевой) пользователь из токена.
        email : str
            Почта, которую вписал человек.
        password : str
            Открытый пароль — будет захэширован.

        Returns
        -------
        tuple[User, str]
            Обновлённый пользователь и свежий токен.

        Raises
        ------
        AlreadyExistsException
            Если аккаунт уже настоящий или почта занята кем-то другим.
        """
        if not user.is_guest:
            raise AlreadyExistsException("Account is already registered")

        if await self.user_repo.exists_by_email(email):
            raise AlreadyExistsException("Email already registered")

        updated = await self.user_repo.update(
            user.id,
            email=email,
            hashed_password=hash_password(password),
            is_guest=False,
        )
        await self.session.commit()

        return updated, create_access_token(updated.id)

    async def login(self, email: str, password: str) -> tuple[User, str, bool]:
        """
        Аутентифицировать пользователя и выдать JWT токен.

        Ищет пользователя по email, проверяет пароль,
        возвращает токен при успешной аутентификации.
        Также проверяет, это ли первый вход (у пользователя ещё нет
        ни одной поездки (отправляется на онбординг)).

        Parameters
        ----------
        email : str
            Email адрес пользователя.
        password : str
            Открытый пароль для проверки.

        Returns
        -------
        tuple[User, str, bool]
            Кортеж из объекта пользователя, JWT access токена и флага is_first_login.
            is_first_login = true если у пользователя ещё нет ни одной поездки
            (отправляется на онбординг).

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

        is_first_login = not await self.trip_repo.exists_by_user_id(user.id)

        return user, token, is_first_login