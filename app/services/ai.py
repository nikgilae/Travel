import json
from openai import AsyncOpenAI
import httpx

from app.config import settings

# Настраиваем кастомный таймаут: 15 секунд на коннект, 60 секунд на ожидание ответа
custom_timeout = httpx.Timeout(60.0, connect=15.0)

client = AsyncOpenAI(
    api_key=settings.AI_API_KEY,
    base_url=settings.AI_BASE_URL,
    timeout=custom_timeout,
)


async def generate_trip(
    city_name: str,
    country_name: str,
    days: int,
    purpose: str,
    budget: str,
    group_size: int,
    interests: list[str],
    pois: list[dict],
    city_rules: list[dict],
    notes: str | None = None,
) -> dict:
    """
    Сгенерировать персонализированный пул мест через AI.
    """
    budget_map = {
        "low": "эконом (минимальные расходы)",
        "medium": "средний (комфортное путешествие)",
        "high": "премиум (без ограничений)",
    }
    purpose_map = {
        "leisure": "отдых и туризм",
        "business": "деловая поездка",
        "education": "образование",
        "other": "другое",
    }

    pois_text = "\n".join([
        f"- ID: {p['id']} | {p['name']}: {p['description']}"
        + (f" | Правила: {', '.join(r['content'] for r in p['rules'])}" if p.get('rules') else "")
        for p in pois
    ])

    rules_text = "\n".join([
        f"- {'⚠️ ОБЯЗАТЕЛЬНО' if r['is_strict'] else '💡 Рекомендация'}: {r['content']}"
        for r in city_rules
    ])

    prompt = f"""Ты — опытный тревел-ассистент. Составь детальный маршрут путешествия.

ПАРАМЕТРЫ ПОЕЗДКИ:
- Город: {city_name}, {country_name}
- Дней: {days}
- Цель: {purpose_map.get(purpose, purpose)}
- Бюджет: {budget_map.get(budget, budget)}
- Группа: {group_size} чел.
- Интересы: {', '.join(interests)}
{f'- Пожелания: {notes}' if notes else ''}

ДОСТУПНЫЕ МЕСТА (используй их poi_id в ответе):
{pois_text}

ВАЖНЫЕ ПРАВИЛА ГОРОДА:
{rules_text}

ЗАДАЧА:
Сформируй расширенный пул мест (минимум 5 объектов на каждый день).
1. Основные (main_pois): 3-4 места, которые идеально подходят под интересы.
2. Дополнительные (additional_pois): 3-4 запасных варианта поблизости или для смены настроения.
Учитывай: время работы мест, логистику между ними, интересы.
Никогда не предлагай одно и то же место дважды в рамках одной поездки. Если у тебя закончились идеи, лучше предложи просто погулять по району

ОТВЕТЬ СТРОГО В JSON ФОРМАТЕ (без markdown, без ```json, только чистый JSON):
{{
    "summary": "краткое описание концепции поездки 2-3 предложения",
    "total_budget_estimate": "оценка общего бюджета на группу",
    "days": [
        {{
            "day": 1,
            "theme": "тема дня например: История и культура",
            "main_pois": [
                {{
                    "poi_id": "id из списка выше",
                    "name": "точное название места из списка",
                    "start_time": "10:00",
                    "duration_hours": 2.5,
                    "budget_estimate": "120 юаней/чел",
                    "ai_tip": "конкретный совет для этого места"
                }}
            ],
            "additional_pois": [
                {{
                    "poi_id": "id из списка выше",
                    "name": "точное название места из списка",
                    "start_time": "14:00",
                    "duration_hours": 1.5,
                    "budget_estimate": "0",
                    "ai_tip": "почему стоит рассмотреть это место как запасное"
                }}
            ]
        }}
    ]
}}"""

    response = await client.chat.completions.create(
        model=settings.AI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты профессиональный тревел-ассистент. "
                    "Отвечаешь только в формате JSON без лишнего текста. "
                    "Используешь реальные poi_id из предоставленного списка."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=10000,
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)