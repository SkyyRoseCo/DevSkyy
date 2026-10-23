"""
LLM Router
==========

Multi-provider router with fallback and load balancing.

Features:
- Provider selection by preference
- Automatic fallback on failure
- 2-LLM agreement architecture support
- Cost-aware routing
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field, replace
from enum import StrEnum
from typing import Any

from core.telemetry.tracer import get_tracer
from core.token_tracker import record_llm_usage

from .base import BaseLLMClient, CompletionResponse, Message, ModelProvider
from .exceptions import LLMError
from .providers import (
    AnthropicClient,
    CohereClient,
    GoogleClient,
    GroqClient,
    MistralClient,
    OpenAIClient,
)
from .providers.deepseek import DeepSeekClient

logger = logging.getLogger(__name__)
_tracer = get_tracer("llm.router")


# =============================================================================
# Provider Configuration
# =============================================================================


@dataclass
class ProviderConfig:
    """Configuration for a provider."""

    provider: ModelProvider
    client_class: type[BaseLLMClient]
    default_model: str
    priority: int = 0  # Lower = higher priority
    enabled: bool = True

    # Pricing per 1K tokens (for cost routing)
    input_price: float = 0.0
    output_price: float = 0.0


# Default provider configurations
PROVIDER_CONFIGS: dict[ModelProvider, ProviderConfig] = {
    ModelProvider.ANTHROPIC: ProviderConfig(
        provider=ModelProvider.ANTHROPIC,
        client_class=AnthropicClient,
        default_model="claude-sonnet-4-20250514",
        priority=1,
        input_price=0.003,
        output_price=0.015,
    ),
    ModelProvider.OPENAI: ProviderConfig(
        provider=ModelProvider.OPENAI,
        client_class=OpenAIClient,
        default_model="gpt-4o-mini",
        priority=2,
        input_price=0.00015,
        output_price=0.0006,
    ),
    ModelProvider.GOOGLE: ProviderConfig(
        provider=ModelProvider.GOOGLE,
        client_class=GoogleClient,
        default_model="gemini-2.0-flash",
        priority=3,
        input_price=0.000075,
        output_price=0.0003,
    ),
    ModelProvider.MISTRAL: ProviderConfig(
        provider=ModelProvider.MISTRAL,
        client_class=MistralClient,
        default_model="mistral-small-latest",
        priority=4,
        input_price=0.001,
        output_price=0.003,
    ),
    ModelProvider.GROQ: ProviderConfig(
        provider=ModelProvider.GROQ,
        client_class=GroqClient,
        default_model="llama-3.3-70b-versatile",
        priority=5,
        input_price=0.00059,
        output_price=0.00079,
    ),
    ModelProvider.COHERE: ProviderConfig(
        provider=ModelProvider.COHERE,
        client_class=CohereClient,
        default_model="command-r-08-2024",
        priority=6,
        input_price=0.0005,
        output_price=0.0015,
    ),
    ModelProvider.DEEPSEEK: ProviderConfig(
        provider=ModelProvider.DEEPSEEK,
        client_class=DeepSeekClient,
        default_model="deepseek-chat",
        priority=0,  # Highest priority for cost optimization
        input_price=0.00014,  # $0.14 per 1M tokens
        output_price=0.00028,  # $0.28 per 1M tokens
    ),
}

# Add LiteLLM as universal fallback if available
try:
    from .providers.litellm_provider import LiteLLMClient

    PROVIDER_CONFIGS[ModelProvider.LITELLM] = ProviderConfig(
        provider=ModelProvider.LITELLM,
        client_class=LiteLLMClient,
        default_model="anthropic/claude-sonnet-4-20250514",
        priority=99,  # Lowest priority — universal fallback only
        input_price=0.003,
        output_price=0.015,
    )
except ImportError:
    pass


class RoutingStrategy(StrEnum):
    """Routing strategy for provider selection."""

    PRIORITY = "priority"  # Use priority order
    COST = "cost"  # Use cheapest available
    LATENCY = "latency"  # Use fastest (based on history)
    ROUND_ROBIN = "round_robin"  # Distribute evenly


# =============================================================================
# Circuit Breaker (Enterprise Hardening)
# =============================================================================


@dataclass
class CircuitBreaker:
    """
    Circuit breaker pattern for LLM providers.

    Enterprise hardening: Prevents cascade failures by temporarily disabling
    failing providers. Automatically recovers after timeout.

    States:
    - CLOSED: Normal operation
    - OPEN: Provider disabled due to failures
    - HALF_OPEN: Testing if provider recovered

    Args:
        failure_threshold: Number of failures before opening circuit (default: 5)
        timeout: Seconds before attempting recovery (default: 60)
        success_threshold: Successes needed to close circuit (default: 2)
    """

    failure_threshold: int = 5
    timeout: int = 60  # seconds
    success_threshold: int = 2

    # Internal state
    failures: dict[ModelProvider, int] = field(default_factory=dict)
    successes: dict[ModelProvider, int] = field(default_factory=dict)
    opened_at: dict[ModelProvider, float] = field(default_factory=dict)
    state: dict[ModelProvider, str] = field(default_factory=dict)  # CLOSED, OPEN, HALF_OPEN

    def is_available(self, provider: ModelProvider) -> bool:
        """
        Check if provider is available (circuit not open).

        Returns:
            True if provider should be tried
        """
        current_state = self.state.get(provider, "CLOSED")

        if current_state == "CLOSED":
            return True

        if current_state == "OPEN":
            # Check if timeout has passed
            opened_time = self.opened_at.get(provider, 0)
            if time.time() - opened_time >= self.timeout:
                # Move to HALF_OPEN (allow one test request)
                self.state[provider] = "HALF_OPEN"
                self.successes[provider] = 0
                logger.info(
                    f"Circuit breaker {provider.value}: OPEN → HALF_OPEN (testing recovery)"
                )
                return True
            return False

        # HALF_OPEN: Allow request
        return True

    def record_success(self, provider: ModelProvider) -> None:
        """Record successful request."""
        current_state = self.state.get(provider, "CLOSED")

        if current_state == "HALF_OPEN":
            # Count successes in HALF_OPEN state
            self.successes[provider] = self.successes.get(provider, 0) + 1

            if self.successes[provider] >= self.success_threshold:
                # Close circuit - provider recovered
                self.state[provider] = "CLOSED"
                self.failures[provider] = 0
                logger.info(f"Circuit breaker {provider.value}: HALF_OPEN → CLOSED (recovered)")

        elif current_state == "CLOSED":
            # Reset failure count on success
            self.failures[provider] = 0

    def record_failure(self, provider: ModelProvider) -> None:
        """Record failed request."""
        current_state = self.state.get(provider, "CLOSED")

        if current_state == "HALF_OPEN":
            # Failed during recovery test - reopen circuit
            self.state[provider] = "OPEN"
            self.opened_at[provider] = time.time()
            logger.warning(
                f"Circuit breaker {provider.value}: HALF_OPEN → OPEN (recovery failed, retry in {self.timeout}s)"
            )

        else:
            # Increment failure count
            self.failures[provider] = self.failures.get(provider, 0) + 1

            if self.failures[provider] >= self.failure_threshold:
                # Open circuit - disable provider
                self.state[provider] = "OPEN"
                self.opened_at[provider] = time.time()
                logger.error(
                    f"Circuit breaker {provider.value}: CLOSED → OPEN "
                    f"({self.failures[provider]} failures, retry in {self.timeout}s)"
                )

    def get_status(self) -> dict[str, Any]:
        """Get circuit breaker status for all providers."""
        return {
            provider.value: {
                "state": self.state.get(provider, "CLOSED"),
                "failures": self.failures.get(provider, 0),
                "opened_at": self.opened_at.get(provider),
            }
            for provider in ModelProvider
        }


# =============================================================================
# LLM Router
# =============================================================================


class LLMRouter:
    """
    Multi-provider LLM router.

    Features:
    - Automatic provider selection
    - Fallback on failures
    - 2-LLM agreement for validation
    - Cost tracking

    Usage:
        router = LLMRouter()

        # Simple completion
        response = await router.complete(
            messages=[Message.user("Hello!")],
            provider=ModelProvider.ANTHROPIC,
        )

        # With fallback
        response = await router.complete_with_fallback(
            messages=[Message.user("Hello!")],
            providers=[ModelProvider.ANTHROPIC, ModelProvider.OPENAI],
        )

        # 2-LLM agreement
        response, agreement = await router.complete_with_agreement(
            messages=[Message.user("Analyze this...")],
            primary=ModelProvider.ANTHROPIC,
            secondary=ModelProvider.OPENAI,
        )
    """

    def __init__(
        self,
        configs: dict[ModelProvider, ProviderConfig] | None = None,
        strategy: RoutingStrategy = RoutingStrategy.PRIORITY,
        circuit_breaker: CircuitBreaker | None = None,
    ) -> None:
        # Provider enablement belongs to this router, not every future request.
        source = PROVIDER_CONFIGS if configs is None else configs
        self.configs = {provider: replace(config) for provider, config in source.items()}
        self.strategy = strategy
        self._clients: dict[ModelProvider, BaseLLMClient] = {}
        self._round_robin_index = 0
        # Enterprise hardening: Circuit breaker prevents cascade failures
        self.circuit_breaker = circuit_breaker or CircuitBreaker()

    async def __aenter__(self) -> LLMRouter:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close all client connections."""
        for client in self._clients.values():
            await client.close()
        self._clients.clear()

    def _get_client(self, provider: ModelProvider) -> BaseLLMClient:
        """Get or create client for provider."""
        if provider not in self._clients:
            config = self.configs.get(provider)
            if not config or not config.enabled:
                raise LLMError(f"Provider not available: {provider.value}")

            self._clients[provider] = config.client_class()

        return self._clients[provider]

    def _select_provider(
        self,
        providers: list[ModelProvider] | None = None,
    ) -> ModelProvider:
        """Select provider based on routing strategy."""
        available = providers or [p for p, c in self.configs.items() if c.enabled]

        if not available:
            raise LLMError("No providers available")

        if self.strategy == RoutingStrategy.PRIORITY:
            # Sort by priority
            available.sort(key=lambda p: self.configs[p].priority)
            return available[0]

        elif self.strategy == RoutingStrategy.COST:
            # Sort by cost (input + output price)
            available.sort(key=lambda p: self.configs[p].input_price + self.configs[p].output_price)
            return available[0]

        elif self.strategy == RoutingStrategy.ROUND_ROBIN:
            # Cycle through providers
            provider = available[self._round_robin_index % len(available)]
            self._round_robin_index += 1
            return provider

        else:
            return available[0]

    # -------------------------------------------------------------------------
    # Completion Methods
    # -------------------------------------------------------------------------

    async def complete(
        self,
        messages: list[Message],
        provider: ModelProvider | None = None,
        model: str | None = None,
        **kwargs: Any,
    ) -> CompletionResponse:
        """
        Generate completion using specified or selected provider.

        Args:
            messages: Conversation messages
            provider: Specific provider (or auto-select)
            model: Model override
            **kwargs: Provider-specific options

        Returns:
            CompletionResponse
        """
        provider = provider or self._select_provider()

        # Enterprise hardening: Check circuit breaker before attempting
        if not self.circuit_breaker.is_available(provider):
            record_llm_usage(
                provider=provider.value,
                model=model or self.configs[provider].default_model,
                success=False,
                error="circuit_breaker_open",
            )
            raise LLMError(
                f"Provider {provider.value} temporarily unavailable (circuit breaker OPEN)",
                details={"circuit_breaker_state": self.circuit_breaker.get_status()},
            )

        client = self._get_client(provider)

        config = self.configs[provider]
        model = model or config.default_model

        with _tracer.start_as_current_span("llm.complete") as span:
            span.set_attribute("llm.provider", provider.value)
            span.set_attribute("llm.model", model)
            span.set_attribute("llm.message_count", len(messages))
            try:
                response = await client.complete(messages, model=model, **kwargs)
                # Record success
                self.circuit_breaker.record_success(provider)
                span.set_attribute("llm.input_tokens", response.input_tokens)
                span.set_attribute("llm.output_tokens", response.output_tokens)
                span.set_attribute("llm.latency_ms", response.latency_ms)
                record_llm_usage(
                    provider=provider.value,
                    model=response.model,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    total_tokens=response.total_tokens,
                    latency_ms=response.latency_ms,
                    success=True,
                )
                return response
            except Exception as e:
                # Record failure
                self.circuit_breaker.record_failure(provider)
                span.record_exception(e)
                record_llm_usage(
                    provider=provider.value,
                    model=model,
                    success=False,
                    error=str(e),
                )
                raise

    async def complete_with_fallback(
        self,
        messages: list[Message],
        providers: list[ModelProvider] | None = None,
        **kwargs: Any,
    ) -> CompletionResponse:
        """
        Generate completion with automatic fallback.

        Tries providers in order until one succeeds.
        Enterprise hardening: Skips providers with open circuit breakers.

        Args:
            messages: Conversation messages
            providers: Ordered list of providers to try
            **kwargs: Provider-specific options

        Returns:
            CompletionResponse from first successful provider
        """
        providers = providers or [
            p for p, c in sorted(self.configs.items(), key=lambda x: x[1].priority) if c.enabled
        ]

        # Filter out providers with open circuits
        available_providers = [p for p in providers if self.circuit_breaker.is_available(p)]

        # Add LiteLLM as universal last-resort fallback
        if (
            ModelProvider.LITELLM in self.configs
            and ModelProvider.LITELLM not in available_providers
            and self.circuit_breaker.is_available(ModelProvider.LITELLM)
        ):
            available_providers.append(ModelProvider.LITELLM)

        if not available_providers:
            raise LLMError(
                "No providers available (all circuit breakers OPEN)",
                details={"circuit_breaker_status": self.circuit_breaker.get_status()},
            )

        last_error: Exception | None = None

        for provider in available_providers:
            try:
                return await self.complete(messages, provider=provider, **kwargs)
            except Exception as e:
                logger.warning(f"Provider {provider.value} failed: {e}")
                last_error = e
                continue

        raise LLMError(
            f"All available providers failed. Last error: {last_error}",
            details={
                "providers_tried": [p.value for p in available_providers],
                "circuit_breaker_status": self.circuit_breaker.get_status(),
            },
        )

    async def complete_with_agreement(
        self,
        messages: list[Message],
        primary: ModelProvider = ModelProvider.ANTHROPIC,
        secondary: ModelProvider = ModelProvider.OPENAI,
        agreement_threshold: float = 0.7,
        **kwargs: Any,
    ) -> tuple[CompletionResponse, float]:
        """
        2-LLM Agreement Architecture.

        Generates completions from two providers and measures agreement.
        Useful for validation and increasing confidence.

        Args:
            messages: Conversation messages
            primary: Primary provider
            secondary: Secondary provider for validation
            agreement_threshold: Minimum similarity for agreement
            **kwargs: Provider-specific options

        Returns:
            Tuple of (primary_response, agreement_score)
        """
        # Run both completions concurrently
        primary_task = self.complete(messages, provider=primary, **kwargs)
        secondary_task = self.complete(messages, provider=secondary, **kwargs)

        primary_response, secondary_response = await asyncio.gather(primary_task, secondary_task)

        # Calculate agreement score (simple word overlap for now)
        agreement_score = self._calculate_agreement(
            primary_response.content,
            secondary_response.content,
        )

        logger.info(
            f"2-LLM Agreement: {primary.value} vs {secondary.value} = {agreement_score:.2f}"
        )

        return primary_response, agreement_score

    def _calculate_agreement(self, text1: str, text2: str) -> float:
        """
        Calculate agreement score between two texts.

        Simple Jaccard similarity on words.
        """
        if not text1 or not text2:
            return 0.0

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------

    def get_available_providers(self) -> list[ModelProvider]:
        """Get list of enabled providers."""
        return [p for p, c in self.configs.items() if c.enabled]

    def enable_provider(self, provider: ModelProvider) -> None:
        """Enable a provider."""
        if provider in self.configs:
            self.configs[provider].enabled = True

    def disable_provider(self, provider: ModelProvider) -> None:
        """Disable a provider."""
        if provider in self.configs:
            self.configs[provider].enabled = False

    def estimate_cost(
        self,
        provider: ModelProvider,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Estimate cost for a completion."""
        config = self.configs.get(provider)
        if not config:
            return 0.0

        input_cost = (input_tokens / 1000) * config.input_price
        output_cost = (output_tokens / 1000) * config.output_price
        return input_cost + output_cost


# =============================================================================
# Convenience Functions
# =============================================================================


_default_router: LLMRouter | None = None


def get_router() -> LLMRouter:
    """Get default router instance."""
    global _default_router
    if _default_router is None:
        _default_router = LLMRouter()
    return _default_router


async def complete(
    messages: list[Message],
    provider: ModelProvider | None = None,
    **kwargs: Any,
) -> CompletionResponse:
    """Convenience function for quick completions."""
    router = get_router()
    return await router.complete(messages, provider=provider, **kwargs)


__all__ = [
    "ProviderConfig",
    "PROVIDER_CONFIGS",
    "RoutingStrategy",
    "LLMRouter",
    "get_router",
    "complete",
]
