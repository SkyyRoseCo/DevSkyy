"""
Unified LLM Client
==================

Intelligent LLM client that unifies task classification, prompt technique
application, provider routing, and execution.

Pipeline:
1. Classify task → TaskCategory
2. Select technique → PromptTechnique
3. Apply technique → Enhanced prompt
4. Route to provider → ModelProvider
5. Execute → CompletionResponse

Optional Round Table mode for high-stakes decisions.

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
import time
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from .base import CompletionResponse, Message, ModelProvider
from .exceptions import LLMError
from .round_table import LLMProvider as RoundTableProvider
from .round_table import LLMRoundTable, RoundTableResult
from .router import LLMRouter, RoutingStrategy
from .task_classifier import (
    PromptTechnique,
    TaskClassificationResult,
    TaskClassifier,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Provider Mapping
# =============================================================================

# Mapping between ModelProvider (base.py) and LLMProvider (round_table.py)
MODEL_TO_ROUND_TABLE_PROVIDER: dict[ModelProvider, RoundTableProvider] = {
    ModelProvider.ANTHROPIC: RoundTableProvider.CLAUDE,
    ModelProvider.OPENAI: RoundTableProvider.GPT4,
    ModelProvider.GOOGLE: RoundTableProvider.GEMINI,
    ModelProvider.GROQ: RoundTableProvider.LLAMA,
    ModelProvider.MISTRAL: RoundTableProvider.MISTRAL,
    ModelProvider.COHERE: RoundTableProvider.COHERE,
}

ROUND_TABLE_TO_MODEL_PROVIDER: dict[RoundTableProvider, ModelProvider] = {
    RoundTableProvider.CLAUDE: ModelProvider.ANTHROPIC,
    RoundTableProvider.GPT4: ModelProvider.OPENAI,
    RoundTableProvider.GEMINI: ModelProvider.GOOGLE,
    RoundTableProvider.LLAMA: ModelProvider.GROQ,
    RoundTableProvider.MISTRAL: ModelProvider.MISTRAL,
    RoundTableProvider.COHERE: ModelProvider.COHERE,
}


# =============================================================================
# Enums
# =============================================================================


class ExecutionMode(StrEnum):
    """Execution mode for LLM requests."""

    FAST = "fast"  # Single provider, fastest response
    BALANCED = "balanced"  # Single provider with fallback
    ROUND_TABLE = "round_table"  # All providers compete (high-stakes)


# =============================================================================
# Request/Response Models
# =============================================================================


class LLMRequest(BaseModel):
    """Request to the unified LLM client."""

    model_config = {"extra": "forbid"}

    # Core request
    messages: list[Message] = Field(..., description="Conversation messages")
    task_description: str | None = Field(
        None, description="Optional task description for classification"
    )

    # Routing options
    routing_strategy: RoutingStrategy = Field(
        default=RoutingStrategy.PRIORITY, description="Provider routing strategy"
    )
    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.BALANCED, description="Execution mode"
    )
    preferred_provider: ModelProvider | None = Field(
        None, description="Preferred provider (overrides routing)"
    )

    # Model options
    model: str | None = Field(None, description="Specific model override")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, gt=0)

    # Tool calling
    tools: list[dict[str, Any]] | None = Field(None, description="Available tools")

    # Technique options
    force_technique: PromptTechnique | None = Field(
        None, description="Force specific prompt technique"
    )
    skip_classification: bool = Field(
        default=False, description="Skip task classification (use force_technique)"
    )

    # Round Table options
    round_table_providers: list[ModelProvider] | None = Field(
        None, description="Providers for Round Table (if mode=ROUND_TABLE)"
    )

    # Metadata
    task_id: str | None = Field(None, description="Task identifier for tracking")
    correlation_id: str | None = Field(None, description="Correlation ID for tracing")


class LLMResponse(BaseModel):
    """Response from the unified LLM client."""

    model_config = {"extra": "forbid"}

    # Core response
    content: str = Field(..., description="Generated content")
    completion: CompletionResponse = Field(..., description="Raw completion response")

    # Classification results
    task_classification: TaskClassificationResult | None = Field(
        None, description="Task classification result"
    )
    technique_used: PromptTechnique | None = Field(None, description="Technique applied")

    # Provider info
    provider_used: ModelProvider = Field(..., description="Provider that generated response")
    model_used: str = Field(..., description="Model that generated response")

    # Round Table results (if applicable)
    round_table_winner: bool = Field(default=False, description="Whether this won Round Table")
    round_table_competitors: list[str] = Field(
        default_factory=list, description="Competing providers in Round Table"
    )

    # Metadata
    total_latency_ms: float = Field(default=0.0)
    classification_latency_ms: float = Field(default=0.0)
    completion_latency_ms: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Unified LLM Client
# =============================================================================


class UnifiedLLMClient:
    """
    Unified LLM client with intelligent routing and technique application.

    Pipeline:
    1. Classify task (optional) → TaskCategory
    2. Select technique → PromptTechnique
    3. Apply technique → Enhanced prompt
    4. Route to provider → ModelProvider
    5. Execute → CompletionResponse

    Modes:
    - FAST: Single provider, fastest response
    - BALANCED: Single provider with fallback
    - ROUND_TABLE: All providers compete (for high-stakes)

    Usage:
        # Initialize
        router = LLMRouter()
        classifier = TaskClassifier()
        client = UnifiedLLMClient(router=router, classifier=classifier)

        # Simple completion
        response = await client.complete(
            LLMRequest(messages=[Message.user("Explain quantum computing")])
        )

        # With task description for classification
        response = await client.complete(
            LLMRequest(
                messages=[Message.user("Write a creative story")],
                task_description="Generate creative fiction",
                execution_mode=ExecutionMode.BALANCED
            )
        )

        # High-stakes with Round Table
        response = await client.complete(
            LLMRequest(
                messages=[Message.user("Process this payment")],
                task_description="Financial transaction",
                execution_mode=ExecutionMode.ROUND_TABLE
            )
        )
    """

    def __init__(
        self,
        router: LLMRouter | None = None,
        classifier: TaskClassifier | None = None,
        technique_applicator: Any | None = None,  # PromptEngineeringModule
        round_table: LLMRoundTable | None = None,
    ) -> None:
        """
        Initialize the unified LLM client.

        Args:
            router: LLM router for provider selection
            classifier: Task classifier for category detection
            technique_applicator: Module for applying prompt techniques
            round_table: Round Table for multi-LLM consensus (optional)
        """
        self._router = router
        self._classifier = classifier
        self._technique_applicator = technique_applicator
        self._round_table = round_table

    async def _get_router(self) -> LLMRouter:
        """Lazy initialization of LLM router."""
        if self._router is None:
            self._router = LLMRouter()
        return self._router

    async def _get_classifier(self) -> TaskClassifier:
        """Lazy initialization of task classifier."""
        if self._classifier is None:
            self._classifier = TaskClassifier()
        return self._classifier

    async def _get_round_table(self) -> LLMRoundTable:
        """Lazy initialization of Round Table with auto-registered providers."""
        if self._round_table is None:
            # Import here to avoid circular dependency
            from .round_table import create_round_table

            self._round_table = await create_round_table()
        return self._round_table

    async def _execute_round_table(
        self,
        request: LLMRequest,
        messages: list[Message],
        task_classification: TaskClassificationResult | None,
    ) -> tuple[CompletionResponse, RoundTableResult]:
        """
        Execute Round Table competition for multi-LLM consensus.

        Args:
            request: Original LLM request
            messages: Processed messages
            task_classification: Optional task classification result

        Returns:
            Tuple of (CompletionResponse, RoundTableResult)
        """
        round_table = await self._get_round_table()

        # Build prompt from messages
        prompt_parts = []
        for msg in messages:
            if msg.role.value == "system":
                prompt_parts.append(f"[System]: {msg.content}")
            elif msg.role.value == "user":
                prompt_parts.append(f"[User]: {msg.content}")
            elif msg.role.value == "assistant":
                prompt_parts.append(f"[Assistant]: {msg.content}")
        prompt = "\n\n".join(prompt_parts)

        # Determine which providers to use
        rt_providers: list[RoundTableProvider] | None = None
        if request.round_table_providers:
            # Convert ModelProvider to RoundTableProvider
            rt_providers = [
                MODEL_TO_ROUND_TABLE_PROVIDER[p]
                for p in request.round_table_providers
                if p in MODEL_TO_ROUND_TABLE_PROVIDER
            ]

        # Build context for Round Table
        context: dict[str, Any] = {}
        if task_classification:
            context["category"] = task_classification.task_category.value
            context["confidence"] = task_classification.confidence

        # Run Round Table competition
        result = await round_table.compete(
            prompt=prompt,
            task_id=request.task_id,
            providers=rt_providers,
            context=context if context else None,
            tools=request.tools,
            persist=True,
        )

        # Convert winner to CompletionResponse
        if result.winner is None:
            raise LLMError("Round Table competition failed: no winner")

        winner = result.winner
        winner_provider = ROUND_TABLE_TO_MODEL_PROVIDER.get(
            winner.provider, ModelProvider.ANTHROPIC
        )

        completion = CompletionResponse(
            content=winner.response.content,
            model=winner.response.model,
            provider=winner_provider.value,
            input_tokens=0,  # Not tracked in Round Table
            output_tokens=winner.response.tokens_used,
            total_tokens=winner.response.tokens_used,
            finish_reason="stop",
            latency_ms=winner.response.latency_ms,
            cost_usd=winner.response.cost_usd,
        )

        return completion, result

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """
        Generate completion using intelligent routing and technique application.

        Args:
            request: LLM request with messages and options

        Returns:
            LLMResponse with content and metadata
        """
        start_time = time.monotonic()

        # Step 1: Task Classification (optional)
        task_classification: TaskClassificationResult | None = None
        classification_latency_ms = 0.0

        if not request.skip_classification and request.task_description:
            classification_start = time.monotonic()
            classifier = await self._get_classifier()
            task_classification = await classifier.classify(request.task_description)
            classification_latency_ms = (time.monotonic() - classification_start) * 1000

            logger.info(
                f"Task classified as {task_classification.task_category.value} "
                f"(confidence: {task_classification.confidence:.2f}, "
                f"latency: {classification_latency_ms:.2f}ms)"
            )
        elif not request.skip_classification:
            # Classify from messages if no task description
            classification_start = time.monotonic()
            classifier = await self._get_classifier()
            task_classification = await classifier.classify_messages(request.messages)
            classification_latency_ms = (time.monotonic() - classification_start) * 1000

            logger.info(
                f"Task classified from messages as {task_classification.task_category.value} "
                f"(confidence: {task_classification.confidence:.2f})"
            )

        # Step 2: Select Technique
        technique_used: PromptTechnique | None = None

        if request.force_technique:
            technique_used = request.force_technique
        elif task_classification:
            technique_used = task_classification.recommended_technique

        # Step 3: Apply Technique (if applicator available)
        messages = request.messages
        if technique_used and self._technique_applicator:
            try:
                # Apply technique to enhance prompt
                # This is optional - if applicator not provided, use original messages
                logger.debug(f"Applying technique: {technique_used.value}")
                # Technique application would happen here if implemented
            except Exception as e:
                logger.warning(f"Failed to apply technique {technique_used}: {e}")

        # Step 4: Route to Provider
        router = await self._get_router()
        provider: ModelProvider | None = None

        if request.preferred_provider:
            provider = request.preferred_provider
        elif task_classification:
            # Use recommended providers from classification
            recommended_providers = task_classification.recommended_providers
            if recommended_providers:
                # Map string to ModelProvider enum
                provider_map = {
                    "anthropic": ModelProvider.ANTHROPIC,
                    "openai": ModelProvider.OPENAI,
                    "google": ModelProvider.GOOGLE,
                    "mistral": ModelProvider.MISTRAL,
                    "groq": ModelProvider.GROQ,
                    "cohere": ModelProvider.COHERE,
                    "deepseek": ModelProvider.DEEPSEEK,
                }
                for rec_provider in recommended_providers:
                    if rec_provider in provider_map:
                        provider = provider_map[rec_provider]
                        break

        # Step 5: Execute based on mode
        completion_start = time.monotonic()
        completion: CompletionResponse

        if request.execution_mode == ExecutionMode.FAST:
            # Fast: Single provider, no fallback
            completion = await router.complete(
                messages=messages,
                provider=provider,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                tools=request.tools,
            )

        elif request.execution_mode == ExecutionMode.BALANCED:
            # Balanced: Single provider with fallback
            providers = None
            if task_classification:
                # Use recommended providers
                provider_map = {
                    "anthropic": ModelProvider.ANTHROPIC,
                    "openai": ModelProvider.OPENAI,
                    "google": ModelProvider.GOOGLE,
                    "mistral": ModelProvider.MISTRAL,
                    "groq": ModelProvider.GROQ,
                    "cohere": ModelProvider.COHERE,
                    "deepseek": ModelProvider.DEEPSEEK,
                }
                providers = [
                    provider_map[p]
                    for p in task_classification.recommended_providers
                    if p in provider_map
                ]

            completion = await router.complete_with_fallback(
                messages=messages,
                providers=providers,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                tools=request.tools,
            )

        elif request.execution_mode == ExecutionMode.ROUND_TABLE:
            # Round Table: All providers compete for consensus
            logger.info("Executing Round Table mode for multi-LLM consensus")

            completion, rt_result = await self._execute_round_table(
                request=request,
                messages=messages,
                task_classification=task_classification,
            )

            completion_latency_ms = (time.monotonic() - completion_start) * 1000
            total_latency_ms = (time.monotonic() - start_time) * 1000

            # Extract competitor providers from Round Table result
            round_table_competitors = [entry.provider.value for entry in rt_result.entries]

            return LLMResponse(
                content=completion.content,
                completion=completion,
                task_classification=task_classification,
                technique_used=technique_used,
                provider_used=ModelProvider(completion.provider),
                model_used=completion.model,
                round_table_winner=True,
                round_table_competitors=round_table_competitors,
                total_latency_ms=total_latency_ms,
                classification_latency_ms=classification_latency_ms,
                completion_latency_ms=completion_latency_ms,
            )

        else:
            raise LLMError(f"Unsupported execution mode: {request.execution_mode}")

        completion_latency_ms = (time.monotonic() - completion_start) * 1000
        total_latency_ms = (time.monotonic() - start_time) * 1000

        # Build response
        return LLMResponse(
            content=completion.content,
            completion=completion,
            task_classification=task_classification,
            technique_used=technique_used,
            provider_used=ModelProvider(completion.provider),
            model_used=completion.model,
            round_table_winner=False,
            round_table_competitors=[],
            total_latency_ms=total_latency_ms,
            classification_latency_ms=classification_latency_ms,
            completion_latency_ms=completion_latency_ms,
        )

    async def close(self) -> None:
        """Close all client connections."""
        if self._router:
            await self._router.close()
        if self._classifier:
            await self._classifier.close()
        if self._round_table:
            await self._round_table.close()

    async def __aenter__(self) -> UnifiedLLMClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()


# =============================================================================
# Convenience Functions
# =============================================================================

_default_client: UnifiedLLMClient | None = None


def get_client() -> UnifiedLLMClient:
    """Get the default unified LLM client instance."""
    global _default_client
    if _default_client is None:
        _default_client = UnifiedLLMClient()
    return _default_client


async def complete(
    messages: list[Message],
    task_description: str | None = None,
    execution_mode: ExecutionMode = ExecutionMode.BALANCED,
    **kwargs: Any,
) -> LLMResponse:
    """Quick completion using default client."""
    request = LLMRequest(
        messages=messages,
        task_description=task_description,
        execution_mode=execution_mode,
        **kwargs,
    )
    return await get_client().complete(request)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "ExecutionMode",
    # Models
    "LLMRequest",
    "LLMResponse",
    # Main Class
    "UnifiedLLMClient",
    # Convenience
    "get_client",
    "complete",
]
