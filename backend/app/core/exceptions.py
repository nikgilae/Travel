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


class BadRequestException(HTTPException):
    """
    Исключение для запросов, которые нельзя выполнить в текущем состоянии данных.

    Возвращает HTTP 400. Используется когда запрос синтаксически корректен
    (прошёл валидацию Pydantic), но противоречит бизнес-правилам —
    например, генерация маршрута для поездки без указанных дат.

    Parameters
    ----------
    detail : str
        Понятное пользователю описание того, что нужно исправить.
    """

    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class AIGenerationError(HTTPException):
    """
    Исключение для случаев когда AI не смог сгенерировать маршрут.

    Возвращает HTTP 502 Bad Gateway: сбой во внешнем сервисе (AI-провайдер
    не ответил, вернул битый JSON или предложил места, которых нет в нашей базе).
    Раньше такой сбой маскировался под успех: пользователь получал HTTP 200
    и пустой план. Теперь мы падаем честно.

    Parameters
    ----------
    detail : str
        Понятное пользователю описание сбоя (на русском).
    retryable : bool
        Поможет ли повтор. True — временный сбой (таймаут, 5xx, битый JSON):
        клиенту показываем «Попробовать ещё раз». False — повтор воспроизведёт
        ту же ошибку (неверный ключ, превышен лимит контекста, ответ обрезан
        по max_tokens): кнопку повтора показывать нельзя, иначе человек будет
        жать её вхолостую и жечь вызовы провайдера.
        Уходит в тело ответа полем ``retryable``.
    """

    def __init__(
        self,
        detail: str = (
            "Сервис подбора мест сейчас недоступен. Попробуйте ещё раз."
        ),
        retryable: bool = True,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        )
        self.retryable = retryable
