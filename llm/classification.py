"""
Groq Fast Classification Helper
================================

Fast classification utility leveraging Groq's sub-100ms inference.

Use cases:
- Intent classification
- Category detection
- Sentiment analysis
- Language detection

Complements DeepSeek (generation) and Claude (verification) in the LLM pipeline.

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from .base import Message
from .exceptions import LLMError
from .providers.groq import GroqClient

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================


class ClassificationType(StrEnum):
    """Supported classification types."""

    INTENT = "intent"
    CATEGORY = "category"
    SENTIMENT = "sentiment"
    LANGUAGE = "language"
    CUSTOM = "custom"


class SentimentLabel(StrEnum):
    """Standard sentiment labels."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


# =============================================================================
# Pydantic Models
# =============================================================================


class ClassificationExample(BaseModel):
    """Few-shot example for classification."""

    model_config = {"extra": "forbid"}

    text: str = Field(..., description="Example input text")
    label: str = Field(..., description="Classification label")
    reasoning: str | None = Field(None, description="Optional reasoning for the label")


class ClassificationResult(BaseModel):
    """Result of a classification operation."""

    model_config = {"extra": "forbid"}

    label: str = Field(..., description="Primary classification label")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    all_scores: dict[str, float] = Field(
        default_factory=dict, description="Scores for all possible labels"
    )
    reasoning: str | None = Field(None, description="Chain-of-thought reasoning")

    # Metadata
    classification_type: ClassificationType = Field(...)
    latency_ms: float = Field(default=0.0)
    model: str = Field(default="llama-3.3-70b-versatile")
    cached: bool = Field(default=False)

    # Raw LLM response (for debugging)
    raw_response: str | None = Field(None, exclude=True)


class ClassificationConfig(BaseModel):
    """Configuration for the classifier."""

    model_config = {"extra": "forbid"}

    # Model settings
    model: str = Field(default="llama-3.3-70b-versatile")
    temperature: float = Field(default=0.1, ge=0.0, le=1.0)
    max_tokens: int = Field(default=256)

    # Cache settings
    cache_enabled: bool = Field(default=True)
    cache_ttl_seconds: int = Field(default=3600)  # 1 hour
    cache_max_size: int = Field(default=1000)

    # Timeout settings
    timeout_seconds: float = Field(default=5.0)

    # Output settings
    include_reasoning: bool = Field(default=False)
    strict_output: bool = Field(default=True)  # Parse JSON strictly


# =============================================================================
# Classification Prompts
# =============================================================================


class ClassificationPrompts:
    """Prompt templates for different classification types."""

    INTENT_PROMPT = """Classify the user's intent from this message.

Message: "{text}"

Available intents: {labels}

Respond with JSON only:
{{"label": "<intent>", "confidence": <0.0-1.0>, "scores": {{<intent>: <score>, ...}}}}"""

    CATEGORY_PROMPT = """Categorize the following text into one of the given categories.

Text: "{text}"

Categories: {labels}

Respond with JSON only:
{{"label": "<category>", "confidence": <0.0-1.0>, "scores": {{<category>: <score>, ...}}}}"""

    SENTIMENT_PROMPT = """Analyze the sentiment of this text.

Text: "{text}"

Possible sentiments: positive, negative, neutral, mixed

Respond with JSON only:
{{"label": "<sentiment>", "confidence": <0.0-1.0>, "scores": {{"positive": <>, "negative": <>, "neutral": <>, "mixed": <>}}}}"""

    LANGUAGE_PROMPT = """Detect the language of this text.

Text: "{text}"

Respond with JSON only:
{{"label": "<ISO 639-1 code>", "confidence": <0.0-1.0>, "language_name": "<full name>"}}"""

    FEW_SHOT_TEMPLATE = """Examples:
{examples}

Now classify:
Text: "{text}"

Labels: {labels}

Respond with JSON only:
{{"label": "<label>", "confidence": <0.0-1.0>, "scores": {{<label>: <score>, ...}}}}"""

    WITH_REASONING = """
First, explain your reasoning briefly, then provide the classification.

{base_prompt}

Respond with JSON only:
{{"reasoning": "<brief explanation>", "label": "<label>", "confidence": <0.0-1.0>, "scores": {{...}}}}"""


# =============================================================================
# Main Classifier Class
# =============================================================================


class GroqFastClassifier:
    """
    Fast classification helper using Groq's sub-100ms inference.

    Designed for:
    - Intent classification (customer support routing)
    - Category detection (content organization)
    - Sentiment analysis (feedback processing)
    - Language detection (i18n routing)
    - Custom classifications with few-shot examples

    Features:
    - Sub-100ms inference with Groq's Llama-3.3-70b
    - Response caching with TTL
    - Few-shot learning support
    - Structured JSON output with confidence scores
    - Fallback to Mistral if Groq unavailable

    Usage:
        classifier = GroqFastClassifier()

        # Intent classification
        result = await classifier.classify_intent(
            "Where is my order?",
            intents=["order_status", "refund", "general_inquiry"]
        )

        # Sentiment analysis
        result = await classifier.analyze_sentiment("I love this product!")

        # Custom classification with examples
        result = await classifier.classify(
            "Looking for winter jackets",
            labels=["browsing", "purchase_intent", "support"],
            examples=[
                ClassificationExample(text="Show me dresses", label="browsing"),
                ClassificationExample(text="I want to buy this now", label="purchase_intent"),
            ]
        )
    """

    def __init__(
        self,
        config: ClassificationConfig | None = None,
        groq_client: GroqClient | None = None,
    ) -> None:
        """
        Initialize the fast classifier.

        Args:
            config: Classification configuration
            groq_client: Optional pre-configured Groq client
        """
        self.config = config or ClassificationConfig()
        self._client = groq_client
        self._cache: dict[str, tuple[ClassificationResult, float]] = {}

    async def _get_client(self) -> GroqClient:
        """Lazy initialization of Groq client."""
        if self._client is None:
            self._client = GroqClient()
        return self._client

    def _generate_cache_key(
        self,
        text: str,
        classification_type: ClassificationType,
        labels: list[str] | None,
        examples_hash: str | None,
    ) -> str:
        """Generate deterministic cache key."""
        components = [
            text.strip().lower(),
            classification_type.value,
            ",".join(sorted(labels)) if labels else "",
            examples_hash or "",
            self.config.model,
        ]
        return hashlib.sha256("|".join(components).encode()).hexdigest()[:16]

    def _check_cache(self, cache_key: str) -> ClassificationResult | None:
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

    def _store_cache(self, cache_key: str, result: ClassificationResult) -> None:
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
        text: str,
        labels: list[str],
        classification_type: ClassificationType = ClassificationType.CUSTOM,
        examples: list[ClassificationExample] | None = None,
        include_reasoning: bool | None = None,
    ) -> ClassificationResult:
        """
        Perform generic classification with optional few-shot examples.

        Args:
            text: Text to classify
            labels: Possible classification labels
            classification_type: Type of classification
            examples: Optional few-shot examples
            include_reasoning: Override config for reasoning inclusion

        Returns:
            ClassificationResult with label, confidence, and scores
        """
        # Generate cache key
        examples_hash = None
        if examples:
            examples_hash = hashlib.sha256(
                "|".join(f"{e.text}:{e.label}" for e in examples).encode()
            ).hexdigest()[:8]

        cache_key = self._generate_cache_key(text, classification_type, labels, examples_hash)

        # Check cache
        cached_result = self._check_cache(cache_key)
        if cached_result:
            return cached_result

        # Build prompt
        include_reasoning = (
            include_reasoning if include_reasoning is not None else self.config.include_reasoning
        )

        if examples:
            examples_str = "\n".join(f'Text: "{e.text}" -> Label: "{e.label}"' for e in examples)
            prompt = ClassificationPrompts.FEW_SHOT_TEMPLATE.format(
                examples=examples_str,
                text=text,
                labels=", ".join(labels),
            )
        else:
            prompt = ClassificationPrompts.CATEGORY_PROMPT.format(
                text=text,
                labels=", ".join(labels),
            )

        if include_reasoning:
            prompt = ClassificationPrompts.WITH_REASONING.format(base_prompt=prompt)

        # Call Groq
        result = await self._classify_with_groq(
            prompt=prompt,
            classification_type=classification_type,
            expected_labels=labels,
        )

        # Cache result
        self._store_cache(cache_key, result)

        return result

    async def classify_intent(
        self,
        text: str,
        intents: list[str],
        examples: list[ClassificationExample] | None = None,
    ) -> ClassificationResult:
        """
        Classify user intent for routing purposes.

        Optimized for customer support and chat applications.

        Args:
            text: User message to classify
            intents: List of possible intents
            examples: Optional few-shot examples

        Returns:
            ClassificationResult with detected intent
        """
        return await self.classify(
            text=text,
            labels=intents,
            classification_type=ClassificationType.INTENT,
            examples=examples,
        )

    async def classify_category(
        self,
        text: str,
        categories: list[str],
        examples: list[ClassificationExample] | None = None,
    ) -> ClassificationResult:
        """
        Categorize text into predefined categories.

        Useful for content organization and routing.

        Args:
            text: Text to categorize
            categories: List of possible categories
            examples: Optional few-shot examples

        Returns:
            ClassificationResult with category
        """
        return await self.classify(
            text=text,
            labels=categories,
            classification_type=ClassificationType.CATEGORY,
            examples=examples,
        )

    async def analyze_sentiment(
        self,
        text: str,
        include_reasoning: bool = False,
    ) -> ClassificationResult:
        """
        Analyze sentiment of text.

        Returns standard sentiment labels: positive, negative, neutral, mixed.

        Args:
            text: Text to analyze
            include_reasoning: Include chain-of-thought reasoning

        Returns:
            ClassificationResult with sentiment
        """
        # Use dedicated sentiment prompt
        cache_key = self._generate_cache_key(text, ClassificationType.SENTIMENT, None, None)

        cached_result = self._check_cache(cache_key)
        if cached_result:
            return cached_result

        prompt = ClassificationPrompts.SENTIMENT_PROMPT.format(text=text)

        if include_reasoning:
            prompt = ClassificationPrompts.WITH_REASONING.format(base_prompt=prompt)

        result = await self._classify_with_groq(
            prompt=prompt,
            classification_type=ClassificationType.SENTIMENT,
            expected_labels=["positive", "negative", "neutral", "mixed"],
        )

        self._store_cache(cache_key, result)
        return result

    async def detect_language(self, text: str) -> ClassificationResult:
        """
        Detect the language of text.

        Returns ISO 639-1 language code with confidence.

        Args:
            text: Text to analyze

        Returns:
            ClassificationResult with language code
        """
        cache_key = self._generate_cache_key(text, ClassificationType.LANGUAGE, None, None)

        cached_result = self._check_cache(cache_key)
        if cached_result:
            return cached_result

        prompt = ClassificationPrompts.LANGUAGE_PROMPT.format(text=text)

        result = await self._classify_with_groq(
            prompt=prompt,
            classification_type=ClassificationType.LANGUAGE,
            expected_labels=None,  # Language codes are open-ended
        )

        self._store_cache(cache_key, result)
        return result

    @staticmethod
    def _parse_result(
        response: Any,
        classification_type: ClassificationType,
        expected_labels: list[str] | None,
        latency_ms: float,
    ) -> ClassificationResult:
        """Build a result from the model's JSON, refusing anything it would have to guess.

        Raises ValueError (wrapped as LLMError by the caller) on unparseable JSON, a
        missing label or confidence, or a label outside ``expected_labels``.
        """
        content = response.content.strip()
        if content.startswith("```"):  # markdown code fence
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        data = json.loads(content)
        if not isinstance(data, dict) or "label" not in data or "confidence" not in data:
            raise ValueError("classification response needs both 'label' and 'confidence'")
        label = str(data["label"])
        if expected_labels:
            matches = [e for e in expected_labels if e.lower() == label.lower()]
            if not matches:
                raise ValueError(f"label {label!r} is not one of {expected_labels}")
            label = matches[0]
        return ClassificationResult(
            label=label,
            confidence=data["confidence"],
            all_scores=data.get("scores", data.get("all_scores", {})),
            reasoning=data.get("reasoning"),
            classification_type=classification_type,
            latency_ms=latency_ms,
            model=response.model,
            cached=False,
            raw_response=response.content,
        )

    async def _classify_with_groq(
        self,
        prompt: str,
        classification_type: ClassificationType,
        expected_labels: list[str] | None,
    ) -> ClassificationResult:
        """
        Execute classification using Groq client.

        Any unusable response (bad JSON, missing label or confidence, a label outside
        ``expected_labels``) raises LLMError; callers decide how to proceed without it.
        """
        client = await self._get_client()

        start_time = time.monotonic()

        try:
            response = await client.complete(
                messages=[
                    Message.system(
                        "You are a classification assistant. Respond with valid JSON only."
                    ),
                    Message.user(prompt),
                ],
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

            latency_ms = (time.monotonic() - start_time) * 1000
            return self._parse_result(response, classification_type, expected_labels, latency_ms)

        except Exception as e:
            logger.error(f"Classification failed: {e}")
            raise LLMError(
                f"Classification failed: {e}",
                provider="groq",
                model=self.config.model,
            ) from e

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache performance statistics."""
        total_attempts = len(self._cache)
        return {
            "cache_size": len(self._cache),
            "cache_max_size": self.config.cache_max_size,
            "total_attempts": total_attempts,
        }

    def clear_cache(self) -> None:
        """Clear the classification cache."""
        self._cache.clear()

    async def close(self) -> None:
        """Close the Groq client connection."""
        if self._client:
            await self._client.close()
            self._client = None


# =============================================================================
# Convenience Functions
# =============================================================================

_default_classifier: GroqFastClassifier | None = None


def get_classifier() -> GroqFastClassifier:
    """Get the default classifier instance."""
    global _default_classifier
    if _default_classifier is None:
        _default_classifier = GroqFastClassifier()
    return _default_classifier


async def classify_intent(
    text: str,
    intents: list[str],
    examples: list[ClassificationExample] | None = None,
) -> ClassificationResult:
    """Quick intent classification using default classifier."""
    return await get_classifier().classify_intent(text, intents, examples)


async def classify_category(
    text: str,
    categories: list[str],
    examples: list[ClassificationExample] | None = None,
) -> ClassificationResult:
    """Quick category classification using default classifier."""
    return await get_classifier().classify_category(text, categories, examples)


async def analyze_sentiment(text: str) -> ClassificationResult:
    """Quick sentiment analysis using default classifier."""
    return await get_classifier().analyze_sentiment(text)


async def detect_language(text: str) -> ClassificationResult:
    """Quick language detection using default classifier."""
    return await get_classifier().detect_language(text)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "ClassificationType",
    "SentimentLabel",
    # Models
    "ClassificationExample",
    "ClassificationResult",
    "ClassificationConfig",
    # Prompts
    "ClassificationPrompts",
    # Main Class
    "GroqFastClassifier",
    # Convenience
    "get_classifier",
    "classify_intent",
    "classify_category",
    "analyze_sentiment",
    "detect_language",
]
