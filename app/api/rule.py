import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.rule import RuleCreate, RuleResponse, AttachRuleRequest
from app.services.rule import RuleService


router = APIRouter(prefix="/rules", tags=["Rules"])


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
    "",
    response_model=RuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать правило",
)
async def create_rule(
    data: RuleCreate,
    service: RuleService = Depends(get_rule_service),
    current_user: User = Depends(get_current_user),
) -> RuleResponse:
    """
    Создать новое переиспользуемое правило.

    Parameters
    ----------
    data : RuleCreate
        Текст правила.
    service : RuleService
        Сервис правил.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    RuleResponse
        Созданное правило.
    """
    return await service.create(data.content)


@router.post(
    "/countries/{country_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Привязать правило к стране",
)
async def attach_to_country(
    country_id: uuid.UUID,
    data: AttachRuleRequest,
    service: RuleService = Depends(get_rule_service),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Привязать существующее правило к стране.

    Parameters
    ----------
    country_id : uuid.UUID
        UUID страны.
    data : AttachRuleRequest
        rule_id и is_strict.
    service : RuleService
        Сервис правил.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    dict
        Подтверждение привязки.
    """
    await service.attach_to_country(country_id, data.rule_id, data.is_strict)
    return {"status": "attached"}


@router.post(
    "/cities/{city_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Привязать правило к городу",
)
async def attach_to_city(
    city_id: uuid.UUID,
    data: AttachRuleRequest,
    service: RuleService = Depends(get_rule_service),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Привязать существующее правило к городу.

    Parameters
    ----------
    city_id : uuid.UUID
        UUID города.
    data : AttachRuleRequest
        rule_id и is_strict.
    service : RuleService
        Сервис правил.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    dict
        Подтверждение привязки.
    """
    await service.attach_to_city(city_id, data.rule_id, data.is_strict)
    return {"status": "attached"}


@router.post(
    "/pois/{poi_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Привязать правило к POI",
)
async def attach_to_poi(
    poi_id: uuid.UUID,
    data: AttachRuleRequest,
    service: RuleService = Depends(get_rule_service),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Привязать существующее правило к точке интереса.

    Parameters
    ----------
    poi_id : uuid.UUID
        UUID точки интереса.
    data : AttachRuleRequest
        rule_id и is_strict.
    service : RuleService
        Сервис правил.
    current_user : User
        Текущий авторизованный пользователь.

    Returns
    -------
    dict
        Подтверждение привязки.
    """
    await service.attach_to_poi(poi_id, data.rule_id, data.is_strict)
    return {"status": "attached"}