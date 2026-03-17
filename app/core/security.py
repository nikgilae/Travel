import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings


def hash_password(password: str) -> str:
    """
    Хэшировать пароль через bcrypt.

    Parameters
    ----------
    password : str
        Открытый пароль пользователя.

    Returns
    -------
    str
        Bcrypt хэш пароля для сохранения в БД.
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверить соответствие открытого пароля его хэшу.

    Parameters
    ----------
    plain_password : str
        Открытый пароль из запроса пользователя.
    hashed_password : str
        Bcrypt хэш из базы данных.

    Returns
    -------
    bool
        True если пароль совпадает с хэшем, иначе False.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(user_id: uuid.UUID) -> str:
    """
    Создать JWT access token для пользователя.

    Токен содержит sub (user_id), exp (время истечения)
    и type (тип токена для защиты от подстановки refresh токена).
    Подписывается SECRET_KEY алгоритмом HS256.

    Parameters
    ----------
    user_id : uuid.UUID
        UUID пользователя — сохраняется в поле sub токена.

    Returns
    -------
    str
        Подписанный JWT токен в формате header.payload.signature.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> uuid.UUID | None:
    """
    Декодировать и валидировать JWT access token.

    Проверяет подпись, срок действия и тип токена.
    Возвращает None при любой ошибке — не пробрасывает исключения
    наружу, HTTP 401 генерируется в dependencies.py.

    Parameters
    ----------
    token : str
        JWT токен из заголовка Authorization: Bearer <token>.

    Returns
    -------
    uuid.UUID | None
        UUID пользователя если токен валидный,
        None если токен невалидный, истёкший или неверного типа.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "access":
            return None
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        return uuid.UUID(user_id_str)
    except (jwt.PyJWTError, ValueError):
        return None