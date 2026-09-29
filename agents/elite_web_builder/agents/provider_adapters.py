"""
Multi-provider LLM adapter layer.

Provides a uniform interface for calling different LLM providers:
- Anthropic (Claude Opus/Sonnet/Haiku)
- Google (Gemini 3 Pro/Flash)
- OpenAI (GPT-4o)
- xAI (Grok-3) — OpenAI-compatible API

Each adapter translates from our canonical LLMMessage format to the
provider's native API. All adapters are stateless and side-effect free
(they create clients lazily but don't store responses).

Usage:
    adapter = get_adapter("anthropic")
    response = await adapter.call(
        model="claude-sonnet-4-6",
        messages=[LLMMessage(role="user", content="Hello")],
    )
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Protocol

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Proxy fix: force HTTP proxy for httpx-based SDKs (Anthropic, OpenAI)
#
# Problem: ALL_PROXY=socks5h://... causes httpx to hang because SOCKS5
# tunneling is unreliable. Anthropic + OpenAI SDKs use httpx under the hood.
# Google Gemini uses urllib (stdlib) which ignores ALL_PROXY — it just works.
#
# Fix: create a custom httpx.Client with HTTP proxy only (no SOCKS).
# ---------------------------------------------------------------------------


def _make_httpx_client(timeout: float = 600.0) -> Any:
    """Create an httpx.Client using HTTP proxy, bypassing SOCKS.

    Args:
        timeout: Request timeout in seconds. Default 600s matches the
                 Anthropic SDK default for long-running requests.
                 See: https://docs.anthropic.com/en/api/errors#long-requests
    """
    import httpx

    http_proxy = (
        os.getenv("HTTPS_PROXY")
        or os.getenv("HTTP_PROXY")
        or os.getenv("https_proxy")
        or os.getenv("http_proxy")
    )

    transport = None
    if http_proxy and not http_proxy.startswith("socks"):
        transport = httpx.HTTPTransport(proxy=http_proxy)

    return httpx.Client(
        timeout=timeout,
        transport=transport,
    )


# ---------------------------------------------------------------------------
# Canonical data models (frozen / immutable)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LLMMessage:
    """A single message in a conversation."""

    role: str  # "system", "user", "assistant"
    content: str


@dataclass(frozen=True)
class LLMResponse:
    """Response from an LLM provider."""

    text: str
    provider: str
    model: str
    usage: dict[str, int]  # input_tokens, output_tokens


# ---------------------------------------------------------------------------
# Provider adapter protocol
# ---------------------------------------------------------------------------


class ProviderAdapter(Protocol):
    """Interface that all provider adapters must implement."""

    async def call(self, model: str, messages: list[LLMMessage]) -> LLMResponse: ...


# ---------------------------------------------------------------------------
# Anthropic adapter
# ---------------------------------------------------------------------------


class AnthropicAdapter:
    """Adapter for Anthropic's Messages API (Claude models)."""

    def _get_client(self) -> Any:
        """Lazy client creation — import only when needed.

        Uses custom httpx.Client to bypass SOCKS proxy issues.
        Timeout set to 600s (Anthropic SDK default) for Opus responses.
        """
        import anthropic

        return anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            http_client=_make_httpx_client(timeout=600.0),
        )

    async def call(self, model: str, messages: list[LLMMessage]) -> LLMResponse:
        """Call Anthropic Messages API via streaming.

        Anthropic requires system prompt as a separate parameter,
        not in the messages array. Uses streaming to keep the connection
        alive during long generation (prevents idle-connection timeouts).
        See: https://docs.anthropic.com/en/api/errors#long-requests
        """
        client = self._get_client()

        # Separate system from conversation messages
        system_text = ""
        conversation = []
        for msg in messages:
            if msg.role == "system":
                system_text = msg.content
            else:
                conversation.append({"role": msg.role, "content": msg.content})

        kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": 16384,
            "messages": conversation,
        }
        if system_text:
            kwargs["system"] = system_text

        # Stream to prevent idle-connection timeout on long responses.
        # get_final_message() collects the full response after streaming
        # completes — same object shape as create().
        with client.messages.stream(**kwargs) as stream:
            response = stream.get_final_message()

        return LLMResponse(
            text=response.content[0].text,
            provider="anthropic",
            model=model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        )


# ---------------------------------------------------------------------------
# Google adapter (Gemini REST)
# ---------------------------------------------------------------------------


_GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class GoogleAdapter:
    """Adapter for Google Gemini API via REST."""

    async def _call_gemini_rest(self, model: str, contents: list[dict[str, Any]]) -> dict[str, Any]:
        """Call Gemini REST API directly (avoids SDK import issues).

        Uses explicit HTTP proxy handler to bypass SOCKS proxy that
        causes '403 Forbidden' tunnel errors with urllib.
        """
        import urllib.request

        api_key = os.getenv("GEMINI_API_KEY", "")
        url = f"{_GEMINI_BASE}/{model}:generateContent?key={api_key}"

        payload = json.dumps({"contents": contents}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        # Build opener with explicit HTTP proxy (bypass SOCKS)
        http_proxy = (
            os.getenv("HTTPS_PROXY")
            or os.getenv("HTTP_PROXY")
            or os.getenv("https_proxy")
            or os.getenv("http_proxy")
        )
        if http_proxy and not http_proxy.startswith("socks"):
            proxy_handler = urllib.request.ProxyHandler(
                {
                    "https": http_proxy,
                    "http": http_proxy,
                }
            )
            opener = urllib.request.build_opener(proxy_handler)
        else:
            # No SOCKS — use default opener (no proxy)
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

        with opener.open(req, timeout=300) as resp:
            return json.loads(resp.read().decode("utf-8"))

    async def call(self, model: str, messages: list[LLMMessage]) -> LLMResponse:
        """Call Gemini API.

        Gemini uses a different message format: system instruction is
        prepended to the first user message as context.
        """
        # Build Gemini contents array
        system_text = ""
        contents: list[dict[str, Any]] = []

        for msg in messages:
            if msg.role == "system":
                system_text = msg.content
            else:
                role = "user" if msg.role == "user" else "model"
                text = msg.content
                # Prepend system to first user message
                if role == "user" and system_text and not contents:
                    text = f"{system_text}\n\n---\n\n{text}"
                contents.append(
                    {
                        "role": role,
                        "parts": [{"text": text}],
                    }
                )

        response = await self._call_gemini_rest(model, contents)

        candidates = response.get("candidates", [])
        if not candidates:
            raise ValueError("Gemini returned empty candidates")

        text = candidates[0]["content"]["parts"][0]["text"]
        usage_meta = response.get("usageMetadata", {})

        return LLMResponse(
            text=text,
            provider="google",
            model=model,
            usage={
                "input_tokens": usage_meta.get("promptTokenCount", 0),
                "output_tokens": usage_meta.get("candidatesTokenCount", 0),
            },
        )


# ---------------------------------------------------------------------------
# OpenAI adapter
# ---------------------------------------------------------------------------


class OpenAIAdapter:
    """Adapter for OpenAI Chat Completions API."""

    def _get_client(self) -> Any:
        """Lazy client creation.

        Uses custom httpx.Client to bypass SOCKS proxy issues.
        """
        import openai

        return openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            http_client=_make_httpx_client(timeout=300.0),
            max_retries=0,  # Runtime owns provider fallback; no hidden SDK retries.
        )

    async def call(
        self,
        model: str,
        messages: list[LLMMessage],
        *,
        max_tokens: int = 16384,
        temperature: float | None = None,
        **settings: Any,
    ) -> LLMResponse:
        """Call OpenAI Chat Completions API."""
        from skyyrose.core.openai_settings import chat_settings

        options = chat_settings(model, max_tokens, temperature, settings, default_temperature=None)

        oai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        def request():
            client = self._get_client()
            try:
                return client.chat.completions.create(model=model, messages=oai_messages, **options)
            finally:
                client.close()

        response = await asyncio.to_thread(request)
        if response.choices[0].finish_reason != "stop":
            raise ValueError("OpenAI returned incomplete output")

        return LLMResponse(
            text=response.choices[0].message.content,
            provider="openai",
            model=model,
            usage={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            },
        )


# ---------------------------------------------------------------------------
# xAI adapter (OpenAI-compatible)
# ---------------------------------------------------------------------------


class XAIAdapter:
    """Adapter for xAI's Grok API (OpenAI-compatible endpoint)."""

    BASE_URL = "https://api.x.ai/v1"

    def _get_client(self) -> Any:
        """Lazy client creation with xAI base URL.

        Uses custom httpx.Client to bypass SOCKS proxy issues.
        """
        import openai

        return openai.OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url=self.BASE_URL,
            http_client=_make_httpx_client(timeout=300.0),
        )

    async def call(self, model: str, messages: list[LLMMessage]) -> LLMResponse:
        """Call xAI's OpenAI-compatible API."""
        client = self._get_client()

        oai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        response = client.chat.completions.create(
            model=model,
            messages=oai_messages,
            max_tokens=16384,
        )

        return LLMResponse(
            text=response.choices[0].message.content,
            provider="xai",
            model=model,
            usage={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            },
        )


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_ADAPTERS: dict[str, type] = {
    "anthropic": AnthropicAdapter,
    "google": GoogleAdapter,
    "openai": OpenAIAdapter,
    "xai": XAIAdapter,
}


def get_adapter(provider: str) -> ProviderAdapter:
    """Get the adapter for a given provider name.

    Args:
        provider: One of "anthropic", "google", "openai", "xai"

    Returns:
        An instance of the appropriate ProviderAdapter

    Raises:
        ValueError: If provider is unknown
    """
    adapter_cls = _ADAPTERS.get(provider)
    if adapter_cls is None:
        raise ValueError(f"Unknown provider: '{provider}'. Available: {sorted(_ADAPTERS.keys())}")
    return adapter_cls()
