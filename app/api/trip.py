import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.trip import (
    TripCreate, TripUpdate, TripPOICreate,
    TripResponse, TripWithPOIsResponse,
    TripPOIWithWarningsResponse,
    TripGenerateRequest, TripGenerateResponse,
    TripDayFinalizeRequest # <--- Эта схема нужна для ручного выбора
)
from app.schemas.rule import RuleWithStrictResponse
from app.services.trip import TripService
from app.services.trip_ai import TripAIService
from app.schemas.trip import TripGenerateRequest, TripGenerateResponse


router = APIRouter(prefix="/trips", tags=["Trips"])


def get_trip_service(session: AsyncSession = Depends(get_db)) -> TripService:
    """
    Dependency для получения TripService.

    Parameters
    ----------
    session : AsyncSession
        Сессия БД.

    Returns
    -------
    TripService
        Экземпляр сервиса поездок.
    """
    return TripService(session)


@router.post(
    "",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать поездку",
)
async def create_trip(
    data: TripCreate,
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(get_current_user),
) -> TripResponse:
    """
    Создать новую поездку для текущего пользователя.

    Parameters
    ----------
    data : TripCreate
        Параметры поездки: страна, город, цель, бюджет и т.д.
    service : TripService
        Сервис поездок.
    current_user : User
        Текущий авторизованный пользователь — владелец поездки.

    Returns
    -------
    TripResponse
        Созданный объект поездки с trip_id.
    """
    return await service.create(
        user_id=current_user.id,
        country_id=data.country_id,
        city_id=data.city_id,
        purpose=data.purpose,
        budget=data.budget,
        group_size=data.group_size,
        other_information=data.other_information,
        start_date=data.start_date,
        end_date=data.end_date,
    )


@router.get(
    "",
    response_model=list[TripResponse],
    summary="Список поездок пользователя",
)
async def get_trips(
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(get_current_user),
) -> list[TripResponse]:
    """
    Получить все поездки текущего пользователя.

    Parameters
    ----------
    service : TripService
        Сервис поездок.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    list[TripResponse]
        Список поездок пользователя.
    """
    return await service.get_user_trips(current_user.id)


@router.get(
    "/{trip_id}",
    response_model=TripWithPOIsResponse,
    summary="Детали поездки",
)
async def get_trip(
    trip_id: uuid.UUID,
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(get_current_user),
) -> TripWithPOIsResponse:
    """
    Получить поездку с полным маршрутом.

    Возвращает только если поездка принадлежит текущему пользователю.

    Parameters
    ----------
    trip_id : uuid.UUID
        UUID поездки.
    service : TripService
        Сервис поездок.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    TripWithPOIsResponse
        Поездка с местами маршрута отсортированными по sequence_order.
    """
    return await service.get_with_details(trip_id, current_user.id)


@router.put(
    "/{trip_id}",
    response_model=TripResponse,
    summary="Обновить поездку",
)
async def update_trip(
    trip_id: uuid.UUID,
    data: TripUpdate,
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(get_current_user),
) -> TripResponse:
    """
    Обновить параметры поездки (partial update).

    Обновляются только переданные поля.
    Возвращает ошибку если поездка не принадлежит пользователю.

    Parameters
    ----------
    trip_id : uuid.UUID
        UUID поездки.
    data : TripUpdate
        Поля для обновления. Все опциональны.
    service : TripService
        Сервис поездок.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    TripResponse
        Обновлённый объект поездки.
    """
    update_data = data.model_dump(exclude_unset=True)
    return await service.update(trip_id, current_user.id, **update_data)


@router.delete(
    "/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить поездку",
)
async def delete_trip(
    trip_id: uuid.UUID,
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Удалить поездку и все её места.

    Каскадное удаление trip_pois через FK.
    Возвращает 204 No Content при успехе.

    Parameters
    ----------
    trip_id : uuid.UUID
        UUID поездки.
    service : TripService
        Сервис поездок.
    current_user : User
        Текущий авторизованный пользователь.
    """
    await service.delete(trip_id, current_user.id)


@router.post(
    "/{trip_id}/pois",
    response_model=TripPOIWithWarningsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить POI в маршрут",
)
async def add_poi_to_trip(
    trip_id: uuid.UUID,
    data: TripPOICreate,
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(get_current_user),
) -> TripPOIWithWarningsResponse:
    """
    Добавить точку интереса в маршрут поездки.

    Core Feature — Contextual Engine. При добавлении места
    автоматически возвращает contextual_warnings — правила
    которые нужно соблюдать при посещении.

    Parameters
    ----------
    trip_id : uuid.UUID
        UUID поездки.
    data : TripPOICreate
        poi_id, sequence_order, planned_start_time.
    service : TripService
        Сервис поездок.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    TripPOIWithWarningsResponse
        trip_id, poi_id, sequence_order и contextual_warnings.
    """
    trip_poi, poi_rules = await service.add_poi(
        trip_id=trip_id,
        user_id=current_user.id,
        poi_id=data.poi_id,
        sequence_order=data.sequence_order,
        planned_start_time=data.planned_start_time,
    )

    warnings = [
        RuleWithStrictResponse(
            id=pr.rule.id,
            is_strict=pr.is_strict,
            content=pr.rule.content,
        )
        for pr in poi_rules
    ]

    return TripPOIWithWarningsResponse(
        trip_id=trip_poi.trip_id,
        poi_id=trip_poi.poi_id,
        sequence_order=trip_poi.sequence_order,
        planned_start_time=trip_poi.planned_start_time,
        contextual_warnings=warnings,
    )


@router.delete(
    "/{trip_id}/pois/{poi_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить POI из маршрута",
)
async def remove_poi_from_trip(
    trip_id: uuid.UUID,
    poi_id: uuid.UUID,
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Удалить точку интереса из маршрута поездки.

    Parameters
    ----------
    trip_id : uuid.UUID
        UUID поездки.
    poi_id : uuid.UUID
        UUID точки интереса для удаления.
    service : TripService
        Сервис поездок.
    current_user : User
        Текущий авторизованный пользователь.
    """
    await service.remove_poi(trip_id, current_user.id, poi_id)

def get_trip_ai_service(session: AsyncSession = Depends(get_db)) -> TripAIService:
    """
    Dependency для получения TripAIService.

    Parameters
    ----------
    session : AsyncSession
        Сессия БД.

    Returns
    -------
    TripAIService
        Экземпляр сервиса генерации маршрута.
    """
    return TripAIService(session)


@router.post(
    "/{trip_id}/generate",
    response_model=TripGenerateResponse,
    summary="Сгенерировать маршрут через AI",
)
async def generate_trip(
    trip_id: uuid.UUID,
    data: TripGenerateRequest,
    service: TripAIService = Depends(get_trip_ai_service),
    current_user: User = Depends(get_current_user),
) -> TripGenerateResponse:
    """
    Сгенерировать персонализированный маршрут через AI.

    AI получает все POI города и правила из нашей БД,
    параметры поездки и интересы пользователя.
    Возвращает упорядоченный маршрут по дням с советами
    и оценкой бюджета. Сохраняет маршрут в БД автоматически.

    Parameters
    ----------
    trip_id : uuid.UUID
        UUID поездки для которой генерируем маршрут.
    data : TripGenerateRequest
        days, interests, notes.
    service : TripAIService
        Сервис генерации маршрута.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    TripGenerateResponse
        Сгенерированный маршрут с summary, days, saved_pois_count.
    """
    result = await service.generate(
        trip_id=trip_id,
        user_id=current_user.id,
        # days=data.days,  <--- ЭТУ СТРОКУ НУЖНО УДАЛИТЬ
        interests=data.interests,
        notes=data.notes,
    )
    return TripGenerateResponse(**result)


@router.post(
    "/{trip_id}/finalize",
    response_model=TripWithPOIsResponse,
    summary="Финализировать маршрут (Ручной выбор)",
)
async def finalize_trip_route(
    trip_id: uuid.UUID,
    data: TripDayFinalizeRequest,
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(get_current_user),
) -> TripWithPOIsResponse:
    """
    Принимает список UUID мест (poi_ids) в том порядке, в котором
    пользователь хочет их посетить. 
    Система автоматически пересортирует их для оптимальной логистики
    и зафиксирует маршрут.
    """
    updated_trip = await service.finalize_route(
        trip_id=trip_id,
        user_id=current_user.id,
        selected_poi_ids=data.poi_ids
    )
    return updated_trip


@router.post(
    "/{trip_id}/finalize/auto-main",
    response_model=TripWithPOIsResponse,
    summary="Авто-финализация (Только основные места)",
)
async def auto_finalize_trip_main(
    trip_id: uuid.UUID,
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(get_current_user),
) -> TripWithPOIsResponse:
    """
    Кнопка 'Сделать как предложил ИИ'. 
    Берет все места со статусом 'main' из сгенерированного пула,
    выстраивает их в удобный маршрут и сохраняет выбор.
    """
    updated_trip = await service.auto_finalize_main_pois(
        trip_id=trip_id, 
        user_id=current_user.id
    )
    return updated_trip