import uuid
from datetime import datetime

from sqlalchemy import Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Rule(Base):
    """
    ORM модель таблицы rules.

    Единая таблица переиспользуемых правил.
    Одно правило может быть привязано к стране, городу
    и POI одновременно через связующие таблицы.

    Attributes
    ----------
    id : uuid.UUID
        Первичный ключ.
    content : str
        Текст правила без ограничения длины.
        Например: 'Закрытые плечи и колени обязательны'.
    created_at : datetime
        Время создания записи.
    updated_at : datetime
        Время последнего обновления.
    country_rules : list[CountryRule]
        Связи с странами. Каскадное удаление.
    city_rules : list[CityRule]
        Связи с городами. Каскадное удаление.
    poi_rules : list[POIRule]
        Связи с POI. Каскадное удаление.
    """

    __tablename__ = "rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    country_rules: Mapped[list["CountryRule"]] = relationship(
        back_populates="rule", cascade="all, delete-orphan"
    )
    city_rules: Mapped[list["CityRule"]] = relationship(
        back_populates="rule", cascade="all, delete-orphan"
    )
    poi_rules: Mapped[list["POIRule"]] = relationship(
        back_populates="rule", cascade="all, delete-orphan"
    )


class CountryRule(Base):
    """
    ORM модель связующей таблицы country_rules.

    Реализует many-to-many между countries и rules.
    Составной PK исключает дублирование одного правила для страны.

    Attributes
    ----------
    country_id : uuid.UUID
        FK на countries.id. Часть составного PK.
    rule_id : uuid.UUID
        FK на rules.id. Часть составного PK.
    is_strict : bool
        True — обязательное правило, False — рекомендация.
        Хранится на связи, а не на правиле — одно правило
        может быть строгим для одной страны и мягким для другой.
    country : Country
        Связанная страна.
    rule : Rule
        Связанное правило.
    """

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
        Boolean, nullable=False, default=True
    )

    country: Mapped["Country"] = relationship(back_populates="rules")
    rule: Mapped["Rule"] = relationship(back_populates="country_rules")


class CityRule(Base):
    """
    ORM модель связующей таблицы city_rules.

    Реализует many-to-many между cities и rules.
    Составной PK исключает дублирование одного правила для города.

    Attributes
    ----------
    city_id : uuid.UUID
        FK на cities.id. Часть составного PK.
    rule_id : uuid.UUID
        FK на rules.id. Часть составного PK.
    is_strict : bool
        True — обязательное правило, False — рекомендация.
    city : City
        Связанный город.
    rule : Rule
        Связанное правило.
    """

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
        Boolean, nullable=False, default=True
    )

    city: Mapped["City"] = relationship(back_populates="rules")
    rule: Mapped["Rule"] = relationship(back_populates="city_rules")


class POIRule(Base):
    """
    ORM модель связующей таблицы poi_rules.

    Реализует many-to-many между pois и rules.
    Составной PK исключает дублирование одного правила для POI.

    Attributes
    ----------
    poi_id : uuid.UUID
        FK на pois.id. Часть составного PK.
    rule_id : uuid.UUID
        FK на rules.id. Часть составного PK.
    is_strict : bool
        True — обязательное правило, False — рекомендация.
    poi : POI
        Связанный POI.
    rule : Rule
        Связанное правило.
    """

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
        Boolean, nullable=False, default=True
    )

    poi: Mapped["POI"] = relationship(back_populates="rules")
    rule: Mapped["Rule"] = relationship(back_populates="poi_rules")