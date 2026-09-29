"""Tests for provider adapters — multi-provider LLM calling layer."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.provider_adapters import (
    AnthropicAdapter,
    GoogleAdapter,
    LLMMessage,
    LLMResponse,
    OpenAIAdapter,
    XAIAdapter,
    get_adapter,
)

# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class TestLLMMessage:
    def test_frozen(self):
        msg = LLMMessage(role="user", content="hello")
        with pytest.raises(AttributeError):
            msg.role = "system"

    def test_fields(self):
        msg = LLMMessage(role="system", content="You are helpful")
        assert msg.role == "system"
        assert msg.content == "You are helpful"


class TestLLMResponse:
    def test_frozen(self):
        resp = LLMResponse(
            text="Hello",
            provider="anthropic",
            model="claude-sonnet-4-6",
            usage={"input_tokens": 10, "output_tokens": 5},
        )
        with pytest.raises(AttributeError):
            resp.text = "changed"

    def test_fields(self):
        resp = LLMResponse(
            text="response",
            provider="google",
            model="gemini-3-pro",
            usage={"input_tokens": 100, "output_tokens": 50},
        )
        assert resp.text == "response"
        assert resp.provider == "google"
        assert resp.usage["input_tokens"] == 100


# ---------------------------------------------------------------------------
# Anthropic adapter
# ---------------------------------------------------------------------------


class TestAnthropicAdapter:
    @staticmethod
    def _mock_stream_client(mock_response):
        """Build a mock client whose messages.stream() context manager
        returns mock_response from get_final_message()."""
        mock_stream = MagicMock()
        mock_stream.get_final_message.return_value = mock_response
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=False)

        mock_client = MagicMock()
        mock_client.messages.stream.return_value = mock_stream
        return mock_client

    @pytest.mark.asyncio
    async def test_success(self):
        adapter = AnthropicAdapter()

        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Generated code here"
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50

        mock_client = self._mock_stream_client(mock_response)

        with patch.object(adapter, "_get_client", return_value=mock_client):
            result = await adapter.call(
                model="claude-sonnet-4-6",
                messages=[
                    LLMMessage(role="system", content="You are helpful"),
                    LLMMessage(role="user", content="Write a function"),
                ],
            )

        assert isinstance(result, LLMResponse)
        assert result.text == "Generated code here"
        assert result.provider == "anthropic"
        assert result.model == "claude-sonnet-4-6"
        assert result.usage["input_tokens"] == 100

    @pytest.mark.asyncio
    async def test_separates_system_from_messages(self):
        adapter = AnthropicAdapter()

        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "ok"
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 5

        mock_client = self._mock_stream_client(mock_response)

        with patch.object(adapter, "_get_client", return_value=mock_client):
            await adapter.call(
                model="claude-sonnet-4-6",
                messages=[
                    LLMMessage(role="system", content="SYS_PROMPT"),
                    LLMMessage(role="user", content="USER_MSG"),
                ],
            )

        call_kwargs = mock_client.messages.stream.call_args[1]
        assert call_kwargs["system"] == "SYS_PROMPT"
        assert call_kwargs["messages"] == [{"role": "user", "content": "USER_MSG"}]

    @pytest.mark.asyncio
    async def test_api_error(self):
        adapter = AnthropicAdapter()

        mock_client = MagicMock()
        mock_client.messages.stream.side_effect = Exception("API overloaded")

        with patch.object(adapter, "_get_client", return_value=mock_client):
            with pytest.raises(Exception, match="API overloaded"):
                await adapter.call(
                    model="claude-sonnet-4-6",
                    messages=[LLMMessage(role="user", content="test")],
                )


# ---------------------------------------------------------------------------
# Google adapter
# ---------------------------------------------------------------------------


class TestGoogleAdapter:
    @pytest.mark.asyncio
    async def test_success(self):
        adapter = GoogleAdapter()

        mock_response = {
            "candidates": [{"content": {"parts": [{"text": "Design tokens"}]}}],
            "usageMetadata": {
                "promptTokenCount": 200,
                "candidatesTokenCount": 100,
            },
        }

        with patch.object(
            adapter, "_call_gemini_rest", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await adapter.call(
                model="gemini-3-pro-preview",
                messages=[
                    LLMMessage(role="system", content="You are a design expert"),
                    LLMMessage(role="user", content="Generate tokens"),
                ],
            )

        assert isinstance(result, LLMResponse)
        assert result.text == "Design tokens"
        assert result.provider == "google"
        assert result.usage["input_tokens"] == 200

    @pytest.mark.asyncio
    async def test_empty_response(self):
        adapter = GoogleAdapter()

        mock_response = {"candidates": []}

        with patch.object(
            adapter, "_call_gemini_rest", new_callable=AsyncMock, return_value=mock_response
        ):
            with pytest.raises(ValueError, match="empty"):
                await adapter.call(
                    model="gemini-3-pro-preview",
                    messages=[LLMMessage(role="user", content="test")],
                )


# ---------------------------------------------------------------------------
# OpenAI adapter
# ---------------------------------------------------------------------------


class TestOpenAIAdapter:
    @pytest.mark.asyncio
    async def test_success(self):
        adapter = OpenAIAdapter()

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "SEO optimized content"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.prompt_tokens = 150
        mock_response.usage.completion_tokens = 80

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(adapter, "_get_client", return_value=mock_client):
            result = await adapter.call(
                model="gpt-4o",
                messages=[
                    LLMMessage(role="system", content="SEO expert"),
                    LLMMessage(role="user", content="Write meta"),
                ],
            )

        assert result.text == "SEO optimized content"
        assert result.provider == "openai"
        assert result.usage["output_tokens"] == 80

    @pytest.mark.asyncio
    async def test_api_error(self):
        adapter = OpenAIAdapter()

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Rate limited")

        with patch.object(adapter, "_get_client", return_value=mock_client):
            with pytest.raises(Exception, match="Rate limited"):
                await adapter.call(
                    model="gpt-4o",
                    messages=[LLMMessage(role="user", content="test")],
                )


# ---------------------------------------------------------------------------
# xAI adapter
# ---------------------------------------------------------------------------


class TestXAIAdapter:
    @pytest.mark.asyncio
    async def test_success(self):
        adapter = XAIAdapter()

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "QA test results"
        mock_response.usage.prompt_tokens = 120
        mock_response.usage.completion_tokens = 60

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(adapter, "_get_client", return_value=mock_client):
            result = await adapter.call(
                model="grok-3",
                messages=[LLMMessage(role="user", content="Run tests")],
            )

        assert result.text == "QA test results"
        assert result.provider == "xai"

    @pytest.mark.asyncio
    async def test_uses_xai_base_url(self):
        """xAI adapter should configure OpenAI client with xAI base URL."""
        adapter = XAIAdapter()
        # The adapter should have a distinct base URL
        assert adapter.BASE_URL == "https://api.x.ai/v1"


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


class TestGetAdapter:
    def test_anthropic(self):
        adapter = get_adapter("anthropic")
        assert isinstance(adapter, AnthropicAdapter)

    def test_google(self):
        adapter = get_adapter("google")
        assert isinstance(adapter, GoogleAdapter)

    def test_openai(self):
        adapter = get_adapter("openai")
        assert isinstance(adapter, OpenAIAdapter)

    def test_xai(self):
        adapter = get_adapter("xai")
        assert isinstance(adapter, XAIAdapter)

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown provider"):
            get_adapter("deepseek")


class TestOpenAIRequestContract:
    @pytest.mark.asyncio
    async def test_network_runs_off_event_loop_and_budget_forwarded(self):
        import asyncio
        import threading

        adapter = OpenAIAdapter()
        loop_thread = threading.get_ident()
        network_threads = []
        response = MagicMock()
        response.choices[0].message.content = "ok"
        response.choices[0].finish_reason = "stop"
        response.usage.prompt_tokens = 1
        response.usage.completion_tokens = 1
        client = MagicMock()
        entered = threading.Event()
        release = threading.Event()

        def create(**kwargs):
            network_threads.append(threading.get_ident())
            entered.set()
            assert release.wait(2), "Event loop did not release worker"
            return response

        client.chat.completions.create.side_effect = create
        with patch.object(adapter, "_get_client", return_value=client):
            task = asyncio.create_task(
                adapter.call(
                    "gpt-4o",
                    [LLMMessage("user", "meta title")],
                    max_tokens=256,
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )
            )
            try:
                await asyncio.wait_for(asyncio.to_thread(entered.wait, 1), timeout=1.5)
                release.set()
                result = await task
            finally:
                release.set()
        assert result.text == "ok"
        assert network_threads and network_threads[0] != loop_thread
        assert client.chat.completions.create.call_args.kwargs["max_tokens"] == 256
        assert client.chat.completions.create.call_args.kwargs["temperature"] == 0.2
        assert client.chat.completions.create.call_args.kwargs["response_format"] == {
            "type": "json_object"
        }
        client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_incompatible_settings_reject_before_client_creation(self):
        adapter = OpenAIAdapter()
        with patch.object(adapter, "_get_client") as factory:
            with pytest.raises(ValueError):
                await adapter.call("gpt-4o", [], reasoning_effort="high")
            factory.assert_not_called()

    @pytest.mark.asyncio
    async def test_incomplete_output_is_error(self):
        adapter = OpenAIAdapter()
        client = MagicMock()
        client.chat.completions.create.return_value.choices[0].finish_reason = "length"
        with patch.object(adapter, "_get_client", return_value=client):
            with pytest.raises(ValueError, match="incomplete"):
                await adapter.call("gpt-4o", [])
        client.close.assert_called_once()
