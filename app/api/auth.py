from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.config import settings
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth import AuthService


router = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    """
    Dependency для получения экземпляра AuthService.

    Parameters
    ----------
    session : AsyncSession
        Сессия БД из get_db dependency.

    Returns
    -------
    AuthService
        Экземпляр сервиса аутентификации.
    """
    return AuthService(session)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
async def register(
    data: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Зарегистрировать нового пользователя.

    Создаёт пользователя в БД, хэширует пароль через bcrypt,
    возвращает JWT токен для немедленной авторизации.

    Parameters
    ----------
    data : RegisterRequest
        Email и пароль нового пользователя.
    service : AuthService
        Сервис аутентификации.

    Returns
    -------
    TokenResponse
        user_id, access_token, token_type, expires_in.
    """
    user, token = await service.register(data.email, data.password)
    return TokenResponse(
        user_id=user.id,
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Авторизация пользователя",
)
async def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Авторизовать пользователя и выдать JWT токен.

    Проверяет email и пароль, возвращает токен при успехе.
    Намеренно одинаковая ошибка для неверного email и пароля —
    не раскрывает существование аккаунта.

    Parameters
    ----------
    data : LoginRequest
        Email и пароль пользователя.
    service : AuthService
        Сервис аутентификации.

    Returns
    -------
    TokenResponse
        user_id, access_token, token_type, expires_in.
    """
    user, token = await service.login(data.email, data.password)
    return TokenResponse(
        user_id=user.id,
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )