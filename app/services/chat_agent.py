import logging
import uuid
import json
import httpx
from openai import AsyncOpenAI

from app.services.trip import TripService
from app.config import settings

logger = logging.getLogger(__name__)

class TravelAgentService:
    """
    ИИ-Оркестратор. Связывает намерения пользователя с методами TripService.
    """

    def __init__(self, trip_service: TripService):
        self.trip_service = trip_service
        
        custom_timeout = httpx.Timeout(60.0)
        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL,
            timeout=custom_timeout,
        ) 
        
        self.model_name = "gemini-2.5-flash" 
        
        self.system_prompt = """
        Ты — элитный тревел-консьерж. Помогай пользователю планировать путешествие.
        У тебя есть доступ к инструментам (tools).

        ПРАВИЛА:
        1. Для финализации маршрута (собери план, сделай завтра как предлагал) вызывай tool_auto_finalize_day.
        2. Для изменения бюджета или цели вызывай tool_update_trip_info.
        3. Для удаления места по просьбе юзера вызывай tool_remove_poi_from_day.
        4. ВСЕГДА бери poi_id из скрытого контекста (ID: ...).
        5. Дополняй ответы своими знаниями о достопримечательностях.
        """

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "tool_update_trip_info",
                    "description": "Обновить бюджет или цель поездки.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "trip_id": {"type": "string"},
                            "user_id": {"type": "string"},
                            "budget": {"type": "string", "enum": ["low", "medium", "high"]},
                            "purpose": {"type": "string"}
                        },
                        "required": ["trip_id", "user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "tool_auto_finalize_day",
                    "description": "Собрать оптимальный маршрут на день.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "trip_id": {"type": "string"},
                            "user_id": {"type": "string"},
                            "day_number": {"type": "integer"}
                        },
                        "required": ["trip_id", "user_id", "day_number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "tool_remove_poi_from_day",
                    "description": "Удалить конкретное место из маршрута.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "trip_id": {"type": "string"},
                            "user_id": {"type": "string"},
                            "poi_id": {"type": "string", "description": "UUID из контекста (ID: ...)"}
                        },
                        "required": ["trip_id", "user_id", "poi_id"]
                    }
                }
            }
        ]

    # --- Методы-обертки для ИИ ---

    async def tool_auto_finalize_day(self, trip_id: str, user_id: str, day_number: int) -> dict:
        try:
            await self.trip_service.auto_finalize_main_pois(uuid.UUID(trip_id), uuid.UUID(user_id), day_number)
            return {"status": "success", "message": f"День {day_number} финализирован."}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def tool_update_trip_info(self, trip_id: str, user_id: str, budget: str = None, purpose: str = None) -> dict:
        try:
            update_data = {k: v for k, v in {"budget": budget, "purpose": purpose}.items() if v is not None}
            await self.trip_service.update(uuid.UUID(trip_id), uuid.UUID(user_id), **update_data)
            return {"status": "success", "message": "Данные обновлены."}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def tool_remove_poi_from_day(self, trip_id: str, user_id: str, poi_id: str) -> dict:
        try:
            await self.trip_service.remove_poi_from_day(uuid.UUID(trip_id), uuid.UUID(user_id), uuid.UUID(poi_id))
            return {"status": "success", "message": f"Место {poi_id} удалено из маршрута."}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # --- Основной цикл обработки ---

    async def process_message(self, messages: list[dict], user_message: str, trip_id: str, user_id: str) -> str:
        # 1. Получаем контекст из БД
        current_trip = await self.trip_service.get_with_details(uuid.UUID(trip_id), uuid.UUID(user_id))
        
        places_info = []
        if current_trip and hasattr(current_trip, 'pois'):
            for tp in current_trip.pois:
                if tp.poi:
                    status = "✅ В маршруте" if tp.is_selected else "🔄 В запасе"
                    info = f"День {tp.day_number}: {tp.poi.name} (ID: {tp.poi.id}) ({status})"
                    if tp.poi.information: info += f" -> {tp.poi.information}"
                    places_info.append(info)
        
        trip_context =  (
            f"ID ТЕКУЩЕЙ ПОЕЗДКИ: {trip_id}\n"
            f"ID ПОЛЬЗОВАТЕЛЯ: {user_id}\n"
            f"Бюджет: {current_trip.budget}. Цель: {current_trip.purpose}.\n"
            f"МЕСТА В МАРШРУТЕ:\n" + "\n".join(places_info)
        )

        if not messages or messages[0].get("role") != "system":
            messages.insert(0, {"role": "system", "content": self.system_prompt})

        full_user_msg = f"[Context: {trip_context}]\n\nUser: {user_message}"
        messages.append({"role": "user", "content": full_user_msg})

        # 2. Запрос к ИИ
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=self.tools
        )

        response_message = response.choices[0].message
        messages.append(response_message.model_dump(exclude_none=True)) 

        # 3. Обработка вызова инструментов
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                logger.info(f"🤖 ИИ вызывает: {function_name}")

                if function_name == "tool_auto_finalize_day":
                    result = await self.tool_auto_finalize_day(**args)
                elif function_name == "tool_update_trip_info": 
                    result = await self.tool_update_trip_info(**args)
                elif function_name == "tool_remove_poi_from_day": 
                    result = await self.tool_remove_poi_from_day(**args)
                else:
                    result = {"status": "error", "error": "Unknown tool"}

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(result, ensure_ascii=False)
                })

            # Финальный ответ после выполнения инструментов
            second_res = await self.client.chat.completions.create(model=self.model_name, messages=messages)
            final_text = second_res.choices[0].message.content
            messages.append({"role": "assistant", "content": final_text})
            return final_text

        return response_message.content