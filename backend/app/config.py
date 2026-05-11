# Модуль конфигурации приложения.
# Читает переменные окружения из файла .env и предоставляет
# типизированный доступ к настройкам через объект settings.
# Использует pydantic-settings для валидации и приведения типов.

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import secrets


class Settings(BaseSettings):
    # URL подключения к PostgreSQL через асинхронный драйвер asyncpg.
    # Формат: postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DB_NAME
    DATABASE_URL: str

    # URL подключения к тестовой БД.
    # Используется в pytest тестах — не трогает продакшн данные.
    TEST_DATABASE_URL: str = ""

    # Секретный ключ для подписи JWT токенов.
    # В продакшне должен быть длинной случайной строкой:
    # uv run python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY: str

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Проверить что SECRET_KEY достаточно длинный (минимум 32 символа)."""
        if len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long. "
                "Generate with: uv run python -c 'import secrets; print(secrets.token_hex(32))'"
            )
        return v

    # Алгоритм подписи JWT токенов.
    # HS256 — симметричный алгоритм, один ключ для создания и проверки.
    ALGORITHM: str = "HS256"

    # Время жизни access токена в минутах.
    # После истечения пользователь должен авторизоваться заново.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Режим отладки. Включить только для разработки.
    # Включает verbose SQL-логирование и другие отладочные функции.
    DEBUG: bool = False

    # CORS origins — список доменов которым разрешён доступ к API.
    # Для разработки: "http://localhost:3000"
    # Для продакшена: "https://yourdomain.com"
    # Формат: comma-separated list или JSON array строк
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    AI_API_KEY: str = ""
    AI_BASE_URL: str = ""
    AI_MODEL: str = ""
    GOOGLE_MAPS_API_KEY: str = ""
    ENRICH_COOLDOWN_HOURS: int = 24

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """
        Парсит CORS_ORIGINS строку в список.
        Поддерживает:
        - CSV: "http://localhost:3000,https://example.com"
        - JSON: '["http://localhost:3000"]'
        """
        import json
        origins = self.CORS_ORIGINS.strip()
        if not origins:
            return []
        # Пробуем распарсить как JSON
        if origins.startswith('['):
            try:
                return json.loads(origins)
            except json.JSONDecodeError:
                pass
        # Иначе как CSV
        return [o.strip() for o in origins.split(',') if o.strip()]


# Глобальный экземпляр настроек — импортируется во всех модулях.
# Создаётся один раз при старте приложения.
# Если обязательные переменные отсутствуют в .env — приложение
# упадёт сразу при импорте с понятной ошибкой.
settings = Settings()
