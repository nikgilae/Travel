"""
Add Kaliningrad city to Russia.
Run: uv run python -m scripts.seed_kaliningrad
"""

import asyncio
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.geography import Country, City
from app.repositories.geography import CityRepository

RUSSIA_NAME = "Россия"
CITY_NAME   = "Калининград"
CITY_CONTENT = (
    "Калининград — самый западный город России, бывший Кёнигсберг (Восточная Пруссия). "
    "Единственный российский эксклав, окружённый Польшей, Литвой и Балтийским морем. "
    "Валюта — рубль (RUB). Въезд для граждан России свободный; для иностранцев — виза РФ. "
    "Часовой пояс: UTC+2 (как Вильнюс и Варшава, на 1 час западнее Москвы). "
    "Янтарный регион — здесь добывается около 90% мирового янтаря. "
    "Богатое немецко-прусское наследие: готические соборы, форты, Кёнигсбергский замок. "
    "Климат мягкий морской: лето тёплое (+18–22°C), зима мягкая (редко ниже −5°C). "
    "Удобный транспорт: трамваи, автобусы, такси; до Балтийского побережья — 30–50 мин."
)


async def seed():
    async with AsyncSessionLocal() as session:
        # Find Russia
        result = await session.execute(select(Country).where(Country.name == RUSSIA_NAME))
        russia = result.scalar_one_or_none()
        if not russia:
            print(f"❌ Страна '{RUSSIA_NAME}' не найдена в БД.")
            return
        print(f"✅ Страна: {russia.name} ({russia.id})")

        # Check if city already exists
        city_repo = CityRepository(session)
        existing = await city_repo.get_by_name_and_country(CITY_NAME, russia.id)
        if existing:
            print(f"⚠️  Город '{CITY_NAME}' уже существует ({existing.id}) — пропускаем")
            return

        city = await city_repo.create(
            country_id=russia.id,
            name=CITY_NAME,
            content=CITY_CONTENT,
        )
        await session.commit()
        print(f"✅ Создан город: {city.name} ({city.id})")


if __name__ == "__main__":
    asyncio.run(seed())
