"""
Prompt Enhancer — the main public interface for prompt intelligence.

Combines analyzer, cache, chain, and history into one call:
  raw prompt → analyze → check cache → enhance via chain → cache result → return
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from skyyrose.core.context_resolver import ResolutionRequest
from skyyrose.core.creative_job import (
    JobPlan,
    build_job,
    render_brief,
    execution_bundle,
    audit_bundle,
)

from skyyrose.elite_studio.prompts.analyzer import PromptAnalysis, PromptAnalyzer
from skyyrose.elite_studio.prompts.cache import PromptCache, _context_digest, _prompt_hash
from skyyrose.elite_studio.prompts.chain import PromptChain


@dataclass(frozen=True)
class EnhancedPrompt:
    """Immutable result of prompt enhancement."""

    original: str
    enhanced: str
    intent: str
    score_before: float
    score_after: float
    context_added: tuple[str, ...]
    cache_key: str
    template_used: str


class PromptEnhancer:
    """Main entry point for prompt intelligence.

    Usage:
        enhancer = PromptEnhancer()
        result = enhancer.enhance("make me a cool hoodie for winter")
        print(result.enhanced)   # fully enriched prompt
        print(result.score_before, "→", result.score_after)
    """

    def __init__(
        self,
        cache: PromptCache | None = None,
        chain: PromptChain | None = None,
        analyzer: PromptAnalyzer | None = None,
    ) -> None:
        self._cache = cache or PromptCache()
        self._chain = chain or PromptChain()
        self._analyzer = analyzer or PromptAnalyzer()

    def enhance(
        self,
        prompt: str,
        intent: str | None = None,
        fashion_context: dict | None = None,
        brand_context: dict | None = None,
    ) -> EnhancedPrompt:
        """Enhance a raw prompt into an expert-level agent brief.

        Args:
            prompt: Raw human-language prompt.
            intent: Creative intent (auto-detected if None).
            fashion_context: Optional fashion vertical context dict.
            brand_context: Optional brand override context dict.

        Returns:
            EnhancedPrompt with original, enhanced text, scores, and metadata.
        """
        # Analyze the raw prompt
        analysis = self._analyzer.analyze(prompt)
        resolved_intent = intent or analysis.intent
        if resolved_intent == "unknown":
            resolved_intent = "product-render"

        # Partition the cache by the caller's context so two tenants (or two
        # brand/fashion overrides) with the same raw prompt cannot receive
        # each other's enhancements.
        ctx_digest = _context_digest(fashion_context, brand_context)
        cache_key = _prompt_hash(prompt, resolved_intent, ctx_digest)

        # Check cache for semantically similar prompt inside this context
        cached = self._cache.check(prompt, resolved_intent, context_digest=ctx_digest)
        if cached is not None:
            return cached

        # Run the enhancement chain
        chain_result = self._chain.enhance(
            prompt=prompt,
            intent=resolved_intent,
            fashion_context=fashion_context,
            brand_context=brand_context,
        )

        # Score the enhanced prompt
        enhanced_analysis = self._analyzer.analyze(chain_result["enhanced"])

        result = EnhancedPrompt(
            original=prompt,
            enhanced=chain_result["enhanced"],
            intent=chain_result["intent"],
            score_before=analysis.score,
            score_after=enhanced_analysis.score,
            context_added=tuple(chain_result["context_added"]),
            cache_key=cache_key,
            template_used=chain_result["template_used"],
        )

        # Store in cache
        self._cache.store(prompt, result, context_digest=ctx_digest)

        return result

    def analyze_only(self, prompt: str) -> PromptAnalysis:
        """Score a prompt without enhancing it."""
        return self._analyzer.analyze(prompt)

    def build_creative_brief(
        self,
        request: ResolutionRequest,
        plan: JobPlan,
        *,
        mode: Literal["resolved", "shadow", "legacy"] = "resolved",
        include_audit: bool = False,
    ) -> dict:
        """Opt-in integration. Existing enhance() callers remain unchanged.

        Shadow returns both texts for review, never substitutes legacy text as
        approved output. Legacy is an explicit rollback without resolver guarantees.
        This deterministic path never calls providers or writes the semantic cache.
        """
        if mode not in ("resolved", "shadow", "legacy"):
            raise ValueError("Unsupported brief mode")
        if mode == "legacy":
            legacy = self._chain.enhance(prompt=request.objective, intent="product-render")
            return {
                "mode": mode,
                "brief": legacy["enhanced"],
                "contract": None,
                "resolver_guarantees": False,
                "action_authorized": False,
            }
        job = build_job(request, plan)
        result = {
            "mode": mode,
            "brief": render_brief(job),
            "contract": {"contract_id": job.contract_id, "status": job.status},
            "execution_bundle": execution_bundle(job),
            "resolver_guarantees": True,
            "action_authorized": False,
        }
        if include_audit:
            result["audit_bundle"] = audit_bundle(job)
        if mode == "shadow":
            legacy = self._chain.enhance(prompt=request.objective, intent="product-render")
            result["comparison"] = {
                "legacy_brief": legacy["enhanced"],
                "legacy_status": "UNVERIFIED_COMPARISON_ONLY",
                "changed": result["brief"] != legacy["enhanced"],
                "legacy_context_added": legacy["context_added"],
                "resolved_rule_ids": job.context.selected_rule_ids,
                "blockers": job.blockers,
            }
        return result
