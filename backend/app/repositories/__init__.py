# Точка входа для всех репозиториев.
# Позволяет импортировать репозитории напрямую из пакета:
#   from app.repositories import UserRepository, TripRepository
# вместо длинного пути:
#   from app.repositories.user import UserRepository

from app.repositories.user import UserRepository
from app.repositories.geography import CountryRepository, CityRepository
from app.repositories.rule import (
    RuleRepository,
    CountryRuleRepository,
    CityRuleRepository,
    POIRuleRepository,
)
from app.repositories.poi import POIRepository
from app.repositories.trip import TripRepository, TripPOIRepository