import uuid
from datetime import datetime

from sqlalchemy import Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
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

    # Relationships
    country_rules: Mapped[list["CountryRule"]] = relationship(
        back_populates="rule",
        cascade="all, delete-orphan",
    )
    city_rules: Mapped[list["CityRule"]] = relationship(
        back_populates="rule",
        cascade="all, delete-orphan",
    )
    poi_rules: Mapped[list["POIRule"]] = relationship(
        back_populates="rule",
        cascade="all, delete-orphan",
    )


class CountryRule(Base):
    __tablename__ = "country_rules"

    country_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("countries.id", ondelete="CASCADE"),
        primary_key=True,
    )
    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rules.id", ondelete="CASCADE"),
        primary_key=True,
    )
    is_strict: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # Relationships
    country: Mapped["Country"] = relationship(
        back_populates="rules",
    )
    rule: Mapped["Rule"] = relationship(
        back_populates="country_rules",
    )


class CityRule(Base):
    __tablename__ = "city_rules"

    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="CASCADE"),
        primary_key=True,
    )
    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rules.id", ondelete="CASCADE"),
        primary_key=True,
    )
    is_strict: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # Relationships
    city: Mapped["City"] = relationship(
        back_populates="rules",
    )
    rule: Mapped["Rule"] = relationship(
        back_populates="city_rules",
    )


class POIRule(Base):
    __tablename__ = "poi_rules"

    poi_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pois.id", ondelete="CASCADE"),
        primary_key=True,
    )
    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rules.id", ondelete="CASCADE"),
        primary_key=True,
    )
    is_strict: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # Relationships
    poi: Mapped["POI"] = relationship(
        back_populates="rules",
    )
    rule: Mapped["Rule"] = relationship(
        back_populates="poi_rules",
    )