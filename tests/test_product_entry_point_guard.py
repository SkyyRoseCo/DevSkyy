"""Guard: product facts are read through the entry point, not scraped from files.

The scatter this prevents is the one the founder named -- agents hunting for
product data across a dozen files, each picking a different subset and each
drifting independently. ``skyyrose.core.product.get_product`` is the one read
path; this test makes a NEW direct reader fail CI instead of quietly becoming
the twelfth source of truth.

It is deliberately an allowlist, not a clean-slate assertion. Two modules read
an authored side-store directly today. They are enumerated below with a reason
and a disposition, so the remaining migration debt is visible in code rather
than implied. Removing an entry from the allowlist is how that debt gets paid;
adding one requires justifying why the entry point cannot serve the need.

Companion guard: ``tests/test_sot_no_adhoc_imagery.py`` does the same job for
hardcoded image paths.

**Boundary — what this does NOT catch.** It matches the four authored
side-stores by filename. A module that bypasses the entry point a different
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

# The authored stores that hold product facts. Reading one of these directly
# means bypassing the layering, provenance, and gap reporting get_product adds.
GUARDED_STORES = (
    "product-content.json",
    "alt-text.json",
    "render-corrections.json",
    "render-keepers.json",
)

# Source trees that can reach product data. Tests, docs, and task artifacts are
# out of scope -- this guards shipping code.
SCANNED_DIRS = ("skyyrose", "api", "scripts", "agents", "database")

# path -> why it is allowed to read a store directly.
#
# "authoring tool" is permanent: something has to write the file.
# "MIGRATE" is debt -- the module should move to get_product(sku).
ALLOWED: dict[str, str] = {
    "skyyrose/core/product.py": "the entry point itself -- it is what assembles the record",
    "skyyrose/skyyrose_content_agent.py": (
        "authoring tool: it WRITES product-content.json, so it owns the file. "
        "A writer legitimately touches its own store."
    ),
    "scripts/oai_render/config.py": (
        "MIGRATE: declares CORRECTIONS_JSON / KEEPERS_JSON for the render pipeline "
        "(pipeline.py consumes them through this module, so migrating here moves both). "
        "Should read get_product(sku)['corrections'] and ['render_policy'] instead."
    ),
}

# A prose mention in a docstring or prompt string is not a read. Only flag a
# path that appears with something that looks like file access.
_ACCESS = re.compile(
    r"(open\(|read_text|json\.load|Path\(|join\(|/\s*[\"']|_JSON\s*=|_PATH\s*=)",
)


def _source_files() -> list[Path]:
    files: list[Path] = []
    for directory in SCANNED_DIRS:
        root = REPO_ROOT / directory
        if not root.is_dir():
            continue
        files.extend(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)
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
