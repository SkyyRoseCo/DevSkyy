"""
LLM Provider Clients
====================

Unified clients for all major LLM providers using official SDKs.

Providers:
- OpenAI (GPT-4, o1) - using `openai` SDK
- Anthropic (Claude) - using `anthropic` SDK
- Google (Gemini) - using `google-genai` SDK
- Mistral - using `mistralai` SDK
- Cohere (Command) - using `cohere` SDK
- Groq (Llama, Mixtral) - using `groq` SDK

Features:
- Async support with official async clients
- Streaming with native SDK streaming
- Function calling / Tool use
- Error handling with SDK built-in retries
- Token counting
- Type safety from official SDKs
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime
from enum import StrEnum
from typing import Any

import cohere

# Official SDK imports
from anthropic import AsyncAnthropic
from google import genai
from groq import AsyncGroq

from skyyrose.core.openai_settings import chat_settings

# langfuse drop-in wrapper auto-traces model + tokens + cost (graceful fallback if extra not installed)
try:
    from langfuse.openai import AsyncOpenAI
except ImportError:
    from openai import AsyncOpenAI

from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

# Import config for API keys (loads .env.hf)
try:
    from config import (
        ANTHROPIC_API_KEY,
        COHERE_API_KEY,
        GOOGLE_API_KEY,
        GROQ_API_KEY,
        MISTRAL_API_KEY,
        OPENAI_API_KEY,
    )
except ImportError:
    # Fallback for standalone usage
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

logger = logging.getLogger(__name__)


# =============================================================================
# Common Models
# =============================================================================


class MessageRole(StrEnum):
    """Message roles"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    """Chat message"""

    role: MessageRole
    content: str
    name: str | None = None
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None


class ToolCall(BaseModel):
    """Tool call request"""

    id: str
    type: str = "function"
    function: dict[str, Any]


class CompletionResponse(BaseModel):
    """Unified completion response"""

    content: str
    model: str
    provider: str

    # Usage
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    # Metadata
    finish_reason: str = ""
    tool_calls: list[ToolCall] = []
    latency_ms: float = 0

    # Raw response
    raw: dict[str, Any] = {}


class StreamChunk(BaseModel):
    """Streaming chunk"""

    content: str = ""
    finish_reason: str | None = None
    tool_calls: list[dict] = []


# =============================================================================
# Base Client
# =============================================================================


class BaseLLMClient(ABC):
    """
    Base LLM Client

    Abstract base class for all provider clients.
    Now uses official SDKs instead of raw HTTP calls.
    """

    provider: str = "base"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 3,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Any = None

    async def __aenter__(self):
        self._init_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _init_client(self):  # noqa: B027
        """Initialize the SDK client - override in subclasses"""
        pass

    async def close(self):  # noqa: B027
        """Close client if needed - override in subclasses"""
        pass

    @abstractmethod
    async def complete(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: list[dict] | None = None,
        **kwargs,
    ) -> CompletionResponse:
        """Generate completion"""
        pass

    @abstractmethod
    async def stream(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        """Stream completion"""
        pass

    def _messages_to_list(self, messages: list[Message]) -> list[dict]:
        """Convert Message objects to dict list"""
        return [{"role": m.role.value, "content": m.content} for m in messages]


# =============================================================================
# OpenAI Client (using official openai SDK)
# =============================================================================


class OpenAIClient(BaseLLMClient):
    """
    OpenAI API Client using official `openai` SDK.

    Supports: GPT-4o, GPT-4o-mini, o1-preview, o1-mini

    Usage:
        client = OpenAIClient()
        response = await client.complete(
            messages=[Message(role=MessageRole.USER, content="Hello")],
            model="gpt-4o-mini"
        )
    """

    provider = "openai"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        **kwargs,
    ):
        super().__init__(
            api_key=api_key or OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", ""),
            base_url=base_url,
            **kwargs,
        )
        self._init_client()

    async def close(self):
        await self._client.close()

    def _init_client(self):
        """Initialize the OpenAI async client"""
        self._client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

    async def complete(
        self,
        messages: list[Message],
        model: str = "gpt-4o-mini",
        temperature: float | None = None,
        max_tokens: int = 1024,
        tools: list[dict] | None = None,
        response_format: dict | None = None,
        **kwargs,
    ) -> CompletionResponse:
        start_time = datetime.now()

        # Build request kwargs
        request_kwargs: dict[str, Any] = {
            "model": model,
            "messages": self._messages_to_list(messages),
            **chat_settings(
                model,
                max_tokens,
                temperature,
                {**kwargs, "response_format": response_format},
                tools=tools,
            ),
        }

        # Call the SDK
        response = await self._client.chat.completions.create(**request_kwargs)

        latency = (datetime.now() - start_time).total_seconds() * 1000

        choice = response.choices[0]
        usage = response.usage

        # Extract tool calls
        tool_calls = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        type=tc.type,
                        function={
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    )
                )

        return CompletionResponse(
            content=choice.message.content or "",
            model=response.model,
            provider=self.provider,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
            finish_reason=choice.finish_reason or "",
            tool_calls=tool_calls,
            latency_ms=latency,
            raw=response.model_dump(),
        )

    async def stream(
        self,
        messages: list[Message],
        model: str = "gpt-4o-mini",
        temperature: float | None = None,
        max_tokens: int = 1024,
        tools: list[dict] | None = None,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        stream = await self._client.chat.completions.create(
            model=model,
            messages=self._messages_to_list(messages),
            **chat_settings(model, max_tokens, temperature, kwargs, tools=tools),
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices:
                delta = chunk.choices[0].delta
                yield StreamChunk(
                    content=delta.content or "",
                    finish_reason=chunk.choices[0].finish_reason,
                )


# =============================================================================
# Anthropic Client (using official anthropic SDK)
# =============================================================================


class AnthropicClient(BaseLLMClient):
    """
    Anthropic API Client using official `anthropic` SDK.

    Supports: Claude Sonnet 4.5, Claude Haiku 4.5, Claude Opus 4.5

    Usage:
        client = AnthropicClient()
        response = await client.complete(
            messages=[Message(role=MessageRole.USER, content="Hello")],
            model="claude-sonnet-4-5"
        )
    """

    provider = "anthropic"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        **kwargs,
    ):
        super().__init__(
            api_key=api_key or ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY", ""),
            base_url=base_url,
            **kwargs,
        )
        self._init_client()

    def _init_client(self):
        """Initialize the Anthropic async client"""
        self._client = AsyncAnthropic(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

    def _messages_to_anthropic(self, messages: list[Message]) -> tuple[str, list[dict]]:
        """Convert to Anthropic format (separate system)"""
        system = ""
        msgs = []

        for m in messages:
            if m.role == MessageRole.SYSTEM:
                system = m.content
            else:
                msgs.append(
                    {
                        "role": "user" if m.role == MessageRole.USER else "assistant",
                        "content": m.content,
                    }
                )

        return system, msgs

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def complete(
        self,
        messages: list[Message],
        model: str = "claude-sonnet-4-5",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: list[dict] | None = None,
        **kwargs,
    ) -> CompletionResponse:
        start_time = datetime.now()

        system, msgs = self._messages_to_anthropic(messages)

        # Build request kwargs
        request_kwargs: dict[str, Any] = {
            "model": model,
            "messages": msgs,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if system:
            request_kwargs["system"] = system

        if tools:
            request_kwargs["tools"] = tools

        # Call the SDK
        response = await self._client.messages.create(**request_kwargs)

        latency = (datetime.now() - start_time).total_seconds() * 1000

        # Extract content
        content = ""
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        type="function",
                        function={
                            "name": block.name,
                            "arguments": (
                                json.dumps(block.input)
                                if isinstance(block.input, dict)
                                else block.input
                            ),
                        },
                    )
                )

        return CompletionResponse(
            content=content,
            model=response.model,
            provider=self.provider,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens,
            finish_reason=response.stop_reason or "",
            tool_calls=tool_calls,
            latency_ms=latency,
            raw=response.model_dump(),
        )

    async def stream(
        self,
        messages: list[Message],
        model: str = "claude-sonnet-4-5",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        system, msgs = self._messages_to_anthropic(messages)

        request_kwargs: dict[str, Any] = {
            "model": model,
            "messages": msgs,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if system:
            request_kwargs["system"] = system

        async with self._client.messages.stream(**request_kwargs) as stream:
            async for text in stream.text_stream:
                yield StreamChunk(content=text)

            # Get final message for finish reason
            final_message = await stream.get_final_message()
            yield StreamChunk(finish_reason=final_message.stop_reason or "stop")


# =============================================================================
# Google Client (using official google-genai SDK)
# =============================================================================


class GoogleClient(BaseLLMClient):
    """
    Google Gemini API Client using official `google-genai` SDK.

    Supports: Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash

    Usage:
        client = GoogleClient()
        response = await client.complete(
            messages=[Message(role=MessageRole.USER, content="Hello")],
            model="gemini-2.0-flash"
        )
    """

    provider = "google"

    def __init__(
        self,
        api_key: str | None = None,
        **kwargs,
    ):
        super().__init__(
            api_key=api_key or GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY", ""),
            **kwargs,
        )
        self._init_client()

    def _init_client(self):
        """Initialize the Google GenAI SDK client"""
        self._client = genai.Client(api_key=self.api_key)

    def _messages_to_gemini(self, messages: list[Message]) -> tuple[str | None, list[Any]]:
        """Convert to Gemini format using new SDK types"""
        system_instruction: str | None = None
        contents: list[Any] = []

        for m in messages:
            if m.role == MessageRole.SYSTEM:
                system_instruction = m.content
            else:
                role = "user" if m.role == MessageRole.USER else "model"
                contents.append({"role": role, "parts": [{"text": m.content}]})

        return system_instruction, contents

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def complete(
        self,
        messages: list[Message],
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: list[dict] | None = None,
        **kwargs,
    ) -> CompletionResponse:
        start_time = datetime.now()

        system_instruction, contents = self._messages_to_gemini(messages)

        # Build configuration using dict (compatible with deprecated SDK)
        config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        if system_instruction:
            config["system_instruction"] = system_instruction

        # Generate content using async client
        response = await self._client.aio.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )

        latency = (datetime.now() - start_time).total_seconds() * 1000

        # Extract content
        content = response.text if response.text else ""
        tool_calls = []

        # Handle function calls if present
        if response.candidates and response.candidates[0].content.parts:
            for i, part in enumerate(response.candidates[0].content.parts):
                if hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    tool_calls.append(
                        ToolCall(
                            id=f"call_{i}",
                            type="function",
                            function={
                                "name": fc.name,
                                "arguments": json.dumps(dict(fc.args)) if fc.args else "{}",
                            },
                        )
                    )

        # Get usage metadata
        usage = getattr(response, "usage_metadata", None)

        return CompletionResponse(
            content=content,
            model=model,
            provider=self.provider,
            input_tokens=usage.prompt_token_count if usage else 0,
            output_tokens=usage.candidates_token_count if usage else 0,
            total_tokens=usage.total_token_count if usage else 0,
            finish_reason=(
                str(response.candidates[0].finish_reason) if response.candidates else ""
            ),
            tool_calls=tool_calls,
            latency_ms=latency,
            raw={"text": content, "model": model},
        )

    async def stream(
        self,
        messages: list[Message],
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        system_instruction, contents = self._messages_to_gemini(messages)

        # Build configuration using dict (compatible with deprecated SDK)
        config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        if system_instruction:
            config["system_instruction"] = system_instruction

        # Stream content using async client
        async for chunk in await self._client.aio.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
        ):
            if chunk.text:
                yield StreamChunk(content=chunk.text)

        yield StreamChunk(finish_reason="stop")


# =============================================================================
# Mistral Client (using official mistralai SDK)
# =============================================================================


class MistralClient(BaseLLMClient):
    """
    Mistral API Client using official `mistralai` SDK.

    Supports: Mistral Large, Mistral Small, Codestral
    """

    provider = "mistral"

    def __init__(
        self,
        api_key: str | None = None,
        **kwargs,
    ):
        super().__init__(
            api_key=api_key or MISTRAL_API_KEY or os.getenv("MISTRAL_API_KEY", ""),
            **kwargs,
        )
        self._init_client()

    def _init_client(self):
        """Initialize the Mistral client"""
        # Optional provider SDKs must not prevent unrelated OpenAI imports.
        from mistralai import Mistral

        self._client = Mistral(api_key=self.api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def complete(
        self,
        messages: list[Message],
        model: str = "mistral-small-latest",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: list[dict] | None = None,
        **kwargs,
    ) -> CompletionResponse:
        start_time = datetime.now()

        # Convert messages to Mistral format
        mistral_messages = [{"role": m.role.value, "content": m.content} for m in messages]

        # Call the SDK (async)
        response = await self._client.chat.complete_async(
            model=model,
            messages=mistral_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        latency = (datetime.now() - start_time).total_seconds() * 1000

        choice = response.choices[0]
        usage = response.usage

        # Extract tool calls if present
        tool_calls = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        type="function",
                        function={
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    )
                )

        return CompletionResponse(
            content=choice.message.content or "",
            model=response.model,
            provider=self.provider,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
            finish_reason=choice.finish_reason or "",
            tool_calls=tool_calls,
            latency_ms=latency,
            raw=response.model_dump() if hasattr(response, "model_dump") else {},
        )

    async def stream(
        self,
        messages: list[Message],
        model: str = "mistral-small-latest",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        # Convert messages to Mistral format
        mistral_messages = [{"role": m.role.value, "content": m.content} for m in messages]

        # Stream using SDK (async)
        stream = await self._client.chat.stream_async(
            model=model,
            messages=mistral_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        async for chunk in stream:
            if chunk.data.choices:
                delta = chunk.data.choices[0].delta
                yield StreamChunk(
                    content=delta.content or "",
                    finish_reason=chunk.data.choices[0].finish_reason,
                )


# =============================================================================
# Cohere Client (using official cohere SDK)
# =============================================================================


class CohereClient(BaseLLMClient):
    """
    Cohere API Client using official `cohere` SDK.

    Supports: Command R+, Command R7B
    """

    provider = "cohere"

    def __init__(
        self,
        api_key: str | None = None,
        **kwargs,
    ):
        super().__init__(
            api_key=api_key or COHERE_API_KEY or os.getenv("COHERE_API_KEY", ""),
            **kwargs,
        )
        self._init_client()

    def _init_client(self):
        """Initialize the Cohere async client"""
        self._client = cohere.AsyncClientV2(api_key=self.api_key)

    def _messages_to_cohere_v2(self, messages: list[Message]) -> list[dict]:
        """Convert to Cohere v2 chat format"""
        cohere_messages = []

        for m in messages:
            if m.role == MessageRole.SYSTEM:
                cohere_messages.append({"role": "system", "content": m.content})
            elif m.role == MessageRole.USER:
                cohere_messages.append({"role": "user", "content": m.content})
            else:
                cohere_messages.append({"role": "assistant", "content": m.content})

        return cohere_messages

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def complete(
        self,
        messages: list[Message],
        model: str = "command-r7b-12-2024",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: list[dict] | None = None,
        **kwargs,
    ) -> CompletionResponse:
        start_time = datetime.now()

        cohere_messages = self._messages_to_cohere_v2(messages)

        # Call the SDK (v2 chat API)
        response = await self._client.chat(
            model=model,
            messages=cohere_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        latency = (datetime.now() - start_time).total_seconds() * 1000

        # Extract content from response
        content = ""
        if response.message and response.message.content:
            for block in response.message.content:
                if hasattr(block, "text"):
                    content += block.text

        # Get usage
        usage = response.usage

        return CompletionResponse(
            content=content,
            model=model,
            provider=self.provider,
            input_tokens=usage.tokens.input_tokens if usage and usage.tokens else 0,
            output_tokens=usage.tokens.output_tokens if usage and usage.tokens else 0,
            total_tokens=(
                (usage.tokens.input_tokens + usage.tokens.output_tokens)
                if usage and usage.tokens
                else 0
            ),
            finish_reason=response.finish_reason or "",
            latency_ms=latency,
            raw=response.model_dump() if hasattr(response, "model_dump") else {},
        )

    async def stream(
        self,
        messages: list[Message],
        model: str = "command-r7b-12-2024",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        cohere_messages = self._messages_to_cohere_v2(messages)

        # Stream using SDK v2
        async for event in self._client.chat_stream(
            model=model,
            messages=cohere_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            if event.type == "content-delta":
                # Extract text from nested event structure
                if (
                    hasattr(event, "delta")
                    and hasattr(event.delta, "message")
                    and hasattr(event.delta.message, "content")
                    and event.delta.message.content
                    and hasattr(event.delta.message.content, "text")
                ):
                    yield StreamChunk(content=event.delta.message.content.text)
            elif event.type == "message-end":
                yield StreamChunk(finish_reason="stop")


# =============================================================================
# Groq Client (using official groq SDK)
# =============================================================================


class GroqClient(BaseLLMClient):
    """
    Groq API Client using official `groq` SDK (Fast Inference).

    Supports: Llama 3.1 70B, Llama 3.1 8B, Mixtral 8x7B
    """

    provider = "groq"

    def __init__(
        self,
        api_key: str | None = None,
        **kwargs,
    ):
        super().__init__(
            api_key=api_key or GROQ_API_KEY or os.getenv("GROQ_API_KEY", ""),
            **kwargs,
        )
        self._init_client()

    def _init_client(self):
        """Initialize the Groq async client"""
        self._client = AsyncGroq(
            api_key=self.api_key,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def complete(
        self,
        messages: list[Message],
        model: str = "llama-3.1-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: list[dict] | None = None,
        **kwargs,
    ) -> CompletionResponse:
        start_time = datetime.now()

        # Convert messages to OpenAI format (Groq uses OpenAI-compatible API)
        groq_messages = [{"role": m.role.value, "content": m.content} for m in messages]

        # Call the SDK
        response = await self._client.chat.completions.create(
            model=model,
            messages=groq_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        latency = (datetime.now() - start_time).total_seconds() * 1000

        choice = response.choices[0]
        usage = response.usage

        # Extract tool calls if present
        tool_calls = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        type="function",
                        function={
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    )
                )

        # Get Groq speed metrics from response headers if available
        raw_data = response.model_dump() if hasattr(response, "model_dump") else {}

        return CompletionResponse(
            content=choice.message.content or "",
            model=response.model,
            provider=self.provider,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
            finish_reason=choice.finish_reason or "",
            tool_calls=tool_calls,
            latency_ms=latency,
            raw=raw_data,
        )

    async def stream(
        self,
        messages: list[Message],
        model: str = "llama-3.1-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        # Convert messages to OpenAI format
        groq_messages = [{"role": m.role.value, "content": m.content} for m in messages]

        # Stream using SDK
        stream = await self._client.chat.completions.create(
            model=model,
            messages=groq_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices:
                delta = chunk.choices[0].delta
                yield StreamChunk(
                    content=delta.content or "",
                    finish_reason=chunk.choices[0].finish_reason,
                )
