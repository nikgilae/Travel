import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class RuleCreate(BaseModel):
    """
    Схема создания правила.

    Attributes
    ----------
    content : str
        Текст правила. Минимум 5 символов.
    """

    content: str = Field(..., min_length=5)


class RuleResponse(BaseModel):
    """
    Схема ответа с данными правила.

    Attributes
    ----------
    id : uuid.UUID
        Уникальный идентификатор.
    content : str
        Текст правила.
    created_at : datetime
        Время создания.
    updated_at : datetime
        Время последнего обновления.
    """

    model_config = {"from_attributes": True}

    id: uuid.UUID
    content: str
    created_at: datetime
    updated_at: datetime


class RuleWithStrictResponse(BaseModel):
    """
    Схема ответа с правилом и флагом строгости.

    Используется в contextual_warnings при добавлении POI
    и в context-info города. Поле rule_id вместо id —
    соответствует API контракту аналитика.

    Attributes
    ----------
    rule_id : uuid.UUID
        Уникальный идентификатор правила.
    content : str
        Текст правила.
    is_strict : bool
        True — обязательное правило, False — рекомендация.
    """

    model_config = {
    "from_attributes": True,
    "populate_by_name": True,
    }

    rule_id: uuid.UUID = Field(alias="id")
    content: str
    is_strict: bool


class AttachRuleRequest(BaseModel):
    """
    Схема запроса на привязку правила к объекту.

    Используется для привязки правила к стране, городу или POI.

    Attributes
    ----------
    rule_id : uuid.UUID
        UUID существующего правила.
    is_strict : bool
        True — обязательное правило, False — рекомендация.
    """

    rule_id: uuid.UUID
    is_strict: bool = True