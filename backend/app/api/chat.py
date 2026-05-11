import logging
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.trip import TripService
from app.services.chat_agent import TravelAgentService
from app.core.security import decode_access_token

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/trips",
    tags=["Chat"]
)

@router.websocket("/{trip_id}/chat")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    trip_id: uuid.UUID,
    token: str = Query(..., description="JWT токен авторизации"),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket-эндпоинт для защищенного общения с ИИ-ассистентом.

    Устанавливает соединение, валидирует входящий JWT токен из параметров 
    запроса, извлекает ID пользователя и маршрутизирует сообщения в ИИ-Оркестратор.

    Parameters
    ----------
    websocket : fastapi.WebSocket
        Объект WebSocket-соединения.
    trip_id : uuid.UUID
        Уникальный идентификатор поездки.
    token : str
        JWT токен, передаваемый через query-параметр (?token=...).
    db : sqlalchemy.ext.asyncio.AsyncSession, optional
        Асинхронная сессия БД.

    Raises
    ------
    WebSocketDisconnect
        Возникает при отключении клиента.
    """
    await websocket.accept()
    
    # 1. БОЕВАЯ АВТОРИЗАЦИЯ
    # Твоя функция уже делает всю грязную работу и возвращает UUID или None
    user_uuid = decode_access_token(token)
    
    if user_uuid is None:
        logger.warning(f"[WS Trip {trip_id}] Отказ в доступе: невалидный токен.")
        await websocket.send_json({"sender": "system", "text": "Неверный или просроченный токен авторизации."})
        await websocket.close(code=1008)
        return

    # 2. Инициализация сервисов (выполнится только если токен валидный)
    trip_service = TripService(db)
    agent_service = TravelAgentService(trip_service)
    chat_history = []
    
    await websocket.send_json({
        "sender": "ai", 
        "text": "Привет! Я ваш тревел-консьерж. Чем могу помочь с маршрутом?"
    })

    try:
        while True:
            # Ждем сообщение от клиента
            user_message = await websocket.receive_text()
            
            # Передаем всё в ИИ
            ai_response = await agent_service.process_message(
                messages=chat_history,
                user_message=user_message,
                trip_id=str(trip_id),
                user_id=str(user_uuid)
            )
            
            # Отвечаем клиенту
            await websocket.send_json({
                "sender": "ai",
                "text": ai_response
            })

    except WebSocketDisconnect:
        logger.info(f"[WS Trip {trip_id}] Пользователь {user_uuid} отключился.")
    except Exception as e:
        logger.error(f"[WS Trip {trip_id}] Внутренняя ошибка: {e}")
        await websocket.send_json({"sender": "system", "text": "Техническая ошибка сервера."})