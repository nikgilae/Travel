import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Country(Base):
    """
    ORM модель таблицы countries.

    Справочник стран с общей информацией и привязанными правилами.
    Используется как destination в поездках.

    Attributes
    ----------
    id : uuid.UUID
        Первичный ключ.
    name : str
        Уникальное название страны. Максимум 100 символов.
    content : str
        Произвольный справочный текст о стране без ограничения длины.
    created_at : datetime
        Время создания записи.
    updated_at : datetime
        Время последнего обновления.
    cities : list[City]
        Города страны. Удаляются каскадно при удалении страны.
    rules : list[CountryRule]
        Правила страны через связующую таблицу. Каскадное удаление.
    trips : list[Trip]
        Поездки в эту страну. Без каскадного удаления —
        страну нельзя удалить пока есть привязанные поездки (RESTRICT).
    """

    __tablename__ = "countries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
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
    """
    ORM модель таблицы cities.

    Справочник городов с привязкой к стране.
    Уникальность по паре (country_id, name) — одинаковые названия
    в разных странах допустимы (Paris, France и Paris, Texas).

    Attributes
    ----------
    id : uuid.UUID
        Первичный ключ.
    country_id : uuid.UUID
        FK на countries.id. Каскадное удаление при удалении страны.
    name : str
        Название города. Уникально в рамках страны.
    content : str
        Произвольный справочный текст о городе.
    created_at : datetime
        Время создания записи.
    updated_at : datetime
        Время последнего обновления.
    country : Country
        Страна к которой принадлежит город.
    rules : list[CityRule]
        Правила города через связующую таблицу.
    trips : list[Trip]
        Поездки в этот город.
    """

    __tablename__ = "cities"
    __table_args__ = (
        UniqueConstraint("country_id", "name", name="idx_cities_country_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
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

    country: Mapped["Country"] = relationship(back_populates="cities")
    rules: Mapped[list["CityRule"]] = relationship(
        back_populates="city",
        cascade="all, delete-orphan",
    )
    trips: Mapped[list["Trip"]] = relationship(back_populates="city")
    
    pois: Mapped[list["POI"]] = relationship(
        back_populates="city",
        cascade="all, delete-orphan",
    )