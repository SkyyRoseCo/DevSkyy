"""Real provider serializers with HTTP transport fixtures; no external calls."""

import asyncio
import json

import httpx
import pytest

from llm.base import ModelProvider
from orchestration.provider_execution import RouterAdapter


@pytest.mark.parametrize(
    "provider",
    ["openai", "anthropic", "google", "mistral", "cohere", "groq", "deepseek"],
)
def test_router_uses_exact_adapter_and_bounded_output(provider):
    async def scenario():
        adapter = RouterAdapter()
        client = adapter.router._get_client(ModelProvider(provider))
        model = adapter.router.configs[ModelProvider(provider)].default_model
        calls = []
        output = json.dumps({"action": "final", "output": "transport fixture"})
        common = {
            "model": "fixture-model",
            "choices": [{"message": {"content": output}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 3, "completion_tokens": 4},
        }
        fixtures = {
            "anthropic": {
                "model": "fixture-model",
                "content": [{"type": "text", "text": output}],
                "usage": {"input_tokens": 3, "output_tokens": 4},
                "stop_reason": "end_turn",
            },
            "google": {
                "candidates": [{"content": {"parts": [{"text": output}]}, "finishReason": "STOP"}],
                "usageMetadata": {"promptTokenCount": 3, "candidatesTokenCount": 4},
            },
            "cohere": {
                "text": output,
                "generation_id": "fixture",
                "meta": {"tokens": {"input_tokens": 3, "output_tokens": 4}},
                "finish_reason": "COMPLETE",
            },
        }

        def respond(req):
            calls.append(json.loads(req.content))
            return httpx.Response(200, json=fixtures.get(provider, common))

        client._client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
        try:
            result = await adapter.complete(
                provider,
                model,
                [
                    {"role": "system", "content": "Mission protocol"},
                    {"role": "user", "content": "Mission input"},
                ],
                128,
            )
            assert json.loads(result["content"])["output"] == "transport fixture"
            assert len(calls) == 1 and client.max_retries == 1
            request = calls[0]
            cap = request.get("max_tokens", request.get("max_completion_tokens"))
            if provider == "google":
                cap = request["generationConfig"]["maxOutputTokens"]
            assert cap == 128
        finally:
            await adapter.close()

    asyncio.run(scenario())


def test_failure_makes_one_http_attempt():
    async def scenario():
        adapter = RouterAdapter()
        client = adapter.router._get_client(ModelProvider.OPENAI)
        calls = []

        def fail(req):
            calls.append(req)
            return httpx.Response(500, json={"error": {"message": "fixture failure"}})

        client._client = httpx.AsyncClient(transport=httpx.MockTransport(fail))
        try:
            with pytest.raises(Exception):
                await adapter.complete(
                    "openai",
                    adapter.router.configs[ModelProvider.OPENAI].default_model,
                    [{"role": "user", "content": "mission"}],
                    128,
                )
            assert len(calls) == 1
        finally:
            await adapter.close()

    asyncio.run(scenario())


def test_real_registry_executes_allowlisted_read_only_once(monkeypatch):
    from core.runtime.tool_registry import (
        ToolCategory,
        ToolRegistry,
        ToolSeverity,
        ToolSpec,
    )
    from orchestration.provider_execution import RegistryTools, RunError

    registry = ToolRegistry()
    monkeypatch.setattr(ToolRegistry, "_instance", registry)
    monkeypatch.setenv("GODMODE_ALLOWED_TOOLS", "fixture_read,fixture_write")
    calls = []

    async def read():
        calls.append("read")
        return {"value": "actual registry handler"}

    registry.register(
        ToolSpec(
            name="fixture_read",
            description="Read test evidence",
            category=ToolCategory.SYSTEM,
            severity=ToolSeverity.READ_ONLY,
        ),
        read,
    )
    registry.register(
        ToolSpec(
            name="fixture_write",
            description="Write test evidence",
            category=ToolCategory.SYSTEM,
            severity=ToolSeverity.HIGH,
        ),
        read,
    )
    tools = RegistryTools("owner")
    assert tools.specs(["fixture_read"])[0]["name"] == "fixture_read"
    result = asyncio.run(tools.execute("fixture_read", {}))
    assert result["success"] is True and calls == ["read"]
    with pytest.raises(RunError):
        tools.specs(["fixture_write"])
    with pytest.raises(RunError):
        tools.specs(["shell"])


def test_litellm_gateway_preserves_model_and_disables_retry():
    from types import SimpleNamespace

    async def scenario():
        adapter = RouterAdapter()
        client = adapter.router._get_client(ModelProvider.LITELLM)
        calls = []

        async def completion(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(
                usage=SimpleNamespace(prompt_tokens=3, completion_tokens=4),
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content='{"action":"final","output":"gateway fixture"}'
                        ),
                        finish_reason="stop",
                    )
                ],
            )

        client._litellm = SimpleNamespace(acompletion=completion)
        try:
            result = await adapter.complete(
                "litellm",
                "configured/model",
                [{"role": "user", "content": "mission"}],
                128,
            )
            assert result["model"] == "configured/model"
            assert len(calls) == 1 and calls[0]["num_retries"] == 0
        finally:
            await adapter.close()

    asyncio.run(scenario())


def test_provider_enablement_is_isolated_between_missions():
    from llm.router import PROVIDER_CONFIGS, LLMRouter

    first = LLMRouter()
    second = LLMRouter()
    first.disable_provider(ModelProvider.OPENAI)
    assert ModelProvider.OPENAI not in first.get_available_providers()
    assert ModelProvider.OPENAI in second.get_available_providers()
    assert ModelProvider.OPENAI in LLMRouter().get_available_providers()
    assert PROVIDER_CONFIGS[ModelProvider.OPENAI].enabled


def test_explicit_provider_config_is_not_mutated():
    from llm.router import PROVIDER_CONFIGS, LLMRouter

    supplied = {ModelProvider.OPENAI: PROVIDER_CONFIGS[ModelProvider.OPENAI]}
    router = LLMRouter(configs=supplied)
    router.disable_provider(ModelProvider.OPENAI)
    assert supplied[ModelProvider.OPENAI].enabled
    assert LLMRouter(configs={}).get_available_providers() == []
