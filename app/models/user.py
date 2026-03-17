import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """
    ORM модель таблицы users.

    Хранит учётные данные пользователей.
    Аутентификация только через email + пароль (OAuth вне скоупа MVP).

    Attributes
    ----------
    id : uuid.UUID
        Первичный ключ. UUID генерируется на стороне Python до INSERT.
    email : str
        Уникальный email адрес. Максимум 254 символа по RFC 5321.
    hashed_password : str
        Bcrypt хэш пароля. Всегда ровно 60 символов.
    created_at : datetime
        Время создания записи. Устанавливается PostgreSQL через now().
    updated_at : datetime
        Время последнего обновления. Обновляется автоматически при UPDATE.
    trips : list[Trip]
        Все поездки пользователя. Удаляются каскадно при удалении юзера.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(254),
        nullable=False,
        unique=True,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(60),
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

    trips: Mapped[list["Trip"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )