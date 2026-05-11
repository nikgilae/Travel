from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.geography import Country, City
from app.repositories.base import BaseRepository


class CountryRepository(BaseRepository[Country]):
    """
    Репозиторий для работы с таблицей countries.

    Содержит методы поиска и проверки существования стран.
    Используется при создании поездок и наполнении справочника.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Country, session)

    async def get_by_name(self, name: str) -> Country | None:
        """
        Найти страну по названию.

        Parameters
        ----------
        name : str
            Название страны.

        Returns
        -------
        Country | None
            Объект страны если найден, иначе None.
        """
        result = await self.session.execute(
            select(Country).where(Country.name == name)
        )
        return result.scalar_one_or_none()

    async def exists_by_name(self, name: str) -> bool:
        """
        Проверить существование страны по названию.

        Используется перед созданием чтобы не допустить дубликатов.

        Parameters
        ----------
        name : str
            Название страны для проверки.

        Returns
        -------
        bool
            True если страна с таким названием уже существует.
        """
        result = await self.session.execute(
            select(Country.id).where(Country.name == name)
        )
        return result.scalar_one_or_none() is not None


class CityRepository(BaseRepository[City]):
    """
    Репозиторий для работы с таблицей cities.

    Поиск всегда выполняется с учётом страны так как
    одинаковые названия городов в разных странах допустимы
    (например Paris, France и Paris, Texas).
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(City, session)

    async def get_by_name_and_country(
        self,
        name: str,
        country_id: str,
    ) -> City | None:
        """
        Найти город по названию и стране одновременно.

        Нельзя искать только по имени — одинаковые названия
        в разных странах допустимы по уникальному индексу
        idx_cities_country_name.

        Parameters
        ----------
        name : str
            Название города.
        country_id : str
            UUID страны к которой принадлежит город.

        Returns
        -------
        City | None
            Объект города если найден, иначе None.
        """
        result = await self.session.execute(
            select(City).where(
                City.name == name,
                City.country_id == country_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_country(self, country_id: str) -> list[City]:
        """
        Получить все города конкретной страны.

        Parameters
        ----------
        country_id : str
            UUID страны.

        Returns
        -------
        list[City]
            Список всех городов страны.
        """
        result = await self.session.execute(
            select(City).where(City.country_id == country_id)
        )
        return list(result.scalars().all())