"""
Тесты уровня app.services.trip_ai.TripAIService — валидация дат перед AI-вызовом.

T3b / п.11 чек-листа T8: поездка без дат → 400; end_date < start_date → 400.

Второй случай нельзя воспроизвести обычной записью в БД: таблица trips имеет
CHECK-констрейнт `chk_trips_dates` (end_date >= start_date), который PostgreSQL
проверяет прямо на INSERT/UPDATE и отклоняет такую строку ещё до того, как до
неё дойдёт прикладной код (проверено эмпирически — asyncpg поднимает
CheckViolationError). Так что «поездка с end_date < start_date» физически не
может существовать в БД ни при вставке через ORM, ни через сырой SQL. Чтобы
всё равно проверить ветку `calculated_days <= 0` в TripAIService.generate (она
защищает от рассинхрона days/dates, если constraint когда-нибудь ослабят),
здесь используется поездка-заглушка с мокнутым trip_repo — как и в
tests/services/test_trip.py для TripService. Это единственный способ дойти до
этой ветки, минуя и Pydantic (TripCreate.validate_dates), и CHECK в БД.
"""
import asyncio
import uuid
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import app.services.trip_ai as trip_ai_module
from app.core.exceptions import BadRequestException
from app.services.trip_ai import TripAIService


def _fake_trip(start_date=None, end_date=None):
    return SimpleNamespace(
        id=uuid.uuid4(),
        start_date=start_date,
        end_date=end_date,
    )


class TestTripAIServiceDateValidation:

    def setup_method(self):
        self.service = TripAIService(AsyncMock())
        self.service.trip_repo = AsyncMock()

    async def test_generate_without_dates_raises_bad_request(self):
        """Поездка без start_date/end_date — 400, AI не вызывается."""
        self.service.trip_repo.get_by_user_and_id.return_value = _fake_trip(
            start_date=None, end_date=None,
        )

        with pytest.raises(BadRequestException):
            await self.service.generate(
                trip_id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                interests=["культура"],
                notes=None,
            )

    async def test_generate_end_date_before_start_date_raises_bad_request(self):
        """
        end_date < start_date (недостижимо через API/БД из-за chk_trips_dates,
        см. docstring модуля) — ветка calculated_days <= 0 всё равно должна
        падать 400, а не считать отрицательное число дней.
        """
        self.service.trip_repo.get_by_user_and_id.return_value = _fake_trip(
            start_date=date(2026, 1, 10), end_date=date(2026, 1, 1),
        )

        with pytest.raises(BadRequestException):
            await self.service.generate(
                trip_id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                interests=["культура"],
                notes=None,
            )


class TestSelectCityPois:
    """
    Тесты app.services.trip_ai.TripAIService._select_city_pois — решающая
    логика Итерации 2 RAG-POI-PLAN.md, вынесена отдельно от generate(),
    т.к. мокать весь generate() (trip_repo, city_repo, country_repo,
    city_rule_repo, poi_rule_repo, generate_trip) ради двух веток флага
    было бы дорого и хрупко.
    """

    def setup_method(self):
        self.service = TripAIService(AsyncMock())
        self.service.poi_repo = AsyncMock()
        self.city_id = uuid.uuid4()

    def _fake_city_pois(self, n: int) -> list:
        return [SimpleNamespace(id=uuid.uuid4()) for _ in range(n)]

    async def test_flag_off_uses_random_sample_poi_repo_untouched(self, monkeypatch):
        monkeypatch.setattr(trip_ai_module.settings, "RAG_POI_RETRIEVAL_ENABLED", False)
        city_pois = self._fake_city_pois(150)

        result = await self.service._select_city_pois(
            self.city_id, city_pois, interests=["cultural"], notes=None, max_pois=100,
        )

        assert len(result) == 100
        assert {poi.id for poi in result} <= {poi.id for poi in city_pois}
        self.service.poi_repo.get_relevant_for_trip.assert_not_awaited()

    async def test_flag_off_returns_all_when_under_limit(self, monkeypatch):
        monkeypatch.setattr(trip_ai_module.settings, "RAG_POI_RETRIEVAL_ENABLED", False)
        city_pois = self._fake_city_pois(10)

        result = await self.service._select_city_pois(
            self.city_id, city_pois, interests=["cultural"], notes=None, max_pois=100,
        )

        assert result == city_pois

    async def test_flag_on_success_calls_retrieval_with_embedded_query(self, monkeypatch):
        monkeypatch.setattr(trip_ai_module.settings, "RAG_POI_RETRIEVAL_ENABLED", True)
        fake_embedding = [0.1, 0.2, 0.3]
        mock_get_embedding = AsyncMock(return_value=fake_embedding)
        monkeypatch.setattr(trip_ai_module, "get_embedding", mock_get_embedding)
        sentinel_result = self._fake_city_pois(5)
        self.service.poi_repo.get_relevant_for_trip.return_value = sentinel_result

        result = await self.service._select_city_pois(
            self.city_id, self._fake_city_pois(150),
            interests=["cultural", "food"], notes="хочу музеи", max_pois=100,
        )

        assert result == sentinel_result
        mock_get_embedding.assert_awaited_once_with("cultural, food\nхочу музеи")
        self.service.poi_repo.get_relevant_for_trip.assert_awaited_once_with(
            self.city_id, fake_embedding, 100,
        )

    async def test_flag_on_embedding_error_falls_back_to_random_sample(self, monkeypatch):
        monkeypatch.setattr(trip_ai_module.settings, "RAG_POI_RETRIEVAL_ENABLED", True)
        mock_get_embedding = AsyncMock(side_effect=RuntimeError("provider down"))
        monkeypatch.setattr(trip_ai_module, "get_embedding", mock_get_embedding)
        city_pois = self._fake_city_pois(150)

        result = await self.service._select_city_pois(
            self.city_id, city_pois, interests=["cultural"], notes=None, max_pois=100,
        )

        assert len(result) == 100
        assert {poi.id for poi in result} <= {poi.id for poi in city_pois}
        self.service.poi_repo.get_relevant_for_trip.assert_not_awaited()

    async def test_flag_on_embedding_timeout_falls_back_to_random_sample(self, monkeypatch):
        """
        Находка feature-flags-architect: get_embedding сам может занять до
        ~60с (ретраи), что дольше AI_GENERATION_BUDGET_SECONDS=30s. Здесь
        сокращаем RAG_RETRIEVAL_TIMEOUT_SECONDS до долей секунды, чтобы не
        ждать реальный таймаут в тесте, но проверить именно asyncio.wait_for,
        а не просто except-ветку (test выше).
        """
        monkeypatch.setattr(trip_ai_module.settings, "RAG_POI_RETRIEVAL_ENABLED", True)
        monkeypatch.setattr(trip_ai_module, "RAG_RETRIEVAL_TIMEOUT_SECONDS", 0.01)

        async def _hangs_forever(text: str):
            await asyncio.sleep(1.0)
            return [0.1]

        monkeypatch.setattr(trip_ai_module, "get_embedding", _hangs_forever)
        city_pois = self._fake_city_pois(150)

        result = await self.service._select_city_pois(
            self.city_id, city_pois, interests=["cultural"], notes=None, max_pois=100,
        )

        assert len(result) == 100
        self.service.poi_repo.get_relevant_for_trip.assert_not_awaited()
