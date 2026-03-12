# Модуль подключения к базе данных.
# Создаёт асинхронный движок SQLAlchemy, фабрику сессий и базовый класс моделей.
# Все модели наследуются от Base — это позволяет Alembic видеть их при генерации миграций.

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# Асинхронный движок — пул соединений с PostgreSQL.
# Создаётся один раз при старте приложения и переиспользуется всеми запросами.
# echo=True выводит все SQL запросы в консоль — убрать в продакшне.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
)

# Фабрика сессий — создаёт новую сессию для каждого HTTP запроса.
# expire_on_commit=False — объекты остаются доступны после commit()
# без повторного запроса к БД.
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Базовый класс для всех ORM моделей.
# Все модели (User, Trip, POI и др.) наследуются от Base.
# SQLAlchemy через Base.metadata знает о всех таблицах проекта —
# это используется Alembic для автогенерации миграций.
class Base(DeclarativeBase):
    pass


# Dependency для FastAPI — предоставляет сессию БД в роутеры.
# Открывает сессию перед запросом и закрывает после — даже при ошибке.
# Использование:
#   async def endpoint(db: AsyncSession = Depends(get_db)):
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session