"""
Tests for LLM Verification Layer
=================================
"""

from unittest.mock import AsyncMock

import pytest

from llm.base import CompletionResponse, Message
from llm.verification import (
    LLMVerificationEngine,
    VerificationConfig,
    VerificationDecision,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verification_approved(mock_api_keys):
    """Test successful verification (code approved)."""
    # Mock generator (DeepSeek)
    generator = AsyncMock()
    gen_response = CompletionResponse(
        content="def add(a, b):\n    return a + b",
        model="deepseek-chat",
        provider="deepseek",
        input_tokens=20,
        output_tokens=30,
        total_tokens=50,
        cost_usd=0.00001,
    )
    generator.complete.return_value = gen_response

    # Mock verifier (Claude) - approves
    verifier = AsyncMock()
    verify_response = CompletionResponse(
        content='{"decision": "approved", "issues": [], "reasoning": "Code is correct and follows best practices."}',
        model="claude-3-5-sonnet",
        provider="anthropic",
        input_tokens=int(30 * 0.4),
        output_tokens=int(30 * 0.6),
        total_tokens=30,
        cost_usd=0.001,
    )
    verifier.complete.return_value = verify_response

    config = VerificationConfig()
    engine = LLMVerificationEngine(generator, verifier, config)

    messages = [Message.user("Write an add function")]
    response, verification = await engine.generate_and_verify("Add function", messages)

    assert verification.decision == VerificationDecision.APPROVED
    assert response.content == gen_response.content
    assert verification.cost_savings_pct > 50  # Should save >50% using cheap model


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verification_rejected_then_fixes(mock_api_keys):
    """Test verification rejection followed by successful fix."""
    # Mock generator
    generator = AsyncMock()

    # First attempt - bad code
    bad_response = CompletionResponse(
        content="def add(a, b): return a - b  # Wrong!",
        model="deepseek-chat",
        provider="deepseek",
        input_tokens=16,
        output_tokens=24,
        total_tokens=40,
        cost_usd=0.00001,
    )

    # Second attempt - fixed code
    fixed_response = CompletionResponse(
        content="def add(a, b): return a + b",
        model="deepseek-chat",
        provider="deepseek",
        input_tokens=16,
        output_tokens=24,
        total_tokens=40,
        cost_usd=0.00001,
    )

    generator.complete.side_effect = [bad_response, fixed_response]

    # Mock verifier
    verifier = AsyncMock()

    # First verification - reject
    reject_response = CompletionResponse(
        content='{"decision": "rejected", "issues": [{"level": "critical", "category": "logic", "message": "Function subtracts instead of adds"}], "reasoning": "Function subtracts instead of adds"}',
        model="claude-3-5-sonnet",
        provider="anthropic",
        input_tokens=int(30 * 0.4),
        output_tokens=int(30 * 0.6),
        total_tokens=30,
        cost_usd=0.001,
    )

    # Second verification - approve
    approve_response = CompletionResponse(
        content='{"decision": "approved", "issues": [], "reasoning": "Code is now correct."}',
        model="claude-3-5-sonnet",
        provider="anthropic",
        input_tokens=int(25 * 0.4),
        output_tokens=int(25 * 0.6),
        total_tokens=25,
        cost_usd=0.001,
    )

    verifier.complete.side_effect = [reject_response, approve_response]

    config = VerificationConfig(max_retries=2)
    engine = LLMVerificationEngine(generator, verifier, config)

    messages = [Message.user("Write an add function")]
    response, verification = await engine.generate_and_verify("Add function", messages)

    assert verification.decision == VerificationDecision.APPROVED
    assert generator.complete.call_count == 2  # Retried once
    assert verifier.complete.call_count == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verification_max_retries_exceeded(mock_api_keys):
    """Test verification when max retries exceeded."""
    generator = AsyncMock()
    bad_response = CompletionResponse(
        content="bad code",
        model="deepseek-chat",
        provider="deepseek",
        input_tokens=16,
        output_tokens=24,
        total_tokens=40,
        cost_usd=0.00001,
    )
    generator.complete.return_value = bad_response

    verifier = AsyncMock()
    reject_response = CompletionResponse(
        content='{"decision": "rejected", "issues": [{"level": "critical", "category": "logic", "message": "Code is incorrect"}], "reasoning": "Code is incorrect"}',
        model="claude-3-5-sonnet",
        provider="anthropic",
        input_tokens=int(30 * 0.4),
        output_tokens=int(30 * 0.6),
        total_tokens=30,
        cost_usd=0.001,
    )
    verifier.complete.return_value = reject_response

    config = VerificationConfig(max_retries=2, auto_escalate=False)
    engine = LLMVerificationEngine(generator, verifier, config)

    messages = [Message.user("Write code")]

    # Should raise RuntimeError after max retries
    with pytest.raises(RuntimeError, match="Code generation failed verification after 2 attempts"):
        await engine.generate_and_verify("Task", messages)
    assert generator.complete.call_count == 2  # Initial + 1 retry


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verification_auto_escalation(mock_api_keys):
    """Test auto-escalation to premium model after failures."""
    generator = AsyncMock()
    bad_response = CompletionResponse(
        content="bad code",
        model="deepseek-chat",
        provider="deepseek",
        input_tokens=16,
        output_tokens=24,
        total_tokens=40,
        cost_usd=0.00001,
    )
    generator.complete.return_value = bad_response

    verifier = AsyncMock()

    # Rejection response
    reject_response = CompletionResponse(
        content='{"decision": "rejected", "issues": [{"level": "critical", "category": "logic", "message": "Code is incorrect"}], "reasoning": "Code is incorrect"}',
        model="claude-3-5-sonnet",
        provider="anthropic",
        input_tokens=int(30 * 0.4),
        output_tokens=int(30 * 0.6),
        total_tokens=30,
        cost_usd=0.001,
    )

    # Final approval (after escalation)
    approve_response = CompletionResponse(
        content="Good escalated code",
        model="claude-3-5-sonnet",
        provider="anthropic",
        input_tokens=int(100 * 0.4),
        output_tokens=int(100 * 0.6),
        total_tokens=100,
        cost_usd=0.005,
    )

    # Escalated output goes back through the verification gate
    approve_escalated = CompletionResponse(
        content='{"decision": "approved", "issues": [], "reasoning": "Escalated code is correct"}',
        model="claude-3-5-sonnet",
        provider="anthropic",
        input_tokens=12,
        output_tokens=18,
        total_tokens=30,
        cost_usd=0.001,
    )

    verifier.complete.side_effect = [
        reject_response,
        reject_response,
        approve_response,
        approve_escalated,
    ]

    config = VerificationConfig(max_retries=2, auto_escalate=True)
    engine = LLMVerificationEngine(generator, verifier, config)

    messages = [Message.user("Write code")]
    response, verification = await engine.generate_and_verify("Task", messages)

    # Should escalate to premium model
    assert verification.decision == VerificationDecision.APPROVED
    assert response.content == "Good escalated code"
    assert generator.complete.call_count == 2  # Retry budget exhausted by the cheap model
    assert verifier.complete.call_count == 4  # 2 verifications + escalated gen + its verification
    assert verification.verified_by == config.verifier_model
    assert verification.cost_savings_pct <= 0  # Escalation never saves vs premium-only
    assert verification.total_cost_usd > 0
    assert "Escalated" in (verification.reasoning or "")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verification_escalation_rejected_raises(mock_api_keys):
    """Escalated output that fails verification raises instead of returning unverified code."""
    generator = AsyncMock()
    generator.complete.return_value = CompletionResponse(
        content="bad code",
        model="deepseek-chat",
        provider="deepseek",
        input_tokens=16,
        output_tokens=24,
        total_tokens=40,
        cost_usd=0.00001,
    )
    reject_json = (
        '{"decision": "rejected", "issues": [{"level": "critical", "category": "logic", '
        '"message": "Code is incorrect"}], "reasoning": "Code is incorrect"}'
    )

    def _response(content: str) -> CompletionResponse:
        return CompletionResponse(
            content=content,
            model="claude-3-5-sonnet",
            provider="anthropic",
            input_tokens=12,
            output_tokens=18,
            total_tokens=30,
            cost_usd=0.001,
        )

    verifier = AsyncMock()
    verifier.complete.side_effect = [
        _response(reject_json),
        _response(reject_json),
        _response("still bad escalated code"),
        _response(reject_json),
    ]

    config = VerificationConfig(max_retries=2, auto_escalate=True)
    engine = LLMVerificationEngine(generator, verifier, config)

    with pytest.raises(RuntimeError, match="and escalation to"):
        await engine.generate_and_verify("Task", [Message.user("Write code")])
    assert verifier.complete.call_count == 4


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verification_cost_savings_calculation(mock_api_keys):
    """Test cost savings calculation."""
    generator = AsyncMock()
    gen_response = CompletionResponse(
        content="code",
        model="deepseek-chat",
        provider="deepseek",
        input_tokens=400,
        output_tokens=600,
        total_tokens=1000,
        cost_usd=0.0002,  # DeepSeek: very cheap
    )
    generator.complete.return_value = gen_response

    verifier = AsyncMock()
    verify_response = CompletionResponse(
        content='{"decision": "approved", "issues": [], "reasoning": "Good"}',
        model="claude-3-5-sonnet",
        provider="anthropic",
        input_tokens=int(100 * 0.4),
        output_tokens=int(100 * 0.6),
        total_tokens=100,
        cost_usd=0.001,  # Claude: more expensive
    )
    verifier.complete.return_value = verify_response

    config = VerificationConfig()
    engine = LLMVerificationEngine(generator, verifier, config)

    messages = [Message.user("Write code")]
    _, verification = await engine.generate_and_verify("Task", messages)

    # DeepSeek + Claude should be much cheaper than GPT-4 alone
    # Assuming GPT-4 would cost ~$0.015 for same task
    gpt4_cost = 0.015
    actual_cost = verification.total_cost_usd
    ((gpt4_cost - actual_cost) / gpt4_cost) * 100

    assert verification.cost_savings_pct > 50  # Should save >50% vs premium-only
    assert verification.total_cost_usd < 0.002
