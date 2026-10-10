"""
OpenAI Client
=============

Client for OpenAI API (GPT-4, o1 models).

Reference: https://platform.openai.com/docs/api-reference
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

# Import config for API keys (loads .env.hf)
try:
    from config import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

from skyyrose.core.openai_settings import chat_settings

from ..base import BaseLLMClient, CompletionResponse, Message, StreamChunk, ToolCall

logger = logging.getLogger(__name__)


class OpenAIClient(BaseLLMClient):
    """
    OpenAI API Client.

    Supports: GPT-4o, GPT-4o-mini, GPT-4-turbo, o1-preview, o1-mini

    Usage:
        client = OpenAIClient()
        response = await client.complete(
            messages=[Message.user("Hello!")],
            model="gpt-4o-mini"
        )
        print(response.content)
    """

    provider = "openai"
    default_model = "gpt-4o-mini"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        organization: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            api_key=api_key or OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", ""),
            base_url=base_url,
            **kwargs,
        )
        self.organization = organization or os.getenv("OPENAI_ORGANIZATION")

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.organization:
            headers["OpenAI-Organization"] = self.organization
        return headers

    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int = 1024,
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> CompletionResponse:
        """Generate completion using OpenAI API."""
        model = model or self.default_model
        start_time = datetime.now(UTC)

        wire_tools = [{"type": "function", "function": t} for t in tools] if tools else None
        data: dict[str, Any] = {
            "model": model,
            "messages": self._messages_to_list(messages),
            **chat_settings(model, max_tokens, temperature, kwargs, tools=wire_tools),
        }

        response = await self._make_request(
            "POST",
            f"{self.base_url}/chat/completions",
            json=data,
        )

        result = response.json()
        choice = result["choices"][0]
        message = choice.get("message", {})
        usage = result.get("usage", {})

        tool_calls = []
        if message.get("tool_calls"):
            for tc in message["tool_calls"]:
                tool_calls.append(
                    ToolCall(
                        id=tc["id"],
                        type=tc["type"],
                        function={
                            "name": tc["function"]["name"],
                            "arguments": json.loads(tc["function"]["arguments"]),
                        },
                    )
                )

        return CompletionResponse(
            content=message.get("content", "") or "",
            model=model,
            provider=self.provider,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            finish_reason=choice.get("finish_reason", ""),
            tool_calls=tool_calls,
            latency_ms=self._calculate_latency(start_time),
            raw=result,
        )

    async def stream(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int = 1024,
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[StreamChunk]:
        """Stream completion using OpenAI API."""
        model = model or self.default_model
        data = {
            "model": model,
            "messages": self._messages_to_list(messages),
            **chat_settings(
                model,
                max_tokens,
                temperature,
                kwargs,
                tools=[{"type": "function", "function": t} for t in tools] if tools else None,
            ),
            "stream": True,
        }

        await self.connect()
        async with self._client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            json=data,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break

                    chunk_data = json.loads(data_str)
                    delta = chunk_data["choices"][0].get("delta", {})

                    yield StreamChunk(
                        content=delta.get("content", ""),
                        delta_content=delta.get("content", ""),
                        finish_reason=chunk_data["choices"][0].get("finish_reason"),
                    )


__all__ = ["OpenAIClient"]
