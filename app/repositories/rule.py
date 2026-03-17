from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.rule import Rule, CountryRule, CityRule, POIRule
from app.repositories.base import BaseRepository


class RuleRepository(BaseRepository[Rule]):
    """
    Репозиторий для работы с таблицей rules.

    Правила переиспользуемые — одно правило может быть
    привязано к стране, городу и POI одновременно.
    Методы get_by_* используют JOIN со связующими таблицами.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Rule, session)

    async def get_by_country(self, country_id: UUID) -> list[Rule]:
        """
        Получить все правила привязанные к стране.

        Использует JOIN с country_rules чтобы получить
        правила за один запрос вместо двух.

        Parameters
        ----------
        country_id : UUID
            UUID страны.

        Returns
        -------
        list[Rule]
            Список правил страны.
        """
        result = await self.session.execute(
            select(Rule)
            .join(CountryRule, CountryRule.rule_id == Rule.id)
            .where(CountryRule.country_id == country_id)
        )
        return list(result.scalars().all())

    async def get_by_city(self, city_id: UUID) -> list[Rule]:
        """
        Получить все правила привязанные к городу.

        Parameters
        ----------
        city_id : UUID
            UUID города.

        Returns
        -------
        list[Rule]
            Список правил города.
        """
        result = await self.session.execute(
            select(Rule)
            .join(CityRule, CityRule.rule_id == Rule.id)
            .where(CityRule.city_id == city_id)
        )
        return list(result.scalars().all())

    async def get_by_poi(self, poi_id: UUID) -> list[Rule]:
        """
        Получить все правила привязанные к POI.

        Parameters
        ----------
        poi_id : UUID
            UUID точки интереса.

        Returns
        -------
        list[Rule]
            Список правил POI.
        """
        result = await self.session.execute(
            select(Rule)
            .join(POIRule, POIRule.rule_id == Rule.id)
            .where(POIRule.poi_id == poi_id)
        )
        return list(result.scalars().all())


class CountryRuleRepository(BaseRepository[CountryRule]):
    """
    Репозиторий для управления связями между странами и правилами.

    Работает со связующей таблицей country_rules.
    В отличие от RuleRepository возвращает объекты CountryRule
    вместе с флагом is_strict.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(CountryRule, session)

    async def get_by_country(self, country_id: UUID) -> list[CountryRule]:
        """
        Получить все связи правил для страны с загрузкой Rule.

        Использует joinedload чтобы избежать проблемы N+1 запросов:
        связанные Rule загружаются в одном запросе через LEFT JOIN.

        Parameters
        ----------
        country_id : UUID
            UUID страны.

        Returns
        -------
        list[CountryRule]
            Список объектов CountryRule с заполненным полем rule.
        """
        result = await self.session.execute(
            select(CountryRule)
            .where(CountryRule.country_id == country_id)
            .options(joinedload(CountryRule.rule))
        )
        return list(result.scalars().all())

    async def exists(self, country_id: UUID, rule_id: UUID) -> bool:
        """
        Проверить существование связи страна-правило.

        Используется перед созданием чтобы вернуть понятную
        ошибку вместо исключения БД о дублировании составного PK.

        Parameters
        ----------
        country_id : UUID
            UUID страны.
        rule_id : UUID
            UUID правила.

        Returns
        -------
        bool
            True если связь уже существует.
        """
        result = await self.session.execute(
            select(CountryRule).where(
                CountryRule.country_id == country_id,
                CountryRule.rule_id == rule_id,
            )
        )
        return result.scalar_one_or_none() is not None


class CityRuleRepository(BaseRepository[CityRule]):
    """
    Репозиторий для управления связями между городами и правилами.

    Аналогичен CountryRuleRepository но для таблицы city_rules.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(CityRule, session)

    async def get_by_city(self, city_id: UUID) -> list[CityRule]:
        """
        Получить все связи правил для города с загрузкой Rule.

        Parameters
        ----------
        city_id : UUID
            UUID города.

        Returns
        -------
        list[CityRule]
            Список объектов CityRule с заполненным полем rule.
        """
        result = await self.session.execute(
            select(CityRule)
            .where(CityRule.city_id == city_id)
            .options(joinedload(CityRule.rule))
        )
        return list(result.scalars().all())

    async def exists(self, city_id: UUID, rule_id: UUID) -> bool:
        """
        Проверить существование связи город-правило.

        Parameters
        ----------
        city_id : UUID
            UUID города.
        rule_id : UUID
            UUID правила.

        Returns
        -------
        bool
            True если связь уже существует.
        """
        result = await self.session.execute(
            select(CityRule).where(
                CityRule.city_id == city_id,
                CityRule.rule_id == rule_id,
            )
        )
        return result.scalar_one_or_none() is not None


class POIRuleRepository(BaseRepository[POIRule]):
    """
    Репозиторий для управления связями между POI и правилами.

    Аналогичен CountryRuleRepository но для таблицы poi_rules.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(POIRule, session)

    async def get_by_poi(self, poi_id: UUID) -> list[POIRule]:
        """
        Получить все связи правил для POI с загрузкой Rule.

        Parameters
        ----------
        poi_id : UUID
            UUID точки интереса.

        Returns
        -------
        list[POIRule]
            Список объектов POIRule с заполненным полем rule.
        """
        result = await self.session.execute(
            select(POIRule)
            .where(POIRule.poi_id == poi_id)
            .options(joinedload(POIRule.rule))
        )
        return list(result.scalars().all())

    async def exists(self, poi_id: UUID, rule_id: UUID) -> bool:
        """
        Проверить существование связи POI-правило.

        Parameters
        ----------
        poi_id : UUID
            UUID точки интереса.
        rule_id : UUID
            UUID правила.

        Returns
        -------
        bool
            True если связь уже существует.
        """
        result = await self.session.execute(
            select(POIRule).where(
                POIRule.poi_id == poi_id,
                POIRule.rule_id == rule_id,
            )
        )
        return result.scalar_one_or_none() is not None