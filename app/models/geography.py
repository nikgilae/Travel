# ORM модели таблиц countries и cities.
# Хранят географические данные и справочную информацию о странах и городах.
# Используются как destination в поездках (trips).

import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # unique=True + index=True — поиск страны по имени быстрый
    # и гарантированно возвращает одну запись.
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    # Text без ограничения длины — произвольный справочный контент о стране.
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # cascade на cities и rules — при удалении страны удаляются
    # все её города и правила автоматически.
    # trips без cascade — нельзя удалить страну пока есть поездки
    # (защита на уровне FK: ondelete=RESTRICT).
    cities: Mapped[list["City"]] = relationship(
        back_populates="country",
        cascade="all, delete-orphan",
    )
    rules: Mapped[list["CountryRule"]] = relationship(
        back_populates="country",
        cascade="all, delete-orphan",
    )
    trips: Mapped[list["Trip"]] = relationship(
        back_populates="country",
    )


class City(Base):
    __tablename__ = "cities"

    # Составной уникальный индекс — два города с одинаковым названием
    # в одной стране недопустимы. Но одинаковые названия в разных
    # странах разрешены (например: Paris, France и Paris, Texas).
    __table_args__ = (
        UniqueConstraint("country_id", "name", name="idx_cities_country_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ondelete="CASCADE" — при удалении страны все её города
    # удаляются автоматически на уровне PostgreSQL.
    country_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("countries.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Через city.country получаем объект Country без отдельного запроса.
    country: Mapped["Country"] = relationship(
        back_populates="cities",
    )
    rules: Mapped[list["CityRule"]] = relationship(
        back_populates="city",
        cascade="all, delete-orphan",
    )
    trips: Mapped[list["Trip"]] = relationship(
        back_populates="city",
    )