# ORM модель таблицы pois (Points of Interest).
# Хранит места которые пользователь добавляет в маршрут.
# Поле geom использует PostGIS для хранения координат и
# пространственных запросов (поиск мест в радиусе).

import uuid

from geoalchemy2 import Geometry
from sqlalchemy import String, Text, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class POI(Base):
    __tablename__ = "pois"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Краткое описание — выводится в карточке места.
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Подробная информация — выводится на странице места.
    information: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # PostGIS тип POINT в системе координат WGS84 (SRID 4326) —
    # стандарт GPS и Google Maps. Хранит координаты (долгота, широта).
    # Используется для пространственных запросов:
    # поиск мест в радиусе, сортировка по расстоянию.
    # Alembic автоматически создаёт GIST индекс для этого поля.
    geom: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=True,
    )

    # True — место внутри здания (музей, ресторан).
    # False — уличное место (парк, площадь).
    # Влияет на логику маршрута (например приоритет крытых мест в дождь).
    is_indoor: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # cascade — при удалении POI удаляются все его правила.
    rules: Mapped[list["POIRule"]] = relationship(
        back_populates="poi",
        cascade="all, delete-orphan",
    )
    trip_pois: Mapped[list["TripPOI"]] = relationship(
        back_populates="poi",
    )