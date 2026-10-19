"""
LLM Verification Layer
======================

Two-stage code generation with cost optimization and quality verification.

Pattern: DeepSeek generates (cheap) → Claude/GPT-4 verifies (quality gate)

This provides 100x cost reduction while maintaining production quality through
automated verification.

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from .base import BaseLLMClient, CompletionResponse, Message

logger = logging.getLogger(__name__)


# =============================================================================
# Enums & Models
# =============================================================================


class VerificationDecision(StrEnum):
    """Verification result decision."""

    APPROVED = "approved"  # Code is production-ready
    REJECTED = "rejected"  # Code has critical issues, regenerate
    NEEDS_FIXES = "needs_fixes"  # Code has minor issues, provide fixes


class IssueLevel(StrEnum):
    """Severity level of code issues."""

    CRITICAL = "critical"  # Security, correctness, breaking changes
    WARNING = "warning"  # Style, performance, maintainability
    INFO = "info"  # Suggestions, best practices


@dataclass
class CodeIssue:
    """A single code issue found during verification."""

    level: IssueLevel
    category: str  # e.g., "security", "type_safety", "logic_error"
    message: str
    location: str | None = None  # File path or line number
    suggestion: str | None = None


@dataclass
class VerificationResult:
    """Result of code verification."""

    decision: VerificationDecision
    issues: list[CodeIssue]
    verified_by: str  # Model name that performed verification
    cost_savings_pct: float  # How much we saved using cheap model
    total_cost_usd: float
    reasoning: str | None = None


class VerificationConfig(BaseModel):
    """Configuration for verification layer."""

    # Generator settings (cheap model)
    generator_provider: str = Field(default="deepseek")
    generator_model: str = Field(default="deepseek-chat")

    # Verifier settings (quality model)
    verifier_provider: str = Field(default="anthropic")
    verifier_model: str = Field(default="claude-3-5-sonnet-20241022")

    # Verification prompts
    verification_prompt_template: str = Field(
        default="""You are a code quality verification expert. Review the following code for production readiness.

TASK: {task_description}

GENERATED CODE:
```
{generated_code}
```

VERIFICATION CHECKLIST:
1. **Correctness**: Does the code solve the task correctly?
2. **Security**: Are there SQL injection, XSS, command injection, or other OWASP risks?
3. **Type Safety**: Are all type hints present and correct?
4. **Error Handling**: Are exceptions handled appropriately?
5. **Best Practices**: Does it follow DevSkyy standards (no TODOs, no placeholders)?
6. **Performance**: Are there obvious performance issues?

OUTPUT FORMAT (JSON):
{{
  "decision": "approved|rejected|needs_fixes",
  "issues": [
    {{
      "level": "critical|warning|info",
      "category": "security|type_safety|logic_error|style|performance",
      "message": "Description of the issue",
      "location": "file:line or function name",
      "suggestion": "How to fix it"
    }}
  ],
  "reasoning": "Overall assessment and recommendation"
}}

IMPORTANT:
- Use "approved" only if code is production-ready with zero critical issues
- Use "rejected" if there are critical issues requiring full regeneration
- Use "needs_fixes" if minor issues can be fixed with small edits
"""
    )

    # Retry budget for the cheap generator before giving up (or escalating)
    max_retries: int = Field(default=2, ge=1)

    # Escalation: after the retry budget is exhausted, generate once with the
    # premium model instead of raising. ``escalation_model`` defaults to the
    # verifier model, which is the premium model already configured for the
    # quality gate; set it explicitly to escalate to a different model.
    auto_escalate: bool = Field(default=False)
    escalation_model: str | None = Field(default=None)

    # Cost tracking
    track_costs: bool = Field(default=True)


# =============================================================================
# Verification Engine
# =============================================================================


class LLMVerificationEngine:
    """
    Two-stage LLM verification system.

    Stage 1: Fast/cheap model generates code (DeepSeek)
    Stage 2: Premium model verifies quality (Claude/GPT-4)
    """

    def __init__(
        self,
        generator_client: BaseLLMClient,
        verifier_client: BaseLLMClient,
        config: VerificationConfig | None = None,
    ):
        self.generator = generator_client
        self.verifier = verifier_client
        self.config = config or VerificationConfig()

    async def generate_and_verify(
        self,
        task_description: str,
        messages: list[Message],
        max_retries: int | None = None,
    ) -> tuple[CompletionResponse, VerificationResult]:
        """
        Generate code with cheap model, verify with premium model.

        Args:
            task_description: What the code should do
            messages: Conversation context for generation
            max_retries: How many times to retry if rejected (defaults to config.max_retries)

        Returns:
            (final_response, verification_result)

        Raises:
            RuntimeError: If code fails verification after max_retries and
                config.auto_escalate is False. With auto_escalate=True the
                final attempt is generated by the premium model instead.
        """
        if max_retries is None:
            max_retries = self.config.max_retries
        attempt = 0
        total_generator_cost = 0.0
        total_verifier_cost = 0.0

        while attempt < max_retries:
            attempt += 1
            logger.info(f"Generation attempt {attempt}/{max_retries}")

            # Stage 1: Generate with cheap model
            start_time = datetime.now(UTC)
            generator_response = await self.generator.complete(
                messages=messages,
                model=self.config.generator_model,
                temperature=0.3,  # Lower temp for more deterministic code
                max_tokens=4096,
            )
            gen_time_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

            # Calculate generator cost
            gen_cost = self._calculate_cost(
                generator_response,
                self.config.generator_provider,
                self.config.generator_model,
            )
            total_generator_cost += gen_cost

            logger.info(
                f"Generated code in {gen_time_ms}ms using {self.config.generator_model} (cost: ${gen_cost:.4f})"
            )

            # Stage 2: Verify with premium model
            verification_result = await self._verify_code(
                task_description=task_description,
                generated_code=generator_response.content,
            )
            total_verifier_cost += self._calculate_cost(
                None,  # Approximate
                self.config.verifier_provider,
                self.config.verifier_model,
            )

            # Check decision
            if verification_result.decision == VerificationDecision.APPROVED:
                logger.info(f"Code APPROVED by {self.config.verifier_model}")
                verification_result.cost_savings_pct = self._calculate_savings(
                    total_generator_cost, total_verifier_cost
                )
                verification_result.total_cost_usd = total_generator_cost + total_verifier_cost
                return generator_response, verification_result

            elif verification_result.decision == VerificationDecision.NEEDS_FIXES:
                logger.warning(f"Code needs fixes ({len(verification_result.issues)} issues)")
                # For minor fixes, return with issues for human review
                # In future, could auto-apply fixes here
                verification_result.cost_savings_pct = self._calculate_savings(
                    total_generator_cost, total_verifier_cost
                )
                verification_result.total_cost_usd = total_generator_cost + total_verifier_cost
                return generator_response, verification_result

            else:  # REJECTED
                logger.error(f"Code REJECTED by {self.config.verifier_model}, retrying...")
                # Add rejection feedback to context for next attempt
                critical_issues = [
                    i for i in verification_result.issues if i.level == IssueLevel.CRITICAL
                ]
                feedback = "PREVIOUS ATTEMPT WAS REJECTED. Critical issues:\n" + "\n".join(
                    f"- {issue.message}" for issue in critical_issues[:3]
                )
                messages.append(Message.assistant(generator_response.content))
                messages.append(Message.user(feedback))

        # Max retries exceeded
        if self.config.auto_escalate:
            return await self._escalate(
                task_description,
                messages,
                max_retries,
                total_generator_cost,
                total_verifier_cost,
            )
        raise RuntimeError(f"Code generation failed verification after {max_retries} attempts")

    async def _escalate(
        self,
        task_description: str,
        messages: list[Message],
        attempts: int,
        generator_cost: float,
        verifier_cost: float,
    ) -> tuple[CompletionResponse, VerificationResult]:
        """
        Generate once with the premium model after the cheap generator's budget is spent.

        ``messages`` already carries every rejected attempt and its critical-issue
        feedback, so the premium model generates with that context. The escalated
        output then goes through the same verification gate as any other attempt;
        a rejection raises rather than returning unverified code.
        """
        model = self.config.escalation_model or self.config.verifier_model
        logger.warning(
            f"Code REJECTED {attempts} times by {self.config.verifier_model}; "
            f"escalating generation to {model}"
        )

        start_time = datetime.now(UTC)
        response = await self.verifier.complete(
            messages=messages,
            model=model,
            temperature=0.3,
            max_tokens=4096,
        )
        gen_time_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

        escalation_cost = self._calculate_cost(response, self.config.verifier_provider, model)
        total_cost = generator_cost + verifier_cost + escalation_cost
        logger.info(
            f"Escalated generation completed in {gen_time_ms}ms using {model} "
            f"(cost: ${escalation_cost:.4f}, total: ${total_cost:.4f})"
        )

        verification = await self._verify_code(
            task_description=task_description,
            generated_code=response.content,
        )
        total_cost += self._calculate_cost(
            None,  # Approximate, as in the retry loop
            self.config.verifier_provider,
            self.config.verifier_model,
        )
        if verification.decision == VerificationDecision.REJECTED:
            raise RuntimeError(
                f"Code generation failed verification after {attempts} attempts "
                f"and escalation to {model}"
            )

        # Savings vs premium-only: the rejected cheap attempts were pure overhead on
        # top of the premium generation, so this is zero at best and negative in practice.
        savings_pct = 0.0
        if escalation_cost > 0:
            savings_pct = round(((escalation_cost - total_cost) / escalation_cost) * 100, 2)

        verification.cost_savings_pct = savings_pct
        verification.total_cost_usd = total_cost
        verification.reasoning = (
            f"Escalated to {model} after {attempts} rejected attempts "
            f"by {self.config.generator_model}; {verification.reasoning or 'verified'}"
        )
        return response, verification

    async def _verify_code(self, task_description: str, generated_code: str) -> VerificationResult:
        """Run verification using premium model."""
        verification_prompt = self.config.verification_prompt_template.format(
            task_description=task_description,
            generated_code=generated_code,
        )

        start_time = datetime.now(UTC)
        response = await self.verifier.complete(
            messages=[Message.user(verification_prompt)],
            model=self.config.verifier_model,
            temperature=0.1,  # Low temp for consistent verification
            max_tokens=2048,
        )
        verify_time_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

        logger.info(
            f"Verification completed in {verify_time_ms}ms using {self.config.verifier_model}"
        )

        # Parse JSON response
        import json

        try:
            result_json = json.loads(response.content)
            issues = [
                CodeIssue(
                    level=IssueLevel(i["level"]),
                    category=i["category"],
                    message=i["message"],
                    location=i.get("location"),
                    suggestion=i.get("suggestion"),
                )
                for i in result_json.get("issues", [])
            ]

            return VerificationResult(
                decision=VerificationDecision(result_json["decision"]),
                issues=issues,
                verified_by=self.config.verifier_model,
                cost_savings_pct=0.0,  # Set later
                total_cost_usd=0.0,  # Set later
                reasoning=result_json.get("reasoning"),
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse verification result: {e}")
            # Conservative fallback: reject
            return VerificationResult(
                decision=VerificationDecision.REJECTED,
                issues=[
                    CodeIssue(
                        level=IssueLevel.CRITICAL,
                        category="verification_error",
                        message=f"Verification parsing failed: {e}",
                    )
                ],
                verified_by=self.config.verifier_model,
                cost_savings_pct=0.0,
                total_cost_usd=0.0,
            )

    def _calculate_cost(
        self, response: CompletionResponse | None, provider: str, model: str
    ) -> float:
        """Calculate cost in USD based on token usage."""
        if not response:
            # Approximate for verification
            return 0.001  # ~$0.001 per verification

        # Cost per 1M tokens
        costs = {
            ("deepseek", "deepseek-chat"): (0.14, 0.28),
            ("deepseek", "deepseek-reasoner"): (0.14, 0.55),
            ("anthropic", "claude-3-5-sonnet-20241022"): (3.0, 15.0),
            ("openai", "gpt-4"): (30.0, 60.0),
            ("openai", "gpt-4-turbo"): (10.0, 30.0),
        }

        input_cost, output_cost = costs.get((provider, model), (1.0, 2.0))

        input_usd = (response.input_tokens / 1_000_000) * input_cost
        output_usd = (response.output_tokens / 1_000_000) * output_cost

        return input_usd + output_usd

    def _calculate_savings(self, generator_cost: float, verifier_cost: float) -> float:
        """Calculate cost savings percentage vs using premium model alone."""
        # Assume premium model would have cost 10x more for the same generation
        premium_only_cost = generator_cost * 100 + verifier_cost
        actual_cost = generator_cost + verifier_cost

        if premium_only_cost == 0:
            return 0.0

        savings_pct = ((premium_only_cost - actual_cost) / premium_only_cost) * 100
        return round(savings_pct, 2)
