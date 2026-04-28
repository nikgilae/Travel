import uuid
from datetime import datetime, date

from sqlalchemy import Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy import Integer, Date, DateTime, Float, ForeignKey, func, CheckConstraint, ARRAY, String
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


trip_purpose_enum = ENUM(
    "leisure", "business", "education", "other",
    name="trip_purpose",
    create_type=True,
)

budget_level_enum = ENUM(
    "low", "medium", "high",
    name="budget_level",
    create_type=True,
)

poi_status_enum = ENUM(
    "main", "additional",
    name="poi_status_enum",
    create_type=True
)

class Trip(Base):
    """
    ORM модель таблицы trips.

    Поездка пользователя с параметрами путешествия.
    Содержит CHECK constraints на уровне БД как второй
    уровень защиты после валидации в Python.

    Attributes
    ----------
    id : uuid.UUID
        Первичный ключ.
    user_id : uuid.UUID
        FK на users.id. CASCADE — поездка удаляется с пользователем.
    country_id : uuid.UUID
        FK на countries.id. RESTRICT — нельзя удалить страну
        пока есть привязанные поездки.
    city_id : uuid.UUID
        FK на cities.id. RESTRICT — аналогично country_id.
    purpose : str
        Цель поездки. ENUM: leisure, business, education, other.
    budget : str
        Уровень бюджета. ENUM: low, medium, high.
    group_size : int
        Количество путешественников. Минимум 1 (CHECK constraint).
    other_information : list[str] or None
        Массив дополнительных предпочтений.
        Например: ['вегетарианец', 'с детьми'].
    start_date : date or None
        Дата начала поездки.
    end_date : date or None
        Дата окончания. Должна быть >= start_date (CHECK constraint).
    created_at : datetime
        Время создания записи.
    user : User
        Владелец поездки.
    country : Country
        Страна назначения.
    city : City
        Город назначения.
    pois : list[TripPOI]
        Места маршрута. Каскадное удаление при удалении поездки.
    """

    __tablename__ = "trips"
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="chk_trips_dates"),
        CheckConstraint("group_size >= 1", name="chk_trips_group_size"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    country_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("countries.id", ondelete="RESTRICT"),
        nullable=False,
    )
    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    purpose: Mapped[str] = mapped_column(
        trip_purpose_enum, nullable=False, default="leisure"
    )
    budget: Mapped[str] = mapped_column(
        budget_level_enum, nullable=False, default="medium"
    )
    group_size: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )
    other_information: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="trips")
    country: Mapped["Country"] = relationship(back_populates="trips")
    city: Mapped["City"] = relationship(back_populates="trips")
    pois: Mapped[list["TripPOI"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
        order_by="TripPOI.sequence_order", # <-- Добавленная сортировка
    )


class TripPOI(Base):
    """
    ORM модель связующей таблицы trip_pois.

    Место в маршруте поездки. Составной PK (trip_id + poi_id)
    исключает дублирование места в одном маршруте.

    Attributes
    ----------
    trip_id : uuid.UUID
        FK на trips.id. Часть составного PK. CASCADE удаление.
    poi_id : uuid.UUID
        FK на pois.id. Часть составного PK. CASCADE удаление.
    sequence_order : float
        Порядковый номер в маршруте. Float позволяет вставлять
        места без перенумерации: между 1.0 и 2.0 можно вставить 1.5.
        Должен быть > 0 (CHECK constraint).
    planned_start_time : datetime or None
        Запланированное время посещения с учётом timezone (TIMESTAMPTZ).
        Важно для поездок в другие страны — разные часовые пояса.
    trip : Trip
        Поездка к которой принадлежит место.
    poi : POI
        Точка интереса.
    """

    __tablename__ = "trip_pois"
    __table_args__ = (
        CheckConstraint("sequence_order > 0", name="chk_trip_pois_order"),
    )

    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trips.id", ondelete="CASCADE"),
        primary_key=True,
    )
    poi_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pois.id", ondelete="CASCADE"),
        primary_key=True,
    )
    sequence_order: Mapped[float | None] = mapped_column(Float, nullable=True)
    planned_start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    poi_status: Mapped[str] = mapped_column(
        poi_status_enum, 
        nullable=False, 
        default="main"
    )
    is_selected: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        default=False
    )

    trip: Mapped["Trip"] = relationship(back_populates="pois")
    poi: Mapped["POI"] = relationship(back_populates="trip_pois")