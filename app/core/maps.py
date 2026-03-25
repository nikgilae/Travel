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
                        "poi_id": uuid.uuid4(), 
                        "name": place.get("name"),
                        "coordinates": {
                            "lat": lat,
                            "lng": lng
                        },
                        "is_indoor": False,
                        # Теперь мы возвращаем еще и эти поля!
                        "description": description,
                        "information": information
                    })
            return results