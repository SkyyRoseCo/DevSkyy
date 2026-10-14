"""
Tests for Groq Fast Classification
===================================

Tests Groq-powered classification following TEST_STRATEGY.md patterns.

Coverage:
- Intent classification
- Sentiment analysis
- Category classification
- Language detection
- Sub-100ms latency
- Caching mechanism
"""

import time
from unittest.mock import AsyncMock

import pytest

from llm.base import CompletionResponse
from llm.classification import (
    ClassificationConfig,
    ClassificationExample,
    ClassificationResult,
    ClassificationType,
    GroqFastClassifier,
    get_classifier,
)
from llm.exceptions import LLMError


@pytest.mark.unit
@pytest.mark.asyncio
async def test_groq_intent_classification(mock_api_keys, mock_groq_response):
    """Test intent classification."""
    classifier = GroqFastClassifier()

    # Mock Groq client
    mock_client = AsyncMock()
    mock_response = CompletionResponse(
        content='{"label": "product_search", "confidence": 0.95, "scores": {"product_search": 0.95, "order_status": 0.03, "support": 0.02}}',
        model="llama-3.3-70b-versatile",
        provider="groq",
        total_tokens=25,
        input_tokens=15,
        output_tokens=10,
    )
    mock_client.complete = AsyncMock(return_value=mock_response)
    classifier._client = mock_client

    result = await classifier.classify_intent(
        text="I want to buy a red dress",
        intents=["product_search", "order_status", "support"],
    )

    assert result.label == "product_search"
    assert result.confidence > 0.9
    assert result.classification_type == ClassificationType.INTENT
    assert "product_search" in result.all_scores
    assert result.all_scores["product_search"] > result.all_scores.get("order_status", 0)


@pytest.mark.performance
@pytest.mark.asyncio
async def test_groq_classification_speed(mock_api_keys):
    """Test sub-100ms classification."""
    classifier = GroqFastClassifier()

    # Mock Groq client with fast response
    mock_client = AsyncMock()
    mock_response = CompletionResponse(
        content='{"label": "intent1", "confidence": 0.9}',
        model="llama-3.3-70b-versatile",
        provider="groq",
        total_tokens=20,
        input_tokens=10,
        output_tokens=10,
    )

    # Mock returns immediately. A unit test with a mocked client must measure the
    # classifier's OWN overhead, not an artificial sleep. The prior 50ms sleep ate
    # the wall-clock budget and made this assert flaky under CI scheduler jitter
    # (observed 125ms > 100ms on a loaded runner). A real perf regression (a sync
    # or blocking call in the hot path) would be seconds, still caught by <100ms.
    async def mock_complete(*args, **kwargs):
        return mock_response

    mock_client.complete = mock_complete
    classifier._client = mock_client

    start = time.monotonic()
    result = await classifier.classify_intent("test", ["intent1", "intent2"])
    elapsed_ms = (time.monotonic() - start) * 1000

    # Classifier overhead only (mock is instant) — robustly sub-100ms.
    assert elapsed_ms < 100
    assert result.latency_ms < 100


@pytest.mark.unit
@pytest.mark.asyncio
async def test_sentiment_analysis(mock_api_keys):
    """Test sentiment analysis."""
    classifier = GroqFastClassifier()

    # Mock Groq client
    mock_client = AsyncMock()
    mock_response = CompletionResponse(
        content='{"label": "positive", "confidence": 0.98, "scores": {"positive": 0.98, "negative": 0.01, "neutral": 0.01, "mixed": 0.0}}',
        model="llama-3.3-70b-versatile",
        provider="groq",
        total_tokens=30,
        input_tokens=20,
        output_tokens=10,
    )
    mock_client.complete = AsyncMock(return_value=mock_response)
    classifier._client = mock_client

    result = await classifier.analyze_sentiment("I love this product!")

    assert result.label == "positive"
    assert result.confidence > 0.9
    assert result.classification_type == ClassificationType.SENTIMENT
    assert result.all_scores["positive"] > result.all_scores["negative"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_category_classification(mock_api_keys):
    """Test category classification."""
    classifier = GroqFastClassifier()

    # Mock Groq client
    mock_client = AsyncMock()
    mock_response = CompletionResponse(
        content='{"label": "fashion", "confidence": 0.92, "scores": {"fashion": 0.92, "electronics": 0.05, "home": 0.03}}',
        model="llama-3.3-70b-versatile",
        provider="groq",
        total_tokens=25,
        input_tokens=15,
        output_tokens=10,
    )
    mock_client.complete = AsyncMock(return_value=mock_response)
    classifier._client = mock_client

    result = await classifier.classify_category(
        text="Looking for winter jackets",
        categories=["fashion", "electronics", "home"],
    )

    assert result.label == "fashion"
    assert result.confidence > 0.9
    assert result.classification_type == ClassificationType.CATEGORY


@pytest.mark.unit
@pytest.mark.asyncio
async def test_language_detection(mock_api_keys):
    """Test language detection."""
    classifier = GroqFastClassifier()

    # Mock Groq client
    mock_client = AsyncMock()
    mock_response = CompletionResponse(
        content='{"label": "es", "confidence": 0.99, "language_name": "Spanish"}',
        model="llama-3.3-70b-versatile",
        provider="groq",
        total_tokens=20,
        input_tokens=10,
        output_tokens=10,
    )
    mock_client.complete = AsyncMock(return_value=mock_response)
    classifier._client = mock_client

    result = await classifier.detect_language("Hola, ¿cómo estás?")

    assert result.label == "es"
    assert result.confidence > 0.9
    assert result.classification_type == ClassificationType.LANGUAGE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classification_with_examples(mock_api_keys):
    """Test few-shot classification with examples."""
    classifier = GroqFastClassifier()

    # Mock Groq client
    mock_client = AsyncMock()
    mock_response = CompletionResponse(
        content='{"label": "browsing", "confidence": 0.88, "scores": {"browsing": 0.88, "purchase_intent": 0.10, "support": 0.02}}',
        model="llama-3.3-70b-versatile",
        provider="groq",
        total_tokens=50,
        input_tokens=40,
        output_tokens=10,
    )
    mock_client.complete = AsyncMock(return_value=mock_response)
    classifier._client = mock_client

    examples = [
        ClassificationExample(text="Show me dresses", label="browsing"),
        ClassificationExample(text="I want to buy this now", label="purchase_intent"),
        ClassificationExample(text="My order is late", label="support"),
    ]

    result = await classifier.classify(
        text="Looking for winter jackets",
        labels=["browsing", "purchase_intent", "support"],
        examples=examples,
    )

    assert result.label == "browsing"
    assert result.confidence > 0.8


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classification_caching(mock_api_keys):
    """Test that caching works correctly."""
    config = ClassificationConfig(cache_enabled=True, cache_ttl_seconds=60)
    classifier = GroqFastClassifier(config=config)

    # Mock Groq client
    mock_client = AsyncMock()
    mock_response = CompletionResponse(
        content='{"label": "positive", "confidence": 0.95}',
        model="llama-3.3-70b-versatile",
        provider="groq",
        total_tokens=20,
        input_tokens=10,
        output_tokens=10,
    )
    mock_client.complete = AsyncMock(return_value=mock_response)
    classifier._client = mock_client

    # First call
    result1 = await classifier.analyze_sentiment("Great product!")
    assert mock_client.complete.call_count == 1
    assert result1.cached is False

    # Second call (should use cache)
    result2 = await classifier.analyze_sentiment("Great product!")
    assert mock_client.complete.call_count == 1  # No additional call
    assert result2.cached is True
    assert result1.label == result2.label


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_expiration(mock_api_keys):
    """Test that cache expires after TTL."""
    config = ClassificationConfig(cache_enabled=True, cache_ttl_seconds=1)
    classifier = GroqFastClassifier(config=config)

    # Mock Groq client
    mock_client = AsyncMock()
    mock_response = CompletionResponse(
        content='{"label": "positive", "confidence": 0.95}',
        model="llama-3.3-70b-versatile",
        provider="groq",
        total_tokens=20,
        input_tokens=10,
        output_tokens=10,
    )
    mock_client.complete = AsyncMock(return_value=mock_response)
    classifier._client = mock_client

    # First call
    await classifier.analyze_sentiment("Great!")
    assert mock_client.complete.call_count == 1

    # Wait for cache to expire
    import asyncio

    await asyncio.sleep(1.5)

    # Second call (cache expired, should call API again)
    await classifier.analyze_sentiment("Great!")
    assert mock_client.complete.call_count == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_json_parse_error_handling(mock_api_keys):
    """Test handling of malformed JSON responses."""
    classifier = GroqFastClassifier()

    # Mock Groq client with invalid JSON
    mock_client = AsyncMock()
    mock_response = CompletionResponse(
        content="This is not valid JSON",
        model="llama-3.3-70b-versatile",
        provider="groq",
        total_tokens=10,
        input_tokens=5,
        output_tokens=5,
    )
    mock_client.complete = AsyncMock(return_value=mock_response)
    classifier._client = mock_client

    # A response that cannot be parsed is an error, never a guessed first label
    with pytest.raises(LLMError, match="Classification failed"):
        await classifier.classify_intent(
            "test",
            intents=["intent1", "intent2"],
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_markdown_code_block_handling(mock_api_keys):
    """Test handling of JSON wrapped in markdown code blocks."""
    classifier = GroqFastClassifier()

    # Mock Groq client with markdown-wrapped JSON
    mock_client = AsyncMock()
    mock_response = CompletionResponse(
        content='```json\n{"label": "positive", "confidence": 0.95}\n```',
        model="llama-3.3-70b-versatile",
        provider="groq",
        total_tokens=25,
        input_tokens=15,
        output_tokens=10,
    )
    mock_client.complete = AsyncMock(return_value=mock_response)
    classifier._client = mock_client

    result = await classifier.analyze_sentiment("Great!")

    # Should parse correctly despite markdown wrapper
    assert result.label == "positive"
    assert result.confidence == 0.95


@pytest.mark.unit
def test_cache_stats():
    """Test cache statistics retrieval."""
    classifier = GroqFastClassifier()

    stats = classifier.get_cache_stats()

    assert "cache_size" in stats
    assert "cache_max_size" in stats
    assert stats["cache_size"] >= 0


@pytest.mark.unit
def test_cache_clear():
    """Test cache clearing."""
    classifier = GroqFastClassifier()

    # Add something to cache
    cache_key = "test_key"
    result = ClassificationResult(
        label="test",
        confidence=0.9,
        classification_type=ClassificationType.CUSTOM,
    )
    classifier._store_cache(cache_key, result)

    assert len(classifier._cache) > 0

    classifier.clear_cache()

    assert len(classifier._cache) == 0


@pytest.mark.unit
def test_get_classifier_singleton():
    """Test that get_classifier returns singleton instance."""
    classifier1 = get_classifier()
    classifier2 = get_classifier()

    assert classifier1 is classifier2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classifier_close(mock_api_keys):
    """Test proper cleanup on close."""
    classifier = GroqFastClassifier()

    # Mock client
    mock_client = AsyncMock()
    mock_client.close = AsyncMock()
    classifier._client = mock_client

    await classifier.close()

    # Client should be closed
    mock_client.close.assert_called_once()
    assert classifier._client is None
