# Репозитории для работы с таблицами rules, country_rules, city_rules, poi_rules.
# RuleRepository — базовые операции с правилами + поиск правил по объекту.
# CountryRuleRepository, CityRuleRepository, POIRuleRepository —
# управление связями между правилами и объектами (страна/город/POI).

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.rule import Rule, CountryRule, CityRule, POIRule
from app.repositories.base import BaseRepository


class RuleRepository(BaseRepository[Rule]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Rule, session)

    async def get_by_country(self, country_id: UUID) -> list[Rule]:
        # JOIN с country_rules — получаем все правила привязанные к стране.
        # Без JOIN пришлось бы делать два отдельных запроса.
        result = await self.session.execute(
            select(Rule)
            .join(CountryRule, CountryRule.rule_id == Rule.id)
            .where(CountryRule.country_id == country_id)
        )
        return list(result.scalars().all())

    async def get_by_city(self, city_id: UUID) -> list[Rule]:
        # Аналогично get_by_country но для города.
        result = await self.session.execute(
            select(Rule)
            .join(CityRule, CityRule.rule_id == Rule.id)
            .where(CityRule.city_id == city_id)
        )
        return list(result.scalars().all())

    async def get_by_poi(self, poi_id: UUID) -> list[Rule]:
        # Аналогично get_by_country но для POI.
        result = await self.session.execute(
            select(Rule)
            .join(POIRule, POIRule.rule_id == Rule.id)
            .where(POIRule.poi_id == poi_id)
        )
        return list(result.scalars().all())


class CountryRuleRepository(BaseRepository[CountryRule]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(CountryRule, session)

    async def get_by_country(self, country_id: UUID) -> list[CountryRule]:
        # joinedload загружает связанный Rule в одном запросе.
        # Без joinedload при обращении к country_rule.rule
        # SQLAlchemy делал бы отдельный запрос для каждого правила.
        result = await self.session.execute(
            select(CountryRule)
            .where(CountryRule.country_id == country_id)
            .options(joinedload(CountryRule.rule))
        )
        return list(result.scalars().all())

    async def exists(self, country_id: UUID, rule_id: UUID) -> bool:
        # Проверка существования связи перед созданием дубликата.
        # Составной PK в БД тоже защищает, но лучше проверить заранее
        # чтобы вернуть понятную ошибку а не исключение БД.
        result = await self.session.execute(
            select(CountryRule).where(
                CountryRule.country_id == country_id,
                CountryRule.rule_id == rule_id,
            )
        )
        return result.scalar_one_or_none() is not None


class CityRuleRepository(BaseRepository[CityRule]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(CityRule, session)

    async def get_by_city(self, city_id: UUID) -> list[CityRule]:
        result = await self.session.execute(
            select(CityRule)
            .where(CityRule.city_id == city_id)
            .options(joinedload(CityRule.rule))
        )
        return list(result.scalars().all())

    async def exists(self, city_id: UUID, rule_id: UUID) -> bool:
        result = await self.session.execute(
            select(CityRule).where(
                CityRule.city_id == city_id,
                CityRule.rule_id == rule_id,
            )
        )
        return result.scalar_one_or_none() is not None


class POIRuleRepository(BaseRepository[POIRule]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(POIRule, session)

    async def get_by_poi(self, poi_id: UUID) -> list[POIRule]:
        result = await self.session.execute(
            select(POIRule)
            .where(POIRule.poi_id == poi_id)
            .options(joinedload(POIRule.rule))
        )
        return list(result.scalars().all())

    async def exists(self, poi_id: UUID, rule_id: UUID) -> bool:
        result = await self.session.execute(
            select(POIRule).where(
                POIRule.poi_id == poi_id,
                POIRule.rule_id == rule_id,
            )
        )
        return result.scalar_one_or_none() is not None