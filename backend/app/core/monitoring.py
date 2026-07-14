"""Видимость ошибок: Sentry + fallback-алерт в Telegram-бот фаундера.

Оба канала опциональны и включаются переменными окружения:
- SENTRY_DSN задан → ошибки уходят в Sentry.
- TG_BOT_TOKEN + TG_CHAT_ID заданы → каждая 5xx дублируется в личный Telegram
  фаундера (fallback на случай, если Sentry недоступен из РФ-инфраструктуры).

Пакет sentry-sdk импортируется мягко: если он не установлен, приложение всё
равно стартует, просто Sentry-канал молчит. Ни одна функция здесь не бросает
исключений наружу — мониторинг не должен ронять обработку запроса.
"""
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

try:
    import sentry_sdk
except ImportError:  # пакет не установлен — работаем без Sentry
    sentry_sdk = None

_sentry_enabled = False


def init_sentry() -> None:
    """Инициализировать Sentry, если установлен пакет и задан DSN. Idempotent-safe."""
    global _sentry_enabled
    if sentry_sdk is None:
        logger.info("Sentry: пакет sentry-sdk не установлен — канал выключен")
        return
    if not settings.SENTRY_DSN:
        logger.info("Sentry: SENTRY_DSN не задан — канал выключен")
        return
    try:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            traces_sample_rate=0.0,  # волна 1: только ошибки, без performance-трейсинга
            send_default_pii=False,
        )
        _sentry_enabled = True
        logger.info("Sentry: инициализирован")
    except Exception:
        logger.exception("Sentry: ошибка инициализации (игнорируем)")


def capture_exception(exc: BaseException) -> None:
    """Отправить исключение в Sentry, если включён. Никогда не бросает."""
    if not _sentry_enabled or sentry_sdk is None:
        return
    try:
        sentry_sdk.capture_exception(exc)
    except Exception:
        logger.exception("Sentry capture_exception failed (ignored)")


def capture_message(message: str, level: str = "error") -> None:
    """
    Отправить произвольное сообщение в Sentry (напр. ошибку фронтенда, у которой
    нет Python-исключения). Если Sentry выключен — no-op. Никогда не бросает.
    """
    if not _sentry_enabled or sentry_sdk is None:
        return
    try:
        sentry_sdk.capture_message(message, level=level)
    except Exception:
        logger.exception("Sentry capture_message failed (ignored)")


async def notify_telegram(text: str) -> None:
    """
    Отправить короткий алерт в Telegram-бот фаундера. Best-effort, не бросает.

    No-op, если TG_BOT_TOKEN/TG_CHAT_ID не заданы.
    """
    if not settings.TG_BOT_TOKEN or not settings.TG_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TG_CHAT_ID,
        "text": text[:4000],  # лимит Telegram — 4096 символов
        "disable_web_page_preview": True,
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(url, json=payload)
    except Exception:
        logger.exception("notify_telegram failed (ignored)")
