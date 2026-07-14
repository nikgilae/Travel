"""
Logging configuration for the application.
Supports both development (pretty) and production (JSON) formats.
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Any

from app.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Create formatter
    if settings.DEBUG:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        # JSON formatter for production (structured)
        formatter = JsonFormatter()

    # Configure root logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    # Долговечные логи (T7): если задан LOG_DIR — дублируем в файл с ротацией.
    # В проде LOG_DIR монтируется на volume, поэтому event-лог и ошибки переживают
    # redeploy. Всегда JSON-формат (structured), даже в DEBUG — файл для разбора.
    if settings.LOG_DIR:
        try:
            os.makedirs(settings.LOG_DIR, exist_ok=True)
            file_handler = RotatingFileHandler(
                os.path.join(settings.LOG_DIR, "app.log"),
                maxBytes=10 * 1024 * 1024,  # 10 МБ на файл
                backupCount=5,               # храним 5 ротаций (~50 МБ суммарно)
                encoding="utf-8",
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(JsonFormatter())
            root_logger.addHandler(file_handler)
        except OSError:
            # Не смогли открыть файл (права/путь) — не роняем старт, остаёмся на stdout.
            root_logger.warning("LOG_DIR=%s недоступен, файловый лог выключен", settings.LOG_DIR)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ("name", "msg", "args", "levelname", "levelno", "pathname",
                          "filename", "module", "exc_info", "exc_text", "stack_info",
                          "lineno", "funcName", "created", "msecs", "relativeCreated",
                          "thread", "threadName", "processName", "process"):
                log_data[key] = value

        return self._dict_to_json(log_data)

    @staticmethod
    def _dict_to_json(data: dict) -> str:
        import json
        return json.dumps(data, ensure_ascii=False, default=str)