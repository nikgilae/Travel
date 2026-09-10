"""
Тесты app.services.city_enrichment — обогащение города вынесено из запроса.

Смысл модуля в том, чего в нём НЕ происходит: генерация маршрута больше не
ждёт двадцати запросов в Google и сотни вызовов эмбеддинга. Поэтому тесты
здесь про две вещи — когда обогащение вообще положено (is_due) и что schedule
отдаёт управление сразу и не заводит второй заход по тому же городу.

Сеть не трогается: сам заход (_enrich) подменяется, проверяется поведение
планировщика, а не Google Maps.
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from types import SimpleNamespace

import app.services.city_enrichment as city_enrichment


def _fake_city(last_enriched_at=None):
    return SimpleNamespace(
        id=uuid.uuid4(),
        name="Пхукет",
        last_enriched_at=last_enriched_at,
    )


class TestIsDue:

    def test_both_sources_off_never_due(self, monkeypatch):
        """Оба источника мест выключены → заходить незачем."""
        monkeypatch.setattr(city_enrichment.settings, "GOOGLE_MAPS_ENABLED", False)
        monkeypatch.setattr(city_enrichment.settings, "AI_POI_FALLBACK_ENABLED", False)
        assert city_enrichment.is_due(_fake_city()) is False

    def test_ai_fallback_alone_is_enough(self, monkeypatch):
        """
        Google выключен, но модель может назвать места — идём.

        Ровно текущее состояние прода: биллинг в Google Cloud выключен,
        Places API отказывает, единственный источник мест для нового города —
        память модели.
        """
        monkeypatch.setattr(city_enrichment.settings, "GOOGLE_MAPS_ENABLED", False)
        monkeypatch.setattr(city_enrichment.settings, "AI_POI_FALLBACK_ENABLED", True)
        assert city_enrichment.is_due(_fake_city()) is True

    def test_never_enriched_is_due(self, monkeypatch):
        """Город, который не обогащали ни разу (свой город из онбординга)."""
        monkeypatch.setattr(city_enrichment.settings, "GOOGLE_MAPS_ENABLED", True)
        assert city_enrichment.is_due(_fake_city()) is True

    def test_inside_cooldown_not_due(self, monkeypatch):
        """Обогащали час назад при кулдауне 24 часа → рано."""
        monkeypatch.setattr(city_enrichment.settings, "GOOGLE_MAPS_ENABLED", True)
        monkeypatch.setattr(city_enrichment.settings, "ENRICH_COOLDOWN_HOURS", 24)
        city = _fake_city(last_enriched_at=datetime.utcnow() - timedelta(hours=1))
        assert city_enrichment.is_due(city) is False

    def test_empty_city_ignores_cooldown(self, monkeypatch):
        """
        У города ноль мест — идём за ними, даже если заходили минуту назад.

        Кулдаун бережёт платные запросы по городу, где места уже есть. Пустой
        город означает, что прошлый заход ничего не дал, и сутки ожидания для
        человека равны «этот город не работает».
        """
        monkeypatch.setattr(city_enrichment.settings, "GOOGLE_MAPS_ENABLED", True)
        monkeypatch.setattr(city_enrichment.settings, "ENRICH_COOLDOWN_HOURS", 24)
        city = _fake_city(last_enriched_at=datetime.utcnow() - timedelta(minutes=1))

        assert city_enrichment.is_due(city, has_pois=False) is True
        assert city_enrichment.is_due(city, has_pois=True) is False

    def test_cooldown_expired_is_due(self, monkeypatch):
        monkeypatch.setattr(city_enrichment.settings, "GOOGLE_MAPS_ENABLED", True)
        monkeypatch.setattr(city_enrichment.settings, "ENRICH_COOLDOWN_HOURS", 24)
        city = _fake_city(last_enriched_at=datetime.utcnow() - timedelta(hours=25))
        assert city_enrichment.is_due(city) is True


class TestSchedule:

    async def test_all_sources_off_returns_none_and_starts_nothing(self, monkeypatch):
        monkeypatch.setattr(city_enrichment.settings, "GOOGLE_MAPS_ENABLED", False)
        monkeypatch.setattr(city_enrichment.settings, "AI_POI_FALLBACK_ENABLED", False)
        started = []
        monkeypatch.setattr(city_enrichment, "_enrich", lambda *a: started.append(a))

        assert city_enrichment.schedule(uuid.uuid4(), "Пхукет") is None
        assert started == []

    async def test_returns_immediately_while_work_continues(self, monkeypatch):
        """
        Главное свойство: schedule возвращает управление, не дожидаясь захода.

        Заход держится на событии — если бы schedule его ждал, тест повис бы
        на самой строке вызова, а не дошёл до проверок.
        """
        monkeypatch.setattr(city_enrichment.settings, "GOOGLE_MAPS_ENABLED", True)
        release = asyncio.Event()

        async def _slow_enrich(city_id, city_name):
            await release.wait()
            return 7

        monkeypatch.setattr(city_enrichment, "_enrich", _slow_enrich)

        task = city_enrichment.schedule(uuid.uuid4(), "Пхукет")
        assert task is not None
        assert not task.done()

        release.set()
        assert await task == 7

    async def test_second_call_for_same_city_reuses_running_task(self, monkeypatch):
        """Два человека выбрали один город — заход всё равно один."""
        monkeypatch.setattr(city_enrichment.settings, "GOOGLE_MAPS_ENABLED", True)
        release = asyncio.Event()
        calls = []

        async def _slow_enrich(city_id, city_name):
            calls.append(city_id)
            await release.wait()
            return 0

        monkeypatch.setattr(city_enrichment, "_enrich", _slow_enrich)
        city_id = uuid.uuid4()

        first = city_enrichment.schedule(city_id, "Пхукет")
        await asyncio.sleep(0)  # даём задаче стартовать
        second = city_enrichment.schedule(city_id, "Пхукет")

        assert first is second
        assert len(calls) == 1

        release.set()
        await first

    async def test_finished_city_can_be_scheduled_again(self, monkeypatch):
        """Задача завершилась — город больше не считается занятым."""
        monkeypatch.setattr(city_enrichment.settings, "GOOGLE_MAPS_ENABLED", True)

        async def _fast_enrich(city_id, city_name):
            return 1

        monkeypatch.setattr(city_enrichment, "_enrich", _fast_enrich)
        city_id = uuid.uuid4()

        first = city_enrichment.schedule(city_id, "Пхукет")
        await first
        second = city_enrichment.schedule(city_id, "Пхукет")

        assert second is not first
        await second
        assert city_id not in city_enrichment._in_flight
