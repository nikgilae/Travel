# ORM модели таблиц trips и trip_pois.
# Trip — поездка пользователя с параметрами (страна, город, бюджет и т.д.).
# TripPOI — связующая таблица между поездкой и местами маршрута.
# sequence_order хранится как Float для вставки мест без перенумерации
# (между 1.0 и 2.0 можно вставить 1.5).

import uuid
from datetime import datetime, date

from sqlalchemy import Integer, Text, Date, DateTime, Float, ForeignKey, func, CheckConstraint, ARRAY, String
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ENUM типы создаются в PostgreSQL один раз и переиспользуются.
# create_type=True — SQLAlchemy создаст тип при миграции автоматически.
trip_purpose_enum = ENUM(
    "leisure",
    "business",
    "education",
    "other",
    name="trip_purpose",
    create_type=True,
)

budget_level_enum = ENUM(
    "low",
    "medium",
    "high",
    name="budget_level",
    create_type=True,
)


class Trip(Base):
    __tablename__ = "trips"

    # CheckConstraint — бизнес-правила на уровне БД.
    # Защищают от некорректных данных даже при прямых SQL запросах в обход ORM.
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="chk_trips_dates"),
        CheckConstraint("group_size >= 1", name="chk_trips_group_size"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ondelete="CASCADE" — при удалении пользователя все его поездки удаляются.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ondelete="RESTRICT" — нельзя удалить страну или город
    # пока существуют привязанные поездки.
    # Защита от случайного удаления справочных данных.
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
        trip_purpose_enum,
        nullable=False,
        default="leisure",
    )
    budget: Mapped[str] = mapped_column(
        budget_level_enum,
        nullable=False,
        default="medium",
    )
    group_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    # Массив строк — дополнительные предпочтения путешественника.
    # Например: ["вегетарианец", "нужен лифт", "с детьми"].
    other_information: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
    )
    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship(back_populates="trips")
    country: Mapped["Country"] = relationship(back_populates="trips")
    city: Mapped["City"] = relationship(back_populates="trips")

    # cascade — при удалении поездки все её POI удаляются автоматически.
    pois: Mapped[list["TripPOI"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
    )


class TripPOI(Base):
    __tablename__ = "trip_pois"

    __table_args__ = (
        # sequence_order должен быть положительным числом.
        CheckConstraint("sequence_order > 0", name="chk_trip_pois_order"),
    )

    # Составной первичный ключ — одно место может быть в поездке только один раз.
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

    # Float вместо Integer — позволяет вставлять места между существующими
    # без перенумерации всего маршрута.
    # Пример: между 1.0 и 2.0 можно вставить 1.5.
    sequence_order: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # timezone=True — хранит время с учётом часового пояса (TIMESTAMPTZ).
    # Важно для поездок в другие страны — время в Токио и Москве разное.
    planned_start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    trip: Mapped["Trip"] = relationship(back_populates="pois")
    poi: Mapped["POI"] = relationship(back_populates="trip_pois")