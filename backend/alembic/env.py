import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool
from alembic import context

from app.config import settings
from app.core.database import Base
import app.models  # импортируем все модели чтобы Base.metadata их видел

# Alembic Config объект — даёт доступ к alembic.ini
config = context.config

# Подставляем DATABASE_URL из .env
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Настройка логирования из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata всех моделей — Alembic сравнивает её с реальной БД
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Режим без подключения к БД — генерирует SQL файл."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Режим с подключением к БД — применяет миграции напрямую."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())