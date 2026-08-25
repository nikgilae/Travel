import asyncio
import uuid
import time
import logging
import random
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import (
    AIGenerationError,
    BadRequestException,
    NotFoundException,
)
from app.models.poi import POI
from app.models.trip import Trip, TripPOI
from app.repositories.trip import TripRepository, TripPOIRepository
from app.repositories.poi import POIRepository
from app.repositories.rule import CityRuleRepository, POIRuleRepository
from app.repositories.geography import CityRepository, CountryRepository
from app.services.ai import generate_trip
from app.services.embedding import get_embedding
from app.services.poi import POIService

logger = logging.getLogger(__name__)

# Исход генерации, который надо отличать в приборах от успеха и от сбоя:
# запрос пришёл на уже наполненную поездку, AI не вызывался.
GENERATE_OUTCOME_SKIPPED_EXISTING = "skipped_existing"

# Свой потолок на весь retrieval-заход (embedding + запрос к БД), меньше
# AI_GENERATION_BUDGET_SECONDS=30s с большим запасом на сам AI-вызов после
# него. get_embedding сам может занять до ~60с (3 попытки × read-таймаут) —
# это дольше всего бюджета генерации, поэтому здесь отдельный, более жёсткий
# потолок, а не переиспользование AI_READ_TIMEOUT_SECONDS.
RAG_RETRIEVAL_TIMEOUT_SECONDS = 5.0


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

    async def _select_city_pois(
        self,
        city_id: uuid.UUID,
        city_pois: list[POI],
        interests: list[str],
        notes: str | None,
        max_pois: int,
    ) -> list[POI]:
        """
        Выбрать не больше max_pois POI города для промпта AI.

        За settings.RAG_POI_RETRIEVAL_ENABLED — top-k по семантической
        близости к interests+notes, ограничено RAG_RETRIEVAL_TIMEOUT_SECONDS;
        при любом сбое (таймаут, сеть, провайдер эмбеддингов) — тот же
        защитный стиль, что у обогащения Google Maps (см. ниже в generate()):
        явный, грепаемый лог отката (не общий warning — иначе "flag on и
        работает" и "flag on и тихо откатился" неотличимы в логах) и
        random.sample. Флаг off — поведение байт-в-байт как до этой итерации.
        """
        if settings.RAG_POI_RETRIEVAL_ENABLED:
            query_text = ", ".join(interests) + (f"\n{notes}" if notes else "")
            try:
                query_embedding = await asyncio.wait_for(
                    get_embedding(query_text), timeout=RAG_RETRIEVAL_TIMEOUT_SECONDS
                )
                return await self.poi_repo.get_relevant_for_trip(city_id, query_embedding, max_pois)
            except Exception as e:
                logger.warning(
                    "RAG_RETRIEVAL_FALLBACK: retrieval POI не удался (city_id=%s) — "
                    "откат на random.sample. %s: %s",
                    city_id, type(e).__name__, e,
                )

        if len(city_pois) > max_pois:
            return random.sample(city_pois, max_pois)
        return city_pois

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
            raise BadRequestException(
                "Для генерации маршрута у поездки должны быть указаны даты"
            )

        calculated_days = (trip.end_date - trip.start_date).days + 1
        if calculated_days <= 0:
            raise BadRequestException(
                "Дата окончания должна быть больше или равна дате начала"
            )

        # ── 1b. План уже есть — короткое замыкание до вызова AI ───────────────
        # Повторный /generate на наполненной поездке НЕ должен дописывать места.
        # При temperature=0.7 AI каждый раз предлагает другой набор, и проверка
        # дублей ниже пропускает большинство предложений как «новые»: замер на
        # живой БД дал 29 → 40 → 51 место за три повтора, а sequence_order
        # второго прогона начинался заново с 1 и сталкивался с первым.
        # Реальный сценарий — клиент оборвал запрос по своему бюджету времени,
        # сервер досчитал и сохранил план, человек жмёт «Попробовать снова».
        # Проверка стоит ДО загрузки POI города, обогащения и вызова AI, чтобы
        # не платить провайдеру (8–30 с и деньги) за результат, который выбросим.
        existing_pois = await self.trip_poi_repo.get_by_trip(trip_id)
        if existing_pois:
            logger.info(
                "Поездка %s: в плане уже %d мест — повторная генерация пропущена, "
                "AI не вызывался",
                trip_id, len(existing_pois),
            )
            return {
                "trip_id": trip_id,
                "summary": trip.ai_summary or "",
                "total_budget_estimate": trip.total_budget_estimate or "",
                # days пустой намеренно: страница плана читает маршрут из БД,
                # пересборка days из TripPOI — отдельная задача.
                "days": [],
                "saved_pois_count": 0,
                "proposed_pois_count": 0,
                "outcome": GENERATE_OUTCOME_SKIPPED_EXISTING,
            }

        # ── 2. Загружаем город и страну ───────────────────────────────────────
        city = await self.city_repo.get_by_id(trip.city_id)
        country = await self.country_repo.get_by_id(trip.country_id)

        # ── 3. Обогащение через Google Maps (кулдаун-контроль) ─────────────────
        city_pois = await self.poi_repo.get_by_city(trip.city_id)

        city = await self.city_repo.get_by_id(trip.city_id)

        now = datetime.utcnow()
        cooldown = timedelta(hours=settings.ENRICH_COOLDOWN_HOURS)
        needs_enrichment = settings.GOOGLE_MAPS_ENABLED and (
            city.last_enriched_at is None
            or (now - city.last_enriched_at) >= cooldown
        )
        if not settings.GOOGLE_MAPS_ENABLED:
            logger.info("Google Maps выключен (GOOGLE_MAPS_ENABLED=false) — обогащение пропущено")

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

        MAX_POIS_FOR_AI = 40 if settings.DEMO_FAST_GENERATION else 100
        city_pois = await self._select_city_pois(
            trip.city_id, city_pois, interests, notes, MAX_POIS_FOR_AI
        )
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
        _t_ai = time.perf_counter()
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
            fast=settings.DEMO_FAST_GENERATION,
        )
        logger.info(
            "AI-генерация маршрута заняла %.1f сек (fast=%s)",
            time.perf_counter() - _t_ai, settings.DEMO_FAST_GENERATION,
        )

        # ── 6. Сохраняем пул мест в БД (FR 2.9) ──────────────────────────────
        # Считаем исходы раздельно: «место уже в поездке» и «места нет в базе» —
        # это принципиально разные ситуации, и путать их в одной ошибке нельзя.
        saved_count = 0
        skipped_duplicates = 0
        proposed = 0

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
        ) -> str:
            """Вернуть исход: 'saved' | 'duplicate' | 'skipped'."""
            poi_id_str = poi_item.get("poi_id")
            if not poi_id_str:
                logger.warning("[day %d] poi_id отсутствует, пропускаем", day_number)
                return "skipped"
            try:
                poi_uuid = uuid.UUID(poi_id_str)
            except ValueError:
                logger.warning("[day %d] Невалидный poi_id '%s', пропускаем", day_number, poi_id_str)
                return "skipped"

            poi = await self.poi_repo.get_by_id(poi_uuid)
            if not poi:
                logger.warning("[day %d] POI %s не найден в БД, пропускаем", day_number, poi_id_str)
                return "skipped"

            existing = await self.trip_poi_repo.get_by_trip_and_poi(trip_id, poi_uuid)
            if existing:
                # Место уже в поездке — это не сбой (типичный случай: повторный
                # /generate после клиентского таймаута).
                return "duplicate"

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
                return "skipped"
            return "saved"

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
                proposed += 1
                outcome = await _save_poi_to_pool(
                    poi_item, status="main", selected=True,
                    day_number=current_day_num, day_theme=current_day_theme,
                    sequence_order=float(main_order),
                )
                if outcome == "saved":
                    saved_count += 1
                    main_order += 1
                elif outcome == "duplicate":
                    skipped_duplicates += 1

            alt_order = main_order + 100  # запасные идут после основных

            for poi_item in day.get("additional_pois", []):
                poi_item.setdefault("name", "Неизвестное место")
                poi_item.setdefault("start_time", "14:00")
                poi_item.setdefault("duration_hours", 1.5)
                poi_item.setdefault("budget_estimate", "Не указано")
                poi_item.setdefault("ai_tip", "")
                proposed += 1
                outcome = await _save_poi_to_pool(
                    poi_item, status="additional", selected=False,
                    day_number=current_day_num, day_theme=current_day_theme,
                    sequence_order=float(alt_order),
                )
                if outcome == "saved":
                    saved_count += 1
                    alt_order += 1
                elif outcome == "duplicate":
                    skipped_duplicates += 1

            logger.info("[day %d] сохранено %d основных + запасных мест", current_day_num, main_order - 1)

        if saved_count and saved_count < proposed * 0.5:
            logger.warning(
                "Генерация для поездки %s: сохранено %d из %d предложенных мест "
                "(дублей %d) — план в БД заметно беднее ответа AI",
                trip_id, saved_count, proposed, skipped_duplicates,
            )

        # ── Второй рубеж честной ошибки ──────────────────────────────────────
        # Сохранять нечего. Различаем два принципиально разных случая:
        #   а) поездка уже наполнена — после короткого замыкания в п.1b сюда
        #      попадает только гонка: две генерации стартовали одновременно на
        #      пустой поездке, первая успела сохранить план. Отдаём его
        #      идемпотентно, иначе человек заперт в вечном 502;
        #   б) в поездке пусто и AI предложил только неизвестные нам места —
        #      вот это настоящий сбой, коммит здесь дал бы HTTP 200 с пустым планом.
        if saved_count == 0:
            existing_pois = await self.trip_poi_repo.get_by_trip(trip_id)
            if existing_pois or skipped_duplicates:
                logger.info(
                    "Генерация для поездки %s: новых мест не добавлено "
                    "(дублей %d, уже в поездке %d) — отдаём существующий план",
                    trip_id, skipped_duplicates, len(existing_pois),
                )
                return {
                    "trip_id": trip_id,
                    "summary": trip.ai_summary or ai_result.get("summary", ""),
                    "total_budget_estimate": (
                        trip.total_budget_estimate
                        or ai_result.get("total_budget_estimate", "")
                    ),
                    "days": ai_result.get("days", []),
                    "saved_pois_count": 0,
                    "proposed_pois_count": proposed,
                }

            logger.error(
                "Генерация для поездки %s: AI вернул %d дней и %d мест, но ни одно "
                "не нашлось в нашей базе — отдаём ошибку",
                trip_id, len(ai_result.get("days", [])), proposed,
            )
            # rollback здесь не зовём: откат делает get_db на выходе из запроса
            # (иначе экспайрится весь identity map сессии, включая current_user).
            raise AIGenerationError(
                "Ни одно из предложенных мест не нашлось в нашей базе. "
                "Попробуйте сгенерировать ещё раз."
            )

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
            "proposed_pois_count": proposed,
        }
