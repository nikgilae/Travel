import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """
    Схема запроса на регистрацию пользователя.

    Attributes
    ----------
    email : EmailStr
        Email адрес. Pydantic автоматически валидирует формат.
    password : str
        Пароль. Минимум 8 символов, должен содержать
        заглавную букву и цифру.
    """

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """
        Проверить сложность пароля.

        Parameters
        ----------
        v : str
            Пароль для проверки.

        Returns
        -------
        str
            Пароль если прошёл проверку.

        Raises
        ------
        ValueError
            Если пароль не содержит заглавную букву или цифру.
        """
        if not any(c.isupper() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not any(c.isdigit() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return v


class LoginRequest(BaseModel):
    """
    Схема запроса на логин.

    Attributes
    ----------
    email : EmailStr
        Email адрес пользователя.
    password : str
        Открытый пароль для проверки.
    """

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    Схема ответа с JWT токеном.

    Attributes
    ----------
    user_id : uuid.UUID
        UUID пользователя. Возвращается чтобы фронтенд
        не делал отдельный запрос /me для получения ID.
    access_token : str
        Подписанный JWT токен.
    token_type : str
        Тип токена. Всегда 'bearer' по стандарту OAuth2.
    expires_in : int
        Время жизни токена в секундах.
    """

    user_id: uuid.UUID
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    """
    Схема ответа с данными пользователя.

    Attributes
    ----------
    id : uuid.UUID
        Уникальный идентификатор пользователя.
    email : str
        Email адрес пользователя.
    created_at : datetime
        Время регистрации.
    """

    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    created_at: datetime