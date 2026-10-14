"""
Task Classification for LLM Routing
====================================

Fast task classification using Groq's sub-100ms inference to determine:
- Task category (reasoning/creative/search/qa/etc.)
- Recommended prompt technique (CoT/ToT/ReAct/etc.)
- Optimal LLM provider selection

This classifier is the first step in the unified LLM client pipeline:
classify task → apply technique → route to provider → execute

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import logging
import time
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from .base import Message
from .classification import ClassificationConfig, ClassificationType, GroqFastClassifier
from .exceptions import LLMError

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================


class TaskCategory(StrEnum):
    """Task categories for intelligent routing and technique selection."""

    REASONING = "reasoning"
    CLASSIFICATION = "classification"
    CREATIVE = "creative"
    SEARCH = "search"
    QA = "qa"
    EXTRACTION = "extraction"
    MODERATION = "moderation"
    GENERATION = "generation"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    DEBUGGING = "debugging"
    OPTIMIZATION = "optimization"
    CODE = "code"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"


class PromptTechnique(StrEnum):
    """Recommended prompt engineering techniques."""

    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    REACT = "react"
    RAG = "rag"
    FEW_SHOT = "few_shot"
    STRUCTURED_OUTPUT = "structured_output"
    CONSTITUTIONAL = "constitutional"
    ROLE_BASED = "role_based"
    SELF_CONSISTENCY = "self_consistency"
    ENSEMBLE = "ensemble"


# =============================================================================
# Technique Mapping
# =============================================================================

# Maps TaskCategory to recommended PromptTechnique
TECHNIQUE_MAPPING: dict[TaskCategory, PromptTechnique] = {
    TaskCategory.REASONING: PromptTechnique.CHAIN_OF_THOUGHT,
    TaskCategory.CLASSIFICATION: PromptTechnique.FEW_SHOT,
    TaskCategory.CREATIVE: PromptTechnique.TREE_OF_THOUGHTS,
    TaskCategory.SEARCH: PromptTechnique.REACT,
    TaskCategory.QA: PromptTechnique.RAG,
    TaskCategory.EXTRACTION: PromptTechnique.STRUCTURED_OUTPUT,
    TaskCategory.MODERATION: PromptTechnique.CONSTITUTIONAL,
    TaskCategory.GENERATION: PromptTechnique.ROLE_BASED,
    TaskCategory.ANALYSIS: PromptTechnique.CHAIN_OF_THOUGHT,
    TaskCategory.PLANNING: PromptTechnique.TREE_OF_THOUGHTS,
    TaskCategory.DEBUGGING: PromptTechnique.REACT,
    TaskCategory.OPTIMIZATION: PromptTechnique.SELF_CONSISTENCY,
    TaskCategory.CODE: PromptTechnique.REACT,
    TaskCategory.SUMMARIZATION: PromptTechnique.CHAIN_OF_THOUGHT,
    TaskCategory.TRANSLATION: PromptTechnique.STRUCTURED_OUTPUT,
}

# Provider preferences by task category
TASK_PROVIDER_PREFERENCES: dict[TaskCategory, list[str]] = {
    TaskCategory.REASONING: ["anthropic", "openai", "google"],
    TaskCategory.CREATIVE: ["openai", "anthropic", "google"],
    TaskCategory.CODE: ["openai", "anthropic", "groq"],
    TaskCategory.ANALYSIS: ["anthropic", "google", "openai"],
    TaskCategory.SEARCH: ["google", "openai", "anthropic"],
    TaskCategory.CLASSIFICATION: ["openai", "anthropic", "groq"],
    TaskCategory.QA: ["anthropic", "google", "openai"],
    TaskCategory.EXTRACTION: ["openai", "anthropic"],
    TaskCategory.MODERATION: ["anthropic", "openai"],
    TaskCategory.GENERATION: ["openai", "anthropic", "google"],
    TaskCategory.PLANNING: ["anthropic", "openai"],
    TaskCategory.DEBUGGING: ["openai", "anthropic", "groq"],
    TaskCategory.OPTIMIZATION: ["anthropic", "openai"],
    TaskCategory.SUMMARIZATION: ["anthropic", "google"],
    TaskCategory.TRANSLATION: ["google", "openai"],
}


# =============================================================================
# Pydantic Models
# =============================================================================


class TaskClassificationResult(BaseModel):
    """Result from task classification."""

    model_config = {"extra": "forbid"}

    task_category: TaskCategory = Field(..., description="Classified task category")
    recommended_technique: PromptTechnique = Field(..., description="Recommended prompt technique")
    recommended_providers: list[str] = Field(
        default_factory=list, description="Ordered list of recommended providers"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")
    reasoning: str | None = Field(None, description="Classification reasoning")

    # Metadata
    latency_ms: float = Field(default=0.0)
    cached: bool = Field(default=False)
    classifier_model: str = Field(default="llama-3.3-70b-versatile")


class TaskClassifierConfig(BaseModel):
    """Configuration for the task classifier."""

    model_config = {"extra": "forbid"}

    # Classifier settings
    model: str = Field(default="llama-3.3-70b-versatile")
    temperature: float = Field(default=0.1, ge=0.0, le=1.0)
    max_tokens: int = Field(default=256)

    # Cache settings
    cache_enabled: bool = Field(default=True)
    cache_ttl_seconds: int = Field(default=3600)
    cache_max_size: int = Field(default=1000)

    # Include reasoning in classification
    include_reasoning: bool = Field(default=False)


# =============================================================================
# Classification Prompt
# =============================================================================

TASK_CLASSIFICATION_PROMPT = """Analyze this task description and classify it into the most appropriate category.

Task Description: "{task_description}"

Available Categories:
- reasoning: Complex logical reasoning, problem-solving, step-by-step analysis
- classification: Categorizing data, labeling, sorting into predefined groups
- creative: Content creation, storytelling, artistic generation, brainstorming
- search: Information retrieval, finding specific data, web searches
- qa: Question answering, factual queries, knowledge lookup
- extraction: Extracting structured data from text, parsing, data mining
- moderation: Content moderation, safety checks, filtering
- generation: Generating structured content, reports, documents
- analysis: Data analysis, insights, trends, patterns
- planning: Project planning, scheduling, task breakdown
- debugging: Code debugging, troubleshooting, error analysis
- optimization: Performance optimization, efficiency improvements
- code: Code generation, refactoring, programming tasks
- summarization: Summarizing text, condensing information
- translation: Language translation, localization

Respond with JSON only:
{{"category": "<category>", "confidence": <0.0-1.0>, "reasoning": "<brief explanation>"}}"""


# =============================================================================
# Task Classifier Class
# =============================================================================


class TaskClassifier:
    """
    Fast task classification for intelligent LLM routing.

    Uses Groq's sub-100ms inference to classify tasks and recommend:
    - Task category
    - Prompt engineering technique
    - Optimal LLM providers

    This is the first step in the unified LLM client pipeline.

    Usage:
        classifier = TaskClassifier()

        # Classify a task
        result = await classifier.classify(
            "Write a step-by-step solution for solving quadratic equations"
        )
        # Returns: TaskCategory.REASONING, PromptTechnique.CHAIN_OF_THOUGHT

        # With custom messages
        result = await classifier.classify_messages([
            Message.system("You are a helpful assistant"),
            Message.user("Generate a creative story about a robot")
        ])
        # Returns: TaskCategory.CREATIVE, PromptTechnique.TREE_OF_THOUGHTS
    """

    def __init__(
        self,
        config: TaskClassifierConfig | None = None,
        groq_classifier: GroqFastClassifier | None = None,
    ) -> None:
        """
        Initialize the task classifier.

        Args:
            config: Classifier configuration
            groq_classifier: Optional pre-configured Groq classifier
        """
        self.config = config or TaskClassifierConfig()
        self._groq_classifier = groq_classifier
        self._cache: dict[str, tuple[TaskClassificationResult, float]] = {}

    async def _get_groq_classifier(self) -> GroqFastClassifier:
        """Lazy initialization of Groq classifier."""
        if self._groq_classifier is None:
            groq_config = ClassificationConfig(
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                cache_enabled=self.config.cache_enabled,
                cache_ttl_seconds=self.config.cache_ttl_seconds,
                cache_max_size=self.config.cache_max_size,
                include_reasoning=self.config.include_reasoning,
            )
            self._groq_classifier = GroqFastClassifier(config=groq_config)
        return self._groq_classifier

    def _generate_cache_key(self, task_description: str) -> str:
        """Generate deterministic cache key."""
        return hashlib.sha256(task_description.strip().lower().encode()).hexdigest()[:16]

    def _check_cache(self, cache_key: str) -> TaskClassificationResult | None:
        """Check cache for existing result."""
        if not self.config.cache_enabled:
            return None

        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if time.monotonic() - timestamp < self.config.cache_ttl_seconds:
                result.cached = True
                return result
            else:
                del self._cache[cache_key]

        return None

    def _store_cache(self, cache_key: str, result: TaskClassificationResult) -> None:
        """Store result in cache with TTL."""
        if not self.config.cache_enabled:
            return

        # LRU eviction
        if len(self._cache) >= self.config.cache_max_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        self._cache[cache_key] = (result, time.monotonic())

    async def classify(
        self,
        task_description: str,
        include_reasoning: bool | None = None,
    ) -> TaskClassificationResult:
        """
        Classify a task description into a category and recommend technique.

        Args:
            task_description: Description of the task to classify
            include_reasoning: Override config for reasoning inclusion

        Returns:
            TaskClassificationResult with category, technique, and providers
        """
        # Generate cache key
        cache_key = self._generate_cache_key(task_description)

        # Check cache
        cached_result = self._check_cache(cache_key)
        if cached_result:
            return cached_result

        # Get Groq classifier
        groq_classifier = await self._get_groq_classifier()

        # Build prompt
        prompt = TASK_CLASSIFICATION_PROMPT.format(task_description=task_description)

        start_time = time.monotonic()

        try:
            # Call Groq for classification
            response = await groq_classifier._classify_with_groq(
                prompt=prompt,
                classification_type=ClassificationType.CATEGORY,
                expected_labels=[cat.value for cat in TaskCategory],
            )

            latency_ms = (time.monotonic() - start_time) * 1000

            # The classifier only returns labels from expected_labels.
            task_category = TaskCategory(response.label)

            # Get recommended technique
            recommended_technique = TECHNIQUE_MAPPING.get(
                task_category, PromptTechnique.CHAIN_OF_THOUGHT
            )

            # Get recommended providers
            recommended_providers = TASK_PROVIDER_PREFERENCES.get(
                task_category, ["anthropic", "openai", "google"]
            )

            # Build result
            result = TaskClassificationResult(
                task_category=task_category,
                recommended_technique=recommended_technique,
                recommended_providers=recommended_providers,
                confidence=response.confidence,
                reasoning=response.reasoning,
                latency_ms=latency_ms,
                cached=False,
                classifier_model=response.model,
            )

            # Cache result
            self._store_cache(cache_key, result)

            return result

        except Exception as e:
            logger.error(f"Task classification failed: {e}")
            raise LLMError(
                f"Task classification failed: {e}",
                provider="groq",
                model=self.config.model,
            )

    async def classify_messages(
        self,
        messages: list[Message],
        include_reasoning: bool | None = None,
    ) -> TaskClassificationResult:
        """
        Classify task from conversation messages.

        Extracts task description from messages and classifies.

        Args:
            messages: Conversation messages
            include_reasoning: Override config for reasoning inclusion

        Returns:
            TaskClassificationResult
        """
        # Extract task description from messages
        # Combine user messages for classification
        user_messages = [msg.content for msg in messages if msg.role.value == "user"]
        task_description = " ".join(user_messages)

        if not task_description:
            # Fallback: use all message content
            task_description = " ".join(msg.content for msg in messages)

        return await self.classify(task_description, include_reasoning)

    def get_technique_for_category(self, category: TaskCategory) -> PromptTechnique:
        """Get recommended prompt technique for a task category."""
        return TECHNIQUE_MAPPING.get(category, PromptTechnique.CHAIN_OF_THOUGHT)

    def get_providers_for_category(self, category: TaskCategory) -> list[str]:
        """Get recommended providers for a task category."""
        return TASK_PROVIDER_PREFERENCES.get(category, ["anthropic", "openai", "google"])

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache performance statistics."""
        return {
            "cache_size": len(self._cache),
            "cache_max_size": self.config.cache_max_size,
            "cache_enabled": self.config.cache_enabled,
        }

    def clear_cache(self) -> None:
        """Clear the classification cache."""
        self._cache.clear()

    async def close(self) -> None:
        """Close the Groq classifier connection."""
        if self._groq_classifier:
            await self._groq_classifier.close()
            self._groq_classifier = None


# =============================================================================
# Convenience Functions
# =============================================================================

_default_classifier: TaskClassifier | None = None


def get_classifier() -> TaskClassifier:
    """Get the default task classifier instance."""
    global _default_classifier
    if _default_classifier is None:
        _default_classifier = TaskClassifier()
    return _default_classifier


async def classify_task(
    task_description: str,
    include_reasoning: bool = False,
) -> TaskClassificationResult:
    """Quick task classification using default classifier."""
    return await get_classifier().classify(task_description, include_reasoning)


async def classify_messages(
    messages: list[Message],
    include_reasoning: bool = False,
) -> TaskClassificationResult:
    """Quick message classification using default classifier."""
    return await get_classifier().classify_messages(messages, include_reasoning)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "TaskCategory",
    "PromptTechnique",
    # Models
    "TaskClassificationResult",
    "TaskClassifierConfig",
    # Main Class
    "TaskClassifier",
    # Convenience
    "get_classifier",
    "classify_task",
    "classify_messages",
    # Mappings
    "TECHNIQUE_MAPPING",
    "TASK_PROVIDER_PREFERENCES",
]
