import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from app.main import app
from app.core.database import Base, get_db
from app.config import settings

TABLES_TO_TRUNCATE = (
    "trip_pois, trips, poi_rules, city_rules, country_rules, "
    "pois, rules, cities, countries, users"
)


@pytest_asyncio.fixture
async def db_session():
    """
    Сессия БД для одного теста.
    Создаёт движок, таблицы, выдаёт сессию.
    После теста очищает таблицы и удаляет движок.
    """
    engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.execute(
            text(f"TRUNCATE TABLE {TABLES_TO_TRUNCATE} RESTART IDENTITY CASCADE")
        )

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    """HTTP клиент с тестовой сессией."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Тестовый пользователь."""
    from app.repositories.user import UserRepository
    from app.core.security import hash_password

    repo = UserRepository(db_session)
    user = await repo.create(
        email="test@example.com",
        hashed_password=hash_password("TestPass123"),
    )
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user):
    """JWT заголовки для тестового пользователя."""
    from app.core.security import create_access_token
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_country(db_session: AsyncSession):
    """Тестовая страна."""
    from app.repositories.geography import CountryRepository
    repo = CountryRepository(db_session)
    country = await repo.create(name="Япония", content="Информация о Японии")
    await db_session.commit()
    return country


@pytest_asyncio.fixture
async def test_city(db_session: AsyncSession, test_country):
    """Тестовый город."""
    from app.repositories.geography import CityRepository
    repo = CityRepository(db_session)
    city = await repo.create(
        country_id=test_country.id,
        name="Токио",
        content="Информация о Токио",
    )
    await db_session.commit()
    return city