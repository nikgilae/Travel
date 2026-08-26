import logging

from app.config import settings
from app.services.ai import RETRYABLE_AI_ERRORS, client

logger = logging.getLogger(__name__)

# Ретраев SDK у общего chat-клиента уже есть (app.services.ai.client,
# max_retries=2) — здесь дополнительный верхнеуровневый цикл нужен только
# чтобы отличить "не получилось после ретраев SDK" от единичного сетевого
# сбоя, тем же паттерном, что у get_embedding (app.services.embedding).
MAX_SUMMARY_ATTEMPTS = 3

# Жёсткое анти-галлюцинационное ограничение: тот же принцип, что и в
# TODOS.md TODO-2 ("без галлюцинаций" — ключевое обещание продукта). Текст
# уходит в build_poi_text → embedding → в промпт generate_trip как факт о
# месте, поэтому саммари не должно добавлять ничего, чего нет в отзывах.
_SUMMARY_SYSTEM_PROMPT = (
    "Ты суммаризируешь отзывы посетителей места в 1-2 предложения на русском. "
    "Используй ТОЛЬКО факты, упомянутые в тексте отзывов — ничего не добавляй "
    "от себя и не придумывай детали, которых там нет. Если отзывы "
    "противоречивы или неинформативны, опиши только то, в чём они сходятся. "
    "Без вступлений вроде 'Судя по отзывам' — сразу суть."
)


async def summarize_reviews(reviews: list[str]) -> str | None:
    """
    Сжать до 5 отзывов в 1-2 предложения через LLM.

    Возвращает None на пустом входе или при неудаче вызова — это сигнал
    build_ai_description откатиться на category_fallback, а не исключение.
    """
    if not reviews:
        return None

    reviews_text = "\n---\n".join(reviews[:5])
    messages = [
        {"role": "system", "content": _SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": f"Отзывы:\n{reviews_text}"},
    ]

    for attempt in range(1, MAX_SUMMARY_ATTEMPTS + 1):
        try:
            response = await client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=messages,
                temperature=0.2,
                max_tokens=150,
            )
            content = response.choices[0].message.content
            return content.strip() if content else None
        except RETRYABLE_AI_ERRORS as e:
            logger.warning(
                "summarize_reviews: попытка %d/%d провалилась — %s: %s",
                attempt, MAX_SUMMARY_ATTEMPTS, type(e).__name__, e,
            )
            continue
        except Exception as e:
            # 4xx и прочее неповторяемое — не тратим попытки, откатываемся сразу.
            logger.warning(
                "summarize_reviews: неповторяемая ошибка — %s: %s", type(e).__name__, e
            )
            return None

    logger.error(
        "summarize_reviews: не удалось получить саммари за %d попыток", MAX_SUMMARY_ATTEMPTS
    )
    return None


async def build_ai_description(
    place_details: dict, fallback_description: str
) -> tuple[str, str]:
    """
    Трёхуровневая приоритезация текста POI по убыванию достоверности
    (RAG-POI-PLAN.md, Итерация 4):

    1. editorial_summary Google — курируемый текст, самый надёжный источник.
    2. Саммари отзывов через LLM — реальный контент, сжатый без добавления фактов.
    3. Fallback — текущий шаблон по категории (то, что уже есть как description).

    Returns
    -------
    tuple[str, str]
        (текст, источник) — источник один из "google_editorial",
        "reviews_summary", "category_fallback".
    """
    editorial = place_details.get("editorial_summary")
    if editorial:
        return editorial, "google_editorial"

    reviews = place_details.get("reviews") or []
    if reviews:
        summary = await summarize_reviews(reviews)
        if summary:
            return summary, "reviews_summary"

    return fallback_description, "category_fallback"
