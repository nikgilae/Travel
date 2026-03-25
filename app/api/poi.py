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
from app.core.maps import GoogleMapsClient
from app.services.geography import CityService


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
    summary="Поиск POI через Google Places API",
)
async def search_pois(
    query: str = Query(..., description="Поисковый запрос, например 'Мечеть Джумейра'"),
    city_id: uuid.UUID = Query(..., description="UUID города для фильтрации"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db), # <-- Добавили сессию
) -> POISearchResponse:
    """
    Поиск точек интереса через Google Places API.
    Не сохраняет результаты в базу данных, а только отдает пользователю.
    """
    # 1. Получаем название города, чтобы сделать поиск умным
    city_service = CityService(session)
    city = await city_service.get_by_id(city_id)
    
    # "Музеи" -> "Музеи Токио" (чтобы Google не искал по всему миру)
    smart_query = f"{query} {city.name}"
    
    # 2. Идем в Google
    maps_client = GoogleMapsClient()
    results = await maps_client.search_places(smart_query)
    
    # 3. Возвращаем результат
    return {"results": results}


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
        city_id=data.city_id
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


@router.get(
    "",
    response_model=list[POIResponse],
    summary="Список всех POI",
)
async def get_pois(
    service: POIService = Depends(get_poi_service),
    current_user: User = Depends(get_current_user),
) -> list[POIResponse]:
    """
    Получить список всех точек интереса.

    Parameters
    ----------
    service : POIService
        Сервис POI.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    list[POIResponse]
        Список всех POI.
    """
    return await service.get_all()


@router.get(
    "/{poi_id}",
    response_model=POIResponse,
    summary="Получить POI по ID",
)
async def get_poi(
    poi_id: uuid.UUID,
    service: POIService = Depends(get_poi_service),
    current_user: User = Depends(get_current_user),
) -> POIResponse:
    """
    Получить конкретную точку интереса по ID.

    Parameters
    ----------
    poi_id : uuid.UUID
        UUID точки интереса.
    service : POIService
        Сервис POI.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    POIResponse
        Объект точки интереса.
    """
    return await service.get_by_id(poi_id)