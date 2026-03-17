import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.geography import (
    CountryCreate, CountryResponse,
    CityCreate, CityResponse,
    CityContextResponse, CityContextRuleResponse,
)
from app.services.geography import CountryService, CityService
from app.services.rule import RuleService


router = APIRouter(tags=["Geography"])


def get_country_service(session: AsyncSession = Depends(get_db)) -> CountryService:
    """
    Dependency для получения CountryService.

    Parameters
    ----------
    session : AsyncSession
        Сессия БД.

    Returns
    -------
    CountryService
        Экземпляр сервиса стран.
    """
    return CountryService(session)


def get_city_service(session: AsyncSession = Depends(get_db)) -> CityService:
    """
    Dependency для получения CityService.

    Parameters
    ----------
    session : AsyncSession
        Сессия БД.

    Returns
    -------
    CityService
        Экземпляр сервиса городов.
    """
    return CityService(session)


def get_rule_service(session: AsyncSession = Depends(get_db)) -> RuleService:
    """
    Dependency для получения RuleService.

    Parameters
    ----------
    session : AsyncSession
        Сессия БД.

    Returns
    -------
    RuleService
        Экземпляр сервиса правил.
    """
    return RuleService(session)


@router.post(
    "/countries",
    response_model=CountryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать страну",
)
async def create_country(
    data: CountryCreate,
    service: CountryService = Depends(get_country_service),
    current_user: User = Depends(get_current_user),
) -> CountryResponse:
    """
    Создать новую страну в справочнике.

    Parameters
    ----------
    data : CountryCreate
        Название и контент страны.
    service : CountryService
        Сервис управления странами.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    CountryResponse
        Созданный объект страны.
    """
    return await service.create(data.name, data.content)


@router.get(
    "/countries",
    response_model=list[CountryResponse],
    summary="Список всех стран",
)
async def get_countries(
    service: CountryService = Depends(get_country_service),
    current_user: User = Depends(get_current_user),
) -> list[CountryResponse]:
    """
    Получить список всех стран справочника.

    Parameters
    ----------
    service : CountryService
        Сервис управления странами.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    list[CountryResponse]
        Список всех стран.
    """
    return await service.get_all()


@router.post(
    "/cities",
    response_model=CityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать город",
)
async def create_city(
    data: CityCreate,
    service: CityService = Depends(get_city_service),
    current_user: User = Depends(get_current_user),
) -> CityResponse:
    """
    Создать новый город в справочнике.

    Parameters
    ----------
    data : CityCreate
        country_id, название и контент города.
    service : CityService
        Сервис управления городами.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    CityResponse
        Созданный объект города.
    """
    return await service.create(data.country_id, data.name, data.content)


@router.get(
    "/countries/{country_id}/cities",
    response_model=list[CityResponse],
    summary="Города страны",
)
async def get_cities(
    country_id: uuid.UUID,
    service: CityService = Depends(get_city_service),
    current_user: User = Depends(get_current_user),
) -> list[CityResponse]:
    """
    Получить все города конкретной страны.

    Parameters
    ----------
    country_id : uuid.UUID
        UUID страны.
    service : CityService
        Сервис управления городами.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    list[CityResponse]
        Список городов страны.
    """
    return await service.get_all_by_country(country_id)


@router.get(
    "/cities/{city_id}/context-info",
    response_model=CityContextResponse,
    summary="Контекстная информация о городе",
)
async def get_city_context(
    city_id: uuid.UUID,
    city_service: CityService = Depends(get_city_service),
    rule_service: RuleService = Depends(get_rule_service),
    current_user: User = Depends(get_current_user),
) -> CityContextResponse:
    """
    Получить глобальную сводку по городу.

    Возвращает название города, страны, общий контент
    и список правил с флагом строгости.
    Core Feature — используется во время поездки.

    Parameters
    ----------
    city_id : uuid.UUID
        UUID города.
    city_service : CityService
        Сервис городов.
    rule_service : RuleService
        Сервис правил.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    CityContextResponse
        Сводка по городу с правилами и disclaimer.
    """
    city = await city_service.get_by_id(city_id)
    country = await city_service.country_repo.get_by_id(city.country_id)
    city_rules = await rule_service.get_by_city(city_id)

    rules = [
        CityContextRuleResponse(
            id=cr.rule.id,
            is_strict=cr.is_strict,
            content=cr.rule.content,
        )
        for cr in city_rules
    ]

    return CityContextResponse(
        city_name=city.name,
        country_name=country.name,
        general_content=city.content,
        rules=rules,
    )