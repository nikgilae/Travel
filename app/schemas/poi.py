import uuid
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.rule import RuleWithStrictResponse


class POICreate(BaseModel):
    """
    Схема создания точки интереса.

    Attributes
    ----------
    name : str
        Название места. От 2 до 255 символов.
    description : Optional[str]
        Краткое описание для карточки.
    information : Optional[str]
        Подробная информация для страницы места.
    lat : Optional[float]
        Широта. От -90 до +90.
    lon : Optional[float]
        Долгота. От -180 до +180.
    is_indoor : bool
        True если место внутри здания.
    """

    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    information: Optional[str] = None
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lon: Optional[float] = Field(None, ge=-180, le=180)
    is_indoor: bool = False


class POIResponse(BaseModel):
    """
    Схема ответа с данными точки интереса.

    Attributes
    ----------
    id : uuid.UUID
        Уникальный идентификатор.
    name : str
        Название места.
    description : Optional[str]
        Краткое описание.
    information : Optional[str]
        Подробная информация.
    is_indoor : bool
        True если место внутри здания.
    """

    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    description: Optional[str]
    information: Optional[str]
    is_indoor: bool


class POIWithRulesResponse(POIResponse):
    """
    Схема ответа с POI и его правилами посещения.

    Расширяет POIResponse добавляя список правил.
    Используется при добавлении POI в маршрут —
    пользователь сразу видит contextual warnings.

    Attributes
    ----------
    rules : list[RuleWithStrictResponse]
        Список правил с флагом is_strict.
    """

    rules: list[RuleWithStrictResponse] = []


class NearbyPOIRequest(BaseModel):
    """
    Схема запроса на поиск ближайших POI.

    Attributes
    ----------
    lat : float
        Широта пользователя. От -90 до +90.
    lon : float
        Долгота пользователя. От -180 до +180.
    radius_meters : float
        Радиус поиска в метрах. От 50 до 50 000.
    """

    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    radius_meters: float = Field(500, ge=50, le=50_000)
    
class CoordinatesResponse(BaseModel):
    """
    Схема координат точки.

    Вложенный объект в POISearchResult.
    Используется в ответе /pois/search.

    Attributes
    ----------
    lat : float
        Широта точки.
    lng : float
        Долгота точки. Поле lng а не lon —
        соответствует формату Google Maps API.
    """

    lat: float
    lng: float


class POISearchResult(BaseModel):
    """
    Схема одного результата поиска POI.

    Attributes
    ----------
    poi_id : uuid.UUID
        Уникальный идентификатор места.
    name : str
        Название места.
    coordinates : CoordinatesResponse
        Координаты места.
    is_indoor : bool
        True если место внутри здания.
    """

    poi_id: uuid.UUID
    name: str
    coordinates: CoordinatesResponse
    is_indoor: bool


class POISearchResponse(BaseModel):
    """
    Схема ответа поиска POI.

    Возвращается при GET /pois/search.
    Заглушка в Sprint 1 — реальная интеграция с
    картографическим API в Sprint 2.

    Attributes
    ----------
    results : list[POISearchResult]
        Список найденных мест.
    """

    results: list[POISearchResult] = []