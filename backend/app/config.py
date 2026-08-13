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
    # 180 = 3 часа: покрывает типичную сессию планирования, чтобы не выкидывать
    # пользователя на вход посреди работы (промежуточное решение до refresh-токенов).
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180

    # Режим отладки. Включить только для разработки.
    # Включает verbose SQL-логирование и другие отладочные функции.
    DEBUG: bool = False

    # Директория для файловых логов. Пусто → пишем только в stdout (dev/тесты).
    # В проде задаётся (например /app/logs) и монтируется на volume, чтобы логи
    # (event-лог, ошибки) переживали redeploy контейнера.
    LOG_DIR: str = ""

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

    # Жёсткий потолок времени на генерацию маршрута (все попытки суммарно, секунды).
    # Фронт рвёт запрос на 45 сек, поэтому здесь оставляем запас на до-AI часть
    # (загрузка POI и правил города) и на сохранение пула в БД: 30 + запас < 45.
    # Превышение обрывается через asyncio.wait_for — человек получает честную
    # ошибку с причиной, а не клиентский таймаут без объяснений.
    AI_GENERATION_BUDGET_SECONDS: float = 30.0

    # Таймаут ожидания ответа AI на один HTTP-запрос генерации (секунды).
    # Ретраев SDK у клиента генерации нет (max_retries=0), поэтому один прикладной
    # заход стоит ровно один такой таймаут: две попытки укладываются в бюджет.
    AI_READ_TIMEOUT_SECONDS: float = 18.0

    # Таймаут установки соединения с AI-провайдером (секунды) — только дозвон,
    # до отправки запроса. Замер 2026-08-11: удачный TLS-хендшейк занимает
    # 0.1-0.7 сек, неудачный не завершается никогда и висит до таймаута.
    # Держать здесь 15 сек (наследство от read=60) означало отдавать половину
    # бюджета заведомо мёртвому ожиданию: после провала оставалось 15 сек из 30,
    # гейт требует свободных AI_READ_TIMEOUT_SECONDS — и вторая попытка
    # запрещалась. С 3 сек остаётся 27 сек, повтор проходит: два захода вместо
    # одного на нестабильном канале. Запас над самым медленным удачным
    # хендшейком — четырёхкратный.
    AI_CONNECT_TIMEOUT_SECONDS: float = 3.0

    # Глобальный рубильник интеграции с Google Maps. False → ни обогащение города
    # при генерации маршрута, ни /places-эндпоинты не ходят в Google (используется
    # для записи демо, чтобы генерация была быстрой и предсказуемой по времени).
    GOOGLE_MAPS_ENABLED: bool = True

    # Быстрый режим генерации маршрута для демо: компактный промпт (3 основных + 1
    # запасное место в день, короткие подсказки) укладывает генерацию в ~8-10 сек
    # вместо ~20+. False → обычный богатый пул мест.
    DEMO_FAST_GENERATION: bool = False

    # Видимость ошибок. Все опциональны — без них приложение работает как раньше.
    # SENTRY_DSN пуст → Sentry выключен. TG_* заданы → каждая 5xx падает в личный
    # Telegram-бот фаундера (fallback, если Sentry недоступен из РФ-инфраструктуры).
    SENTRY_DSN: str = ""
    TG_BOT_TOKEN: str = ""
    TG_CHAT_ID: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Игнорировать переменные из .env, которые не являются настройками приложения
        # (например POSTGRES_USER/PASSWORD/DB — их читает docker-compose для контейнера БД).
        extra="ignore",
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
