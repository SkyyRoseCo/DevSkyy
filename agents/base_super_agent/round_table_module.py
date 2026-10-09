"""
LLM Round Table Interface
==========================

Multi-LLM competition framework: all providers generate responses in parallel,
score and rank using 5 metrics, select top 2 for A/B comparison, and a judge
LLM determines the winner.
"""

import asyncio
import hashlib
import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from .types import LLMProvider, RoundTableEntry, RoundTableResult

# Import production Round Table
try:
    from llm.round_table import LLMProvider as RoundTableProvider
    from llm.round_table import LLMRoundTable as ProductionRoundTable
    from llm.round_table import ResponseScorer as ProductionResponseScorer
    from llm.round_table import RoundTableEntry as ProductionRoundTableEntry
    from llm.round_table import RoundTableResult as ProductionRoundTableResult
    from llm.round_table import create_round_table

    PRODUCTION_ROUND_TABLE_AVAILABLE = True
except ImportError:
    ProductionRoundTable = None
    RoundTableProvider = None
    ProductionRoundTableResult = None
    ProductionRoundTableEntry = None
    ProductionResponseScorer = None
    create_round_table = None
    PRODUCTION_ROUND_TABLE_AVAILABLE = False

# Import Prometheus metrics for Round Table observability
try:
    from security.prometheus_exporter import exporter as prometheus_exporter

    METRICS_AVAILABLE = True
except ImportError:
    prometheus_exporter = None
    METRICS_AVAILABLE = False

logger = logging.getLogger(__name__)


# =============================================================================
# LLM Round Table Interface
# =============================================================================


class LLMRoundTableInterface:
    """
    Interface for LLM Round Table competitions.

    This interface wraps the production Round Table (llm/round_table.py) when available,
    falling back to a lightweight implementation otherwise.

    Flow:
    1. All LLMs generate responses in parallel
    2. Score and rank using 5 metrics (relevance, quality, completeness, efficiency, brand)
    3. Select top 2 for A/B comparison
    4. Judge LLM determines winner
    5. Persist results to database
    6. Return winning response

    Production Features (when llm/round_table.py is available):
    - Database persistence to Neon PostgreSQL
    - Enhanced ResponseScorer with brand alignment
    - ABTestResult with confidence scores
    - Comprehensive history and analytics
    """

    SCORING_CRITERIA = {
        "relevance": 0.25,  # How relevant is the response
        "quality": 0.25,  # Overall quality of output
        "completeness": 0.20,  # Does it fully answer the prompt
        "efficiency": 0.15,  # Token efficiency and cost
        "brand_alignment": 0.15,  # SkyyRose brand voice adherence
    }

    def __init__(self, db_url: str | None = None, use_production: bool = True):
        """
        Initialize Round Table Interface.

        Args:
            db_url: Database URL for persistence (production mode)
            use_production: Whether to use production Round Table when available
        """
        self._providers: dict[LLMProvider, Callable] = {}
        self._judge_provider: LLMProvider = LLMProvider.CLAUDE
        self._history: list[RoundTableResult] = []
        self._db_url = db_url
        self._use_production = use_production and PRODUCTION_ROUND_TABLE_AVAILABLE
        self._production_rt: Any = None  # ProductionRoundTable instance
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the Round Table (creates database connection if in production mode)."""
        if self._use_production and create_round_table is not None:
            try:
                self._production_rt = await create_round_table(self._db_url)
                self._initialized = True
                logger.info(
                    "LLM Round Table initialized with production backend (database persistence enabled)"
                )
            except Exception as e:
                logger.warning(f"Failed to initialize production Round Table: {e}. Using fallback.")
                self._use_production = False
                self._initialized = True
        else:
            self._initialized = True
            logger.info("LLM Round Table initialized with lightweight backend")

    def register_provider(self, provider: LLMProvider, generator: Callable):
        """Register an LLM provider"""
        self._providers[provider] = generator

        # Also register with production Round Table if available
        if self._production_rt is not None and RoundTableProvider is not None:
            # Map internal LLMProvider to production RoundTableProvider
            provider_map = {
                LLMProvider.CLAUDE: RoundTableProvider.CLAUDE,
                LLMProvider.GPT4: RoundTableProvider.GPT4,
                LLMProvider.GEMINI: RoundTableProvider.GEMINI,
                LLMProvider.LLAMA: RoundTableProvider.LLAMA,
                LLMProvider.MISTRAL: RoundTableProvider.MISTRAL,
                LLMProvider.COHERE: RoundTableProvider.COHERE,
            }
            if provider in provider_map:
                self._production_rt.register_provider(provider_map[provider], generator)

    def set_judge(self, provider: LLMProvider):
        """Set the judge LLM for A/B testing"""
        self._judge_provider = provider

        # Also set in production Round Table
        if self._production_rt is not None and RoundTableProvider is not None:
            provider_map = {
                LLMProvider.CLAUDE: RoundTableProvider.CLAUDE,
                LLMProvider.GPT4: RoundTableProvider.GPT4,
                LLMProvider.GEMINI: RoundTableProvider.GEMINI,
            }
            if provider in provider_map:
                self._production_rt.set_judge(provider_map[provider])

    async def compete(
        self,
        prompt: str,
        providers: list[LLMProvider] | None = None,
        context: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> RoundTableResult:
        """
        Run Round Table competition.

        Args:
            prompt: The task prompt
            providers: LLM providers to include (default: all registered)
            context: Additional context for generation
            correlation_id: Optional correlation ID for tracing

        Returns:
            RoundTableResult with winner and all entries
        """
        # Ensure initialized
        if not self._initialized:
            await self.initialize()

        start_time = time.time()
        task_id = hashlib.md5(
            f"{prompt}{datetime.now(UTC).isoformat()}".encode(), usedforsecurity=False
        ).hexdigest()[:16]
        corr_id = correlation_id or task_id

        logger.info(
            "Round Table competition started",
            extra={
                "correlation_id": corr_id,
                "task_id": task_id,
                "provider_count": len(providers) if providers else len(self._providers),
                "use_production": self._use_production,
            },
        )

        # Delegate to production Round Table if available
        if self._use_production and self._production_rt is not None:
            try:
                prod_result = await self._production_rt.compete(prompt, context=context)
                # Convert production result to our format
                result = self._convert_production_result(prod_result, task_id)
                self._history.append(result)
                duration = time.time() - start_time

                # Emit metrics
                self._emit_competition_metrics(result, duration, use_production=True)

                logger.info(
                    "Round Table competition completed (production)",
                    extra={
                        "correlation_id": corr_id,
                        "winner": result.winner.provider.value,
                        "entries_count": len(result.entries),
                        "duration_seconds": duration,
                    },
                )
                return result
            except Exception as e:
                logger.warning(f"Production Round Table failed, using fallback: {e}")
                if METRICS_AVAILABLE and prometheus_exporter:
                    prometheus_exporter.record_round_table_error("production_fallback", "system")

        # Fallback to lightweight implementation
        active_providers = providers or list(self._providers.keys())

        # Generate responses in parallel with retry logic
        entries = await self._generate_all_with_retry(
            prompt, active_providers, context, max_retries=2
        )

        if not entries:
            if METRICS_AVAILABLE and prometheus_exporter:
                prometheus_exporter.record_round_table_error("no_responses", "all")
            raise ValueError("No providers generated responses")

        # Score all entries
        scored_entries = self._score_entries(entries, prompt)

        # Sort by total score
        sorted_entries = sorted(scored_entries, key=lambda x: x.total_score, reverse=True)

        # Select top 2
        top_two = sorted_entries[:2]

        # A/B test between top 2
        winner, judge_reasoning = await self._ab_test(prompt, top_two)

        result = RoundTableResult(
            task_id=task_id,
            prompt=prompt,
            entries=sorted_entries,
            top_two=top_two,
            winner=winner,
            judge_reasoning=judge_reasoning,
        )

        self._history.append(result)
        duration = time.time() - start_time

        # Emit metrics
        self._emit_competition_metrics(result, duration, use_production=False)

        logger.info(
            "Round Table competition completed (fallback)",
            extra={
                "correlation_id": corr_id,
                "winner": result.winner.provider.value,
                "entries_count": len(result.entries),
                "duration_seconds": duration,
            },
        )
        return result

    def _emit_competition_metrics(
        self,
        result: RoundTableResult,
        duration_seconds: float,
        use_production: bool,
    ) -> None:
        """Emit Prometheus metrics for a Round Table competition."""
        if not METRICS_AVAILABLE or prometheus_exporter is None:
            return

        # Record competition
        prometheus_exporter.record_round_table_competition(
            winner_provider=result.winner.provider.value,
            duration_seconds=duration_seconds,
            use_production=use_production,
        )

        # Record each provider's participation
        for entry in result.entries:
            if entry == result.winner:
                outcome = "winner"
            elif entry in result.top_two:
                outcome = "finalist"
            else:
                outcome = "participant"

            prometheus_exporter.record_round_table_provider(
                provider=entry.provider.value,
                outcome=outcome,
                latency_ms=entry.latency_ms,
            )

        # Update win rates
        stats = self.get_provider_stats()
        for provider_name, provider_stats in stats.items():
            if provider_stats["participations"] > 0:
                win_rate = provider_stats["wins"] / provider_stats["participations"]
                prometheus_exporter.update_round_table_win_rate(provider_name, win_rate)

    def _convert_production_result(self, prod_result: Any, task_id: str) -> RoundTableResult:
        """Convert production RoundTableResult to our format."""
        # Map production entries to our format
        entries = []
        for prod_entry in prod_result.entries:
            entry = RoundTableEntry(
                provider=LLMProvider(prod_entry.provider.value),
                response=prod_entry.response,
                latency_ms=prod_entry.latency_ms,
                cost_usd=prod_entry.cost_usd,
                scores=prod_entry.scores if hasattr(prod_entry, "scores") else {},
                total_score=prod_entry.total_score if hasattr(prod_entry, "total_score") else 0.0,
            )
            entries.append(entry)

        # Map winner
        winner_entry = entries[0]  # Default
        for entry in entries:
            if entry.provider.value == prod_result.winner.provider.value:
                winner_entry = entry
                break

        # Map top two
        top_two = entries[:2]

        return RoundTableResult(
            task_id=task_id,
            prompt=prod_result.prompt,
            entries=entries,
            top_two=top_two,
            winner=winner_entry,
            judge_reasoning=(
                prod_result.judge_reasoning if hasattr(prod_result, "judge_reasoning") else ""
            ),
            ab_test_id=prod_result.ab_test_id if hasattr(prod_result, "ab_test_id") else None,
        )

    async def _generate_all_with_retry(
        self,
        prompt: str,
        providers: list[LLMProvider],
        context: dict[str, Any] | None,
        max_retries: int = 2,
    ) -> list[RoundTableEntry]:
        """Generate responses from all providers in parallel with retry logic."""
        entries = []

        async def generate_one_with_retry(provider: LLMProvider) -> RoundTableEntry | None:
            generator = self._providers.get(provider)
            if not generator:
                return None

            last_error: Exception | None = None
            for attempt in range(max_retries + 1):
                start_time = time.time()
                try:
                    response = await generator(prompt, context)
                    latency = (time.time() - start_time) * 1000

                    return RoundTableEntry(
                        provider=provider,
                        response=response.get("text", str(response)),
                        latency_ms=latency,
                        cost_usd=response.get("cost", 0.0),
                    )
                except Exception as e:
                    last_error = e
                    if attempt < max_retries:
                        # Exponential backoff: 0.5s, 1s, 2s...
                        wait_time = 0.5 * (2**attempt)
                        logger.warning(
                            f"Provider {provider.value} failed (attempt {attempt + 1}/{max_retries + 1}), "
                            f"retrying in {wait_time}s: {e}"
                        )
                        await asyncio.sleep(wait_time)

            logger.error(
                f"Provider {provider.value} failed after {max_retries + 1} attempts: {last_error}"
            )
            return None

        # Run all generators concurrently
        tasks = [generate_one_with_retry(p) for p in providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, RoundTableEntry):
                entries.append(result)

        return entries

    async def _generate_all(
        self, prompt: str, providers: list[LLMProvider], context: dict[str, Any] | None
    ) -> list[RoundTableEntry]:
        """Generate responses from all providers in parallel (no retry, for backward compat)."""
        return await self._generate_all_with_retry(prompt, providers, context, max_retries=0)

    # SkyyRose brand keywords for brand alignment scoring
    BRAND_KEYWORDS = {
        "luxury",
        "premium",
        "elegant",
        "sophisticated",
        "exclusive",
        "skyyrose",
        "rose",
        "love",
        "collection",
        "fashion",
        "quality",
        "crafted",
        "artisan",
        "bespoke",
        "curated",
    }

    def _score_entries(self, entries: list[RoundTableEntry], prompt: str) -> list[RoundTableEntry]:
        """Score all entries using defined criteria including brand alignment."""
        for entry in entries:
            scores = {}
            response_lower = entry.response.lower()

            # Relevance: Basic keyword matching with TF-IDF-like weighting
            prompt_words = set(prompt.lower().split())
            response_words = set(response_lower.split())
            overlap = len(prompt_words & response_words)
            scores["relevance"] = min(overlap / max(len(prompt_words), 1), 1.0)

            # Quality: Length, structure, and formatting heuristics
            response_len = len(entry.response)
            has_structure = any(
                marker in entry.response for marker in ["- ", "* ", "1.", "##", "**"]
            )
            base_quality = 0.0
            if 100 <= response_len <= 2000:
                base_quality = 1.0
            elif response_len < 100:
                base_quality = response_len / 100
            else:
                base_quality = max(0.5, 1 - (response_len - 2000) / 5000)
            # Bonus for structured responses
            scores["quality"] = min(1.0, base_quality + (0.1 if has_structure else 0))

            # Completeness: Check for common completion indicators
            completion_indicators = [
                "therefore",
                "in conclusion",
                "finally",
                "to summarize",
                "in summary",
            ]
            has_completion = any(ind in response_lower for ind in completion_indicators)
            scores["completeness"] = 1.0 if has_completion else 0.7

            # Efficiency: Based on latency and cost
            latency_score = max(0, 1 - entry.latency_ms / 10000)
            cost_score = max(0, 1 - entry.cost_usd / 0.1)
            scores["efficiency"] = (latency_score + cost_score) / 2

            # Brand Alignment: SkyyRose brand voice adherence
            brand_matches = sum(1 for kw in self.BRAND_KEYWORDS if kw in response_lower)
            scores["brand_alignment"] = min(
                1.0, brand_matches / 3
            )  # 3+ brand keywords = full score

            entry.scores = scores

            # Calculate weighted total
            entry.total_score = sum(
                scores.get(criterion, 0.0) * weight
                for criterion, weight in self.SCORING_CRITERIA.items()
            )

        return entries

    async def _ab_test(
        self, prompt: str, top_two: list[RoundTableEntry]
    ) -> tuple[RoundTableEntry, str]:
        """A/B test between top 2 entries using judge LLM"""
        if len(top_two) < 2:
            return top_two[0], "Only one entry, selected by default"

        # Create judge prompt
        judge_prompt = f"""Compare these two responses to the prompt: "{prompt[:500]}"

Response A ({top_two[0].provider.value}):
{top_two[0].response[:1000]}

Response B ({top_two[1].provider.value}):
{top_two[1].response[:1000]}

Which response better addresses the prompt? Consider:
- Accuracy and correctness
- Completeness of the answer
- Clarity and structure
- Actionable insights

Respond with:
WINNER: A or B
REASONING: Your explanation"""

        # Get judge's decision
        judge_generator = self._providers.get(self._judge_provider)
        if judge_generator:
            try:
                result = await judge_generator(judge_prompt, None)
                response_text = result.get("text", str(result))

                # Parse winner
                if "WINNER: A" in response_text.upper():
                    return top_two[0], response_text
                elif "WINNER: B" in response_text.upper():
                    return top_two[1], response_text
            except Exception as e:
                logger.error(f"Judge failed: {e}")

        # Default to highest scored if judge fails
        winner = top_two[0] if top_two[0].total_score >= top_two[1].total_score else top_two[1]
        return winner, f"Fallback to highest score: {winner.total_score:.2f}"

    def get_history(self, limit: int = 100) -> list[RoundTableResult]:
        """Get recent Round Table results"""
        return self._history[-limit:]

    def get_provider_stats(self) -> dict[str, dict]:
        """Get statistics for each provider"""
        stats = {p.value: {"wins": 0, "participations": 0, "avg_score": 0.0} for p in LLMProvider}

        for result in self._history:
            for entry in result.entries:
                prov = entry.provider.value
                stats[prov]["participations"] += 1
                n = stats[prov]["participations"]
                stats[prov]["avg_score"] = (
                    stats[prov]["avg_score"] * (n - 1) + entry.total_score
                ) / n

                if entry == result.winner:
                    stats[prov]["wins"] += 1

        return stats


__all__ = [
    "LLMRoundTableInterface",
    "PRODUCTION_ROUND_TABLE_AVAILABLE",
]
