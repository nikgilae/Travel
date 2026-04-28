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
    Сервис генерации пула мест для поездки через AI (FR 2.9).
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
        """Сгенерировать пул мест для существующей поездки."""
        
        # ── 1. Загружаем поездку и проверяем даты ─────────────────────────────
        trip = await self.trip_repo.get_by_user_and_id(trip_id, user_id)
        if not trip:
            raise NotFoundException("Trip not found")

        if not trip.start_date or not trip.end_date:
            raise ValueError("Для генерации маршрута у поездки должны быть указаны даты")

        calculated_days = (trip.end_date - trip.start_date).days + 1
        if calculated_days <= 0:
            raise ValueError("Дата окончания должна быть больше или равна дате начала")

        # ── 2. Загружаем город и страну ───────────────────────────────────────
        city = await self.city_repo.get_by_id(trip.city_id)
        country = await self.country_repo.get_by_id(trip.country_id)

        # ── 3. Загружаем POI ТОЛЬКО для этого города ──────────────────────────
        city_pois = await self.poi_repo.get_by_city(trip.city_id)
        
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

        # ── 5. Вызываем AI ────────────────────────────────────────────────────
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

        # ── 6. Сохраняем пул мест в БД (FR 2.9) ───────────────────────────────
        saved_count = 0

        async def _save_poi_to_pool(poi_item: dict, status: str, selected: bool):
            poi_id_str = poi_item.get("poi_id")
            if not poi_id_str:
                return 0
            try:
                poi_uuid = uuid.UUID(poi_id_str)
            except ValueError:
                return 0

            poi = await self.poi_repo.get_by_id(poi_uuid)
            if not poi:
                return 0

            existing = await self.trip_poi_repo.get_by_trip_and_poi(trip_id, poi_uuid)
            if existing:
                return 0

            await self.trip_poi_repo.create(
                trip_id=trip_id,
                poi_id=poi_uuid,
                sequence_order=None,  
                planned_start_time=None,
                poi_status=status,
                is_selected=selected
            )
            return 1

        for day in ai_result.get("days", []):
            
            # Защита от галлюцинаций (подстановка дефолтов для Pydantic)
            for poi_item in day.get("main_pois", []):
                poi_item.setdefault("name", "Неизвестное место")
                poi_item.setdefault("start_time", "10:00")
                poi_item.setdefault("duration_hours", 2.0)
                poi_item.setdefault("budget_estimate", "Не указано")
                poi_item.setdefault("ai_tip", "")
                
                saved_count += await _save_poi_to_pool(poi_item, status="main", selected=True)
            
            for poi_item in day.get("additional_pois", []):
                poi_item.setdefault("name", "Неизвестное место")
                poi_item.setdefault("start_time", "14:00")
                poi_item.setdefault("duration_hours", 1.5)
                poi_item.setdefault("budget_estimate", "Не указано")
                poi_item.setdefault("ai_tip", "")
                
                saved_count += await _save_poi_to_pool(poi_item, status="additional", selected=False)

        await self.session.commit()

        # ── 7. Возвращаем результат ───────────────────────────────────────────
        return {
            "trip_id": trip_id,
            "summary": ai_result.get("summary", ""),
            "total_budget_estimate": ai_result.get("total_budget_estimate", ""),
            "days": ai_result.get("days", []),
            "saved_pois_count": saved_count,
        }