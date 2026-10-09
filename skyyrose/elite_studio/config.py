"""
Elite Studio configuration — paths, provider clients, constants.

Provider clients use @lru_cache for lazy singleton initialization.
Tests can import config without requiring live API keys.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # optional env loader — minimal CI/validation envs don't ship it

    def load_dotenv(*_args, **_kwargs):  # type: ignore[misc]
        """No-op fallback when python-dotenv is absent (e.g. the Dossier Check CI job).

        Catalog/dossier validation reads tracked files only; it never needs .env."""
        return False


# ---------------------------------------------------------------------------
# Environment loading (authoritative key last with override=True)
# ---------------------------------------------------------------------------

_BASE_DIR = Path(__file__).parent.parent  # skyyrose/
_REPO_DIR = _BASE_DIR.parent  # DevSkyy/

# Load order (priority high → low). Each `override=True` lets a later file
# win; `override=False` preserves whatever the previous file already set.
# Adding .env.hf and .env.secrets closes the loading hole that left
# OPENAI_API_KEY unloaded even though it was present in .env.hf.
_LOCAL_ENV = _BASE_DIR / ".env"
if _LOCAL_ENV.exists():
    load_dotenv(_LOCAL_ENV, override=False)

_PARENT_ENV = _REPO_DIR / ".env"
if _PARENT_ENV.exists():
    load_dotenv(_PARENT_ENV, override=True)

_GEMINI_ENV = _REPO_DIR / "gemini" / ".env"
if _GEMINI_ENV.exists():
    load_dotenv(_GEMINI_ENV, override=True)

# .env.hf holds HuggingFace-tier provider keys (GOOGLE_API_KEY, OPENAI_API_KEY,
# MESHY_API_KEY). override=False so the more authoritative parent .env wins
# when the same key appears in both.
_HF_ENV = _REPO_DIR / ".env.hf"
if _HF_ENV.exists():
    load_dotenv(_HF_ENV, override=False)

# .env.secrets holds rotated/scoped secrets that should NEVER be overridden
# by less-authoritative sources. Loaded last with override=True.
_SECRETS_ENV = _REPO_DIR / ".env.secrets"
if _SECRETS_ENV.exists():
    load_dotenv(_SECRETS_ENV, override=True)

# Ensure GOOGLE_API_KEY is explicitly in environ for SDKs
if not os.getenv("GOOGLE_API_KEY"):
    _gkey = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if _gkey:
        os.environ["GOOGLE_API_KEY"] = _gkey

# ---------------------------------------------------------------------------
# Environment parsing helpers
# ---------------------------------------------------------------------------


def _int_env(name: str, default: int) -> int:
    """Parse an int from the environment, falling back to ``default``.

    ``os.getenv(name, default)`` returns the default only when the key is
    *absent*. A key that is present but empty (``ELITE_MAX_QC_RETRIES=`` in a
    .env) yields ``""``, and ``int("")`` raises ValueError at import time —
    taking the whole module graph down. Treat empty / whitespace-only values,
    and any unparseable value, as "use the default".
    """
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

OVERRIDES_DIR = _BASE_DIR / "assets" / "data" / "prompts" / "overrides"
SOURCE_DIR = _BASE_DIR / "assets" / "images" / "source-products"
OUTPUT_DIR = _BASE_DIR / "assets" / "images" / "products"

# ---------------------------------------------------------------------------
# Pipeline Model Registry — single source of truth
# ---------------------------------------------------------------------------
#
# Verified against Context7 official docs on 2026-04-25 (Anthropic, Google
# Gemini, OpenAI, Meshy). All agents MUST import model IDs from this module —
# do NOT hardcode model strings in agent files. Hardcoded model IDs scattered
# across vision_agent.py / generator_agent.py / three_d_agent.py were the
# root cause of the v1.2 model-drift bugs (see ROADMAP.md Phase 16 note).
#
# Migration timeline:
#   2026-04-14: Anthropic announced retirement of claude-sonnet-4-20250514
#               and claude-opus-4-20250514 — effective 2026-06-15.
#               Replacements: claude-sonnet-4-6 / claude-opus-4-7.
#   2026-04-25: Pipeline migrated to current Context7 docs values.
#
# Drift prevention: call validate_pipeline_models() at deploy time.

# --- Centralized model IDs ---
# Single source of truth lives at llm/model_ids.py. Re-exported here so
# legacy callers that import from this module keep working unchanged.
# Never hardcode model strings inline in this file — update llm/model_ids.py
# and the change propagates everywhere.
from llm.model_ids import GENERATION_MODEL  # noqa: F401
from llm.model_ids import MESHY_AI_MODEL  # noqa: F401
from llm.model_ids import QC_MODEL  # noqa: F401
from llm.model_ids import RAS_GENERATION_MODEL  # noqa: F401
from llm.model_ids import (  # noqa: E402, F401  -- re-exported for legacy importers
    CLAUDE_HAIKU_MODEL,
    CLAUDE_OPUS_MODEL,
    CLAUDE_SONNET_MODEL,
    COMPOSITOR_CLAUDE_MODEL,
    COMPOSITOR_OPUS_MODEL,
    COMPOSITOR_QA_MODEL,
)
from llm.model_ids import GEMINI_FLASH_IMAGE_MODEL as GEMINI_IMAGE_GEN_MODEL  # noqa: E402, F401
from llm.model_ids import (  # noqa: E402, F401  -- re-exported for legacy importers
    GEMINI_VISION_MODEL,
    OPENAI_IMAGE_MODEL,
    OPENAI_VISION_MODEL,
)

# Local-only back-compat aliases — these names exist only here, not in
# llm/model_ids.py, because they're skyyrose-specific re-spellings.
VISION_GEMINI_MODEL = GEMINI_VISION_MODEL
VISION_OPENAI_MODEL = OPENAI_VISION_MODEL
GENERATION_ASPECT_RATIO = "3:4"

# Timeouts (seconds)
GEMINI_TIMEOUT = 90.0
OPENAI_TIMEOUT = 60.0
ANTHROPIC_TIMEOUT = 60.0

# Rate limiting
BATCH_DELAY_SECONDS = 10
RETRY_DELAY_SECONDS = 5
MAX_RETRIES = 2

# LangGraph engine
MAX_QC_RETRIES = _int_env("ELITE_MAX_QC_RETRIES", 2)
GRAPH_CHECKPOINT_DIR = Path(os.getenv("ELITE_CHECKPOINT_DIR", str(_BASE_DIR / ".checkpoints")))

# ---------------------------------------------------------------------------
# Compositor configuration
# ---------------------------------------------------------------------------

# COMPOSITOR_OPUS_MODEL and COMPOSITOR_QA_MODEL are now imported from
# llm.model_ids above (at the top of this file's "Centralized model IDs"
# block). Don't redefine them here.
COMPOSITOR_STAGE_DELAY = 2
SCENES_DIR = _BASE_DIR / "assets" / "scenes"
EDITORIAL_STAGING_DIR = _BASE_DIR / "assets" / "images" / "editorial-staging"
COMPOSITOR_FLUX_PROVIDERS = ["fal-fill", "kontext", "replicate"]

# Product source images (for compositor subject lookup)
PRODUCT_IMAGES_DIR = (
    _REPO_DIR / "wordpress-theme" / "skyyrose-flagship" / "assets" / "images" / "products"
)

# IC-Light relighting
ICLIGHT_WEIGHTS_PATH = _BASE_DIR / "assets" / "models" / "ic-light" / "iclight_sd15_fbc.safetensors"
ICLIGHT_BASE_MODEL = "stablediffusionapi/realistic-vision-v51"
ICLIGHT_STEPS = 25
ICLIGHT_CFG = 2.0
ICLIGHT_RESOLUTION = 384

# ---------------------------------------------------------------------------
# Lazy provider clients (cached singletons — no mutable globals)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Queue / worker configuration
# ---------------------------------------------------------------------------

REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Worker concurrency (number of concurrent render jobs per worker process)
WORKER_CONCURRENCY: int = _int_env("ELITE_WORKER_CONCURRENCY", 1)

# Cost tracking — set to "false" to disable Redis cost writes
COST_TRACKING_ENABLED: bool = os.getenv("ELITE_COST_TRACKING", "true").lower() != "false"

# Rate limit constants per provider (requests / minute)
RATE_LIMIT_GEMINI: int = _int_env("ELITE_RATE_LIMIT_GEMINI", 60)
RATE_LIMIT_OPENAI: int = _int_env("ELITE_RATE_LIMIT_OPENAI", 500)
RATE_LIMIT_ANTHROPIC: int = _int_env("ELITE_RATE_LIMIT_ANTHROPIC", 50)

# ---------------------------------------------------------------------------
# Stripe / Billing configuration
# ---------------------------------------------------------------------------

STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Comma-separated list of tier:price_id pairs.
# Example: "starter:price_abc123,pro:price_def456,enterprise:price_ghi789"
STRIPE_PRICE_IDS_RAW: str = os.getenv("STRIPE_PRICE_IDS", "")

# Parsed as a dict for convenient lookups.
STRIPE_PRICE_IDS: dict[str, str] = {
    _k.strip(): _v.strip()
    for _entry in STRIPE_PRICE_IDS_RAW.split(",")
    if ":" in _entry
    for _k, _v in [_entry.strip().split(":", 1)]
}

# ---------------------------------------------------------------------------
# Lazy provider clients (cached singletons — no mutable globals)
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def get_openai_client():
    """Lazy-init OpenAI client (cached singleton)."""
    import openai

    return openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=OPENAI_TIMEOUT,
    )


@lru_cache(maxsize=1)
def get_anthropic_client():
    """Lazy-init Anthropic client (cached singleton)."""
    import anthropic

    return anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        timeout=ANTHROPIC_TIMEOUT,
    )


# ---------------------------------------------------------------------------
# Pipeline model validation — drift detector
# ---------------------------------------------------------------------------


def validate_catalog_readers(*, raise_on_mismatch: bool = False) -> dict[str, str]:
    """Verify every catalog reader in the project resolves to the canonical CSV.

    Per MEMORY.md, four reader paths exist (Python: core.catalog_loader,
    elite_studio.catalog, scripts.nano_banana.catalog; PHP: skyyrose_get_product_catalog).
    All MUST resolve to wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv.
    This function imports each Python reader and asserts they expose the same path.

    Returns:
        Mapping reader_name -> resolved CSV path string. The PHP reader is
        verified by source-file inspection rather than import.
    """
    import importlib
    import re as _re

    results: dict[str, str] = {}
    canonical: str | None = None

    # --- Python readers ---
    py_readers = [
        ("skyyrose.core.catalog_loader", "CATALOG_CSV"),
        ("skyyrose.elite_studio.catalog", "CATALOG_CSV"),
    ]
    for mod_name, attr in py_readers:
        try:
            mod = importlib.import_module(mod_name)
            path = getattr(mod, attr, None)
            results[mod_name] = str(path) if path else "<missing constant>"
            if mod_name == "skyyrose.core.catalog_loader" and path:
                canonical = str(path)
        except Exception as exc:
            results[mod_name] = f"<import_failed: {exc}>"

    # nano_banana lives at scripts/nano_banana — re-imports core's CATALOG_CSV,
    # so verifying it reaches the same target requires path inspection rather
    # than import (scripts/ isn't on sys.path).
    nano_banana_src = (
        Path(__file__).resolve().parent.parent.parent / "scripts" / "nano_banana" / "catalog.py"
    )
    if nano_banana_src.exists():
        text = nano_banana_src.read_text()
        # Accept either the preferred import form OR the equivalent standalone path
        # constant that resolves to the same CSV (nano_banana predates the core import).
        imports_core = "from skyyrose.core.catalog_loader import CATALOG_CSV" in text
        uses_canonical_path = (
            'wordpress-theme" / "skyyrose-flagship" / "data" / "skyyrose-catalog.csv"' in text
            or "wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv" in text
        )
        if imports_core or uses_canonical_path:
            results["scripts.nano_banana.catalog"] = canonical or "<inherits from core>"
        else:
            results["scripts.nano_banana.catalog"] = "<does NOT import core CATALOG_CSV>"
    else:
        results["scripts.nano_banana.catalog"] = "<source file not found>"

    # --- PHP reader (source inspection) ---
    php_helper = (
        Path(__file__).resolve().parent.parent.parent
        / "wordpress-theme"
        / "skyyrose-flagship"
        / "inc"
        / "product-catalog.php"
    )
    if php_helper.exists():
        text = php_helper.read_text()
        php_csv = _re.search(r"['\"]([^'\"]*skyyrose[-_]catalog[^'\"]*\.csv)['\"]", text)
        results["inc/product-catalog.php"] = (
            php_csv.group(1) if php_csv else "<no csv reference found>"
        )
    else:
        results["inc/product-catalog.php"] = "<source file not found>"

    if raise_on_mismatch and canonical:
        canonical_basename = Path(canonical).name
        for name, resolved in results.items():
            if not resolved.endswith(canonical_basename) and "<inherits" not in resolved:
                raise RuntimeError(
                    f"Catalog reader divergence: {name} resolves to {resolved}, "
                    f"expected basename {canonical_basename}"
                )
    return results


def validate_dossier_readers(
    sku: str = "br-001", *, raise_on_mismatch: bool = False
) -> dict[str, str]:
    """Verify every Python catalog reader returns the same merged dossier for a SKU.

    Imports the dossier-aware function from each reader and asserts they
    return identical (sku, name, dossier slug, dossier raw bytes) for the
    given SKU. Default SKU is br-001 (Black Rose Crewneck), which is the
    first authored dossier — pass any active SKU once its dossier exists.

    Returns a mapping reader_name -> verification status string.
    """
    import hashlib
    import importlib

    targets = [
        ("skyyrose.core.catalog_loader", "get_product_with_dossier"),
        ("skyyrose.elite_studio.catalog", "get_product_with_dossier"),
    ]

    results: dict[str, str] = {}
    canonical_hash: str | None = None

    for mod_name, attr in targets:
        try:
            mod = importlib.import_module(mod_name)
            fn = getattr(mod, attr)
            merged = fn(sku)
            payload = "\n".join(
                [
                    str(merged.get("sku")),
                    str(merged.get("name")),
                    str(merged.get("dossier_slug")),
                    str(merged.get("dossier", {}).get("branding_block", "")),
                    str(merged.get("dossier", {}).get("negative_block", "")),
                ]
            )
            digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
            results[mod_name] = digest
            if canonical_hash is None:
                canonical_hash = digest
        except Exception as exc:
            results[mod_name] = f"<failed: {exc}>"

    # nano_banana lives at scripts/nano_banana — invoke via the import path used
    # in production (PROJECT_ROOT must be on sys.path for `scripts.nano_banana`).
    try:
        nb_mod = importlib.import_module("scripts.nano_banana.catalog")
        merged = nb_mod.load_dossier_for(sku)
        payload = "\n".join(
            [
                str(merged.get("sku")),
                str(merged.get("name")),
                str(merged.get("dossier_slug")),
                str(merged.get("dossier", {}).get("branding_block", "")),
                str(merged.get("dossier", {}).get("negative_block", "")),
            ]
        )
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
        results["scripts.nano_banana.catalog"] = digest
    except Exception as exc:
        results["scripts.nano_banana.catalog"] = f"<failed: {exc}>"

    if raise_on_mismatch and canonical_hash:
        for name, value in results.items():
            if value != canonical_hash and not value.startswith("<"):
                raise RuntimeError(
                    f"Dossier reader divergence on SKU {sku}: {name} → {value}, "
                    f"expected {canonical_hash}"
                )
    return results


def verify_no_orphans(*, raise_on_orphan: bool = False) -> dict[str, list[str]]:
    """Audit production image dirs — flag any SKU-prefixed file whose SKU
    is not in the canonical CSV.

    Walks wordpress-theme/.../products/, assets/products/source-photos/,
    skyyrose/assets/images/products/. For every file matching SKU_RE, asserts
    the SKU prefix is in canonical OR explicitly retired. Files in neither set
    are orphans (the dress-mislabel class of bug).

    Returns:
        Mapping bucket -> list of orphan file paths. Buckets:
          'orphan'   = SKU prefix in no canonical or retired list
          'retired'  = SKU prefix in retired list (per MEMORY.md)
                       and the file lives in wordpress-theme/.../products/
                       (live theme — should not contain retired SKUs)

    Files in source-products that match retired SKUs are NOT flagged here —
    that directory functions as an archive zone. Use the audit script for
    a deeper sweep.
    """
    import csv as _csv
    import re as _re

    repo = Path(__file__).resolve().parent.parent.parent
    canonical_csv = repo / "wordpress-theme" / "skyyrose-flagship" / "data" / "skyyrose-catalog.csv"

    canonical_skus: set[str] = set()
    if canonical_csv.exists():
        with open(canonical_csv) as f:
            for row in _csv.DictReader(f):
                canonical_skus.add(row["sku"])

    # Per MEMORY.md retired SKU codes
    retired_skus = {
        "lh-001",
        "br-d01",
        "br-d02",
        "br-d03",
        "br-d04",
        "sg-d01",
        "sg-d02",
        "sg-d03",
        "sg-d04",
        "sg-008",
        "sg-010",
    }

    sku_re = _re.compile(r"^(br|lh|sg|kids)-([0-9d][0-9]{1,2})")

    live_theme_dir = (
        repo / "wordpress-theme" / "skyyrose-flagship" / "assets" / "images" / "products"
    )
    image_exts = (".jpg", ".jpeg", ".png", ".webp")

    orphans: list[str] = []
    retired_in_live: list[str] = []

    if live_theme_dir.exists():
        for root, _, files in os.walk(live_theme_dir):
            for fname in files:
                if not fname.lower().endswith(image_exts):
                    continue
                m = sku_re.match(fname.lower())
                if not m:
                    continue
                sku = f"{m.group(1)}-{m.group(2)}"
                full = str(Path(root) / fname)
                if sku in retired_skus:
                    retired_in_live.append(full)
                elif sku not in canonical_skus:
                    orphans.append(full)

    # Also check skyyrose/assets/images/products/ for true orphan SKU dirs
    secondary = repo / "skyyrose" / "assets" / "images" / "products"
    if secondary.exists():
        for sku_dir in secondary.iterdir():
            if not sku_dir.is_dir():
                continue
            if not sku_re.match(sku_dir.name.lower()):
                continue
            sku = sku_dir.name.lower()
            if sku not in canonical_skus and sku not in retired_skus:
                # Generated-render directory for a SKU that doesn't exist
                for f in sku_dir.iterdir():
                    if f.is_file() and f.suffix.lower() in image_exts:
                        orphans.append(str(f))

    issues = {"orphan": orphans, "retired_in_live_theme": retired_in_live}
    if raise_on_orphan and (orphans or retired_in_live):
        raise RuntimeError(f"Orphan / retired-in-live findings: {issues}")
    return issues


def validate_pipeline_models(*, raise_on_missing: bool = False) -> dict[str, list[str]]:
    """Verify every configured pipeline model is available at the provider.

    Calls each provider's models.list() endpoint and asserts every model in
    the registry resolves. Use this at deploy time (not per-request) to catch
    model deprecation/drift before user requests hit a 404.

    Args:
        raise_on_missing: When True, raises RuntimeError on any missing model.

    Returns:
        Mapping of provider name -> list of unavailable model IDs (empty list
        means that provider is healthy). Special sentinel "<list_failed: ...>"
        indicates the list call itself failed (auth, network, etc.).
    """
    issues: dict[str, list[str]] = {"anthropic": [], "openai": [], "google": []}

    # --- Anthropic ---
    try:
        client = get_anthropic_client()
        available = {m.id for m in client.models.list().data}
        for required in (CLAUDE_OPUS_MODEL, CLAUDE_SONNET_MODEL):
            if required not in available:
                issues["anthropic"].append(required)
    except Exception as exc:
        issues["anthropic"].append(f"<list_failed: {exc}>")

    # --- OpenAI ---
    try:
        client = get_openai_client()
        available = {m.id for m in client.models.list().data}
        for required in (OPENAI_IMAGE_MODEL, OPENAI_VISION_MODEL):
            if required not in available:
                issues["openai"].append(required)
    except Exception as exc:
        issues["openai"].append(f"<list_failed: {exc}>")

    # --- Google Gemini (google-genai SDK) ---
    try:
        from google import genai as _genai

        client = _genai.Client()
        available = set()
        for m in client.models.list():
            name = getattr(m, "name", "")
            available.add(name.removeprefix("models/") if name else "")
        for required in (GEMINI_IMAGE_GEN_MODEL, GEMINI_VISION_MODEL):
            if required not in available:
                issues["google"].append(required)
    except Exception as exc:
        issues["google"].append(f"<list_failed: {exc}>")

    if raise_on_missing:
        all_missing = [m for v in issues.values() for m in v]
        if all_missing:
            raise RuntimeError(f"Pipeline model validation failed: {issues}")

    return issues
