import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.poi import POIResponse
from app.schemas.rule import RuleWithStrictResponse


class TripCreate(BaseModel):
    """
    Схема создания поездки.

    Attributes
    ----------
    country_id : uuid.UUID
        UUID страны назначения.
    city_id : uuid.UUID
        UUID города назначения.
    purpose : str
        Цель поездки. Допустимые значения: leisure, business,
        education, other.
    budget : str
        Уровень бюджета. Допустимые значения: low, medium, high.
    group_size : int
        Количество путешественников. Минимум 1.
    other_information : Optional[list[str]]
        Дополнительные предпочтения. Например: ['вегетарианец'].
    start_date : Optional[date]
        Дата начала поездки.
    end_date : Optional[date]
        Дата окончания. Должна быть >= start_date.
    """

    country_id: uuid.UUID
    city_id: uuid.UUID
    purpose: str = Field("leisure", pattern="^(leisure|business|education|other)$")
    budget: str = Field("medium", pattern="^(low|medium|high)$")
    group_size: int = Field(1, ge=1)
    other_information: Optional[list[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @model_validator(mode="after")
    def validate_dates(self) -> "TripCreate":
        """
        Проверить что дата окончания не раньше даты начала.

        Returns
        -------
        TripCreate
            Объект схемы если даты валидны.

        Raises
        ------
        ValueError
            Если end_date раньше start_date.
        """
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date должна быть >= start_date")
        return self


class TripUpdate(BaseModel):
    """
    Схема обновления поездки.

    Все поля опциональны — обновляются только переданные.

    Attributes
    ----------
    purpose : Optional[str]
        Новая цель поездки.
    budget : Optional[str]
        Новый уровень бюджета.
    group_size : Optional[int]
        Новый размер группы.
    other_information : Optional[list[str]]
        Новые дополнительные предпочтения.
    start_date : Optional[date]
        Новая дата начала.
    end_date : Optional[date]
        Новая дата окончания.
    """

    purpose: Optional[str] = Field(
        None, pattern="^(leisure|business|education|other)$"
    )
    budget: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    group_size: Optional[int] = Field(None, ge=1)
    other_information: Optional[list[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class TripPOICreate(BaseModel):
    """
    Схема добавления POI в маршрут.

    Attributes
    ----------
    poi_id : uuid.UUID
        UUID точки интереса.
    sequence_order : float
        Порядковый номер в маршруте. Должен быть > 0.
        Float позволяет вставлять между позициями: 1.5 между 1.0 и 2.0.
    planned_start_time : Optional[datetime]
        Запланированное время посещения с timezone.
    """

    poi_id: uuid.UUID
    sequence_order: float = Field(..., gt=0)
    planned_start_time: Optional[datetime] = None


class TripPOIResponse(BaseModel):
    """
    Схема ответа с местом маршрута и данными POI.

    Attributes
    ----------
    poi : POIResponse
        Данные точки интереса.
    sequence_order : float
        Порядковый номер в маршруте.
    planned_start_time : Optional[datetime]
        Запланированное время посещения.
    """

    model_config = {"from_attributes": True}

    poi: POIResponse
    sequence_order: float
    planned_start_time: Optional[datetime]


class TripPOIWithWarningsResponse(BaseModel):
    """
    Схема ответа при добавлении POI в маршрут.

    Возвращается при POST /trips/{trip_id}/pois.
    Плоская структура по контракту аналитика —
    trip_id и poi_id как отдельные поля.

    Attributes
    ----------
    trip_id : uuid.UUID
        UUID поездки.
    poi_id : uuid.UUID
        UUID добавленного места.
    sequence_order : float
        Порядковый номер в маршруте.
    planned_start_time : Optional[datetime]
        Запланированное время посещения.
    contextual_warnings : list[RuleWithStrictResponse]
        Правила посещения POI. Строгие правила (is_strict=True)
        показываются как предупреждения, остальные как советы.
    """

    model_config = {"from_attributes": True}

    trip_id: uuid.UUID
    poi_id: uuid.UUID
    sequence_order: float
    planned_start_time: Optional[datetime] = None
    contextual_warnings: list[RuleWithStrictResponse] = []


class TripResponse(BaseModel):
    """
    Схема ответа с данными поездки.

    Attributes
    ----------
    id : uuid.UUID
        Уникальный идентификатор поездки.
    user_id : uuid.UUID
        UUID владельца поездки.
    country_id : uuid.UUID
        UUID страны назначения.
    city_id : uuid.UUID
        UUID города назначения.
    purpose : str
        Цель поездки.
    budget : str
        Уровень бюджета.
    group_size : int
        Количество путешественников.
    other_information : Optional[list[str]]
        Дополнительные предпочтения.
    start_date : Optional[date]
        Дата начала.
    end_date : Optional[date]
        Дата окончания.
    created_at : datetime
        Время создания поездки.
    """

    model_config = {"from_attributes": True}

    id: uuid.UUID
    user_id: uuid.UUID
    country_id: uuid.UUID
    city_id: uuid.UUID
    purpose: str
    budget: str
    group_size: int
    other_information: Optional[list[str]]
    start_date: Optional[date]
    end_date: Optional[date]
    created_at: datetime


class TripWithPOIsResponse(TripResponse):
    """
    Схема ответа с поездкой и полным маршрутом.

    Расширяет TripResponse добавляя список мест.
    Используется в GET /trips/{trip_id}.

    Attributes
    ----------
    pois : list[TripPOIResponse]
        Места маршрута отсортированные по sequence_order.
    """

    pois: list[TripPOIResponse] = []
    
    
class TripGenerateRequest(BaseModel):
    """
    Схема запроса на генерацию маршрута через AI.

    Attributes
    ----------
    days : int
        Количество дней поездки. Минимум 1, максимум 30.
    interests : list[str]
        Интересы пользователя. Например: ['история', 'еда', 'шопинг'].
    notes : Optional[str]
        Дополнительные пожелания. Например: 'хотим посетить рынки'.
    """

    interests: list[str] = Field(..., description="Список интересов пользователя")
    notes: str | None = Field(None, description="Дополнительные пожелания")


class GeneratedPOIResponse(BaseModel):
    """
    Схема одного места в сгенерированном маршруте.

    Attributes
    ----------
    poi_id : str
        UUID точки интереса из нашей БД.
    name : str
        Название места.
    start_time : str
        Время начала посещения. Например: '09:00'.
    duration_hours : float
        Продолжительность посещения в часах.
    budget_estimate : str
        Оценка бюджета на посещение. Например: '120 юаней/чел'.
    ai_tip : str
        Персональный совет AI для этого места.
    """

    poi_id: str
    name: str
    start_time: str
    duration_hours: float
    budget_estimate: str
    ai_tip: str


class GeneratedDayResponse(BaseModel):
    """
    Схема одного дня в сгенерированном маршруте.

    Attributes
    ----------
    day : int
        Номер дня.
    theme : str
        Тема дня. Например: 'История и культура'.
    pois : list[GeneratedPOIResponse]
        Места для посещения в этот день.
    """

    day: int
    theme: str
    pois: list[GeneratedPOIResponse]


class TripGenerateResponse(BaseModel):
    """
    Схема ответа с полностью сгенерированным маршрутом.

    Attributes
    ----------
    trip_id : uuid.UUID
        UUID поездки.
    summary : str
        Краткое описание маршрута от AI.
    total_budget_estimate : str
        Общая оценка бюджета на группу.
    days : list[GeneratedDayResponse]
        Маршрут по дням.
    saved_pois_count : int
        Количество мест сохранённых в БД из маршрута.
    """

    trip_id: uuid.UUID
    summary: str
    total_budget_estimate: str
    days: list[GeneratedDayResponse]
    saved_pois_count: int