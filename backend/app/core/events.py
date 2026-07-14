"""Событийный лог — «чёрный ящик» поведения пользователей волны 1.

Каждое важное действие пишется одной структурной JSON-строкой в обычный логгер
(logging_config уже настроен). При N<20 отдельная таблица events не нужна —
читается grep/jq по лог-файлу. Ключевые поля: event, user_id, trip_id, ts.

log_event НИКОГДА не бросает исключение: сбой аналитики не должен ронять запрос.
"""
import json
import logging
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ── Константы имён событий (чтобы не расходились строки по коду) ──────────────
EVENT_LOGIN = "login"
EVENT_TRIP_CREATED = "trip_created"
EVENT_GENERATE = "generate"
EVENT_DAY_FINALIZED = "day_finalized"
EVENT_POI_REMOVED = "poi_removed"
EVENT_CHAT_MESSAGE = "chat_message"


def log_event(
    event: str,
    user_id: uuid.UUID | str | None = None,
    trip_id: uuid.UUID | str | None = None,
    **extra,
) -> None:
    """
    Записать событие в лог структурной JSON-строкой. Не бросает исключений.

    Parameters
    ----------
    event : str
        Имя события — одна из EVENT_* констант.
    user_id : uuid.UUID or str or None
        Кто совершил действие.
    trip_id : uuid.UUID or str or None
        Связанная поездка, если применимо.
    **extra
        Доп. поля события (day_number, poi_id, channel, count и т.п.).
    """
    try:
        payload = {
            "event": event,
            "user_id": str(user_id) if user_id is not None else None,
            "trip_id": str(trip_id) if trip_id is not None else None,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        if extra:
            payload.update(extra)
        logger.info("event %s", json.dumps(payload, ensure_ascii=False, default=str))
    except Exception:
        # аналитика — не критичный путь; глотаем любые ошибки сериализации/логирования
        logger.exception("log_event failed (ignored)")
