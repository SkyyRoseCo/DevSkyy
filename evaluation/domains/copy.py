"""Brand Copy Evaluator — copy/content domain adapter.

Scores SkyyRose product/collection/marketing copy against brand canon via forced
tool-use (text-only Claude judge — no vision). Mirrors the imagery adapter's shape:
a module-level TOOL dict with a leading chain-of-thought field, fail-closed parsing,
and deterministic free pre-checks. Subject = copy text (str); ref = CopyBrief.

The revise loop (content's differentiator over imagery) is wired via a `regenerate_fn`
injected at construction — the same dependency-injection seam EvaluationCore uses for
`judge_fn`. This keeps the adapter import-free from agents/ (no circular dependency).

Rubric dimensions and the hard-fail vocabulary trace to brand canon — see
memory/feedback_collection_canon_attribution.md, memory/project_founder_voice.md,
memory/feedback_product_naming.md, memory/project_brand.md, and docs/brand/.
"""

from __future__ import annotations

import json
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path

from evaluation.contracts import Verdict

# Weighted-composite floor. Matches the imagery stage_g QA gate (24/30 = 0.80).
# Advisory in soft_signal mode; promote to a hard gate only after calibration
# (calibration.decide_mode requires kappa >= 0.65 against labeled ground truth).
_PASS_THRESHOLD = 0.80

# Dimension order MUST match the COPY_TOOL required list (minus the non-scored fields).
_DIMENSIONS: tuple[str, ...] = (
    "brand_voice_fidelity",
    "correct_collection_canon",
    "garment_as_protagonist",
    "no_urgency_theatre",
    "no_related_products_push",
    "name_not_sku_referencing",
    "canonical_tagline_only",
    "oakland_anchoring",
)

# Canon-traced relative priorities (sum to 1.0). Founder-tunable — advisory in v1.
_WEIGHTS: dict[str, float] = {
    "brand_voice_fidelity": 0.20,
    "correct_collection_canon": 0.20,
    "garment_as_protagonist": 0.15,
    "no_urgency_theatre": 0.10,
    "no_related_products_push": 0.10,
    "name_not_sku_referencing": 0.10,
    "canonical_tagline_only": 0.10,
    "oakland_anchoring": 0.05,
}

# Any of these tags (deterministic or judge-emitted) fails the verdict regardless of score.
_HARD_FAIL_TAGS: frozenset[str] = frozenset(
    {
        "wrong_collection_canon",
        "retired_tagline_present",
        "urgency_timer_present",
        "related_products_push",
        "sku_first_naming",
        "cross_collection_quote_mix",
        "tagline_misuse",
        "gendered_language",
        "blue_in_palette_reference",
        "european_luxury_lineage_reference",
        "locked_out_visual_reference",
        "love_hurts_quote_on_black_rose",
        "black_rose_quote_on_love_hurts",
    }
)

# Deterministic free pre-checks (str/regex only — never call the LLM).
_RETIRED_RE = re.compile(r"where love meets luxury", re.IGNORECASE)
# SKU tokens (br-001 etc.). Allowed ONLY as a parenthetical backend key right after the
# name — i.e. the nearest non-space char before the token is "(" (see _uses_sku_as_handle).
_SKU_TOKEN_RE = re.compile(r"\b(?:br|lh|sg|kc)-\d{3}\b", re.IGNORECASE)
_URGENCY_RES = [
    re.compile(r"\bcountdown\b", re.IGNORECASE),
    re.compile(r"only\s+\d+\s+left", re.IGNORECASE),
    re.compile(r"selling\s+fast", re.IGNORECASE),
    re.compile(r"limited[\s-]time", re.IGNORECASE),
    re.compile(r"buy\s+before", re.IGNORECASE),
    re.compile(r"\bhurry\b", re.IGNORECASE),
    re.compile(r"ends\s+(?:tonight|soon|today)", re.IGNORECASE),
]
_RELATED_RES = [
    re.compile(r"you\s+m(?:ay|ight)\s+also\s+like", re.IGNORECASE),
    re.compile(r"customers\s+also\s+bought", re.IGNORECASE),
    re.compile(r"\brelated\s+products", re.IGNORECASE),
    re.compile(r"frequently\s+bought\s+together", re.IGNORECASE),
]

_RUBRIC_PROMPT = (
    "Score each dimension 0-5 (5 = fully on-brand). First fill brand_analysis: quote 2-3 "
    "specific phrases from the copy and note cadence (declarative vs hedging), urgency "
    "markers, collection attribution, and product/SKU naming.\n"
    "Dimensions:\n"
    "- brand_voice_fidelity: declarative founder register, no hedging/apology/mood-board generic.\n"
    "- correct_collection_canon: collection-locked quotes/taglines stay on their own collection "
    "(Love Hurts lines never on Black Rose, etc.).\n"
    "- garment_as_protagonist: the piece is the subject (material/construction/motif), not a "
    "lifestyle prop ('perfect for the weekend').\n"
    "- no_urgency_theatre: no countdowns, scarcity nudges, or FOMO CTAs.\n"
    "- no_related_products_push: no 'you may also like' / 'customers also bought' framing.\n"
    "- name_not_sku_referencing: products named in full, never by SKU handle.\n"
    "- canonical_tagline_only: no tagline is authorised; any tagline use scores 0, including the retired 'Where Love Meets Luxury'.\n"
    "- oakland_anchoring: Oakland-first vocabulary ('The Town', 'frisco'), never glossed; "
    "'Bay Area' in supporting copy is acceptable.\n"
    "Emit failure_tags from the approved vocabulary for any canon violation; empty if clean."
)

COPY_TOOL: dict[str, object] = {
    "name": "copy_qc_verdict",
    "description": "Score the candidate copy against the SkyyRose brand brief.",
    "input_schema": {
        "type": "object",
        "properties": {
            "brand_analysis": {
                "type": "string",
                "description": "FIRST: quote 2-3 phrases from the copy and note cadence, urgency "
                "markers, collection attribution, and product/SKU naming BEFORE scoring.",
            },
            "brand_voice_fidelity": {"type": "integer", "minimum": 0, "maximum": 5},
            "correct_collection_canon": {"type": "integer", "minimum": 0, "maximum": 5},
            "garment_as_protagonist": {"type": "integer", "minimum": 0, "maximum": 5},
            "no_urgency_theatre": {"type": "integer", "minimum": 0, "maximum": 5},
            "no_related_products_push": {"type": "integer", "minimum": 0, "maximum": 5},
            "name_not_sku_referencing": {"type": "integer", "minimum": 0, "maximum": 5},
            "canonical_tagline_only": {"type": "integer", "minimum": 0, "maximum": 5},
            "oakland_anchoring": {"type": "integer", "minimum": 0, "maximum": 5},
            "failure_tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Zero or more tags describing why the copy fails; empty if clean.",
            },
            "reason": {"type": "string"},
        },
        "required": ["brand_analysis", *(_DIMENSIONS), "failure_tags", "reason"],
        "additionalProperties": False,
    },
}


@dataclass(frozen=True)
class CopyBrief:
    """Reference brief for a copy evaluation — the data available at the agent seam."""

    collection: str | None
    content_type: str
    product_name: str | None
    brand_voice_context: str = ""
    additional_direction: str = ""


def _clamp_score(value: object) -> int:
    """Coerce a judge dimension value to an int in [0, 5]; missing/None/garbage -> 0."""
    try:
        n = int(value)  # type: ignore[arg-type]  # handles 5, "5", 5.0
    except (TypeError, ValueError):
        return 0
    return max(0, min(5, n))


def _uses_sku_as_handle(text: str) -> bool:
    """True if any SKU token is used as a primary handle (not a parenthetical key).

    A SKU is permitted only as a backend key right after the name, e.g. "Crewneck (br-001)"
    or "( br-001 )" — i.e. the nearest non-space character before the token is "(".
    """
    for match in _SKU_TOKEN_RE.finditer(text):
        if not text[: match.start()].rstrip().endswith("("):
            return True
    return False


class CopyAdapter:
    domain = "copy"

    def __init__(
        self,
        regenerate_fn: Callable[[CopyBrief, dict], Awaitable[str]] | None = None,
        review_state_path: Path | None = None,
        mode: str = "soft_signal",
    ) -> None:
        self._regenerate_fn = regenerate_fn
        self._review_state = (
            Path(review_state_path)
            if review_state_path
            else (Path(__file__).parent / "copy-review-state.json")
        )
        self._mode = mode

    def deterministic_checks(self, subject: str, ref: CopyBrief) -> list[str]:
        text = subject or ""
        tags: list[str] = []
        if _RETIRED_RE.search(text):
            tags.append("retired_tagline_present")
        if _uses_sku_as_handle(text):
            tags.append("sku_first_naming")
        if any(p.search(text) for p in _URGENCY_RES):
            tags.append("urgency_timer_present")
        if any(p.search(text) for p in _RELATED_RES):
            tags.append("related_products_push")
        return tags

    def build_judge_request(self, subject: str, ref: CopyBrief) -> dict:
        brief_lines = [
            "You are a SkyyRose brand-copy evaluator. Score the candidate copy against the brief.",
            f"Collection: {ref.collection or 'brand-wide (no single collection)'}",
            f"Content type: {ref.content_type}",
            f"Product: {ref.product_name or 'n/a'}",
        ]
        if ref.brand_voice_context:
            brief_lines.append(f"Brand voice: {ref.brand_voice_context}")
        if ref.additional_direction:
            brief_lines.append(f"Direction: {ref.additional_direction}")
        prompt = (
            "\n".join(brief_lines)
            + "\n\n"
            + _RUBRIC_PROMPT
            + "\n\nCandidate copy to evaluate:\n"
            + (subject or "")
        )
        return {
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            "tool": COPY_TOOL,
        }

    def parse_verdict(self, judge_output: dict, det_failures: list[str]) -> Verdict:
        raw = {d: _clamp_score(judge_output.get(d)) for d in _DIMENSIONS}
        judge_tags = tuple(str(t) for t in (judge_output.get("failure_tags") or ()) if t)
        all_tags = tuple(det_failures) + judge_tags
        hard_fail = any(t in _HARD_FAIL_TAGS for t in all_tags)
        composite = sum(_WEIGHTS[d] * raw[d] for d in _DIMENSIONS) / 5.0
        passed = composite >= _PASS_THRESHOLD and not hard_fail
        return Verdict(
            domain="copy",
            passed=passed,
            score=composite,
            gate_results=dict(raw),
            failure_tags=all_tags,
            reason=str(judge_output.get("reason", ""))[:300],
            detail={"brand_analysis": judge_output.get("brand_analysis", "")},
            mode=self._mode,
        )

    async def revise(self, ref: CopyBrief, critique: dict) -> str:
        if self._regenerate_fn is None:
            raise NotImplementedError(
                "CopyAdapter.revise requires a regenerate_fn injected at construction"
            )
        return await self._regenerate_fn(ref, critique)

    def load_ground_truth(self) -> list[dict]:
        if not self._review_state.exists():
            return []
        state = json.loads(self._review_state.read_text(encoding="utf-8"))
        out: list[dict] = []
        for subject_id, entry in state.items():
            label_pass = bool(entry.get("approved")) and not bool(entry.get("flagged"))
            out.append(
                {
                    "subject_id": subject_id,
                    "label_pass": label_pass,
                    "comment": entry.get("comment", ""),
                }
            )
        return out


__all__ = ["COPY_TOOL", "CopyAdapter", "CopyBrief"]
