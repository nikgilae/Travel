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
import uuid
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

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
