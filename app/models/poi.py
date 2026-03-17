import uuid

from geoalchemy2 import Geometry
from sqlalchemy import String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class POI(Base):
    """
    ORM модель таблицы pois (Points of Interest).

    Хранит места которые пользователь добавляет в маршрут.
    Поле geom использует PostGIS для хранения координат
    и пространственных запросов (поиск в радиусе).

    Attributes
    ----------
    id : uuid.UUID
        Первичный ключ.
    name : str
        Название места. Максимум 255 символов.
    description : str or None
        Краткое описание для карточки места.
    information : str or None
        Подробная информация для страницы места.
    geom : str or None
        Координаты в формате PostGIS POINT, SRID 4326 (WGS84).
        Используется для пространственных запросов через ST_DWithin.
        Alembic автоматически создаёт индекс GIST для этого поля.
    is_indoor : bool
        True если место внутри здания (музей, ресторан).
        Влияет на логику маршрута (приоритет крытых мест в дождь).
    rules : list[POIRule]
        Правила посещения через связующую таблицу.
    trip_pois : list[TripPOI]
        Записи маршрутов где встречается это место.
    """

    __tablename__ = "pois"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    information: Mapped[str | None] = mapped_column(Text, nullable=True)
    geom: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=True,
    )
    is_indoor: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    rules: Mapped[list["POIRule"]] = relationship(
        back_populates="poi",
        cascade="all, delete-orphan",
    )
    trip_pois: Mapped[list["TripPOI"]] = relationship(back_populates="poi")