"""
SkyyRose DirectContext — Semantic codebase index for the auggie-sdk.

Builds a single shared DirectContext that indexes:
- skyyrose-catalog.csv + data/sot-images.json + logo-registry.json + SOT.md
- Per-SKU golden dossiers from skyyrose/elite_studio/assets/golden/
- OODA scene contracts from Comfy/scene-contracts/
- AGENTS.md + CLAUDE.md (engineering protocol)

Usage:
    from sdk.python.agent_sdk.context import get_skyyrose_context

    ctx = get_skyyrose_context()
    answer = ctx.search_and_ask("What are the exact specs for br-005?")
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_CONTEXT = None
_REPO_ROOT = Path(__file__).resolve().parents[3]
_CACHE_PATH = _REPO_ROOT / ".augment" / "skyyrose-context.json"

_SOT_PATHS = [
    "skyyrose-catalog.csv",
    "data/sot-images.json",
    "logo-registry.json",
    "SOT.md",
    "AGENTS.md",
    "CLAUDE.md",
]

_GLOB_PATTERNS = [
    ("skyyrose/elite_studio/assets/golden", "**/*.md"),
    ("Comfy/scene-contracts", "*.json"),
    ("docs", "ARCHITECTURE.md"),
]

_MAX_FILE_BYTES = 200_000  # skip binary / huge files


def _collect_files():
    """Collect all files to index, skipping missing or too-large paths."""
    try:
        from auggie_sdk.context import File
    except ImportError:
        logger.warning("auggie_sdk not installed — context indexing unavailable")
        return []

    files = []

    for rel in _SOT_PATHS:
        p = _REPO_ROOT / rel
        if p.is_file() and p.stat().st_size < _MAX_FILE_BYTES:
            files.append(File(path=rel, contents=p.read_text(encoding="utf-8", errors="replace")))

    for base_rel, pattern in _GLOB_PATTERNS:
        base = _REPO_ROOT / base_rel
        if not base.is_dir():
            continue
        for p in sorted(base.glob(pattern)):
            if p.stat().st_size > _MAX_FILE_BYTES:
                continue
            rel = str(p.relative_to(_REPO_ROOT))
            files.append(File(path=rel, contents=p.read_text(encoding="utf-8", errors="replace")))

    logger.info("[context] collected %d files for indexing", len(files))
    return files


def get_skyyrose_context(*, force_rebuild: bool = False):
    """Return the shared DirectContext, building it on first call.

    The context is cached in-process and exported to
    .augment/skyyrose-context.json for cross-session reuse.
    """
    global _CONTEXT
    if _CONTEXT is not None and not force_rebuild:
        return _CONTEXT

    try:
        from auggie_sdk.context import DirectContext
    except ImportError:
        raise RuntimeError("auggie_sdk is not installed. Run: pip install auggie-sdk") from None

    ctx = DirectContext.create()
    files = _collect_files()
    if files:
        result = ctx.add_to_index(files)
        logger.info(
            "[context] indexed %d files (%d newly uploaded)",
            len(files),
            len(getattr(result, "newly_uploaded", [])),
        )

    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ctx.export_to_file(str(_CACHE_PATH))
    logger.info("[context] exported to %s", _CACHE_PATH)

    _CONTEXT = ctx
    return ctx


def search(query: str) -> str:
    """Semantic search over the SkyyRose codebase index."""
    return get_skyyrose_context().search_and_ask(query)
