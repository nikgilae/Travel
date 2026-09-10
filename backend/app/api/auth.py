from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.config import settings
from app.core.events import log_event, EVENT_LOGIN
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    ClaimRequest,
    RegisterRequest,
    LoginRequest,
    TokenResponse,
)
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
    request: Request,
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
        user_id, access_token, token_type, expires_in, is_first_login.
    """
    user, token, is_first_login = await service.register(data.email, data.password)
    return TokenResponse(
        user_id=user.id,
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        is_first_login=is_first_login,
    )


@router.post(
    "/guest",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Гостевой вход без регистрации",
)
async def guest(
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Завести гостевой аккаунт и выдать токен.

    Вызывается фронтом при первом заходе, без участия человека: весь
    онбординг требует авторизации, а форму регистрации мы показываем
    только после того, как человек увидел маршрут (POST /auth/claim).

    Returns
    -------
    TokenResponse
        user_id, access_token, token_type, expires_in, is_first_login=true.
    """
    user, token = await service.create_guest()
    return TokenResponse(
        user_id=user.id,
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        is_first_login=True,
    )


@router.post(
    "/claim",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Превратить гостевой аккаунт в настоящий",
)
async def claim(
    data: ClaimRequest,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Дописать почту и пароль к уже существующему гостевому аккаунту.

    Поездки никуда не переносятся: они и так принадлежат этому же
    пользователю, у него просто появляется способ войти второй раз.

    Parameters
    ----------
    data : ClaimRequest
        Почта и пароль, вписанные человеком.
    current_user : User
        Гостевой пользователь из токена.
    service : AuthService
        Сервис аутентификации.

    Returns
    -------
    TokenResponse
        user_id, свежий access_token, token_type, expires_in.
    """
    user, token = await service.claim(current_user, data.email, data.password)
    return TokenResponse(
        user_id=user.id,
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        is_first_login=False,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Авторизация пользователя",
)
async def login(
    request: Request,
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
        user_id, access_token, token_type, expires_in, is_first_login.
    """
    user, token, is_first_login = await service.login(data.email, data.password)
    log_event(EVENT_LOGIN, user_id=user.id)
    return TokenResponse(
        user_id=user.id,
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        is_first_login=is_first_login,
    )