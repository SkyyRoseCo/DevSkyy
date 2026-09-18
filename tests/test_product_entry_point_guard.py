"""Guard: product facts are read through the entry point, not scraped from files.

The scatter this prevents is the one the founder named -- agents hunting for
product data across a dozen files, each picking a different subset and each
drifting independently. ``skyyrose.core.product.get_product`` is the one read
path; this test makes a NEW direct reader fail CI instead of quietly becoming
the twelfth source of truth.

It is deliberately an allowlist, not a clean-slate assertion. The render
corrections, keep decisions, and collection identity are folded into the
registry (schema v2); the remaining readers of a retired store are legacy
scripts awaiting deletion, each enumerated below with its disposition so the
debt is visible in code rather than implied. Removing an entry from the
allowlist is how that debt gets paid; adding one requires justifying why the
entry point cannot serve the need.

Companion guard: ``tests/test_sot_no_adhoc_imagery.py`` does the same job for
hardcoded image paths.

**Boundary — what this does NOT catch.** It matches the retired stores by
filename. A module that bypasses the entry point a different
way still passes: calling ``load_registry()["products"][sku]`` directly, or
reading a generated projection such as ``sot-images.json`` or the catalog CSV,
is invisible here. Those narrow readers stay public on purpose (single-field
needs), so this guard cannot simply ban them. Treat a green run as "no new
side-store scraping", not as "everything goes through get_product".
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from skyyrose.core.paths import REPO_ROOT

# Stores that hold, or held, product facts outside the registry. Reading one
# directly means bypassing the registry and the gap reporting get_product adds.
# garment-analysis.json is Gemini vision output: never a product fact (bug-096).
GUARDED_STORES = (
    "product-content.json",
    "alt-text.json",
    "render-corrections.json",
    "render-keepers.json",
    "identity.json",
    "garment-analysis.json",
)

# Source trees that can reach product data. Tests, docs, and task artifacts are
# out of scope -- this guards shipping code.
SCANNED_DIRS = (
    "skyyrose",
    "api",
    "scripts",
    "agents",
    "database",
    "mcp_tools",
    "devskyy-sdk-app",
    "frontend/app",
    "frontend/lib",
    "wordpress-theme/skyyrose-flagship/data",
    "wordpress-theme/skyyrose-flagship/inc",
)
SCANNED_SUFFIXES = (".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".php")
_SKIPPED_PARTS = {"__pycache__", "node_modules", "vendor", "tests", "__tests__", ".next"}

# path -> why it is allowed to read a store directly.
#
# "RETIRE" is debt with a known end: the file is in the deletion manifest the
# founder approves, and leaves this list in the same change that deletes it.
_LEGACY_NODE_TOOLCHAIN = (
    "RETIRE: legacy Feb-2026 Node toolchain under skyyrose/build (no package.json, "
    "no callers). It reads or writes the retired product-content.json / alt-text.json "
    "copy that its own hard-coded 20-SKU table produced. In the deletion manifest."
)
_RETIRED_RENDER_ENGINE = (
    "RETIRE: pre-OAI render engine (new renders are gpt-image-2 via scripts/oai_render). "
    "Injects garment-analysis.json vision output into render prompts as a spec, the "
    "bug-096 contamination path. In the deletion manifest."
)
ALLOWED: dict[str, str] = {
    "skyyrose/build/gemini-content.js": _LEGACY_NODE_TOOLCHAIN,
    "skyyrose/build/tool-calling.js": _LEGACY_NODE_TOOLCHAIN,
    "skyyrose/build/generate-embeddings.js": _LEGACY_NODE_TOOLCHAIN,
    "skyyrose/build/verify.js": _LEGACY_NODE_TOOLCHAIN,
    "skyyrose/build/generate-skyy-poses.js": _RETIRED_RENDER_ENGINE,
    "scripts/nano-banana-vton.py": _RETIRED_RENDER_ENGINE,
}

# A prose mention in a docstring or prompt string is not a read. Only flag a
# path that appears with something that looks like file access.
_ACCESS = re.compile(
    r"(open\(|read_text|json\.load|Path\(|join\(|/\s*[\"']|_JSON\s*=|_PATH\s*=|"
    r"read[A-Z]\w*\(|resolve\(|require\(|file_get_contents|_OUT\s*=)",
)


def _source_files() -> list[Path]:
    files: list[Path] = []
    for directory in SCANNED_DIRS:
        root = REPO_ROOT / directory
        assert root.is_dir(), f"scanned directory {directory} is missing -- update SCANNED_DIRS"
        files.extend(
            p
            for p in root.rglob("*")
            if p.suffix in SCANNED_SUFFIXES
            and not p.name.endswith(".min.js")
            and not _SKIPPED_PARTS.intersection(p.relative_to(REPO_ROOT).parts)
        )
    return files


def _reads_a_store(text: str) -> list[str]:
    """Stores this file appears to open, as opposed to merely mention.

    The access construct is often on a line ABOVE the filename -- a wrapped
    ``os.path.join(...)`` puts the opening call and the store name two lines
    apart -- so match against a small window rather than a single line.
    """
    lines = text.splitlines()
    hits = []
    for store in GUARDED_STORES:
        for index, line in enumerate(lines):
            if store not in line:
                continue
            window = "\n".join(lines[max(0, index - 2) : index + 1])
            if _ACCESS.search(window):
                hits.append(store)
                break
    return hits


@pytest.fixture(scope="module")
def direct_readers() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for path in _source_files():
        stores = _reads_a_store(path.read_text(encoding="utf-8", errors="ignore"))
        if stores:
            found[str(path.relative_to(REPO_ROOT))] = stores
    return found


def test_no_new_direct_readers(direct_readers: dict[str, list[str]]) -> None:
    """Every module reading an authored store directly must be on the allowlist."""
    unlisted = {path: stores for path, stores in direct_readers.items() if path not in ALLOWED}
    assert not unlisted, (
        "These modules read product facts directly instead of through "
        "skyyrose.core.product.get_product:\n"
        + "\n".join(f"  {path} -> {', '.join(stores)}" for path, stores in unlisted.items())
        + "\n\nUse get_product(sku); it returns the same facts with their source named "
        "and anything absent listed in 'gaps'. If the entry point genuinely cannot "
        "serve this need, add the path to ALLOWED with a reason."
    )


def test_allowlist_has_no_dead_entries(direct_readers: dict[str, list[str]]) -> None:
    """An allowlisted module that no longer reads a store should leave the list.

    This is what turns the MIGRATE entries into progress: once a module is moved
    onto get_product, this test fails until its exemption is deleted.
    """
    dead = sorted(set(ALLOWED) - set(direct_readers))
    assert not dead, (
        "These paths are allowlisted but no longer read an authored store directly. "
        "Remove them from ALLOWED:\n" + "\n".join(f"  {path}" for path in dead)
    )


def test_every_allowlist_entry_states_a_reason() -> None:
    for path, reason in ALLOWED.items():
        assert len(reason) > 20, f"{path} has no real justification"
