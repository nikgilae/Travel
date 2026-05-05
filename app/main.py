from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

from app.api.auth import router as auth_router
from app.api.geography import router as geo_router
from app.api.rule import router as rule_router
from app.api.poi import router as poi_router
from app.api.trip import router as trip_router
from app.core.exceptions import (
    NotFoundException,
    AlreadyExistsException,
    UnauthorizedException,
    ForbiddenException,
)
from app.api import chat


app = FastAPI(
    title="Smart Travel Companion API",
    description="Backend API для планирования путешествий и контекстного ассистента",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── ОБРАБОТЧИКИ ОШИБОК (RFC 7807) ─────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Обработчик ошибок валидации Pydantic.

    Форматирует ошибки валидации по стандарту RFC 7807.
    Вызывается автоматически когда Pydantic не может
    валидировать входящие данные запроса.

    Parameters
    ----------
    request : Request
        Входящий HTTP запрос.
    exc : RequestValidationError
        Исключение с деталями ошибок валидации.

    Returns
    -------
    JSONResponse
        HTTP 422 с полями error_code, message, details.
    """
    details = []
    for error in exc.errors():
        details.append({
            "field": " → ".join(str(loc) for loc in error["loc"]),
            "issue": error["msg"],
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "error_code": "VALIDATION_FAILED",
            "message": "Input validation failed",
            "details": details,
        },
    )


@app.exception_handler(NotFoundException)
async def not_found_handler(
    request: Request,
    exc: NotFoundException,
) -> JSONResponse:
    """
    Обработчик ошибки 404 Not Found.

    Parameters
    ----------
    request : Request
        Входящий HTTP запрос.
    exc : NotFoundException
        Исключение с описанием не найденного ресурса.

    Returns
    -------
    JSONResponse
        HTTP 404 с полями error_code и message.
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error_code": "RESOURCE_NOT_FOUND",
            "message": exc.detail,
        },
    )


@app.exception_handler(AlreadyExistsException)
async def already_exists_handler(
    request: Request,
    exc: AlreadyExistsException,
) -> JSONResponse:
    """
    Обработчик ошибки 409 Conflict.

    Parameters
    ----------
    request : Request
        Входящий HTTP запрос.
    exc : AlreadyExistsException
        Исключение с описанием конфликта.

    Returns
    -------
    JSONResponse
        HTTP 409 с полями error_code и message.
    """
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error_code": "ALREADY_EXISTS",
            "message": exc.detail,
        },
    )


@app.exception_handler(UnauthorizedException)
async def unauthorized_handler(
    request: Request,
    exc: UnauthorizedException,
) -> JSONResponse:
    """
    Обработчик ошибки 401 Unauthorized.

    Parameters
    ----------
    request : Request
        Входящий HTTP запрос.
    exc : UnauthorizedException
        Исключение аутентификации.

    Returns
    -------
    JSONResponse
        HTTP 401 с полями error_code и message.
    """
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error_code": "UNAUTHORIZED",
            "message": exc.detail,
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(ForbiddenException)
async def forbidden_handler(
    request: Request,
    exc: ForbiddenException,
) -> JSONResponse:
    """
    Обработчик ошибки 403 Forbidden.

    Parameters
    ----------
    request : Request
        Входящий HTTP запрос.
    exc : ForbiddenException
        Исключение доступа.

    Returns
    -------
    JSONResponse
        HTTP 403 с полями error_code и message.
    """
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error_code": "FORBIDDEN",
            "message": exc.detail,
        },
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    """
    Обработчик непредвиденных ошибок базы данных.

    Перехватывает необработанные ошибки SQLAlchemy
    и возвращает HTTP 500 без деталей внутренней ошибки —
    детали не раскрываются клиенту из соображений безопасности.

    Parameters
    ----------
    request : Request
        Входящий HTTP запрос.
    exc : SQLAlchemyError
        Исключение SQLAlchemy.

    Returns
    -------
    JSONResponse
        HTTP 500 с полями error_code и message.
    """
    print(f"РЕАЛЬНАЯ ОШИБКА БАЗЫ: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "DATABASE_ERROR",
            "message": "An internal database error occurred",
        },
    )


# ── РОУТЕРЫ ───────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(geo_router)
app.include_router(rule_router)
app.include_router(poi_router)
app.include_router(trip_router)
app.include_router(chat.router)


# ── HEALTHCHECK ───────────────────────────────────────────────────────────────


@app.get("/health", tags=["System"])
async def health_check() -> dict:
    """
    Проверка работоспособности сервера и базы данных.

    Выполняет реальный запрос к PostgreSQL чтобы убедиться
    что БД доступна и принимает соединения.

    Returns
    -------
    dict
        Статус сервера, БД и версия API.
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "unavailable"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "version": "1.0.0",
        "database": db_status,
    }