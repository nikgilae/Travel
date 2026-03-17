import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.models.rule import Rule, CountryRule, CityRule, POIRule
from app.repositories.rule import (
    RuleRepository,
    CountryRuleRepository,
    CityRuleRepository,
    POIRuleRepository,
)
from app.repositories.geography import CountryRepository, CityRepository
from app.repositories.poi import POIRepository


class RuleService:
    """
    Сервис управления правилами.

    Содержит логику создания правил и привязки их
    к странам, городам и POI.

    Parameters
    ----------
    session : AsyncSession
        Асинхронная сессия БД.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.rule_repo = RuleRepository(session)
        self.country_rule_repo = CountryRuleRepository(session)
        self.city_rule_repo = CityRuleRepository(session)
        self.poi_rule_repo = POIRuleRepository(session)
        self.country_repo = CountryRepository(session)
        self.city_repo = CityRepository(session)
        self.poi_repo = POIRepository(session)

    async def create(self, content: str) -> Rule:
        """
        Создать новое правило.

        Parameters
        ----------
        content : str
            Текст правила.

        Returns
        -------
        Rule
            Созданный объект правила.
        """
        rule = await self.rule_repo.create(content=content)
        await self.session.commit()
        return rule

    async def attach_to_country(
        self,
        country_id: uuid.UUID,
        rule_id: uuid.UUID,
        is_strict: bool,
    ) -> CountryRule:
        """
        Привязать правило к стране.

        Parameters
        ----------
        country_id : uuid.UUID
            UUID страны.
        rule_id : uuid.UUID
            UUID правила.
        is_strict : bool
            True — обязательное правило, False — рекомендация.

        Returns
        -------
        CountryRule
            Созданная связь страна-правило.

        Raises
        ------
        NotFoundException
            Если страна или правило не найдены.
        AlreadyExistsException
            Если правило уже привязано к этой стране.
        """
        if not await self.country_repo.get_by_id(country_id):
            raise NotFoundException("Country not found")
        if not await self.rule_repo.get_by_id(rule_id):
            raise NotFoundException("Rule not found")
        if await self.country_rule_repo.exists(country_id, rule_id):
            raise AlreadyExistsException("Rule already attached to this country")

        country_rule = await self.country_rule_repo.create(
            country_id=country_id,
            rule_id=rule_id,
            is_strict=is_strict,
        )
        await self.session.commit()
        return country_rule

    async def attach_to_city(
        self,
        city_id: uuid.UUID,
        rule_id: uuid.UUID,
        is_strict: bool,
    ) -> CityRule:
        """
        Привязать правило к городу.

        Parameters
        ----------
        city_id : uuid.UUID
            UUID города.
        rule_id : uuid.UUID
            UUID правила.
        is_strict : bool
            True — обязательное правило, False — рекомендация.

        Returns
        -------
        CityRule
            Созданная связь город-правило.

        Raises
        ------
        NotFoundException
            Если город или правило не найдены.
        AlreadyExistsException
            Если правило уже привязано к этому городу.
        """
        if not await self.city_repo.get_by_id(city_id):
            raise NotFoundException("City not found")
        if not await self.rule_repo.get_by_id(rule_id):
            raise NotFoundException("Rule not found")
        if await self.city_rule_repo.exists(city_id, rule_id):
            raise AlreadyExistsException("Rule already attached to this city")

        city_rule = await self.city_rule_repo.create(
            city_id=city_id,
            rule_id=rule_id,
            is_strict=is_strict,
        )
        await self.session.commit()
        return city_rule

    async def attach_to_poi(
        self,
        poi_id: uuid.UUID,
        rule_id: uuid.UUID,
        is_strict: bool,
    ) -> POIRule:
        """
        Привязать правило к POI.

        Parameters
        ----------
        poi_id : uuid.UUID
            UUID точки интереса.
        rule_id : uuid.UUID
            UUID правила.
        is_strict : bool
            True — обязательное правило, False — рекомендация.

        Returns
        -------
        POIRule
            Созданная связь POI-правило.

        Raises
        ------
        NotFoundException
            Если POI или правило не найдены.
        AlreadyExistsException
            Если правило уже привязано к этому POI.
        """
        if not await self.poi_repo.get_by_id(poi_id):
            raise NotFoundException("POI not found")
        if not await self.rule_repo.get_by_id(rule_id):
            raise NotFoundException("Rule not found")
        if await self.poi_rule_repo.exists(poi_id, rule_id):
            raise AlreadyExistsException("Rule already attached to this POI")

        poi_rule = await self.poi_rule_repo.create(
            poi_id=poi_id,
            rule_id=rule_id,
            is_strict=is_strict,
        )
        await self.session.commit()
        return poi_rule

    async def get_by_country(self, country_id: uuid.UUID) -> list[CountryRule]:
        """
        Получить все правила страны с флагом is_strict.

        Parameters
        ----------
        country_id : uuid.UUID
            UUID страны.

        Returns
        -------
        list[CountryRule]
            Список связей страна-правило с флагом is_strict.
        """
        return await self.country_rule_repo.get_by_country(country_id)

    async def get_by_city(self, city_id: uuid.UUID) -> list[CityRule]:
        """
        Получить все правила города с флагом is_strict.

        Parameters
        ----------
        city_id : uuid.UUID
            UUID города.

        Returns
        -------
        list[CityRule]
            Список связей город-правило с флагом is_strict.
        """
        return await self.city_rule_repo.get_by_city(city_id)

    async def get_by_poi(self, poi_id: uuid.UUID) -> list[POIRule]:
        """
        Получить все правила POI с флагом is_strict.

        Parameters
        ----------
        poi_id : uuid.UUID
            UUID точки интереса.

        Returns
        -------
        list[POIRule]
            Список связей POI-правило с флагом is_strict.
        """
        return await self.poi_rule_repo.get_by_poi(poi_id)