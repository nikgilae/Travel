"""
Тесты app.services.poi_description (Итерация 4, RAG-POI-PLAN.md).

Никакой сетевой активности — app.services.ai.client.chat.completions.create
подменяется моком (тот же общий chat-клиент, что и у /chat, отдельного
клиента здесь не заводим — не критический путь, батч-скрипт).
"""
import httpx
from unittest.mock import AsyncMock

from openai import APIConnectionError, AuthenticationError

import app.services.poi_description as poi_description_module
from app.services.poi_description import (
    MAX_SUMMARY_ATTEMPTS,
    build_ai_description,
    summarize_reviews,
)


def _fake_completion(content: str):
    return type(
        "FakeCompletion", (),
        {
            "choices": [
                type(
                    "FakeChoice", (),
                    {"message": type("FakeMessage", (), {"content": content})()},
                )()
            ]
        },
    )()


class TestSummarizeReviews:
    async def test_empty_reviews_returns_none_without_call(self, monkeypatch):
        mock_create = AsyncMock()
        monkeypatch.setattr(poi_description_module.client.chat.completions, "create", mock_create)

        result = await summarize_reviews([])

        assert result is None
        mock_create.assert_not_awaited()

    async def test_success_returns_stripped_summary(self, monkeypatch):
        mock_create = AsyncMock(return_value=_fake_completion("  Уютное место с хорошей кухней.  "))
        monkeypatch.setattr(poi_description_module.client.chat.completions, "create", mock_create)

        result = await summarize_reviews(["Отличная кухня", "Уютно"])

        assert result == "Уютное место с хорошей кухней."
        mock_create.assert_awaited_once()

    async def test_prompt_instructs_no_hallucination(self, monkeypatch):
        mock_create = AsyncMock(return_value=_fake_completion("ok"))
        monkeypatch.setattr(poi_description_module.client.chat.completions, "create", mock_create)

        await summarize_reviews(["Отзыв"])

        messages = mock_create.call_args.kwargs["messages"]
        system_message = messages[0]["content"]
        assert "ТОЛЬКО факты" in system_message
        assert "не придумывай" in system_message

    async def test_caps_at_five_reviews(self, monkeypatch):
        mock_create = AsyncMock(return_value=_fake_completion("ok"))
        monkeypatch.setattr(poi_description_module.client.chat.completions, "create", mock_create)

        await summarize_reviews([f"Отзыв {i}" for i in range(10)])

        user_message = mock_create.call_args.kwargs["messages"][1]["content"]
        assert "Отзыв 4" in user_message
        assert "Отзыв 5" not in user_message

    async def test_retries_on_retryable_error_then_succeeds(self, monkeypatch):
        mock_create = AsyncMock(
            side_effect=[APIConnectionError(request=None), _fake_completion("ok")]
        )
        monkeypatch.setattr(poi_description_module.client.chat.completions, "create", mock_create)

        result = await summarize_reviews(["Отзыв"])

        assert result == "ok"
        assert mock_create.await_count == 2

    async def test_returns_none_after_exhausting_retries(self, monkeypatch):
        mock_create = AsyncMock(side_effect=APIConnectionError(request=None))
        monkeypatch.setattr(poi_description_module.client.chat.completions, "create", mock_create)

        result = await summarize_reviews(["Отзыв"])

        assert result is None
        assert mock_create.await_count == MAX_SUMMARY_ATTEMPTS

    async def test_non_retryable_error_returns_none_immediately(self, monkeypatch):
        error = AuthenticationError(
            message="invalid key",
            response=httpx.Response(status_code=401, request=httpx.Request("POST", "https://x")),
            body=None,
        )
        mock_create = AsyncMock(side_effect=error)
        monkeypatch.setattr(poi_description_module.client.chat.completions, "create", mock_create)

        result = await summarize_reviews(["Отзыв"])

        assert result is None
        mock_create.assert_awaited_once()


class TestBuildAiDescription:
    async def test_prefers_editorial_summary(self, monkeypatch):
        mock_summarize = AsyncMock(return_value="не должно вызываться")
        monkeypatch.setattr(poi_description_module, "summarize_reviews", mock_summarize)

        text, source = await build_ai_description(
            {"editorial_summary": "Курируемый текст Google", "reviews": ["что-то"]},
            fallback_description="Категория",
        )

        assert text == "Курируемый текст Google"
        assert source == "google_editorial"
        mock_summarize.assert_not_awaited()

    async def test_falls_back_to_reviews_summary(self, monkeypatch):
        mock_summarize = AsyncMock(return_value="Саммари отзывов")
        monkeypatch.setattr(poi_description_module, "summarize_reviews", mock_summarize)

        text, source = await build_ai_description(
            {"editorial_summary": None, "reviews": ["Отзыв 1"]},
            fallback_description="Категория",
        )

        assert text == "Саммари отзывов"
        assert source == "reviews_summary"

    async def test_falls_back_to_category_when_reviews_summary_fails(self, monkeypatch):
        mock_summarize = AsyncMock(return_value=None)
        monkeypatch.setattr(poi_description_module, "summarize_reviews", mock_summarize)

        text, source = await build_ai_description(
            {"editorial_summary": None, "reviews": ["Отзыв 1"]},
            fallback_description="Категория",
        )

        assert text == "Категория"
        assert source == "category_fallback"

    async def test_falls_back_to_category_without_editorial_or_reviews(self, monkeypatch):
        mock_summarize = AsyncMock()
        monkeypatch.setattr(poi_description_module, "summarize_reviews", mock_summarize)

        text, source = await build_ai_description(
            {"editorial_summary": None, "reviews": []},
            fallback_description="Категория",
        )

        assert text == "Категория"
        assert source == "category_fallback"
        mock_summarize.assert_not_awaited()
