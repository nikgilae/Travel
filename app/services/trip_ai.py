import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.trip import Trip, TripPOI
from app.repositories.trip import TripRepository, TripPOIRepository
from app.repositories.poi import POIRepository
from app.repositories.rule import CityRuleRepository, POIRuleRepository
from app.repositories.geography import CityRepository, CountryRepository
from app.services.ai import generate_trip


class TripAIService:
    """
    Сервис генерации маршрута через AI.

    Оркестрирует взаимодействие между AI и репозиториями:
    достаёт данные из БД → передаёт в AI → сохраняет результат.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.trip_repo = TripRepository(session)
        self.trip_poi_repo = TripPOIRepository(session)
        self.poi_repo = POIRepository(session)
        self.city_repo = CityRepository(session)
        self.country_repo = CountryRepository(session)
        self.city_rule_repo = CityRuleRepository(session)
        self.poi_rule_repo = POIRuleRepository(session)

    async def generate(
        self,
        trip_id: uuid.UUID,
        user_id: uuid.UUID,
        interests: list[str],
        notes: str | None,
    ) -> dict:
        """Сгенерировать маршрут для существующей поездки."""
        
        # ── 1. Загружаем поездку и проверяем даты ─────────────────────────────
        trip = await self.trip_repo.get_by_user_and_id(trip_id, user_id)
        if not trip:
            raise NotFoundException("Trip not found")

        if not trip.start_date or not trip.end_date:
            raise ValueError("Для генерации маршрута у поездки должны быть указаны даты (start_date и end_date)")

        # Автоматически высчитываем количество дней
        calculated_days = (trip.end_date - trip.start_date).days + 1
        if calculated_days <= 0:
            raise ValueError("Дата окончания должна быть больше или равна дате начала")

        # ── 2. Загружаем город и страну ───────────────────────────────────────
        city = await self.city_repo.get_by_id(trip.city_id)
        country = await self.country_repo.get_by_id(trip.country_id)

        # ── 3. Загружаем POI ТОЛЬКО для этого города ──────────────────────────
        city_pois = await self.poi_repo.get_by_city(trip.city_id)
        
        # Защита от галлюцинаций: если в БД нет мест для этого города, прерываем процесс
        if not city_pois:
            raise NotFoundException(f"К сожалению, в нашей базе пока нет мест для города {city.name}")

        pois_with_rules = []
        for poi in city_pois:
            poi_rules = await self.poi_rule_repo.get_by_poi(poi.id)
            pois_with_rules.append({
                "id": str(poi.id),
                "name": poi.name,
                "description": poi.description or "",
                "is_indoor": poi.is_indoor,
                "rules": [
                    {
                        "content": pr.rule.content,
                        "is_strict": pr.is_strict,
                    }
                    for pr in poi_rules
                ],
            })

        # ── 4. Загружаем правила города ───────────────────────────────────────
        city_rules_raw = await self.city_rule_repo.get_by_city(trip.city_id)
        city_rules = [
            {"content": cr.rule.content, "is_strict": cr.is_strict}
            for cr in city_rules_raw
        ]

        # ── 5. Вызываем AI передавая вычисленные дни ──────────────────────────
        ai_result = await generate_trip(
            city_name=city.name,
            country_name=country.name,
            days=calculated_days, 
            purpose=trip.purpose,
            budget=trip.budget,
            group_size=trip.group_size,
            interests=interests,
            pois=pois_with_rules, 
            city_rules=city_rules,
            notes=notes,
        )

        # ── 6. Сохраняем маршрут в БД ─────────────────────────────────────────
        saved_count = 0
        sequence_order = 1.0

        for day in ai_result.get("days", []):
            day_number = day.get("day", 1)
            for poi_item in day.get("pois", []):
                poi_id_str = poi_item.get("poi_id")
                if not poi_id_str:
                    continue

                try:
                    poi_uuid = uuid.UUID(poi_id_str)
                except ValueError:
                    continue

                poi = await self.poi_repo.get_by_id(poi_uuid)
                if not poi:
                    continue

                existing = await self.trip_poi_repo.get_by_trip_and_poi(
                    trip_id, poi_uuid
                )
                if existing:
                    continue

                planned_time = None
                start_time_str = poi_item.get("start_time")
                if start_time_str and trip.start_date:
                    try:
                        from datetime import timedelta
                        visit_date = trip.start_date + timedelta(days=day_number - 1)
                        hour, minute = map(int, start_time_str.split(":"))
                        planned_time = datetime(
                            visit_date.year, visit_date.month, visit_date.day, hour, minute
                        )
                    except (ValueError, AttributeError):
                        planned_time = None

                await self.trip_poi_repo.create(
                    trip_id=trip_id,
                    poi_id=poi_uuid,
                    sequence_order=sequence_order,
                    planned_start_time=planned_time,
                )
                sequence_order += 1.0
                saved_count += 1

        await self.session.commit()

        # ── 7. Возвращаем результат ───────────────────────────────────────────
        return {
            "trip_id": trip_id,
            "summary": ai_result.get("summary", ""),
            "total_budget_estimate": ai_result.get("total_budget_estimate", ""),
            "days": ai_result.get("days", []),
            "saved_pois_count": saved_count,
        }