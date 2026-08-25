"""
Тесты scripts.backfill_poi_embeddings.backfill.

Работает на реальной тестовой БД (db_session, conftest.py) — не мок. Мокается
только app.services.embedding.get_embedding, чтобы не ходить в сеть.
"""
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select

import app.services.embedding as embedding_module
from app.models.poi import POI
from app.repositories.poi import POIRepository
from scripts.backfill_poi_embeddings import backfill


EMBEDDING_DIM = 3072


def _fake_vector(seed: float = 0.1) -> list[float]:
    return [seed] * EMBEDDING_DIM


@pytest.fixture
def mock_get_embedding(monkeypatch):
    mock = AsyncMock(side_effect=lambda text: _fake_vector())
    monkeypatch.setattr(embedding_module, "get_embedding", mock)
    # backfill script импортирует get_embedding напрямую в свой namespace
    import scripts.backfill_poi_embeddings as backfill_module
    monkeypatch.setattr(backfill_module, "get_embedding", mock)
    return mock


async def _create_poi(db_session, test_city, name="Музей", embedding=None):
    poi = await POIRepository(db_session).create(
        name=name,
        description="Описание",
        information=None,
        geom=None,
        is_indoor=False,
        city_id=test_city.id,
    )
    poi.embedding = embedding
    await db_session.commit()
    return poi


class TestBackfill:
    async def test_computes_embedding_for_pois_without_one(
        self, db_session, test_city, mock_get_embedding
    ):
        poi = await _create_poi(db_session, test_city)

        await backfill(db_session, force=False)

        await db_session.refresh(poi)
        assert poi.embedding is not None
        mock_get_embedding.assert_awaited_once()

    async def test_idempotent_skips_pois_with_existing_embedding(
        self, db_session, test_city, mock_get_embedding
    ):
        await _create_poi(db_session, test_city, embedding=_fake_vector())

        await backfill(db_session, force=False)

        mock_get_embedding.assert_not_awaited()

    async def test_force_recomputes_all(
        self, db_session, test_city, mock_get_embedding
    ):
        await _create_poi(db_session, test_city, embedding=_fake_vector())

        await backfill(db_session, force=True)

        mock_get_embedding.assert_awaited_once()

    async def test_second_run_without_force_is_noop(
        self, db_session, test_city, mock_get_embedding
    ):
        await _create_poi(db_session, test_city)

        await backfill(db_session, force=False)
        mock_get_embedding.reset_mock()
        await backfill(db_session, force=False)

        mock_get_embedding.assert_not_awaited()
