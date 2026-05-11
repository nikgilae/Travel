from typing import Generic, TypeVar, Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


Model = TypeVar("Model", bound=Base)


class BaseRepository(Generic[Model]):
    """
    Базовый репозиторий с общими CRUD операциями.

    Все репозитории наследуются от этого класса и получают
    стандартные методы автоматически. Специфичные методы
    добавляются в конкретных репозиториях.

    Parameters
    ----------
    model : Type[Model]
        Класс ORM модели с которой работает репозиторий.
    session : AsyncSession
        Асинхронная сессия БД. Приходит снаружи чтобы несколько
        репозиториев могли работать в одной транзакции.
    """

    def __init__(self, model: Type[Model], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, id: UUID) -> Model | None:
        """
        Найти запись по первичному ключу.

        Parameters
        ----------
        id : UUID
            Первичный ключ записи.

        Returns
        -------
        Model | None
            Объект модели если найден, иначе None.
            Если найдено больше одного — выбрасывает исключение.
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Model]:
        """
        Получить все записи таблицы.

        Returns
        -------
        list[Model]
            Список всех объектов модели.
        """
        result = await self.session.execute(
            select(self.model)
        )
        return list(result.scalars().all())

    async def create(self, **kwargs) -> Model:
        """
        Создать новую запись в БД.

        Выполняет flush для получения серверных дефолтов
        (created_at, updated_at и др.), затем refresh для
        синхронизации Python объекта с актуальными данными БД.
        commit выполняется на уровне сервиса после всех операций.

        Parameters
        ----------
        **kwargs
            Именованные аргументы передаются в конструктор модели.
            Например: email="test@test.com", hashed_password="hash"

        Returns
        -------
        Model
            Созданный объект с заполненными серверными полями
            (id, created_at, updated_at).
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: UUID, **kwargs) -> Model | None:
        """
        Обновить существующую запись по первичному ключу.

        Выполняет refresh после flush чтобы Python объект
        содержал актуальное значение updated_at и других
        серверных полей после UPDATE.

        Parameters
        ----------
        id : UUID
            Первичный ключ записи для обновления.
        **kwargs
            Именованные аргументы — поля и их новые значения.

        Returns
        -------
        Model | None
            Обновлённый объект если запись найдена, иначе None.
        """
        instance = await self.get_by_id(id)
        if not instance:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: UUID) -> bool:
        """
        Удалить запись по первичному ключу.

        Parameters
        ----------
        id : UUID
            Первичный ключ записи для удаления.

        Returns
        -------
        bool
            True если запись найдена и удалена,
            False если запись не найдена (сервис вернёт 404).
        """
        instance = await self.get_by_id(id)
        if not instance:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True