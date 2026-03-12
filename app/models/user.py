# ORM модель таблицы users.
# Хранит учётные данные пользователей.
# Аутентификация только через email + пароль (OAuth вне скоупа MVP).

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    # UUID генерируется на стороне Python до записи в БД.
    # Это позволяет знать ID объекта ещё до INSERT.
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Максимум 254 символа по стандарту RFC 5321.
    # unique=True создаёт уникальный индекс — два пользователя
    # с одним email зарегистрироваться не смогут.
    email: Mapped[str] = mapped_column(
        String(254),
        nullable=False,
        unique=True,
        index=True,
    )

    # Bcrypt всегда возвращает строку ровно 60 символов.
    # Никогда не хранить открытый пароль — только хэш.
    hashed_password: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
    )

    # server_default=func.now() — значение now() вычисляется
    # на стороне PostgreSQL в момент INSERT.
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    # onupdate=func.now() — SQLAlchemy автоматически обновляет
    # это поле при любом UPDATE через ORM.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # cascade="all, delete-orphan" — при удалении пользователя
    # все его поездки удаляются автоматически через ORM.
    trips: Mapped[list["Trip"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )