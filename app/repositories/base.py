# Базовый репозиторий — общие методы для работы с БД.
# Все репозитории наследуются от этого класса и получают
# стандартные CRUD операции автоматически.
# Специфичные методы (get_by_email, get_by_country и т.д.)
# добавляются в конкретных репозиториях.

from typing import Generic, TypeVar, Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


# TypeVar с bound=Base — Model может быть только классом
# унаследованным от Base (User, Trip, POI и т.д.).
Model = TypeVar("Model", bound=Base)


class BaseRepository(Generic[Model]):

    def __init__(self, model: Type[Model], session: AsyncSession) -> None:
        # model — класс модели с которой работает репозиторий.
        # session — сессия БД, приходит снаружи чтобы несколько
        # репозиториев могли работать в одной транзакции.
        self.model = model
        self.session = session

    async def get_by_id(self, id: UUID) -> Model | None:
        # scalar_one_or_none() — возвращает объект или None.
        # Если найдено больше одного — выбрасывает исключение.
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Model]:
        # scalars() — извлекает Python объекты из результата запроса.
        result = await self.session.execute(
            select(self.model)
        )
        return list(result.scalars().all())

    async def create(self, **kwargs) -> Model:
        instance = self.model(**kwargs)
        self.session.add(instance)
        # flush() отправляет SQL в БД в рамках текущей транзакции
        # но не делает commit. После flush объект получает id из БД.
        # commit делается на уровне сервиса после всех операций.
        await self.session.flush()
        return instance

    async def delete(self, id: UUID) -> bool:
        instance = await self.get_by_id(id)
        if not instance:
            # Возвращаем False чтобы сервис мог вернуть 404.
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True