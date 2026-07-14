"""Приём ошибок фронтенда — чтобы «чёрный ящик» не был слеп на клиент (T8).

Фронт ловит window.onerror / onunhandledrejection и шлёт их сюда. Мы логируем
структурной строкой и отправляем в Sentry как сообщение. Эндпоинт публичный:
ошибки бывают и до логина. Размеры полей ограничены, чтобы не принимать мусор.
"""
import logging

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.core.monitoring import capture_message

logger = logging.getLogger("client_errors")

router = APIRouter(tags=["Monitoring"])


class ClientErrorReport(BaseModel):
    message: str = Field(max_length=2000)
    kind: str | None = Field(default=None, max_length=50)  # onerror | unhandledrejection
    source: str | None = Field(default=None, max_length=500)
    lineno: int | None = None
    colno: int | None = None
    stack: str | None = Field(default=None, max_length=8000)
    url: str | None = Field(default=None, max_length=1000)


@router.post("/client-errors", status_code=204)
async def report_client_error(data: ClientErrorReport, request: Request) -> None:
    """Принять ошибку фронтенда, залогировать и отправить в Sentry."""
    payload = data.model_dump()
    payload["user_agent"] = request.headers.get("user-agent")
    logger.error("client_error %s", payload)
    capture_message(
        f"[frontend:{data.kind or 'error'}] {data.message} @ {data.url or data.source}",
        level="error",
    )
