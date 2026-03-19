from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user import UserRepository


# HTTPBearer вместо OAuth2PasswordBearer —
# показывает простое поле для токена в Swagger
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency для получения текущего аутентифицированного пользователя.

    Извлекает JWT токен из заголовка Authorization: Bearer <token>,
    декодирует его, загружает пользователя из БД.

    Parameters
    ----------
    credentials : HTTPAuthorizationCredentials
        Credentials извлечённые из заголовка Authorization.
        Содержит scheme (Bearer) и credentials (сам токен).
    session : AsyncSession
        Сессия БД.

    Returns
    -------
    User
        Объект текущего пользователя.

    Raises
    ------
    HTTPException
        401 если токен невалидный или пользователь не найден.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise credentials_exception

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user