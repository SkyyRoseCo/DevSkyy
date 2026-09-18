"""Configuration for the OpenAI gpt-image-2 product render pipeline.

Loads API keys from the project root ``.env`` without allowing legacy env
files to override caller-provided credentials, and exposes the pinned render
parameters that make every product render reproducible. No Gemini /
nano-banana dependencies.
"""

from __future__ import annotations

import os
from pathlib import Path

# Load the render pipeline's approved root environment without importing the
# top-level ``config`` package. Importing ``config.load_env`` executes
# ``config/__init__.py`` first; that module imports ``config.settings``, whose
# legacy ``.env.hf`` override can silently replace a freshly provisioned
# project key before the render client is constructed.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
try:  # pragma: no cover - optional dependency guard
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env", override=False)
except ImportError:  # pragma: no cover - environment already populated by caller
    pass

# ── Model + render parameters (the "identical procedure") ───────────────────
# Pin the exact Image 2 snapshot. The floating alias can change underneath a
# paid batch, making otherwise identical calls non-reproducible.
MODEL = "gpt-image-2-2026-04-21"
QUALITY = "high"  # highest fidelity tier
SIZE = "1024x1536"  # portrait → feeds the 4:5 holo card crop
OUTPUT_FORMAT = "png"  # lossless
BACKGROUND = "auto"  # "transparent" | "opaque" | "auto"
N = 1
MAX_REFERENCE_IMAGES = 16  # gpt-image edit hard limit
# input_fidelity controls how hard the model matches the reference images'
# style/features, values "high" | "low", DEFAULT "low". We send "high" so
# garment graphics, logos, and the style-reference anchor are reproduced as
# faithfully as possible -- but ONLY for models that accept the parameter.
# CORRECTED 2026-06-30: the 2026-06-24 comment claiming gpt-image-2 support
# was wrong -- the LIVE API rejects input_fidelity for gpt-image-2 with a 400
# invalid_input_fidelity_model error (reproduced; bug-172). Context7
# (openai/openai-openapi, images/edits schema) confirms support is listed for
# gpt-image-1 / gpt-image-1-mini / gpt-image-1.5 only. client.edit() now only
# sends this parameter when config.MODEL is in INPUT_FIDELITY_SUPPORTED_MODELS.
# Cost note: "high" raises per-image input-token cost vs the "low" default,
# on models where it applies.
INPUT_FIDELITY = "high"
INPUT_FIDELITY_SUPPORTED_MODELS = frozenset({"gpt-image-1", "gpt-image-1-mini", "gpt-image-1.5"})

# ── Networking / resilience ─────────────────────────────────────────────────
REQUEST_TIMEOUT_S = 180.0
# Paid image calls have one retry owner and one billable-attempt budget entry.
# Keep both the SDK and this wrapper at zero automatic retries; the batch can
# resume explicitly from its receipts without a hidden retry storm.
MAX_RETRIES = 0
RETRY_BACKOFF_BASE_S = 2.0  # exponential: base * 2**attempt (+ jitter)
RETRY_BACKOFF_MAX_S = 60.0

# ── Cost guardrails ─────────────────────────────────────────────────────────
# Estimate for the STOP-AND-SHOW manifest; real spend is whatever OpenAI bills.
# Verified 2026-06: gpt-image-2 high quality ≈ $0.21 at 1024x1024. Our 1024x1536
# portrait + multi-image edit (reference input tokens) ≈ $0.35–0.40/image. Edit-
# heavy / retried calls can run higher — treat this as a floor, not a ceiling.
EST_COST_PER_IMAGE_USD = 0.40
HARD_COST_CAP_USD = 50.0  # abort any run whose manifest estimate exceeds this

# ── QC gate (post-generation validation, pre-acceptance) ────────────────────
# Layered: free deterministic checks (decode / dimensions / collage panels),
# then a cheap VLM judge. The HARD_COST_CAP_USD above guards the manifest
# ESTIMATE; the SpendTracker in cost.py enforces the same cap against ACTUAL
# accumulated spend (renders + judged retries + judge calls) at runtime, which
# closes the retry-storm gap (worst case previously ~$189 vs the $50 cap).
QC_ENABLED = True
# Vision judge. Was gpt-4o-mini @ detail:"low" — that combo was UNRELIABLE in both
# directions: it hallucinated defects (green that wasn't there), false-PASSED a
# missing-sherpa-lining render, and false-REJECTED good renders. Root cause:
# detail:"low" downsamples to ~512px / 85 image tokens, so the judge cannot resolve
# logo art, colorway, or material — exactly the gates it must enforce. A wrong verdict
# costs a wasted $0.40 render (or discards good work); the few-cent token cost of a
# capable judge at full detail is trivial by comparison. gpt-4.1 keeps the existing
# chat.completions + max_tokens + json_schema call shape (GPT-5.x would need
# max_completion_tokens); detail:"high" lets it actually see the garment.
# Provider: "anthropic" (Claude-class vision — reliable) | "openai" (gpt-* — proven
# UNRELIABLE on fine garment/colorway perception). The ground-truth eval harness
# (scripts/oai-render-qc-eval.py) scored Claude correctly where THREE OpenAI models
# (gpt-4o-mini, gpt-4.1, gpt-5.1) each hit only ~2/6 — all missed a gross missing-sherpa
# defect and mis-read fine logo art. Default is anthropic; fail-closed without its key so
# a paid batch never runs on the unreliable judge or, worse, silently un-judged.
QC_JUDGE_PROVIDER = "anthropic"
# OpenAI fallback (do NOT trust as a sole gate — kept for offline/keyless smoke tests).
QC_JUDGE_MODEL = "gpt-4.1"
QC_JUDGE_DETAIL = "high"  # full-resolution tiles (OpenAI only)
# Anthropic judge (preferred). Needs ANTHROPIC_API_KEY. Structured output via a FORCED
# tool call (tool_choice={"type":"any"}). claude-fable-5 IS API-callable (verified live
# 2026-06-12) but rejects forced tool_choice with 400 "tool_choice forces tool use is not
# compatible with this model" (it always emits thinking blocks first) — so it cannot be
# the in-process judge without reworking the structured-output path. sonnet/opus 4.x work.
QC_JUDGE_MODEL_ANTHROPIC = "claude-sonnet-4-6"
ANTHROPIC_API_KEY_ENV = "ANTHROPIC_API_KEY"
# Budget covers a forced chain-of-thought: the schema's leading `visual_analysis`
# field makes the judge describe the garment (type, body color, lining/material,
# logo art+colorway+panel) BEFORE the boolean gates, so the gates are decided from
# observation. 300 tokens forced an instant verdict with no room to look — it
# false-PASSED the missing-sherpa br-006. ~1500 fits analysis + 6 gates + reason.
QC_JUDGE_MAX_OUTPUT_TOKENS = 1500
QC_MAX_RENDER_RETRIES = 2  # judged re-renders per plan before quarantine
# Per-judge-call cost ceiling for the cap math. OpenAI gpt-4.1@high ≈ $0.005-0.008;
# Anthropic claude-sonnet-4-6 (1 candidate + 3 refs, full-res) ≈ $0.04-0.05.
EST_JUDGE_COST_USD = 0.05

# Q-fusion centroid gate mode: "off" (default) | "advisory" | "hard".
#   off      — centroid never runs (no CLIP/DINO cost); the verdict carries no centroid fields.
#   advisory — centroid runs and is RECORDED alongside the judge, but never rejects
#              (verdict.passed = judge only) → collects centroid-vs-judge calibration data.
#   hard     — passed = on_brand AND judge.pass. Enable ONLY after the centroid threshold is
#              calibrated for oai_render; the compositor-tuned threshold can over-reject here.
# Env-overridable so promotion (advisory → hard) is a one-value flip with no code change.
QC_CENTROID_GATE = os.environ.get("OAI_QC_CENTROID_GATE", "off").strip().lower()


EXPECTED_RENDER_SIZE = (1024, 1536)  # must match SIZE above

# ── Batch exclusions ────────────────────────────────────────────────────────
# SKUs auto-skipped from --all / --collection batches (known-bad source asset).
# Explicit --sku/--skus still renders them (founder override). Reason logged.
EXCLUDED_SKUS: dict[str, str] = {
    "sg-015": "only reference is a 4-panel composite techflat — needs a clean cropped front "
    "techflat before it can render as a single garment (would otherwise produce a multi-panel).",
    # sg-006 / sg-014 removed 2026-06-10: dossiers re-authored from the real mint
    # garments (bug-119 contamination cleared) — both SKUs render again.
}

# ── Paths (single authority: skyyrose/core/paths.py) ────────────────────────
from skyyrose.core import paths as _ap  # noqa: E402

THEME_ROOT = _ap.THEME_ROOT
CATALOG_CSV = _ap.CATALOG_CSV
DOSSIER_DIR = _ap.DOSSIERS_DIR
# Founder's verbatim render-review corrections, injected into prompts per SKU
# (generated from the 2026-06-09 review board; see the file's _meta block).
CORRECTIONS_JSON = THEME_ROOT / "data" / "render-corrections.json"
# Founder-approved surviving assets (tasks/mockup-render-inventory.md keep pass):
# each entry skips one (sku, style, view) plan in batches; explicit --sku overrides.
KEEPERS_JSON = THEME_ROOT / "data" / "render-keepers.json"
PRODUCT_REFERENCES_DIR = _ap.PRODUCT_REFERENCES
PRODUCT_SOURCE_PHOTOS_DIR = _ap.PRODUCT_SOURCE_PHOTOS
PRODUCTS_DIR = _ap.WP_PRODUCTS_DIR
SPLIT_DIR = _ap.PRODUCT_TECHFLATS / "split"
OVERLAYS_DIR = _ap.PRODUCT_TECHFLATS / "hero-overlays"
TECHFLATS_DIR = _ap.PRODUCT_TECHFLATS
LOGOS_DIR = _ap.PRODUCT_LOGOS  # colorway-correct three-rose-cluster render references
OUTPUT_DIR = PROJECT_ROOT / "renders" / "oai"
REJECTED_DIR = OUTPUT_DIR / "_rejected"  # QC-failed renders quarantined for human review

API_KEY_ENV = "OPENAI_API_KEY"


def get_api_key() -> str:
    """Return the OpenAI API key from the environment, or raise a clear error.

    The key is loaded from the project root ``.env`` without overriding an
    explicit caller environment. It is never logged or printed.
    """
    key = os.environ.get(API_KEY_ENV, "").strip()
    if not key:
        raise RuntimeError(
            f"{API_KEY_ENV} not set. Add it to the project root .env or export it "
            "for this process and retry."
        )
    return key


def api_key_present() -> bool:
    """True if an API key is available, without raising (for dry-run / status)."""
    return bool(os.environ.get(API_KEY_ENV, "").strip())
