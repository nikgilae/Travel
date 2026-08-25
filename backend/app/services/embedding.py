import logging

import httpx
from openai import AsyncOpenAI

from app.config import settings
from app.models.poi import POI
from app.services.ai import RETRYABLE_AI_ERRORS

logger = logging.getLogger(__name__)

# Свой клиент, не переиспользуем app.services.ai.client/gen_client напрямую —
# отдельный модуль со своей зоной ответственности, но те же таймауты
# (AI_READ_TIMEOUT_SECONDS/AI_CONNECT_TIMEOUT_SECONDS), т.к. это тот же прокси
# и сравнимый порядок задержки, что и chat-вызовы в ai.py.
_embedding_timeout = httpx.Timeout(
    settings.AI_READ_TIMEOUT_SECONDS,
    connect=settings.AI_CONNECT_TIMEOUT_SECONDS,
)

client = AsyncOpenAI(
    api_key=settings.AI_API_KEY,
    base_url=settings.AI_BASE_URL,
    timeout=_embedding_timeout,
    max_retries=0,
)

# Ретраев SDK нет (как и у gen_client в ai.py) — сами решаем, когда повторять.
MAX_EMBEDDING_ATTEMPTS = 3


def build_poi_text(poi: POI) -> str:
    """
    Собрать текст POI для эмбеддинга.

    name + description + information через перенос строки, None-поля
    пропускаются. Единственное место, где считается этот текст — используется
    и синхронными хуками записи, и scripts/backfill_poi_embeddings.py, и
    scripts/export_poi_corpus.py, чтобы не разъезжаться при изменении полей POI.
    """
    parts = [part for part in (poi.name, poi.description, poi.information) if part]
    return "\n".join(parts)


async def get_embedding(text: str) -> list[float]:
    """
    Получить вектор эмбеддинга текста через settings.AI_EMBEDDING_MODEL.

    Ретраи только на сетевые/5xx сбои (RETRYABLE_AI_ERRORS из app.services.ai) —
    4xx (неверный ключ, пустой input) повтором не лечится, падаем сразу же.
    """
    last_error: Exception | None = None
    for attempt in range(1, MAX_EMBEDDING_ATTEMPTS + 1):
        try:
            response = await client.embeddings.create(
                model=settings.AI_EMBEDDING_MODEL,
                input=text,
            )
            return response.data[0].embedding
        except RETRYABLE_AI_ERRORS as e:
            last_error = e
            logger.warning(
                "get_embedding: попытка %d/%d провалилась — %s: %s",
                attempt, MAX_EMBEDDING_ATTEMPTS, type(e).__name__, e,
            )
            continue

    logger.error(
        "get_embedding: не удалось получить эмбеддинг за %d попыток — %s",
        MAX_EMBEDDING_ATTEMPTS, last_error,
    )
    raise last_error
