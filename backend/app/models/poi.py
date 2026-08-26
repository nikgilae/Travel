import uuid

from geoalchemy2 import Geometry
from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from geoalchemy2.shape import to_shape

# Размерность вектора зависит от модели эмбеддинга (settings.AI_EMBEDDING_MODEL,
# сейчас openai/text-embedding-3-large = 3072). Смена модели на другую размерность
# требует новой миграции.
EMBEDDING_DIM = 3072


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
    embedding : list[float] or None
        Векторное представление текста POI (ai_description, если есть, иначе
        name + description + information) для семантического retrieval.
        None, пока не посчитан backfill'ом или синхронным хуком в POIService.
    ai_description : str or None
        Обогащённое описание места (Итерация 4 RAG-POI-PLAN.md) — по
        убыванию достоверности: editorial_summary Google, саммари отзывов
        или None, если обогащение не проводилось/не дало результата.
    ai_description_source : str or None
        Источник ai_description: "google_editorial" / "reviews_summary" /
        "category_fallback" / None (не обогащалось).
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
    
    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    city: Mapped["City"] = relationship(back_populates="pois")

    rules: Mapped[list["POIRule"]] = relationship(
        back_populates="poi",
        cascade="all, delete-orphan",
    )
    trip_pois: Mapped[list["TripPOI"]] = relationship(back_populates="poi")
    
    google_place_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIM),
        nullable=True,
    )

    ai_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_description_source: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )

    @property
    def lat(self) -> float:
        """Достает широту из PostGIS объекта geom"""
        if self.geom is not None:
            # Превращаем бинарные данные geom в объект shapely и берем Y (широту)
            return to_shape(self.geom).y
        return 0.0

    @property
    def lon(self) -> float:
        """Достает долготу из PostGIS объекта geom"""
        if self.geom is not None:
            # Превращаем бинарные данные geom в объект shapely и берем X (долготу)
            return to_shape(self.geom).x
        return 0.0