import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from app.main import app
from app.core.database import Base, get_db
from app.config import settings

TABLES_TO_TRUNCATE = (
    "messages, trip_pois, trips, poi_rules, city_rules, country_rules, "
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

    # save_messages() использует свою сессию через AsyncSessionLocal (для изоляции
    # best-effort записи). В тестах перенаправляем её на тестовый движок, чтобы
    # записи чата попадали в тестовую БД и были видны в этом же event loop.
    import app.services.message_log as _ml
    _orig_session_local = _ml.AsyncSessionLocal
    _ml.AsyncSessionLocal = session_factory

    async with session_factory() as session:
        yield session

    _ml.AsyncSessionLocal = _orig_session_local

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


@pytest_asyncio.fixture
async def test_trip(db_session: AsyncSession, test_user, test_country, test_city):
    """Тестовая поездка для test_user (нужна WS-чату и событиям)."""
    from app.repositories.trip import TripRepository
    repo = TripRepository(db_session)
    trip = await repo.create(
        user_id=test_user.id,
        country_id=test_country.id,
        city_id=test_city.id,
        purpose="leisure",
        budget="medium",
        group_size=2,
    )
    await db_session.commit()
    return trip


# ── Мок AI в одной точке ──────────────────────────────────────────────────────
# Оба чата (REST /chat/general и WS-агент) ходят через общий app.services.ai.client
# (после T12). Значит, мок этого единственного клиента покрывает оба пути.

class FakeToolCall:
    """Имитация tool_call из ответа OpenAI (для WS-агента)."""
    def __init__(self, call_id: str, name: str, arguments: str):
        self.id = call_id
        self.type = "function"
        self.function = type("Fn", (), {"name": name, "arguments": arguments})()


class FakeMessage:
    """Имитация response.choices[0].message."""
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls
        self.role = "assistant"

    def model_dump(self, exclude_none=True):
        d = {"role": self.role}
        if self.content is not None or not exclude_none:
            d["content"] = self.content
        if self.tool_calls is not None:
            d["tool_calls"] = [
                {"id": tc.id, "type": tc.type,
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in self.tool_calls
            ]
        return d


class FakeCompletion:
    def __init__(self, message: FakeMessage):
        self.choices = [type("Choice", (), {"message": message})()]


def make_completion(content=None, tool_calls=None) -> FakeCompletion:
    return FakeCompletion(FakeMessage(content=content, tool_calls=tool_calls))


@pytest.fixture
def mock_ai(monkeypatch):
    """
    Подменяет единственный AI-клиент. Возвращает объект, у которого можно задать
    последовательность ответов: mock_ai.queue = [FakeCompletion, ...].
    По умолчанию отдаёт простой текстовый ответ без вызова инструментов.
    """
    from unittest.mock import AsyncMock
    import app.services.ai as ai_module

    class _Controller:
        def __init__(self):
            self.queue = []
            self.calls = []
            self.default = make_completion(content="Ответ ассистента.")

        async def _create(self, *args, **kwargs):
            self.calls.append(kwargs)
            if self.queue:
                return self.queue.pop(0)
            return self.default

    ctrl = _Controller()
    monkeypatch.setattr(
        ai_module.client.chat.completions, "create", AsyncMock(side_effect=ctrl._create)
    )
    return ctrl