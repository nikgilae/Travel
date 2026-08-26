"""
Тесты GoogleMapsClient.get_place_details (Итерация 4, RAG-POI-PLAN.md).

Никакой сетевой активности — httpx.AsyncClient подменяется фейком, по
образцу мокирования внешних клиентов в других тестах (app.services.ai/embedding).
"""
import httpx
import pytest

from app.core.maps import GoogleMapsClient


class _FakeResponse:
    def __init__(self, json_data):
        self._json_data = json_data

    def raise_for_status(self):
        pass

    def json(self):
        return self._json_data


class _FakeAsyncClient:
    def __init__(self, response=None, exc=None):
        self._response = response
        self._exc = exc

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def get(self, *args, **kwargs):
        if self._exc:
            raise self._exc
        return self._response


def _patch_httpx(monkeypatch, response=None, exc=None):
    monkeypatch.setattr(
        "app.core.maps.httpx.AsyncClient",
        lambda: _FakeAsyncClient(response=response, exc=exc),
    )


@pytest.fixture
def google_maps_client():
    client = GoogleMapsClient()
    client.api_key = "fake-key"
    return client


class TestGetPlaceDetails:
    async def test_returns_editorial_summary_and_reviews(self, monkeypatch, google_maps_client):
        _patch_httpx(monkeypatch, response=_FakeResponse({
            "status": "OK",
            "result": {
                "editorial_summary": {"overview": "Уютное место у моря."},
                "reviews": [{"text": "Отличный вид"}, {"text": "Вкусная еда"}],
            },
        }))

        result = await google_maps_client.get_place_details("place123")

        assert result == {
            "editorial_summary": "Уютное место у моря.",
            "reviews": ["Отличный вид", "Вкусная еда"],
        }

    async def test_missing_fields_return_empty_values(self, monkeypatch, google_maps_client):
        _patch_httpx(monkeypatch, response=_FakeResponse({"status": "OK", "result": {}}))

        result = await google_maps_client.get_place_details("place123")

        assert result == {"editorial_summary": None, "reviews": []}

    async def test_reviews_without_text_are_dropped(self, monkeypatch, google_maps_client):
        _patch_httpx(monkeypatch, response=_FakeResponse({
            "status": "OK",
            "result": {"reviews": [{"rating": 5}, {"text": "Хорошо"}]},
        }))

        result = await google_maps_client.get_place_details("place123")

        assert result["reviews"] == ["Хорошо"]

    async def test_non_ok_status_returns_empty_dict(self, monkeypatch, google_maps_client):
        _patch_httpx(monkeypatch, response=_FakeResponse({"status": "NOT_FOUND"}))

        result = await google_maps_client.get_place_details("place123")

        assert result == {}

    async def test_request_error_returns_empty_dict(self, monkeypatch, google_maps_client):
        _patch_httpx(monkeypatch, exc=httpx.ConnectError("boom"))

        result = await google_maps_client.get_place_details("place123")

        assert result == {}

    async def test_no_api_key_returns_empty_dict_without_request(self, monkeypatch):
        client = GoogleMapsClient()
        client.api_key = ""

        def _fail(*a, **kw):
            raise AssertionError("не должно ходить в сеть без api_key")

        monkeypatch.setattr("app.core.maps.httpx.AsyncClient", _fail)

        result = await client.get_place_details("place123")

        assert result == {}
