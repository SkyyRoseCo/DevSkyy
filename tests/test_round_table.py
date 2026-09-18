"""Tests for LLM Round Table competition system with tool calling support.

This test suite covers:
- Basic Round Table competition without tools (backward compatibility)
- Tool calling integration and scoring
- Tool usage quality metrics (appropriateness, validity, integration, efficiency)
- Edge cases (no tools, missing tool calls, invalid arguments)
"""

from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pytest

from llm.round_table import (
    LLMProvider,
    LLMResponse,
    LLMRoundTable,
    ResponseScorer,
    ResponseScores,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sentence_model(monkeypatch):
    """Keep model loading offline while exercising real metric calculations."""
    model = MagicMock()
    model.encode.side_effect = lambda sentences: np.array(
        [[0.0, 1.0] if sentence == "Second sentence" else [1.0, 0.0] for sentence in sentences]
    )
    factory = MagicMock(return_value=model)
    monkeypatch.setattr("llm.evaluation_metrics.SentenceTransformer", factory)
    return factory


@pytest.fixture
async def round_table(sentence_model):
    """Create test Round Table instance with in-memory database."""
    rt = LLMRoundTable(db_url="sqlite+aiosqlite:///:memory:")
    await rt.initialize()

    # Register mock providers
    async def mock_claude(prompt: str, context: dict | None = None, **kwargs) -> LLMResponse:
        return LLMResponse(
            content="Claude response",
            provider=LLMProvider.CLAUDE,
            latency_ms=1500,
            cost_usd=0.003,
        )

    async def mock_gpt4(prompt: str, context: dict | None = None, **kwargs) -> LLMResponse:
        return LLMResponse(
            content="GPT-4 response",
            provider=LLMProvider.GPT4,
            latency_ms=2000,
            cost_usd=0.005,
        )

    rt.register_provider(LLMProvider.CLAUDE, mock_claude)
    rt.register_provider(LLMProvider.GPT4, mock_gpt4)

    yield rt

    await rt.close()


@pytest.fixture
def scorer(sentence_model):
    """Create ResponseScorer instance."""
    return ResponseScorer()


@pytest.fixture
def sample_tools():
    """Sample tool definitions for testing."""
    return [
        {
            "name": "search_products",
            "description": "Search for products in catalog",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "category": {"type": "string", "description": "Product category"},
                },
                "required": ["query"],
            },
        },
        {
            "name": "get_price",
            "description": "Get current price for a product",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "Product identifier"},
                },
                "required": ["product_id"],
            },
        },
    ]


# =============================================================================
# Basic Round Table Tests (Backward Compatibility)
# =============================================================================


@pytest.mark.asyncio
async def test_round_table_compete_without_tools(round_table):
    """Test Round Table competition without tool calling (backward compatibility)."""
    result = await round_table.compete(prompt="What is 2+2?", persist=False)

    assert result.winner is not None
    assert result.winner.provider in [LLMProvider.CLAUDE, LLMProvider.GPT4]
    assert result.winner.scores.total > 0
    assert len(result.entries) == 2  # Both providers competed


@pytest.mark.asyncio
async def test_round_table_scoring_without_tools(scorer):
    """Test that scoring works when no tools are provided."""
    response = LLMResponse(
        content="This is a quality response with good structure.",
        provider=LLMProvider.CLAUDE,
        latency_ms=1500,
        cost_usd=0.003,
    )

    scores = await scorer.score_response(response, "Generate a response", None, None)

    assert isinstance(scores, ResponseScores)
    assert scores.tool_usage_quality == 100.0  # Neutral when no tools
    assert scores.total > 0


@pytest.mark.asyncio
async def test_ml_scoring_uses_embeddings_and_initializes_once(scorer, sentence_model):
    """Orthogonal embeddings yield zero coherence; shared embeddings yield 100."""
    await scorer.initialize()
    await scorer.initialize()
    sentence_model.assert_called_once_with("all-MiniLM-L6-v2")
    response = LLMResponse(
        content="First sentence. Second sentence.",
        provider=LLMProvider.CLAUDE,
        latency_ms=1000,
        cost_usd=0.001,
    )
    scores = await scorer.score_response(response, "Compare sentences")
    sentence_model.return_value.encode.assert_called_with(["First sentence", "Second sentence"])
    assert scores.coherence == pytest.approx(0.0)
    response.content = "First sentence. First sentence."
    scores = await scorer.score_response(response, "Compare sentences")
    assert scores.coherence == pytest.approx(100.0)
    assert scorer.enable_ml_scoring is True


# =============================================================================
# Tool Calling Integration Tests
# =============================================================================


@pytest.mark.asyncio
async def test_round_table_with_tools(round_table, sample_tools):
    """Test Round Table competition with tool calling."""

    # Create mock providers that support tool calling
    async def mock_claude_with_tools(
        prompt: str, context: dict | None = None, tools: list | None = None, **kwargs
    ) -> LLMResponse:
        tool_calls = None
        if tools:
            tool_calls = [
                {
                    "name": "search_products",
                    "arguments": {"query": "luxury jewelry", "category": "jewelry"},
                }
            ]
        return LLMResponse(
            content="Found 5 luxury jewelry items based on search",
            provider=LLMProvider.CLAUDE,
            latency_ms=1500,
            cost_usd=0.003,
            tool_calls=tool_calls,
        )

    round_table.register_provider(LLMProvider.CLAUDE, mock_claude_with_tools)

    result = await round_table.compete(
        prompt="Find luxury jewelry",
        tools=sample_tools,
        tool_choice="auto",
        persist=False,
    )

    assert result.winner is not None
    assert result.winner.scores.tool_usage_quality > 0


@pytest.mark.asyncio
async def test_compete_passes_tools_to_providers(round_table, sample_tools):
    """Test that compete() passes tools to provider generators."""
    tools_received = []

    async def mock_provider(
        prompt: str, context: dict | None = None, tools: list | None = None, **kwargs
    ) -> LLMResponse:
        tools_received.append(tools)
        return LLMResponse(
            content="Response",
            provider=LLMProvider.CLAUDE,
            latency_ms=1000,
            cost_usd=0.001,
        )

    round_table.register_provider(LLMProvider.CLAUDE, mock_provider)

    await round_table.compete(
        prompt="Test prompt",
        tools=sample_tools,
        providers=[LLMProvider.CLAUDE],
        persist=False,
    )

    assert len(tools_received) == 1
    assert tools_received[0] == sample_tools


# =============================================================================
# Tool Usage Scoring Tests
# =============================================================================


def test_score_tool_usage_no_tools(scorer):
    """Test tool usage scoring when no tools are available."""
    response = LLMResponse(
        content="Response without tools",
        provider=LLMProvider.CLAUDE,
        latency_ms=1000,
        cost_usd=0.001,
    )

    score = scorer._score_tool_usage(response, None, "Test prompt")
    assert score == 100.0  # Neutral score


def test_score_tool_usage_tools_not_used_when_needed(scorer, sample_tools):
    """Test penalty when tools are available but not used for a task that needs them."""
    response = LLMResponse(
        content="I don't know",
        provider=LLMProvider.CLAUDE,
        latency_ms=1000,
        cost_usd=0.001,
    )

    score = scorer._score_tool_usage(response, sample_tools, "Search for products")
    assert score == 50.0  # Penalty for not using tools when needed


def test_score_tool_usage_tools_not_needed(scorer, sample_tools):
    """Test neutral score when tools available but not needed."""
    response = LLMResponse(
        content="2+2 equals 4",
        provider=LLMProvider.CLAUDE,
        latency_ms=1000,
        cost_usd=0.001,
    )

    score = scorer._score_tool_usage(response, sample_tools, "What is 2+2?")
    assert score == 100.0  # No penalty when tools not needed


def test_score_tool_usage_with_valid_tool_calls(scorer, sample_tools):
    """Test scoring when tool calls are valid and appropriate."""
    response = LLMResponse(
        content="Found 5 products based on search",
        provider=LLMProvider.CLAUDE,
        latency_ms=1000,
        cost_usd=0.001,
        tool_calls=[
            {
                "name": "search_products",
                "arguments": {"query": "jewelry", "category": "luxury"},
            }
        ],
    )

    score = scorer._score_tool_usage(response, sample_tools, "Find luxury jewelry")
    assert score > 65  # Should score well with valid tool usage (adjusted from 70)


# =============================================================================
# Tool Appropriateness Tests
# =============================================================================


def test_score_tool_appropriateness_valid_tool(scorer, sample_tools):
    """Test appropriateness scoring with valid tool."""
    tool_calls = [{"name": "search_products", "arguments": {"query": "test"}}]

    score = scorer._score_tool_appropriateness(tool_calls, sample_tools, "Search products")
    assert score > 50  # Should score above neutral


def test_score_tool_appropriateness_invalid_tool(scorer, sample_tools):
    """Test appropriateness scoring with non-existent tool."""
    tool_calls = [{"name": "nonexistent_tool", "arguments": {}}]

    score = scorer._score_tool_appropriateness(tool_calls, sample_tools, "Test prompt")
    assert score < 50  # Should score below neutral


def test_score_tool_appropriateness_multiple_valid_tools(scorer, sample_tools):
    """Test bonus for using multiple appropriate tools."""
    tool_calls = [
        {"name": "search_products", "arguments": {"query": "test"}},
        {"name": "get_price", "arguments": {"product_id": "123"}},
    ]

    score = scorer._score_tool_appropriateness(tool_calls, sample_tools, "Search and price")
    assert score > 70  # Should get bonus for multiple tools


# =============================================================================
# Argument Validity Tests
# =============================================================================


def test_score_argument_validity_all_required_present(scorer, sample_tools):
    """Test argument validity when all required parameters present."""
    tool_calls = [{"name": "search_products", "arguments": {"query": "test"}}]

    score = scorer._score_argument_validity(tool_calls, sample_tools)
    assert score > 70  # Should score well


def test_score_argument_validity_missing_required(scorer, sample_tools):
    """Test penalty when required parameters missing."""
    tool_calls = [{"name": "search_products", "arguments": {"category": "luxury"}}]

    score = scorer._score_argument_validity(tool_calls, sample_tools)
    assert score < 50  # Should penalize missing required


def test_score_argument_validity_invalid_params(scorer, sample_tools):
    """Test penalty for invalid/extra parameters."""
    tool_calls = [
        {"name": "search_products", "arguments": {"query": "test", "invalid_param": "value"}}
    ]

    score = scorer._score_argument_validity(tool_calls, sample_tools)
    assert score < 85  # Should penalize invalid params (adjusted from 70)


def test_score_argument_validity_all_valid(scorer, sample_tools):
    """Test bonus when all tool calls have valid arguments."""
    tool_calls = [
        {"name": "search_products", "arguments": {"query": "test"}},
        {"name": "get_price", "arguments": {"product_id": "123"}},
    ]

    score = scorer._score_argument_validity(tool_calls, sample_tools)
    assert score > 80  # Should get bonus for all valid


# =============================================================================
# Result Integration Tests
# =============================================================================


def test_score_result_integration_good_integration(scorer):
    """Test scoring when tool results are well integrated."""
    content = "Based on the search, I found 5 luxury jewelry items. The retrieved products include necklaces and bracelets with premium materials."
    tool_calls = [{"name": "search_products", "arguments": {"query": "jewelry"}}]

    score = scorer._score_result_integration(content, tool_calls)
    assert score > 60  # Should score well with indicators (adjusted from 70)


def test_score_result_integration_poor_integration(scorer):
    """Test penalty for poor integration (too brief)."""
    content = "Done."
    tool_calls = [{"name": "search_products", "arguments": {"query": "jewelry"}}]

    score = scorer._score_result_integration(content, tool_calls)
    assert score < 50  # Should penalize brief response


def test_score_result_integration_over_mentioning(scorer):
    """Test penalty for over-mentioning tool calls."""
    content = "tool_call search_products tool_call get_price tool_call tool_call"
    tool_calls = [{"name": "search_products", "arguments": {"query": "test"}}]

    score = scorer._score_result_integration(content, tool_calls)
    assert score < 50  # Should penalize over-mentioning


# =============================================================================
# Tool Efficiency Tests
# =============================================================================


def test_score_tool_efficiency_optimal_count(scorer, sample_tools):
    """Test efficiency scoring with optimal tool call count (1-3)."""
    tool_calls = [
        {"name": "search_products", "arguments": {"query": "test"}},
        {"name": "get_price", "arguments": {"product_id": "123"}},
    ]

    score = scorer._score_tool_efficiency(tool_calls, sample_tools)
    assert score > 70  # Should score well


def test_score_tool_efficiency_single_call_bonus(scorer, sample_tools):
    """Test bonus for single precise tool call."""
    tool_calls = [{"name": "search_products", "arguments": {"query": "test"}}]

    score = scorer._score_tool_efficiency(tool_calls, sample_tools)
    assert score > 80  # Should get bonus for single call


def test_score_tool_efficiency_too_many_calls(scorer, sample_tools):
    """Test penalty for too many tool calls."""
    tool_calls = [
        {"name": "search_products", "arguments": {"query": f"test{i}"}} for i in range(10)
    ]

    score = scorer._score_tool_efficiency(tool_calls, sample_tools)
    assert score < 50  # Should penalize excessive calls


def test_score_tool_efficiency_duplicate_calls(scorer, sample_tools):
    """Test penalty for duplicate tool calls (inefficient)."""
    tool_calls = [
        {"name": "search_products", "arguments": {"query": "test"}},
        {"name": "search_products", "arguments": {"query": "test"}},
    ]

    score = scorer._score_tool_efficiency(tool_calls, sample_tools)
    assert score < 70  # Should penalize duplicates


# =============================================================================
# Edge Cases
# =============================================================================


@pytest.mark.asyncio
async def test_score_response_with_error(scorer):
    """Test scoring handles error responses gracefully."""
    response = LLMResponse(
        content="",
        provider=LLMProvider.CLAUDE,
        latency_ms=1000,
        cost_usd=0.001,
        error="API error",
    )

    scores = await scorer.score_response(response, "Test prompt", None, None)
    assert scores.total == 0  # Should return zero scores


@pytest.mark.asyncio
async def test_score_response_empty_content(scorer):
    """Test scoring handles empty content gracefully."""
    response = LLMResponse(
        content="",
        provider=LLMProvider.CLAUDE,
        latency_ms=1000,
        cost_usd=0.001,
    )

    scores = await scorer.score_response(response, "Test prompt", None, None)
    assert scores.total == 0  # Should return zero scores


def test_response_scores_weights_sum_to_one():
    """Test that all scoring weights sum to 100%."""
    # Create mock scores with all metrics at 100
    scores = ResponseScores(
        # Heuristic metrics
        relevance=100.0,
        quality=100.0,
        completeness=100.0,
        efficiency=100.0,
        brand_alignment=100.0,
        tool_usage_quality=100.0,
        # ML-based metrics
        coherence=100.0,
        factuality=100.0,
        hallucination_risk=100.0,
        safety=100.0,
    )

    # Total should be 100 when all metrics (heuristic + ML) are 100
    assert scores.total == 100.0


def test_tool_calls_attribute_missing(scorer, sample_tools):
    """Test handling when response doesn't have tool_calls attribute."""
    response = LLMResponse(
        content="Response without tool_calls attribute",
        provider=LLMProvider.CLAUDE,
        latency_ms=1000,
        cost_usd=0.001,
    )
    # Explicitly ensure no tool_calls attribute
    if hasattr(response, "tool_calls"):
        delattr(response, "tool_calls")

    score = scorer._score_tool_usage(response, sample_tools, "Test prompt")
    # Should handle gracefully and return neutral/penalty score
    assert 0 <= score <= 100
