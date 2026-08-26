"""
Тесты scripts.enrich_poi_descriptions.enrich.

Работает на реальной тестовой БД (db_session, conftest.py) — не мок. Мокается
только GoogleMapsClient.get_place_details, чтобы не ходить в сеть; логика
приоритезации источников (build_ai_description) тестируется отдельно в
tests/services/test_poi_description.py.
"""
from unittest.mock import AsyncMock

import pytest

import app.core.maps as maps_module
from app.config import settings
from app.repositories.poi import POIRepository
from scripts.enrich_poi_descriptions import enrich

EMBEDDING_DIM = 3072


def _fake_vector(seed: float = 0.1) -> list[float]:
    return [seed] * EMBEDDING_DIM


async def _create_poi(
    db_session, test_city, name="Музей", google_place_id="place1", embedding=None
):
    poi = await POIRepository(db_session).create(
        name=name,
        description="Museum, establishment",
        information=None,
        geom=None,
        is_indoor=False,
        city_id=test_city.id,
        google_place_id=google_place_id,
    )
    poi.embedding = embedding
    await db_session.commit()
    return poi


@pytest.fixture
def mock_get_place_details(monkeypatch):
    mock = AsyncMock(return_value={"editorial_summary": "Курируемый текст", "reviews": []})
    monkeypatch.setattr(maps_module.GoogleMapsClient, "get_place_details", mock)
    return mock


class TestEnrich:
    async def test_enriches_poi_with_google_place_id(
        self, db_session, test_city, mock_get_place_details
    ):
        poi = await _create_poi(db_session, test_city)

        await enrich(db_session, force=False)

        await db_session.refresh(poi)
        assert poi.ai_description == "Курируемый текст"
        assert poi.ai_description_source == "google_editorial"

    async def test_invalidates_embedding_when_text_changes(
        self, db_session, test_city, mock_get_place_details
    ):
        poi = await _create_poi(db_session, test_city, embedding=_fake_vector())

        await enrich(db_session, force=False)

        await db_session.refresh(poi)
        assert poi.embedding is None

    async def test_category_fallback_keeps_embedding(self, db_session, test_city, monkeypatch):
        mock = AsyncMock(return_value={"editorial_summary": None, "reviews": []})
        monkeypatch.setattr(maps_module.GoogleMapsClient, "get_place_details", mock)
        poi = await _create_poi(db_session, test_city, embedding=_fake_vector())

        await enrich(db_session, force=False)

        await db_session.refresh(poi)
        assert poi.ai_description_source == "category_fallback"
        assert poi.embedding is not None

    async def test_skips_poi_without_google_place_id(
        self, db_session, test_city, mock_get_place_details
    ):
        poi = await _create_poi(db_session, test_city, google_place_id=None)

        await enrich(db_session, force=False)

        await db_session.refresh(poi)
        assert poi.ai_description is None
        mock_get_place_details.assert_not_awaited()

    async def test_idempotent_skips_already_enriched(
        self, db_session, test_city, mock_get_place_details
    ):
        poi = await _create_poi(db_session, test_city)
        poi.ai_description = "уже обогащено"
        poi.ai_description_source = "google_editorial"
        await db_session.commit()

        await enrich(db_session, force=False)

        mock_get_place_details.assert_not_awaited()

    async def test_force_recomputes_all(self, db_session, test_city, mock_get_place_details):
        poi = await _create_poi(db_session, test_city)
        poi.ai_description = "старый текст"
        poi.ai_description_source = "google_editorial"
        await db_session.commit()

        await enrich(db_session, force=True)

        mock_get_place_details.assert_awaited_once()

    async def test_google_maps_disabled_skips_entirely(
        self, db_session, test_city, mock_get_place_details, monkeypatch
    ):
        monkeypatch.setattr(settings, "GOOGLE_MAPS_ENABLED", False)
        await _create_poi(db_session, test_city)

        await enrich(db_session, force=False)

        mock_get_place_details.assert_not_awaited()
