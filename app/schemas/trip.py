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
        """
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date должна быть >= start_date")
        return self


class TripUpdate(BaseModel):
    """
    Схема обновления поездки.
    Все поля опциональны — обновляются только переданные.
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
    Схема добавления POI в маршрут/пул вручную.
    """

    poi_id: uuid.UUID
    # Теперь порядок опционален (FR 2.9)
    sequence_order: Optional[float] = None
    planned_start_time: Optional[datetime] = None
    # Новые поля статуса
    poi_status: str = Field("main", pattern="^(main|additional)$")
    is_selected: bool = False


class TripPOIResponse(BaseModel):
    """
    Схема ответа с местом маршрута и данными POI.
    """

    model_config = {"from_attributes": True}

    poi: POIResponse
    sequence_order: Optional[float]
    planned_start_time: Optional[datetime]
    poi_status: str
    is_selected: bool


class TripPOIWithWarningsResponse(BaseModel):
    """
    Схема ответа при добавлении POI в маршрут.
    Возвращается при POST /trips/{trip_id}/pois.
    """

    model_config = {"from_attributes": True}

    trip_id: uuid.UUID
    poi_id: uuid.UUID
    sequence_order: Optional[float] = None
    planned_start_time: Optional[datetime] = None
    poi_status: str
    is_selected: bool
    contextual_warnings: list[RuleWithStrictResponse] = []


class TripResponse(BaseModel):
    """
    Схема ответа с данными поездки.
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
    Схема ответа с поездкой и полным пулом/маршрутом.
    """
    pois: list[TripPOIResponse] = []


class TripGenerateRequest(BaseModel):
    """
    Схема запроса на генерацию маршрута через AI.
    """
    interests: list[str] = Field(..., description="Список интересов пользователя")
    notes: str | None = Field(None, description="Дополнительные пожелания")


class GeneratedPOIResponse(BaseModel):
    """
    Схема одного места в сгенерированном пуле (FR 2.9).
    """
    poi_id: str
    name: str
    budget_estimate: str
    ai_tip: str
    # Жесткий тайминг опционален на этапе пула
    start_time: Optional[str] = None
    duration_hours: Optional[float] = None


class GeneratedDayResponse(BaseModel):
    """
    Схема пула мест на один день от AI (FR 2.9).
    Разделено на основные и запасные локации.
    """
    day: int
    theme: str
    main_pois: list[GeneratedPOIResponse]
    additional_pois: list[GeneratedPOIResponse]


class TripGenerateResponse(BaseModel):
    """
    Схема ответа с полностью сгенерированным пулом.
    """
    trip_id: uuid.UUID
    summary: str
    total_budget_estimate: str
    days: list[GeneratedDayResponse]
    saved_pois_count: int


class TripDayFinalizeRequest(BaseModel):
    """
    Схема для финализации маршрута накануне (FR 2.10).
    Принимает список UUID выбранных мест в том порядке, 
    в котором пользователь планирует их посетить.
    """
    poi_ids: list[uuid.UUID] = Field(
        ..., 
        description="Список UUID выбранных мест из пула в желаемом порядке посещения",
        min_length=1
    )