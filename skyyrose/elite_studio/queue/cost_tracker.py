"""
Cost tracker for Elite Studio API usage.

Records token usage and estimated cost per job in Redis hashes.
Degrades gracefully when Redis is unavailable (logs warning, no exception).
"""

from __future__ import annotations

import logging
import math
import os
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)

# Pricing constants (USD per 1K tokens)
PRICING_PER_1K: dict[str, float] = {
    "gemini": 0.000075,  # Gemini Flash
    "openai": 0.005,  # GPT-4o input
    "anthropic": 0.003,  # Claude Sonnet input
}

# Redis key patterns
_COST_KEY_PREFIX = "elite_studio:costs:"
_TOTAL_COST_SORTED_SET = "elite_studio:costs:timeline"

# TTL for individual job cost records: 7 days
_COST_TTL_SECONDS = 604_800

# Hard cost ceiling — kill-switch for runaway retry loops. The previous
# implementation had only tier alerts ($5/$10/$20/$50) with no automatic
# stop, so a stuck retry loop on a paid provider could incur unbounded
# spend. CostBudgetExceeded is raised when the rolling 24h total crosses
# this ceiling. Override via ELITE_STUDIO_COST_CAP_USD env var (default
# 100.0). Set to 0 to disable the cap entirely (NOT recommended).
# [P0 cleanup, bug-100]
DEFAULT_COST_CAP_USD: float = 100.0


class CostBudgetExceeded(RuntimeError):
    """Raised when the rolling 24h cost crosses the configured cap."""


class CostTracker:
    """Records API token usage and estimated cost per job.

    Storage layout (per job):
        HASH  elite_studio:costs:{job_id}
              gemini_tokens    <int>
              openai_tokens    <int>
              anthropic_tokens <int>
              total_usd        <float>

    Timeline (for get_total_cost):
        ZADD  elite_studio:costs:timeline  <unix_ts> <job:provider:call_id:cost>
    """

    def __init__(self, redis_url: str | None = None) -> None:
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._redis: Any = None

    def _get_redis(self) -> Any:
        """Lazy-connect to Redis synchronously. Raises on failure."""
        if self._redis is not None:
            return self._redis
        try:
            import redis as sync_redis

            client = sync_redis.from_url(
                self._redis_url,
                decode_responses=True,
                socket_timeout=3.0,
                socket_connect_timeout=3.0,
            )
            client.ping()
            self._redis = client  # Only cache after successful ping
            return self._redis
        except Exception as exc:
            self._redis = None  # Ensure broken client is not cached
            logger.error("CostTracker: Redis unavailable — cannot verify budget: %s", exc)
            raise RuntimeError("Redis unavailable for cost tracking") from exc

    def get_cost_cap(self) -> float:
        """Return the configured rolling-24h cost ceiling in USD.

        Reads ELITE_STUDIO_COST_CAP_USD env var; defaults to DEFAULT_COST_CAP_USD.
        Returns 0.0 if the env var explicitly disables the cap.
        Negative, NaN, and infinite values are rejected as invalid.
        """
        import math

        raw = os.getenv("ELITE_STUDIO_COST_CAP_USD")
        if raw is None:
            return DEFAULT_COST_CAP_USD
        try:
            value = float(raw)
        except ValueError:
            logger.warning(
                "CostTracker: ELITE_STUDIO_COST_CAP_USD=%r is not a number; using default $%.2f",
                raw,
                DEFAULT_COST_CAP_USD,
            )
            return DEFAULT_COST_CAP_USD

        if not math.isfinite(value):
            logger.warning(
                "CostTracker: ELITE_STUDIO_COST_CAP_USD=%r is non-finite; using default $%.2f",
                raw,
                DEFAULT_COST_CAP_USD,
            )
            return DEFAULT_COST_CAP_USD
        if value == 0.0:
            return 0.0
        if value < 0.0:
            logger.warning(
                "CostTracker: ELITE_STUDIO_COST_CAP_USD=%r is negative/invalid; using default $%.2f",
                raw,
                DEFAULT_COST_CAP_USD,
            )
            return DEFAULT_COST_CAP_USD
        return value

    def check_budget(self, projected_cost_usd: float = 0.0) -> None:
        """Raise CostBudgetExceeded if rolling 24h spend (+ projected) crosses the cap.

        Call before kicking off any paid API request. Set ELITE_STUDIO_COST_CAP_USD=0
        in the environment to disable the cap entirely (not recommended for prod).

        Fails closed (raises CostBudgetExceeded) when the total is unverifiable,
        including Redis failure or invalid data. The existing explicit
        ELITE_STUDIO_COST_CAP_ALLOW_DEGRADED=1 setting skips that verification.

        Args:
            projected_cost_usd: Expected cost of the upcoming call. Must be >= 0.
        """
        import math

        if not math.isfinite(projected_cost_usd) or projected_cost_usd < 0.0:
            raise ValueError(
                f"projected_cost_usd must be a non-negative finite number; got {projected_cost_usd!r}"
            )
        cap = self.get_cost_cap()
        if cap <= 0.0:
            return  # Cap explicitly disabled

        # Reporting may degrade to zero; authorization requires a verified read,
        # including when a previously cached Redis connection fails during a query.
        try:
            current = self._read_total_cost(since_hours=24)
        except RuntimeError as exc:
            if os.getenv("ELITE_STUDIO_COST_CAP_ALLOW_DEGRADED") == "1":
                logger.warning(
                    "CostTracker: total unverifiable but degraded mode allowed — skipping budget check"
                )
                return
            logger.critical(
                "CostTracker: total unverifiable and no degraded mode flag — failing closed to prevent runaway spend"
            )
            raise CostBudgetExceeded(
                "Budget check failed: cost total could not be verified. "
                "Set ELITE_STUDIO_COST_CAP_ALLOW_DEGRADED=1 to allow degraded operation (NOT recommended)."
            ) from exc

        if current + projected_cost_usd > cap:
            raise CostBudgetExceeded(
                f"Cost cap exceeded: ${current:.2f} spent in last 24h "
                f"+ ${projected_cost_usd:.4f} projected > ${cap:.2f} cap. "
                f"Set ELITE_STUDIO_COST_CAP_USD to raise the limit."
            )

    def record(self, job_id: str, provider: str, tokens: int, cost_usd: float) -> None:
        """Record token usage and cost for a provider call in a job.

        Args:
            job_id: The job this cost belongs to.
            provider: One of "gemini", "openai", "anthropic".
            tokens: Number of tokens consumed.
            cost_usd: Estimated cost in USD.
        """
        try:
            r = self._get_redis()
        except RuntimeError:
            logger.warning("CostTracker.record: Redis unavailable, skipping cost record")
            return

        try:
            key = f"{_COST_KEY_PREFIX}{job_id}"
            token_field = f"{provider}_tokens"

            pipe = r.pipeline()
            pipe.hincrbyfloat(key, token_field, tokens)
            pipe.hincrbyfloat(key, "total_usd", cost_usd)
            pipe.expire(key, _COST_TTL_SECONDS)

            # Record in timeline for aggregation
            # Each invocation represents a distinct call, even for equal costs.
            # Keep cost last so existing legacy members remain readable.
            timeline_entry = f"{job_id}:{provider}:{uuid4().hex}:{cost_usd:.6f}"
            score = datetime.now(UTC).timestamp()
            pipe.zadd(_TOTAL_COST_SORTED_SET, {timeline_entry: score})
            pipe.execute()

            logger.debug(
                "CostTracker: job=%s provider=%s tokens=%d cost=$%.6f",
                job_id,
                provider,
                tokens,
                cost_usd,
            )
        except Exception as exc:
            logger.warning("CostTracker.record: failed to write cost data: %s", exc)

    def get_job_cost(self, job_id: str) -> float:
        """Return total USD cost recorded for a job.

        Returns 0.0 if Redis is unavailable or job not found.
        """
        try:
            r = self._get_redis()
        except RuntimeError:
            logger.warning("CostTracker.get_job_cost: Redis unavailable")
            return 0.0

        try:
            key = f"{_COST_KEY_PREFIX}{job_id}"
            value = r.hget(key, "total_usd")
            return float(value) if value is not None else 0.0
        except Exception as exc:
            logger.warning("CostTracker.get_job_cost: %s", exc)
            return 0.0

    def get_total_cost(self, since_hours: int = 24) -> float:
        """Return total USD cost across all jobs in the last N hours.

        Degrades gracefully when Redis is unavailable: logs a warning and
        returns 0.0 rather than raising, consistent with the module-level
        contract and ``get_job_cost`` behaviour.

        Args:
            since_hours: Look-back window in hours (default 24).

        Returns:
            Summed cost in USD, or 0.0 when Redis is unavailable.
        """
        try:
            return self._read_total_cost(since_hours)
        except RuntimeError:
            logger.error("CostTracker.get_total_cost: unverifiable total — returning 0.0")
            return 0.0

    def _read_total_cost(self, since_hours: int) -> float:
        """Read a complete valid total or fail; never turn a failed read into spend zero."""
        try:
            r = self._get_redis()
            cutoff = (datetime.now(UTC) - timedelta(hours=since_hours)).timestamp()
            entries = r.zrangebyscore(_TOTAL_COST_SORTED_SET, cutoff, "+inf")
            total = 0.0
            for entry in entries:
                # Both legacy job:provider:cost and unique-call members end in cost.
                parts = entry.rsplit(":", 1)
                if len(parts) != 2:
                    raise ValueError("Invalid cost timeline entry")
                amount = float(parts[1])
                if not math.isfinite(amount) or amount < 0:
                    raise ValueError("Invalid cost timeline amount")
                total += amount
            if not math.isfinite(total):
                raise ValueError("Invalid cost timeline total")
            return round(total, 6)
        except Exception as exc:
            raise RuntimeError("Cost total could not be verified") from exc

    @staticmethod
    def estimate_cost(provider: str, tokens: int) -> float:
        """Estimate cost for a provider call without recording it.

        Args:
            provider: Provider name (gemini, openai, anthropic).
            tokens: Token count.

        Returns:
            Estimated cost in USD.
        """
        rate = PRICING_PER_1K.get(provider, 0.0)
        return round(rate * tokens / 1000, 6)
