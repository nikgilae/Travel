"""
Тесты app.services.embedding.

Никакой сетевой активности — app.services.embedding.client.embeddings.create
подменяется моком. build_poi_text проверяется отдельно как чистая функция.
"""
from unittest.mock import AsyncMock

import pytest
from openai import APIConnectionError, AuthenticationError

import app.services.embedding as embedding_module
from app.services.embedding import build_poi_text, get_embedding, MAX_EMBEDDING_ATTEMPTS


class _FakePOI:
    def __init__(self, name=None, description=None, information=None):
        self.name = name
        self.description = description
        self.information = information


def _fake_response(vector: list[float]):
    return type(
        "FakeEmbeddingResponse", (),
        {"data": [type("FakeEmbeddingData", (), {"embedding": vector})()]},
    )()


class TestBuildPoiText:
    def test_joins_all_present_fields(self):
        poi = _FakePOI(name="Музей", description="Городской музей", information="Рейтинг 4.5")
        assert build_poi_text(poi) == "Музей\nГородской музей\nРейтинг 4.5"

    def test_skips_none_fields(self):
        poi = _FakePOI(name="Музей", description=None, information=None)
        assert build_poi_text(poi) == "Музей"

    def test_empty_when_all_none(self):
        poi = _FakePOI(name=None, description=None, information=None)
        assert build_poi_text(poi) == ""

    def test_deterministic(self):
        poi = _FakePOI(name="Парк", description="Городской парк", information=None)
        assert build_poi_text(poi) == build_poi_text(poi)


class TestGetEmbedding:
    async def test_success_returns_vector(self, monkeypatch):
        mock_create = AsyncMock(return_value=_fake_response([0.1, 0.2, 0.3]))
        monkeypatch.setattr(embedding_module.client.embeddings, "create", mock_create)

        result = await get_embedding("текст запроса")

        assert result == [0.1, 0.2, 0.3]
        mock_create.assert_awaited_once()

    async def test_retries_on_retryable_error_then_succeeds(self, monkeypatch):
        mock_create = AsyncMock(
            side_effect=[
                APIConnectionError(request=None),
                _fake_response([0.4, 0.5]),
            ]
        )
        monkeypatch.setattr(embedding_module.client.embeddings, "create", mock_create)

        result = await get_embedding("текст запроса")

        assert result == [0.4, 0.5]
        assert mock_create.await_count == 2

    async def test_raises_after_exhausting_retries(self, monkeypatch):
        mock_create = AsyncMock(side_effect=APIConnectionError(request=None))
        monkeypatch.setattr(embedding_module.client.embeddings, "create", mock_create)

        with pytest.raises(APIConnectionError):
            await get_embedding("текст запроса")

        assert mock_create.await_count == MAX_EMBEDDING_ATTEMPTS

    async def test_non_retryable_error_fails_immediately(self, monkeypatch):
        import httpx

        error = AuthenticationError(
            message="invalid key",
            response=httpx.Response(status_code=401, request=httpx.Request("POST", "https://x")),
            body=None,
        )
        mock_create = AsyncMock(side_effect=error)
        monkeypatch.setattr(embedding_module.client.embeddings, "create", mock_create)

        with pytest.raises(AuthenticationError):
            await get_embedding("текст запроса")

        mock_create.assert_awaited_once()
