import logging
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.trip import TripService
from app.services.chat_agent import TravelAgentService
from app.services.ai import client as ai_client
from app.config import settings
from app.core.security import decode_access_token
from app.dependencies import get_current_user
from app.models.user import User
from app.services.message_log import save_messages, extract_delta
from app.core.events import log_event, EVENT_CHAT_MESSAGE
from app.core.monitoring import capture_exception, notify_telegram

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trips", tags=["Chat"])
general_router = APIRouter(prefix="/chat", tags=["Chat"])

GENERAL_SYSTEM_PROMPT = (
    "Ты — помощник по путешествиям TourRhythm. "
    "Отвечай коротко и конкретно, на русском языке. "
    "Пользователь ещё не создал маршрут — можешь помочь с выбором направления, "
    "ответить на вопросы о странах, визах, бюджете. "
    "Если пользователь хочет спланировать поездку, предложи создать маршрут."
)


class ChatHistoryItem(BaseModel):
    role: str   # "user" | "assistant"
    content: str


class GeneralChatRequest(BaseModel):
    message: str
    history: list[ChatHistoryItem] = []


@general_router.post("/general")
async def general_chat(
    data: GeneralChatRequest,
    current_user: User = Depends(get_current_user),
) -> dict:
    # Пишем сырой ход пользователя ДО вызова AI — если AI упадёт, диалог не потеряется.
    await save_messages(current_user.id, None, [{"role": "user", "content": data.message}])
    log_event(EVENT_CHAT_MESSAGE, user_id=current_user.id, trip_id=None, channel="general")

    messages = [{"role": "system", "content": GENERAL_SYSTEM_PROMPT}]
    for item in data.history[-20:]:  # keep last 20 turns max
        messages.append({"role": item.role, "content": item.content})
    messages.append({"role": "user", "content": data.message})

    response = await ai_client.chat.completions.create(
        model=settings.AI_MODEL,
        messages=messages,
        max_tokens=600,
    )
    reply = response.choices[0].message.content

    # Ответ ассистента — тоже best-effort.
    await save_messages(current_user.id, None, [{"role": "assistant", "content": reply}])

    return {"reply": reply}

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

            # Пишем сырой ход пользователя ДО агента — аварийные диалоги не теряются.
            await save_messages(user_uuid, trip_id, [{"role": "user", "content": user_message}])
            log_event(EVENT_CHAT_MESSAGE, user_id=user_uuid, trip_id=trip_id, channel="ws")

            # Запоминаем длину истории, чтобы после агента забрать только новые ходы.
            before_len = len(chat_history)

            # Передаем всё в ИИ
            ai_response = await agent_service.process_message(
                messages=chat_history,
                user_message=user_message,
                trip_id=str(trip_id),
                user_id=str(user_uuid)
            )

            # Ответы ассистента и вызовы инструментов — по дельте истории, best-effort.
            await save_messages(user_uuid, trip_id, extract_delta(chat_history, before_len))

            # Отвечаем клиенту
            await websocket.send_json({
                "sender": "ai",
                "text": ai_response
            })

    except WebSocketDisconnect:
        logger.info(f"[WS Trip {trip_id}] Пользователь {user_uuid} отключился.")
    except Exception as e:
        logger.exception(f"[WS Trip {trip_id}] Внутренняя ошибка")
        # WS не проходит через HTTP exception-handlers — шлём ошибку в мониторинг тут.
        capture_exception(e)
        await notify_telegram(
            f"🛑 WS_ERROR (trip {trip_id})\n{type(e).__name__}: {e}"
        )
        await websocket.send_json({"sender": "system", "text": "Техническая ошибка сервера."})