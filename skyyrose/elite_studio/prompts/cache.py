"""
Prompt Cache — Redis-backed caching with token-based similarity matching.

Caches enhanced prompts so similar future requests skip the chain.
Uses Jaccard similarity on token sets for fast matching without ML models.
Graceful degradation: if Redis is unavailable, operates as a passthrough.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from skyyrose.elite_studio.prompts.enhancer import EnhancedPrompt

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Token-based similarity (no ML dependency required)
# ---------------------------------------------------------------------------

_STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "shall",
        "can",
        "need",
        "dare",
        "ought",
        "to",
        "of",
        "in",
        "for",
        "on",
        "with",
        "at",
        "by",
        "from",
        "as",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "out",
        "off",
        "over",
        "under",
        "again",
        "further",
        "then",
        "once",
        "and",
        "but",
        "or",
        "nor",
        "not",
        "so",
        "yet",
        "both",
        "each",
        "all",
        "any",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "only",
        "own",
        "same",
        "than",
        "too",
        "very",
        "just",
        "because",
        "i",
        "me",
        "my",
        "we",
        "our",
        "you",
        "your",
        "it",
        "its",
        "this",
        "that",
        "make",
        "create",
        "generate",
        "give",
        "want",
        "something",
    }
)


def _tokenize(text: str) -> frozenset[str]:
    """Extract meaningful tokens from text, excluding stop words."""
    words = re.findall(r"[a-z0-9#]+", text.lower())
    return frozenset(w for w in words if w not in _STOP_WORDS and len(w) > 1)


def _jaccard_similarity(a: frozenset[str], b: frozenset[str]) -> float:
    """Compute Jaccard similarity between two token sets."""
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union > 0 else 0.0


def _prompt_hash(prompt: str, intent: str, context_digest: str = "") -> str:
    """Deterministic hash for exact-match cache lookup.

    Including *context_digest* prevents one tenant's brand/fashion context
    from leaking into another's cache hit when the raw prompt+intent match.
    """
    raw = f"{intent}:{context_digest}:{prompt.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _context_digest(*contexts: Any) -> str:
    """Stable short hash of optional enhancement contexts (fashion, brand, …).

    Returns an empty string when no context is supplied so the hash behaves
    identically to the pre-context code path.
    """
    payload: list[Any] = [c for c in contexts if c]
    if not payload:
        return ""
    try:
        raw = json.dumps(payload, sort_keys=True, default=str)
    except TypeError:
        raw = repr(payload)
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


class PromptCache:
    """Redis-backed prompt cache with similarity matching.

    Graceful degradation: all methods return None / 0 if Redis is unavailable.
    """

    CACHE_PREFIX = "elite_studio:prompt_cache"
    INDEX_PREFIX = "elite_studio:prompt_cache:index"
    STATS_KEY = "elite_studio:prompt_cache:stats"
    DEFAULT_TTL = 86400  # 24 hours

    def __init__(self, redis_url: str | None = None) -> None:
        self._redis = self._connect(redis_url)
        self._hits = 0
        self._misses = 0

    def _connect(self, redis_url: str | None) -> Any:
        """Connect to Redis. Returns None on failure."""
        try:
            import redis as redis_lib

            url = redis_url or "redis://localhost:6379/0"
            client = redis_lib.Redis.from_url(url, decode_responses=True)
            client.ping()
            return client
        except Exception:
            logger.warning("PromptCache: Redis unavailable — operating in passthrough mode")
            return None

    def check(
        self,
        prompt: str,
        intent: str,
        threshold: float = 0.75,
        context_digest: str = "",
    ) -> EnhancedPrompt | None:
        """Find a cached enhancement for a similar prompt.

        First checks exact hash match, then falls back to similarity search.
        The *context_digest* partitions both exact and similarity lookups so
        different fashion/brand contexts never share cache entries.
        """
        if self._redis is None:
            return None

        try:
            key = f"{self.CACHE_PREFIX}:{_prompt_hash(prompt, intent, context_digest)}"
            cached_json = self._redis.get(key)
            if cached_json:
                self._hits += 1
                self._record_stat("hits")
                return self._deserialize(cached_json)

            # Similarity search — partitioned by intent + context so different
            # brand/fashion contexts do not cross-match.
            index_partition = f"{intent}:{context_digest}" if context_digest else intent
            index_key = f"{self.INDEX_PREFIX}:{index_partition}"
            index_data = self._redis.hgetall(index_key)
            if not index_data:
                self._misses += 1
                self._record_stat("misses")
                return None

            query_tokens = _tokenize(prompt)
            best_match: str | None = None
            best_score = 0.0

            for cache_key, tokens_json in index_data.items():
                stored_tokens = frozenset(json.loads(tokens_json))
                sim = _jaccard_similarity(query_tokens, stored_tokens)
                if sim > best_score and sim >= threshold:
                    best_score = sim
                    best_match = cache_key

            if best_match:
                cached_json = self._redis.get(best_match)
                if cached_json:
                    self._hits += 1
                    self._record_stat("hits")
                    return self._deserialize(cached_json)

            self._misses += 1
            self._record_stat("misses")
            return None

        except Exception:
            logger.warning("PromptCache: check failed", exc_info=True)
            return None

    def store(
        self,
        original: str,
        enhanced: Any,
        ttl: int | None = None,
        context_digest: str = "",
    ) -> None:
        """Cache an enhanced prompt result."""
        if self._redis is None:
            return

        try:
            intent = enhanced.intent
            key = f"{self.CACHE_PREFIX}:{_prompt_hash(original, intent, context_digest)}"
            ttl = ttl or self.DEFAULT_TTL

            self._redis.setex(key, ttl, self._serialize(enhanced))

            # Store tokens in intent+context-partitioned index (only tokens,
            # no redundant intent field). Different contexts never share.
            index_partition = f"{intent}:{context_digest}" if context_digest else intent
            index_key = f"{self.INDEX_PREFIX}:{index_partition}"
            tokens = json.dumps(list(_tokenize(original)))
            self._redis.hset(index_key, key, tokens)

            self._record_stat("stores")
        except Exception:
            logger.warning("PromptCache: store failed", exc_info=True)

    def invalidate_by_intent(self, intent: str) -> int:
        """Remove all cached prompts for a given intent."""
        if self._redis is None:
            return 0

        try:
            index_key = f"{self.INDEX_PREFIX}:{intent}"
            index_data = self._redis.hgetall(index_key)
            if not index_data:
                return 0
            # Batch delete data keys + wipe the intent index in one pass
            pipe = self._redis.pipeline()
            for cache_key in index_data:
                pipe.delete(cache_key)
            pipe.delete(index_key)
            pipe.execute()
            return len(index_data)
        except Exception:
            logger.warning("PromptCache: invalidate failed", exc_info=True)
            return 0

    def get_stats(self) -> dict:
        """Return cache hit/miss/store statistics."""
        if self._redis is None:
            return {"hits": self._hits, "misses": self._misses, "stores": 0, "redis": False}

        try:
            stats = self._redis.hgetall(self.STATS_KEY)
            return {
                "hits": int(stats.get("hits", 0)),
                "misses": int(stats.get("misses", 0)),
                "stores": int(stats.get("stores", 0)),
                "redis": True,
            }
        except Exception:
            return {"hits": self._hits, "misses": self._misses, "stores": 0, "redis": False}

    def _record_stat(self, field: str) -> None:
        """Increment a stats counter in Redis."""
        if self._redis is None:
            return
        try:
            self._redis.hincrby(self.STATS_KEY, field, 1)
        except Exception:
            pass

    def _serialize(self, enhanced: Any) -> str:
        """Serialize an EnhancedPrompt to JSON."""
        return json.dumps(
            {
                "original": enhanced.original,
                "enhanced": enhanced.enhanced,
                "intent": enhanced.intent,
                "score_before": enhanced.score_before,
                "score_after": enhanced.score_after,
                "context_added": list(enhanced.context_added),
                "cache_key": enhanced.cache_key,
                "template_used": enhanced.template_used,
                "brief_status": enhanced.brief_status,
                "gaps": list(enhanced.gaps),
                "cached_at": time.time(),
            }
        )

    def _deserialize(self, json_str: str) -> Any:
        """Deserialize JSON back to EnhancedPrompt."""
        from skyyrose.elite_studio.prompts.enhancer import EnhancedPrompt

        data = json.loads(json_str)
        return EnhancedPrompt(
            original=data["original"],
            enhanced=data["enhanced"],
            intent=data["intent"],
            score_before=data["score_before"],
            score_after=data["score_after"],
            context_added=tuple(data.get("context_added", [])),
            cache_key=data.get("cache_key", ""),
            template_used=data.get("template_used", ""),
            brief_status=data.get("brief_status", "unverified"),
            gaps=tuple(data.get("gaps", [])),
        )
