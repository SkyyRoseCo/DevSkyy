"""Request serialization and retry tests use only mocked transports."""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from llm.base import Message
from llm.providers.openai import OpenAIClient
from skyyrose.core.openai_settings import OpenAIChatSettings, chat_settings

FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "result",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {"ok": {"type": "boolean"}},
            "required": ["ok"],
            "additionalProperties": False,
        },
    },
}


@pytest.mark.parametrize("model", ["gpt-4o", "gpt-4o-mini", "gpt-4o-2024-08-06"])
def test_legacy_models_keep_defaults_and_schema(model):
    request = chat_settings(model, 512, None, {"response_format": FORMAT})
    assert request == {"temperature": 0.7, "max_tokens": 512, "response_format": FORMAT}


@pytest.mark.parametrize(
    "options",
    [
        {"reasoning_effort": "high"},
        {"verbosity": "low"},
        {"typo": True},
        {"response_format": {"type": "yaml"}},
    ],
)
@pytest.mark.parametrize("model", ["gpt-4o", "gpt-4o-mini"])
def test_unsupported_options_rejected(model, options):
    with pytest.raises(ValueError):
        chat_settings(model, 512, None, options)


def test_astra_settings_do_not_silently_drop_incompatible_values():
    result = chat_settings(
        "gpt-6-astra",
        2048,
        None,
        {"reasoning_effort": "high", "verbosity": "low", "response_format": FORMAT},
    )
    assert result["max_completion_tokens"] == 2048
    assert "temperature" not in result
    assert result["reasoning_effort"] == "high"
    with pytest.raises(ValueError):
        chat_settings("gpt-6-astra", 2048, 0.7, {})
    with pytest.raises(ValueError):
        chat_settings("gpt-6-astra", 2048, None, {"reasoning_effort": "none"})
    with pytest.raises(ValueError, match="Responses"):
        chat_settings("gpt-6-astra", 2048, None, {}, tools=[{"type": "function"}])


def test_sol_tools_only_when_reasoning_none():
    tool = {"type": "function", "function": {"name": "example"}}
    request = chat_settings(
        "gpt-6-sol", 200, 0.2, {"reasoning_effort": "none", "tool_choice": "auto"}, tools=[tool]
    )
    assert request["tools"] == [tool]
    assert request["temperature"] == 0.2
    with pytest.raises(ValueError):
        chat_settings("gpt-6-sol", 200, None, {}, tools=[tool])


@pytest.mark.parametrize("budget", [0, -1, True, 2.5])
def test_invalid_budgets(budget):
    with pytest.raises(ValueError):
        OpenAIChatSettings(max_tokens=budget).to_request("gpt-4o")


def wire_response():
    return {
        "choices": [{"message": {"content": '{"ok":true}'}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }


@pytest.mark.asyncio
async def test_http_adapter_serializes_schema_and_settings(monkeypatch):
    client = OpenAIClient(api_key="offline-test")
    transport = AsyncMock(return_value=Mock(json=lambda: wire_response()))
    monkeypatch.setattr(client, "_make_request", transport)
    result = await client.complete(
        [Message.user("JSON result")], response_format=FORMAT, max_tokens=333, top_p=0.8
    )
    body = transport.call_args.kwargs["json"]
    assert body["response_format"] == FORMAT
    assert body["max_tokens"] == 333
    assert body["top_p"] == 0.8
    assert result.content == '{"ok":true}'
    transport.reset_mock()
    with pytest.raises(ValueError):
        await client.complete([Message.user("x")], verbosity="low")
    transport.assert_not_called()


@pytest.mark.asyncio
async def test_stream_forwards_settings_via_mock_http_transport():
    captured = []

    def handle(request):
        captured.append(json.loads(request.content))
        return httpx.Response(
            200,
            text='data: {"choices":[{"delta":{"content":"ok"},"finish_reason":"stop"}]}\n\ndata: [DONE]\n\n',
        )

    client = OpenAIClient(api_key="offline-test")
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handle))
    chunks = [
        chunk
        async for chunk in client.stream(
            [Message.user("JSON")], response_format=FORMAT, max_tokens=123
        )
    ]
    assert chunks[0].content == "ok"
    assert captured[0]["response_format"] == FORMAT
    assert captured[0]["max_tokens"] == 123
    await client.close()


@pytest.mark.asyncio
async def test_sdk_adapter_forwards_options_and_has_one_retry_owner(monkeypatch):
    from orchestration import llm_clients

    sdk = Mock()
    sdk.chat.completions.create = AsyncMock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="ok", tool_calls=[]), finish_reason="stop"
                )
            ],
            usage=None,
            model="gpt-4o-mini",
            model_dump=lambda: {},
        )
    )
    factory = Mock(return_value=sdk)
    monkeypatch.setattr(llm_clients, "AsyncOpenAI", factory)
    client = llm_clients.OpenAIClient(api_key="offline-test", max_retries=2)
    await client.complete([], response_format=FORMAT, max_tokens=245, top_p=0.5)
    body = sdk.chat.completions.create.call_args.kwargs
    assert body["response_format"] == FORMAT and body["top_p"] == 0.5
    assert body["max_tokens"] == 245
    assert factory.call_args.kwargs["max_retries"] == 2
    sdk.chat.completions.create.reset_mock()
    sdk.chat.completions.create.side_effect = RuntimeError("offline failure")
    with pytest.raises(RuntimeError):
        await client.complete([])
    assert sdk.chat.completions.create.call_count == 1  # no outer tenacity layer


@pytest.mark.asyncio
async def test_sdk_retry_budget_is_not_multiplied(monkeypatch):
    from openai import AsyncOpenAI, RateLimitError

    from orchestration.llm_clients import OpenAIClient as SDKClient

    attempts = []

    def rate_limited(request):
        attempts.append(request)
        return httpx.Response(
            429,
            json={
                "error": {
                    "message": "offline rate limit",
                    "type": "rate_limit_error",
                    "code": "rate_limit",
                }
            },
            headers={"retry-after-ms": "1"},
        )

    sdk = AsyncOpenAI(
        api_key="offline-test",
        max_retries=1,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(rate_limited)),
    )
    adapter = object.__new__(SDKClient)
    adapter._client = sdk
    try:
        with pytest.raises(RateLimitError):
            await adapter.complete([])
        assert len(attempts) == 2  # initial + one retry, not an outer 3x loop
    finally:
        await adapter.close()


@pytest.mark.asyncio
async def test_raw_http_retry_budget(monkeypatch):
    from llm.exceptions import ServiceUnavailableError

    attempts = []

    def unavailable(request):
        attempts.append(request)
        return httpx.Response(503, json={"error": "offline"})

    client = OpenAIClient(api_key="offline-test", max_retries=2)
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(unavailable))
    monkeypatch.setattr("llm.base.asyncio.sleep", AsyncMock())
    try:
        with pytest.raises(ServiceUnavailableError):
            await client.complete([Message.user("fixture")])
        assert len(attempts) == 2  # legacy raw client max_retries counts total attempts
    finally:
        await client.close()
