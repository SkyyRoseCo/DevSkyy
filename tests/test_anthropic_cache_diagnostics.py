"""Tests for Anthropic cache diagnostics on AnthropicClient.complete().

Cache diagnostics is opt-in per request: the client sends a ``diagnostics``
object only when the caller asks, and surfaces the API's ``diagnostics``
result in ``CompletionResponse.metadata``. The HTTP call is replaced by a
fake ``_make_request`` that records the request body, so these tests check
the exact payload and the parsing of each documented response shape.
"""

from __future__ import annotations

import logging

import pytest

from llm.base import Message
from llm.providers.anthropic import AnthropicClient


def _api_result(diagnostics: object = None, *, include_diagnostics: bool = True) -> dict:
    result = {
        "id": "msg_02New",
        "content": [{"type": "text", "text": "ok"}],
        "usage": {"input_tokens": 42, "output_tokens": 10, "cache_read_input_tokens": 0},
        "stop_reason": "end_turn",
    }
    if include_diagnostics:
        result["diagnostics"] = diagnostics
    return result


async def _complete(monkeypatch, result: dict, **kwargs):
    client = AnthropicClient(api_key="test-key")
    captured: dict = {}

    class FakeResponse:
        def json(self):
            return result

    async def fake_make_request(method, url, **request_kwargs):
        captured["json"] = request_kwargs.get("json")
        return FakeResponse()

    monkeypatch.setattr(client, "_make_request", fake_make_request)
    response = await client.complete(
        messages=[Message.system("Brand DNA context."), Message.user("Summarize.")],
        **kwargs,
    )
    return captured["json"], response


@pytest.mark.asyncio
class TestRequestPayload:
    async def test_not_sent_by_default(self, monkeypatch):
        body, response = await _complete(monkeypatch, _api_result(include_diagnostics=False))

        assert "diagnostics" not in body
        assert "cache_diagnostics_status" not in response.metadata
        assert "cache_miss_reason" not in response.metadata

    async def test_first_turn_opts_in_with_null_previous_id(self, monkeypatch):
        body, _ = await _complete(monkeypatch, _api_result(None), cache_diagnostics=True)

        assert body["diagnostics"] == {"previous_message_id": None}

    async def test_previous_message_id_is_sent(self, monkeypatch):
        body, _ = await _complete(monkeypatch, _api_result(None), previous_message_id="msg_01Prev")

        assert body["diagnostics"] == {"previous_message_id": "msg_01Prev"}

    async def test_message_id_always_in_metadata(self, monkeypatch):
        _, response = await _complete(monkeypatch, _api_result(include_diagnostics=False))

        assert response.metadata["message_id"] == "msg_02New"


@pytest.mark.asyncio
class TestResponseParsing:
    async def test_null_means_no_divergence(self, monkeypatch):
        _, response = await _complete(
            monkeypatch, _api_result(None), previous_message_id="msg_01Prev"
        )

        assert response.metadata["cache_diagnostics_status"] == "no_divergence"
        assert response.metadata["cache_miss_reason"] is None

    async def test_null_on_first_turn_means_not_compared(self, monkeypatch):
        _, response = await _complete(monkeypatch, _api_result(None), cache_diagnostics=True)

        assert response.metadata["cache_diagnostics_status"] == "not_compared"
        assert response.metadata["cache_miss_reason"] is None

    async def test_null_reason_means_pending(self, monkeypatch):
        _, response = await _complete(
            monkeypatch, _api_result({"cache_miss_reason": None}), previous_message_id="msg_01Prev"
        )

        assert response.metadata["cache_diagnostics_status"] == "pending"
        assert response.metadata["cache_miss_reason"] is None

    async def test_changed_reason_is_reported_and_warned(self, monkeypatch, caplog):
        reason = {"type": "system_changed", "cache_missed_input_tokens": 41850}

        with caplog.at_level(logging.WARNING, logger="llm.providers.anthropic"):
            _, response = await _complete(
                monkeypatch,
                _api_result({"cache_miss_reason": reason}),
                previous_message_id="msg_01Prev",
            )

        assert response.metadata["cache_diagnostics_status"] == "reported"
        assert response.metadata["cache_miss_reason"] == reason
        assert any(
            "system_changed" in record.getMessage() and "41850" in record.getMessage()
            for record in caplog.records
            if record.levelno == logging.WARNING
        )

    @pytest.mark.parametrize("reason_type", ["previous_message_not_found", "unavailable"])
    async def test_no_comparison_reasons_are_not_warnings(self, monkeypatch, caplog, reason_type):
        reason = {"type": reason_type}

        with caplog.at_level(logging.INFO, logger="llm.providers.anthropic"):
            _, response = await _complete(
                monkeypatch,
                _api_result({"cache_miss_reason": reason}),
                previous_message_id="msg_01Prev",
            )

        assert response.metadata["cache_diagnostics_status"] == "reported"
        assert response.metadata["cache_miss_reason"] == reason
        assert not [r for r in caplog.records if r.levelno >= logging.WARNING]
        assert any(reason_type in r.getMessage() for r in caplog.records)

    async def test_cache_metrics_still_present(self, monkeypatch):
        _, response = await _complete(monkeypatch, _api_result(None), cache_diagnostics=True)

        assert response.metadata["cache_read_input_tokens"] == 0
        assert response.metadata["cache_creation_input_tokens"] == 0
