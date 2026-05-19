import uuid
import logging
import random
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import NotFoundException
from app.models.trip import Trip, TripPOI
from app.repositories.trip import TripRepository, TripPOIRepository
from app.repositories.poi import POIRepository
from app.repositories.rule import CityRuleRepository, POIRuleRepository
from app.repositories.geography import CityRepository, CountryRepository
from app.services.ai import generate_trip
from app.services.poi import POIService

logger = logging.getLogger(__name__)


class TripAIService:
    """
    Сервис генерации пула мест для поездки через AI (FR 2.9).
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.trip_repo = TripRepository(session)
        self.trip_poi_repo = TripPOIRepository(session)
        self.poi_repo = POIRepository(session)
        self.poi_service = POIService(session)
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

        # ── 3. Обогащение через Google Maps (кулдаун-контроль) ─────────────────
        city_pois = await self.poi_repo.get_by_city(trip.city_id)

        city = await self.city_repo.get_by_id(trip.city_id)

        now = datetime.utcnow()
        cooldown = timedelta(hours=settings.ENRICH_COOLDOWN_HOURS)
        needs_enrichment = (
            city.last_enriched_at is None
            or (now - city.last_enriched_at) >= cooldown
        )

        if needs_enrichment:
            logger.info(
                "Город '%s': запускаем обогащение через Google Maps (last_enriched_at=%s)",
                city.name, city.last_enriched_at,
            )
            try:
                added = await self.poi_service.enrich_city_from_google(trip.city_id, city.name)
                logger.info("Google Maps: добавлено %d новых POI для '%s'", added, city.name)
                await self.city_repo.update(city.id, last_enriched_at=datetime.utcnow())
                await self.session.commit()
                city_pois = await self.poi_repo.get_by_city(trip.city_id)
            except Exception as e:
                logger.warning("Обогащение через Google Maps не удалось: %s", e)

        if not city_pois:
            raise NotFoundException(
                f"В нашей базе нет мест для города {city.name}. "
                "Попробуйте позже или выберите другой город."
            )

        MAX_POIS_FOR_AI = 100
        if len(city_pois) > MAX_POIS_FOR_AI:
            city_pois = random.sample(city_pois, MAX_POIS_FOR_AI)
        logger.info("Отправляем в AI %d POI для города '%s'", len(city_pois), city.name)

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

        # ── 6. Сохраняем пул мест в БД (FR 2.9) ──────────────────────────────
        saved_count = 0

        def _calc_end_time(start_time: str | None, duration_hours: float | None) -> str | None:
            if not start_time or not duration_hours:
                return None
            try:
                from datetime import datetime as dt, timedelta as td
                base = dt.strptime(start_time, "%H:%M")
                end = base + td(hours=duration_hours)
                return end.strftime("%H:%M")
            except Exception:
                return None

        async def _save_poi_to_pool(
            poi_item: dict,
            status: str,
            selected: bool,
            day_number: int,
            day_theme: str | None,
            sequence_order: float,
        ):
            poi_id_str = poi_item.get("poi_id")
            if not poi_id_str:
                logger.warning("[day %d] poi_id отсутствует, пропускаем", day_number)
                return 0
            try:
                poi_uuid = uuid.UUID(poi_id_str)
            except ValueError:
                logger.warning("[day %d] Невалидный poi_id '%s', пропускаем", day_number, poi_id_str)
                return 0

            poi = await self.poi_repo.get_by_id(poi_uuid)
            if not poi:
                logger.warning("[day %d] POI %s не найден в БД, пропускаем", day_number, poi_id_str)
                return 0

            existing = await self.trip_poi_repo.get_by_trip_and_poi(trip_id, poi_uuid)
            if existing:
                return 0

            st = poi_item.get("start_time")
            dh = poi_item.get("duration_hours")
            raw_level = poi_item.get("activity_level")
            activity_level = int(raw_level) if raw_level is not None else None
            if activity_level is not None:
                activity_level = max(1, min(5, activity_level))
            try:
                async with self.session.begin_nested():
                    await self.trip_poi_repo.create(
                        trip_id=trip_id,
                        poi_id=poi_uuid,
                        sequence_order=sequence_order,
                        planned_start_time=None,
                        poi_status=status,
                        is_selected=selected,
                        day_number=day_number,
                        start_time=st,
                        end_time=_calc_end_time(st, dh),
                        duration_hours=dh,
                        budget_estimate=poi_item.get("budget_estimate"),
                        ai_tip=poi_item.get("ai_tip"),
                        day_theme=day_theme,
                        activity_level=activity_level,
                    )
            except Exception as e:
                logger.error("[day %d] Ошибка сохранения POI %s: %s", day_number, poi_id_str, e)
                return 0
            return 1

        for day in ai_result.get("days", []):
            current_day_num = day.get("day", 1)
            current_day_theme = day.get("theme")
            main_order = 1

            for poi_item in day.get("main_pois", []):
                poi_item.setdefault("name", "Неизвестное место")
                poi_item.setdefault("start_time", "10:00")
                poi_item.setdefault("duration_hours", 2.0)
                poi_item.setdefault("budget_estimate", "Не указано")
                poi_item.setdefault("ai_tip", "")
                n = await _save_poi_to_pool(
                    poi_item, status="main", selected=True,
                    day_number=current_day_num, day_theme=current_day_theme,
                    sequence_order=float(main_order),
                )
                saved_count += n
                if n:
                    main_order += 1

            alt_order = main_order + 100  # запасные идут после основных

            for poi_item in day.get("additional_pois", []):
                poi_item.setdefault("name", "Неизвестное место")
                poi_item.setdefault("start_time", "14:00")
                poi_item.setdefault("duration_hours", 1.5)
                poi_item.setdefault("budget_estimate", "Не указано")
                poi_item.setdefault("ai_tip", "")
                n = await _save_poi_to_pool(
                    poi_item, status="additional", selected=False,
                    day_number=current_day_num, day_theme=current_day_theme,
                    sequence_order=float(alt_order),
                )
                saved_count += n
                if n:
                    alt_order += 1

            logger.info("[day %d] сохранено %d основных + запасных мест", current_day_num, main_order - 1)

        trip.ai_summary = ai_result.get("summary")
        trip.total_budget_estimate = ai_result.get("total_budget_estimate")

        await self.session.commit()

        # ── 7. Возвращаем результат ───────────────────────────────────────────
        return {
            "trip_id": trip_id,
            "summary": ai_result.get("summary", ""),
            "total_budget_estimate": ai_result.get("total_budget_estimate", ""),
            "days": ai_result.get("days", []),
            "saved_pois_count": saved_count,
        }
