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
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    information: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    geom: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=True,
    )
    is_indoor: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Relationships
    rules: Mapped[list["POIRule"]] = relationship(
        back_populates="poi",
        cascade="all, delete-orphan",
    )
    trip_pois: Mapped[list["TripPOI"]] = relationship(
        back_populates="poi",
    )