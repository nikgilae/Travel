# Репозитории для работы с таблицами countries и cities.
# CountryRepository — поиск и проверка существования стран.
# CityRepository — поиск городов с учётом страны (составной уникальный ключ).

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.geography import Country, City
from app.repositories.base import BaseRepository


class CountryRepository(BaseRepository[Country]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Country, session)

    async def get_by_name(self, name: str) -> Country | None:
        # Поиск страны по названию — используется при создании поездки.
        result = await self.session.execute(
            select(Country).where(Country.name == name)
        )
        return result.scalar_one_or_none()

    async def exists_by_name(self, name: str) -> bool:
        # Проверка существования страны перед созданием дубликата.
        result = await self.session.execute(
            select(Country.id).where(Country.name == name)
        )
        return result.scalar_one_or_none() is not None


class CityRepository(BaseRepository[City]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(City, session)

    async def get_by_name_and_country(
        self,
        name: str,
        country_id: str,
    ) -> City | None:
        # Поиск города по имени И стране одновременно.
        # Нельзя искать только по имени — одинаковые названия
        # в разных странах допустимы (Paris, France и Paris, Texas).
        result = await self.session.execute(
            select(City).where(
                City.name == name,
                City.country_id == country_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_country(self, country_id: str) -> list[City]:
        # Все города конкретной страны — используется в справочнике.
        result = await self.session.execute(
            select(City).where(City.country_id == country_id)
        )
        return list(result.scalars().all())