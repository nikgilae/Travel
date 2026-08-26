"""
Регрессионные тесты уровня app.services.ai.generate_trip.

Покрывают «честные ошибки» коммита 1: детект обрезки/битого JSON, разделение
retryable/не-retryable сбоев провайдера, бюджет времени и масштабирование
max_tokens под длину поездки. Никакой сетевой активности — AI-клиент подменён
фикстурой `mock_gen_ai` (patches app.services.ai.gen_client, отдельный объект
от чатового app.services.ai.client).
"""
import asyncio
import json
import time

import httpx
import pytest
from openai import AuthenticationError, BadRequestError, APITimeoutError

import app.services.ai as ai_module
from app.config import settings
from app.core.exceptions import AIGenerationError
from app.services.ai import generate_trip
from tests.conftest import make_completion, FakeEmptyChoicesCompletion


def _pois() -> list[dict]:
    return [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "name": "Музей",
            "description": "Городской музей",
            "rules": [],
        },
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "name": "Парк",
            "description": "Центральный парк",
            "rules": [],
        },
    ]


def _valid_payload(days: int = 1) -> str:
    """Валидный ответ AI на заданное число дней."""
    return json.dumps({
        "summary": "Отличная поездка",
        "total_budget_estimate": "500$",
        "days": [
            {
                "day": d,
                "theme": f"День {d}",
                "main_pois": [
                    {
                        "poi_id": "11111111-1111-1111-1111-111111111111",
                        "name": "Музей",
                        "start_time": "10:00",
                        "duration_hours": 2.0,
                        "budget_estimate": "0",
                        "ai_tip": "Идите утром",
                        "activity_level": 3,
                    },
                ],
                "additional_pois": [
                    {
                        "poi_id": "22222222-2222-2222-2222-222222222222",
                        "name": "Парк",
                        "start_time": "14:00",
                        "duration_hours": 1.0,
                        "budget_estimate": "0",
                        "ai_tip": "Отдохните",
                        "activity_level": 1,
                    },
                ],
            }
            for d in range(1, days + 1)
        ],
    })


async def _call(days: int = 1, **overrides) -> dict:
    kwargs = dict(
        city_name="Токио",
        country_name="Япония",
        days=days,
        purpose="leisure",
        budget="medium",
        group_size=2,
        interests=["культура"],
        pois=_pois(),
        city_rules=[],
        notes=None,
        fast=False,
    )
    kwargs.update(overrides)
    return await generate_trip(**kwargs)


def _fake_request() -> httpx.Request:
    return httpx.Request("POST", "https://example.test/v1/chat/completions")


def _fake_response(status_code: int) -> httpx.Response:
    return httpx.Response(
        status_code,
        request=_fake_request(),
        json={"error": {"message": "boom"}},
    )


class TestGenerateTripHonestErrors:
    """Пункты 1-8 и 13 из чек-листа T8: см. docstring модуля."""

    async def test_valid_json_returns_parsed_result_with_single_call(self, mock_gen_ai):
        """П.1 (часть): валидный JSON парсится с первой попытки, лишних вызовов нет."""
        mock_gen_ai.queue = [make_completion(content=_valid_payload(days=1))]

        result = await _call(days=1)

        assert result["days"][0]["day"] == 1
        assert result["summary"] == "Отличная поездка"
        assert len(mock_gen_ai.calls) == 1

    async def test_retries_after_malformed_json_then_succeeds(self, mock_gen_ai):
        """П.2: битый JSON на попытке 1, валидный на попытке 2 → успех, ровно 2 вызова."""
        mock_gen_ai.queue = [
            make_completion(content="это не json, а мусор"),
            make_completion(content=_valid_payload(days=1)),
        ]

        result = await _call(days=1)

        assert result["days"][0]["day"] == 1
        assert len(mock_gen_ai.calls) == 2

    async def test_malformed_json_both_attempts_raises_ai_generation_error(self, mock_gen_ai):
        """П.3: битый JSON на всех попытках → AIGenerationError, retryable, попытки исчерпаны."""
        mock_gen_ai.queue = [
            make_completion(content=f"мусор номер {i}")
            for i in range(ai_module.MAX_AI_ATTEMPTS)
        ]

        with pytest.raises(AIGenerationError) as exc_info:
            await _call(days=1)

        assert exc_info.value.retryable is True
        assert len(mock_gen_ai.calls) == ai_module.MAX_AI_ATTEMPTS

    async def test_empty_days_list_is_not_treated_as_success(self, mock_gen_ai):
        """
        П.4 — КЛЮЧЕВАЯ регрессия коммита: {"days": []} должен провалиться,
        а не молча вернуться как «успешный» пустой план.
        """
        empty_payload = json.dumps({
            "summary": "ok", "total_budget_estimate": "0", "days": [],
        })
        mock_gen_ai.queue = [
            make_completion(content=empty_payload)
            for _ in range(ai_module.MAX_AI_ATTEMPTS)
        ]

        with pytest.raises(AIGenerationError):
            await _call(days=1)

        assert len(mock_gen_ai.calls) == ai_module.MAX_AI_ATTEMPTS

    async def test_empty_choices_and_none_content_raises_ai_error_not_crash(self, mock_gen_ai):
        """П.5: choices == [] (content недостижим) → AIGenerationError, а не 500/AttributeError."""
        mock_gen_ai.queue = [
            FakeEmptyChoicesCompletion() for _ in range(ai_module.MAX_AI_ATTEMPTS)
        ]

        with pytest.raises(AIGenerationError):
            await _call(days=1)

        assert len(mock_gen_ai.calls) == ai_module.MAX_AI_ATTEMPTS

    async def test_timeout_all_attempts_raises_after_exhausting_them(self, mock_gen_ai):
        """П.6: APITimeoutError на всех попытках → AIGenerationError, попытки исчерпаны, быстро."""
        req = _fake_request()
        mock_gen_ai.queue = [
            APITimeoutError(request=req) for _ in range(ai_module.MAX_AI_ATTEMPTS)
        ]

        started = time.perf_counter()
        with pytest.raises(AIGenerationError):
            await _call(days=1)
        elapsed = time.perf_counter() - started

        assert len(mock_gen_ai.calls) == ai_module.MAX_AI_ATTEMPTS
        # Ошибки подняты мгновенно (не настоящий сетевой таймаут) — бюджет не тратится.
        assert elapsed < settings.AI_GENERATION_BUDGET_SECONDS

    async def test_stops_retrying_when_budget_exhausted(self, mock_gen_ai, monkeypatch):
        """
        П.7: бюджет почти исчерпан после первой попытки → вторая попытка не
        стартует вовсе (create вызван один раз). Ветка выхода по бюджету.
        """
        monkeypatch.setattr(settings, "AI_GENERATION_BUDGET_SECONDS", 0.05)

        async def _slow_then_malformed(*args, **kwargs):
            await asyncio.sleep(0.1)  # съедает весь мини-бюджет
            raise json.JSONDecodeError("bad json", "doc", 0)

        mock_gen_ai.queue = [_slow_then_malformed]

        with pytest.raises(AIGenerationError):
            await _call(days=1)

        assert len(mock_gen_ai.calls) == 1

    async def test_nonretryable_provider_error_immediate_502_not_retryable(self, mock_gen_ai):
        """П.8: AuthenticationError — не сетевой сбой, повтор не поможет → 1 вызов, retryable=False."""
        mock_gen_ai.queue = [
            AuthenticationError("invalid api key", response=_fake_response(401), body=None),
        ]

        with pytest.raises(AIGenerationError) as exc_info:
            await _call(days=1)

        assert exc_info.value.retryable is False
        assert len(mock_gen_ai.calls) == 1

    async def test_bad_request_provider_error_immediate_502_not_retryable(self, mock_gen_ai):
        """П.8 (вторая ошибка того же класса): BadRequestError — тоже неповторяемая."""
        mock_gen_ai.queue = [
            BadRequestError("prompt too long", response=_fake_response(400), body=None),
        ]

        with pytest.raises(AIGenerationError) as exc_info:
            await _call(days=1)

        assert exc_info.value.retryable is False
        assert len(mock_gen_ai.calls) == 1

    async def test_max_tokens_scales_with_trip_length(self, mock_gen_ai):
        """
        П.13: 12-дневная поездка → max_tokens = 1500 + 1100*12 = 14700.
        Страховка от регрессии потолка в 8000 (9-дневные поездки становились
        негенерируемыми).
        """
        mock_gen_ai.queue = [make_completion(content=_valid_payload(days=12))]

        await _call(days=12)

        assert mock_gen_ai.calls[-1]["max_tokens"] == 14700

    async def test_truncated_response_finish_reason_length_not_retryable(self, mock_gen_ai):
        """
        Доп.: finish_reason == "length" — модель упёрлась в потолок токенов,
        повтор с теми же параметрами воспроизведёт ту же обрезку → 1 вызов,
        retryable=False. Без этого теста детект обрезки легко откатят.
        """
        truncated = make_completion(
            content='{"summary": "s", "days": [{"day": 1, "theme": "t", '
                    '"main_pois": [], "additional_pois": []}]}',
            finish_reason="length",
        )
        mock_gen_ai.queue = [truncated]

        with pytest.raises(AIGenerationError) as exc_info:
            await _call(days=1)

        assert exc_info.value.retryable is False
        assert len(mock_gen_ai.calls) == 1

    async def test_fewer_days_than_requested_is_treated_as_failure(self, mock_gen_ai):
        """Доп.: AI вернул меньше дней, чем запрошено — это брак, а не успех."""
        payload = _valid_payload(days=1)  # запросим 3 дня, а получим 1
        mock_gen_ai.queue = [
            make_completion(content=payload) for _ in range(ai_module.MAX_AI_ATTEMPTS)
        ]

        with pytest.raises(AIGenerationError):
            await _call(days=3)

        assert len(mock_gen_ai.calls) == ai_module.MAX_AI_ATTEMPTS


class TestAIClientConfiguration:
    """
    П.14: страховка от регрессии таймаутов — у чата и у генерации разные
    клиенты с разными таймаутами/ретраями (см. app/services/ai.py).
    """

    def test_chat_client_uses_generous_timeout_and_sdk_retries(self):
        assert ai_module.client.timeout.read == 60.0
        assert ai_module.client.max_retries == 2

    def test_generation_client_uses_tight_timeout_and_no_sdk_retries(self):
        assert ai_module.gen_client.timeout.read == settings.AI_READ_TIMEOUT_SECONDS
        assert ai_module.gen_client.max_retries == 0

    def test_chat_and_generation_clients_are_distinct_objects(self):
        """Регрессия ловушки T8: мок одного клиента не должен покрывать другой."""
        assert ai_module.client.chat.completions is not ai_module.gen_client.chat.completions


class TestMainPoisInterestPriorityInstruction:
    """
    Мини-фикс: промпт должен явно ограничивать долю "известных
    достопримечательностей" не по интересам в main_pois (не более одной на
    день), а не запрещать их совсем — реальный прод-кейс показал 3 из 3
    main_pois дня были музей/собор/башня при интересах food/night/relaxed,
    хотя retrieval передал AI релевантные food/night места (RAG-POI-PLAN.md).
    """

    async def _sent_prompt(self, mock_gen_ai, **overrides) -> str:
        mock_gen_ai.queue = [make_completion(content=_valid_payload(days=1))]
        await _call(days=1, **overrides)
        return mock_gen_ai.calls[-1]["messages"][-1]["content"]

    async def test_normal_prompt_limits_landmarks_to_one_per_day(self, mock_gen_ai):
        prompt = await self._sent_prompt(mock_gen_ai, fast=False, interests=["food", "night"])
        assert "не более" in prompt
        assert "интерес" in prompt.lower()

    async def test_fast_prompt_limits_landmarks_to_one_per_day(self, mock_gen_ai):
        prompt = await self._sent_prompt(mock_gen_ai, fast=True, interests=["food", "night"])
        assert "не более" in prompt
        assert "интерес" in prompt.lower()

    async def test_prompt_mentions_declared_interests_verbatim(self, mock_gen_ai):
        """Инструкция должна ссылаться на реально переданные интересы, не общие слова."""
        prompt = await self._sent_prompt(mock_gen_ai, fast=False, interests=["food", "night"])
        assert "food, night" in prompt
