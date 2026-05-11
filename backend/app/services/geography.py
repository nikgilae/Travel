from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.models.geography import Country, City
from app.repositories.geography import CountryRepository, CityRepository


class CountryService:
    """
    Сервис управления странами.

    Содержит логику создания и получения стран.
    Проверяет уникальность названия перед созданием.

    Parameters
    ----------
    session : AsyncSession
        Асинхронная сессия БД.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.country_repo = CountryRepository(session)

    async def create(self, name: str, content: str) -> Country:
        """
        Создать новую страну.

        Parameters
        ----------
        name : str
            Название страны. Должно быть уникальным.
        content : str
            Справочная информация о стране.

        Returns
        -------
        Country
            Созданный объект страны.

        Raises
        ------
        AlreadyExistsException
            Если страна с таким названием уже существует.
        """
        if await self.country_repo.exists_by_name(name):
            raise AlreadyExistsException(f"Country '{name}' already exists")

        country = await self.country_repo.create(name=name, content=content)
        await self.session.commit()
        return country

    async def get_all(self) -> list[Country]:
        """
        Получить все страны.

        Returns
        -------
        list[Country]
            Список всех стран в справочнике.
        """
        return await self.country_repo.get_all()

    async def get_by_id(self, country_id) -> Country:
        """
        Получить страну по ID.

        Parameters
        ----------
        country_id : uuid.UUID
            UUID страны.

        Returns
        -------
        Country
            Объект страны.

        Raises
        ------
        NotFoundException
            Если страна не найдена.
        """
        country = await self.country_repo.get_by_id(country_id)
        if not country:
            raise NotFoundException(f"Country not found")
        return country


class CityService:
    """
    Сервис управления городами.

    Содержит логику создания и получения городов.
    При создании проверяет существование страны и
    уникальность города в рамках этой страны.

    Parameters
    ----------
    session : AsyncSession
        Асинхронная сессия БД.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.city_repo = CityRepository(session)
        self.country_repo = CountryRepository(session)

    async def create(
        self,
        country_id,
        name: str,
        content: str,
    ) -> City:
        """
        Создать новый город.

        Parameters
        ----------
        country_id : uuid.UUID
            UUID страны к которой принадлежит город.
        name : str
            Название города.
        content : str
            Справочная информация о городе.

        Returns
        -------
        City
            Созданный объект города.

        Raises
        ------
        NotFoundException
            Если страна не найдена.
        AlreadyExistsException
            Если город с таким названием уже существует в этой стране.
        """
        country = await self.country_repo.get_by_id(country_id)
        if not country:
            raise NotFoundException("Country not found")

        existing = await self.city_repo.get_by_name_and_country(name, country_id)
        if existing:
            raise AlreadyExistsException(
                f"City '{name}' already exists in this country"
            )

        city = await self.city_repo.create(
            country_id=country_id,
            name=name,
            content=content,
        )
        await self.session.commit()
        return city

    async def get_all_by_country(self, country_id) -> list[City]:
        """
        Получить все города страны.

        Parameters
        ----------
        country_id : uuid.UUID
            UUID страны.

        Returns
        -------
        list[City]
            Список всех городов страны.

        Raises
        ------
        NotFoundException
            Если страна не найдена.
        """
        country = await self.country_repo.get_by_id(country_id)
        if not country:
            raise NotFoundException("Country not found")
        return await self.city_repo.get_all_by_country(country_id)

    async def get_by_id(self, city_id) -> City:
        """
        Получить город по ID.

        Parameters
        ----------
        city_id : uuid.UUID
            UUID города.

        Returns
        -------
        City
            Объект города.

        Raises
        ------
        NotFoundException
            Если город не найден.
        """
        city = await self.city_repo.get_by_id(city_id)
        if not city:
            raise NotFoundException("City not found")
        return city