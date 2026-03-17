import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CountryCreate(BaseModel):
    """
    Схема создания страны.

    Attributes
    ----------
    name : str
        Название страны. От 2 до 100 символов.
    content : str
        Справочная информация о стране.
    """

    name: str = Field(..., min_length=2, max_length=100)
    content: str = Field(..., min_length=1)


class CountryResponse(BaseModel):
    """
    Схема ответа с данными страны.

    Attributes
    ----------
    id : uuid.UUID
        Уникальный идентификатор.
    name : str
        Название страны.
    content : str
        Справочная информация.
    created_at : datetime
        Время создания записи.
    updated_at : datetime
        Время последнего обновления.
    """

    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    content: str
    created_at: datetime
    updated_at: datetime


class CityCreate(BaseModel):
    """
    Схема создания города.

    Attributes
    ----------
    country_id : uuid.UUID
        UUID страны к которой принадлежит город.
    name : str
        Название города. От 2 до 100 символов.
    content : str
        Справочная информация о городе.
    """

    country_id: uuid.UUID
    name: str = Field(..., min_length=2, max_length=100)
    content: str = Field(..., min_length=1)


class CityResponse(BaseModel):
    """
    Схема ответа с данными города.

    Attributes
    ----------
    id : uuid.UUID
        Уникальный идентификатор.
    country_id : uuid.UUID
        UUID страны.
    name : str
        Название города.
    content : str
        Справочная информация.
    created_at : datetime
        Время создания записи.
    updated_at : datetime
        Время последнего обновления.
    """

    model_config = {"from_attributes": True}

    id: uuid.UUID
    country_id: uuid.UUID
    name: str
    content: str
    created_at: datetime
    updated_at: datetime


class CityWithCountryResponse(CityResponse):
    """
    Схема ответа с городом и вложенной страной.

    Расширяет CityResponse добавляя объект страны.
    Используется в эндпоинтах где нужен полный контекст.

    Attributes
    ----------
    country : CountryResponse
        Полный объект страны.
    """

    country: CountryResponse
    
class CityContextRuleResponse(BaseModel):
    """
    Схема правила в контексте города.

    Используется в GET /cities/{city_id}/context-info.
    Без поля category — убрано по решению команды.

    Attributes
    ----------
    rule_id : uuid.UUID
        Уникальный идентификатор правила.
    is_strict : bool
        True — обязательное правило, False — рекомендация.
    content : str
        Текст правила.
    """

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

    rule_id: uuid.UUID = Field(alias="id")
    is_strict: bool
    content: str


class CityContextResponse(BaseModel):
    """
    Схема ответа глобальной сводки по городу.

    Возвращается при GET /cities/{city_id}/context-info.
    Содержит общую информацию о городе, стране и список правил.

    Attributes
    ----------
    city_name : str
        Название города.
    country_name : str
        Название страны.
    general_content : str
        Общая справочная информация о городе.
    rules : list[CityContextRuleResponse]
        Список правил города с флагом строгости.
    disclaimer : str
        Предупреждение об актуальности данных.
        Статичная строка — одинакова для всех городов.
    """

    city_name: str
    country_name: str
    general_content: str
    rules: list[CityContextRuleResponse] = []
    disclaimer: str = (
        "Правила могли измениться, "
        "проверяйте официальные источники перед поездкой."
    )