import uuid
from datetime import datetime, date

from sqlalchemy import Integer, Text, Date, DateTime, Float, ForeignKey, func, CheckConstraint, ARRAY, String
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


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
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="chk_trips_dates"),
        CheckConstraint("group_size >= 1", name="chk_trips_group_size"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
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

    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="trips",
    )
    country: Mapped["Country"] = relationship(
        back_populates="trips",
    )
    city: Mapped["City"] = relationship(
        back_populates="trips",
    )
    pois: Mapped[list["TripPOI"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
    )


class TripPOI(Base):
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
    sequence_order: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    planned_start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    trip: Mapped["Trip"] = relationship(
        back_populates="pois",
    )
    poi: Mapped["POI"] = relationship(
        back_populates="trip_pois",
    )