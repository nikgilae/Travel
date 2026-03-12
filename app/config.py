# Модуль конфигурации приложения.
# Читает переменные окружения из файла .env и предоставляет
# типизированный доступ к настройкам через объект settings.
# Использует pydantic-settings для валидации и приведения типов.

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # URL подключения к PostgreSQL через асинхронный драйвер asyncpg.
    # Формат: postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DB_NAME
    DATABASE_URL: str

    # Секретный ключ для подписи JWT токенов.
    # В продакшне должен быть длинной случайной строкой:
    # uv run python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY: str

    # Алгоритм подписи JWT токенов.
    # HS256 — симметричный алгоритм, один ключ для создания и проверки.
    ALGORITHM: str = "HS256"

    # Время жизни access токена в минутах.
    # После истечения пользователь должен авторизоваться заново.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        # Путь к файлу с переменными окружения.
        # Файл .env не коммитится в git — используй .env.example как шаблон.
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Глобальный экземпляр настроек — импортируется во всех модулях.
# Создаётся один раз при старте приложения.
# Если обязательные переменные отсутствуют в .env — приложение
# упадёт сразу при импорте с понятной ошибкой.
settings = Settings()