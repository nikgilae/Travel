from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """
    Исключение для случаев когда запрашиваемый ресурс не найден.

    Возвращает HTTP 404 с описанием какой именно ресурс не найден.

    Parameters
    ----------
    detail : str
        Описание ресурса. Например: 'Trip not found'.
    """

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class AlreadyExistsException(HTTPException):
    """
    Исключение для случаев когда ресурс уже существует.

    Возвращает HTTP 409 Conflict.

    Parameters
    ----------
    detail : str
        Описание конфликта. Например: 'Email already registered'.
    """

    def __init__(self, detail: str = "Resource already exists") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class UnauthorizedException(HTTPException):
    """
    Исключение для случаев невалидной аутентификации.

    Возвращает HTTP 401 с заголовком WWW-Authenticate: Bearer
    как требует стандарт OAuth2.

    Parameters
    ----------
    detail : str
        Описание ошибки аутентификации.
    """

    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(HTTPException):
    """
    Исключение для случаев когда доступ к ресурсу запрещён.

    Возвращает HTTP 403. Используется когда пользователь
    аутентифицирован но не имеет прав на ресурс.

    Parameters
    ----------
    detail : str
        Описание причины запрета доступа.
    """

    def __init__(self, detail: str = "Access forbidden") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )