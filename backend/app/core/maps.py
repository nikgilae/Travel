import uuid
import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class GoogleMapsClient:
    """
    Адаптер для работы с Google Places API.
    """
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        self.details_url = "https://maps.googleapis.com/maps/api/place/details/json"

    async def search_places(self, query: str) -> list[dict]:
        """
        Поиск мест по текстовому запросу.
        """
        if not self.api_key:
            logger.warning("GOOGLE_MAPS_API_KEY не установлен!")
            return []

        async with httpx.AsyncClient() as client:
            try:
                # Делаем запрос к Google
                response = await client.get(
                    self.base_url,
                    params={
                        "query": query,
                        "key": self.api_key,
                        "language": "ru", # Чтобы названия были на русском
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
            except httpx.RequestError as e:
                logger.error(f"Ошибка HTTP при запросе к Google API: {e}")
                return []

            results = []
            
            # Парсим ответ от Google
            for place in data.get("results", []):
                lat = place.get("geometry", {}).get("location", {}).get("lat")
                lng = place.get("geometry", {}).get("location", {}).get("lng")
                
                if lat and lng:
                    # 1. Достаем типы (теги) и делаем из них описание
                    types_raw = place.get("types", [])
                    # Берем первые два тега, убираем нижние подчеркивания (shopping_mall -> shopping mall)
                    clean_types = [t.replace("_", " ") for t in types_raw[:2]]
                    description = ", ".join(clean_types).capitalize() if clean_types else "Интересное место"

                    # 2. Достаем рейтинг и адрес для дополнительной информации
                    rating = place.get("rating", "Нет оценки")
                    reviews = place.get("user_ratings_total", 0)
                    address = place.get("formatted_address", "Адрес не указан")
                    
                    information = f"Рейтинг Google: {rating} ({reviews} отзывов). Адрес: {address}"

                    results.append({
                        # ДОБАВЛЯЕМ СЮДА ПАРСИНГ PLACE_ID
                        "google_place_id": place.get("place_id"),
                        "name": place.get("name"),
                        "coordinates": {
                            "lat": lat,
                            "lng": lng
                        },
                        "is_indoor": False,
                        "description": description,
                        "information": information
                    })
            return results

    async def get_place_details(self, place_id: str) -> dict:
        """
        Получить editorial_summary и reviews места через Place Details API.

        Text Search (search_places выше) их не отдаёт — нужен отдельный вызов
        по place_id. Источник для обогащения корпуса (Итерация 4, RAG-POI-PLAN.md):
        editorial_summary — курируемый Google текст, reviews — сырые отзывы для
        LLM-суммаризации. Тот же стиль отказоустойчивости, что у search_places:
        сбой сети/API — пустой dict, не исключение (вызывающий код должен уметь
        работать без обогащения).
        """
        if not self.api_key:
            logger.warning("GOOGLE_MAPS_API_KEY не установлен!")
            return {}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.details_url,
                    params={
                        "place_id": place_id,
                        "fields": "editorial_summary,reviews",
                        "key": self.api_key,
                        "language": "ru",
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
            except httpx.RequestError as e:
                logger.error(f"Ошибка HTTP при запросе Place Details к Google API: {e}")
                return {}

            if data.get("status") != "OK":
                logger.warning(
                    "Place Details для %s вернул статус %s", place_id, data.get("status")
                )
                return {}

            result = data.get("result", {})
            editorial_summary = result.get("editorial_summary", {}).get("overview")
            reviews = [
                r["text"] for r in result.get("reviews", []) if r.get("text")
            ]

            return {
                "editorial_summary": editorial_summary,
                "reviews": reviews,
            }