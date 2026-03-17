import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.poi import (
    POICreate, POIResponse,
    POISearchResponse, NearbyPOIRequest,
)
from app.services.poi import POIService


router = APIRouter(prefix="/pois", tags=["POI"])


def get_poi_service(session: AsyncSession = Depends(get_db)) -> POIService:
    """
    Dependency для получения POIService.

    Parameters
    ----------
    session : AsyncSession
        Сессия БД.

    Returns
    -------
    POIService
        Экземпляр сервиса POI.
    """
    return POIService(session)


@router.get(
    "/search",
    response_model=POISearchResponse,
    summary="Поиск POI через картографический API",
)
async def search_pois(
    query: str = Query(..., description="Поисковый запрос, например 'Мечеть Джумейра'"),
    city_id: uuid.UUID = Query(..., description="UUID города для фильтрации"),
    current_user: User = Depends(get_current_user),
) -> POISearchResponse:
    """
    Поиск точек интереса через картографический API.

    Заглушка Sprint 1 — всегда возвращает пустой список.
    В Sprint 2 будет реализована реальная интеграция с
    Google Maps / Яндекс Картами через абстрактный адаптер.
    NFR: ответ должен быть < 1.5 сек после реализации.

    Parameters
    ----------
    query : str
        Поисковый запрос.
    city_id : uuid.UUID
        UUID города для фильтрации результатов.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    POISearchResponse
        Список найденных мест. Сейчас всегда пустой.
    """
    # TODO Sprint 2: реализовать интеграцию с картографическим API
    # Абстрактный адаптер: Google Maps / Яндекс Карты / Mapbox
    return POISearchResponse(results=[])


@router.post(
    "",
    response_model=POIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать POI вручную",
)
async def create_poi(
    data: POICreate,
    service: POIService = Depends(get_poi_service),
    current_user: User = Depends(get_current_user),
) -> POIResponse:
    """
    Создать точку интереса вручную.

    Используется для наполнения базы данных.
    Если переданы координаты lat/lon — формирует PostGIS геометрию.

    Parameters
    ----------
    data : POICreate
        Данные точки интереса.
    service : POIService
        Сервис POI.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    POIResponse
        Созданный объект POI.
    """
    return await service.create(
        name=data.name,
        description=data.description,
        information=data.information,
        lat=data.lat,
        lon=data.lon,
        is_indoor=data.is_indoor,
    )


@router.get(
    "/nearby",
    response_model=list[POIResponse],
    summary="Поиск ближайших POI",
)
async def get_nearby_pois(
    lat: float = Query(..., ge=-90, le=90, description="Широта"),
    lon: float = Query(..., ge=-180, le=180, description="Долгота"),
    radius_meters: float = Query(500, ge=50, le=50_000, description="Радиус в метрах"),
    service: POIService = Depends(get_poi_service),
    current_user: User = Depends(get_current_user),
) -> list[POIResponse]:
    """
    Найти POI в заданном радиусе через PostGIS ST_DWithin.

    Parameters
    ----------
    lat : float
        Широта пользователя.
    lon : float
        Долгота пользователя.
    radius_meters : float
        Радиус поиска в метрах. По умолчанию 500.
    service : POIService
        Сервис POI.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    list[POIResponse]
        Список POI в радиусе.
    """
    return await service.get_nearby(lat, lon, radius_meters)