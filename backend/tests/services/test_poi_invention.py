"""
Тесты app.services.poi_invention — места из памяти модели.

Сеть не трогается: подменяется gen_client. Проверяется разбор ответа, потому
что именно он защищает человека от мусора — выдуманных координат, пустых
названий и дублей.
"""
import json
from types import SimpleNamespace

import pytest

import app.services.poi_invention as invention


def _response(payload):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))]
    )


class _FakeClient:
    def __init__(self, response=None, exc=None):
        self._response = response
        self._exc = exc
        self.calls = 0

    def with_options(self, **kwargs):
        return self

    @property
    def chat(self):
        return SimpleNamespace(completions=SimpleNamespace(create=self._create))

    async def _create(self, **kwargs):
        self.calls += 1
        if self._exc:
            raise self._exc
        return self._response


class TestParse:

    def test_keeps_valid_place(self):
        places = invention._parse(json.dumps({"places": [{
            "name": "Пляж Ао Нанг",
            "description": "пляж",
            "information": "Закаты и лодки к островам.",
            "lat": 8.03, "lng": 98.82,
            "is_indoor": False,
        }]}))

        assert len(places) == 1
        assert places[0]["name"] == "Пляж Ао Нанг"
        assert places[0]["lat"] == 8.03

    def test_drops_impossible_coordinates(self):
        """
        Координаты вне диапазона — признак того, что модель их досочинила.

        Место остаётся (название модель помнит лучше), но без точки: пусть
        лучше не встанет на карту, чем встанет посреди океана.
        """
        places = invention._parse(json.dumps({"places": [
            {"name": "Место А", "lat": 999, "lng": 10},
            {"name": "Место Б", "lat": 10, "lng": None},
        ]}))

        assert [p["lat"] for p in places] == [None, None]
        assert [p["lng"] for p in places] == [None, None]

    def test_drops_nameless_and_duplicates(self):
        places = invention._parse(json.dumps({"places": [
            {"name": "Рынок", "lat": 1, "lng": 1},
            {"name": "рынок", "lat": 2, "lng": 2},
            {"name": "   "},
            {},
        ]}))

        assert len(places) == 1

    def test_empty_answer_is_not_an_error(self):
        """Модель не знает города — пустой список, а не исключение."""
        assert invention._parse(json.dumps({"places": []})) == []
        assert invention._parse(None) == []


class TestInventCityPois:

    async def test_returns_places_from_model(self, monkeypatch):
        client = _FakeClient(response=_response({"places": [
            {"name": "Храм Ват Тхам Сыа", "lat": 8.12, "lng": 98.92},
        ]}))
        monkeypatch.setattr(invention, "gen_client", client)

        places = await invention.invent_city_pois("Краби", "Таиланд")

        assert len(places) == 1
        assert client.calls == 1

    async def test_provider_failure_returns_empty_not_raises(self, monkeypatch):
        """
        Отказ провайдера — это «город остался без мест», а не 500.

        Вызов живёт в фоновой задаче: упасть ей некуда, а человек должен
        получить внятное сообщение на генерации, а не оборванный запрос.
        """
        monkeypatch.setattr(
            invention, "gen_client", _FakeClient(exc=RuntimeError("провайдер лёг"))
        )

        assert await invention.invent_city_pois("Краби", "Таиланд") == []
