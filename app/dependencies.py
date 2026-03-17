from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user import UserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency для получения текущего аутентифицированного пользователя.

    Извлекает JWT токен из заголовка Authorization: Bearer <token>,
    декодирует его, загружает пользователя из БД.
    Используется во всех защищённых эндпоинтах через Depends.

    Parameters
    ----------
    token : str
        JWT токен извлечённый из заголовка FastAPI автоматически.
    session : AsyncSession
        Сессия БД предоставленная через get_db dependency.

    Returns
    -------
    User
        Объект текущего пользователя из БД.

    Raises
    ------
    HTTPException
        401 если токен невалидный, истёкший или пользователь не найден.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user