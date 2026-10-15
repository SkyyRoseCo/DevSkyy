"""Brand enforcement — retired taglines must never appear in generated content.

This test reads retired taglines from `assets/brand/brand.yaml` and asserts
they do not appear (case-insensitively) in any tracked source file EXCEPT:
  - brand.yaml itself (the source of the list)
  - test files (they use the phrases as negative fixtures)
  - the brand loader (it reads the list to expose it)
  - the founder's verbatim Signature story quote and the Kids Capsule
    insert-card copy, retained by founder decision 2026-10-06

Run: pytest skyyrose/elite_studio/tests/test_brand_enforcement.py -v

If this test fails, a retired phrase has crept back into generated content.
Remove it or migrate the caller to read `BrandConfig.tagline_active` instead.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from skyyrose.elite_studio.brand import BrandConfig

pytest.importorskip("yaml")


_REPO_ROOT = Path(__file__).resolve().parents[3]

# Files that ARE allowed to reference retired taglines (they catalog them or
# enforce them). Any other tracked file is a violation.
_ALLOWED_PATHS = frozenset(
    {
        "assets/brand/brand.yaml",
        "skyyrose/elite_studio/tests/test_brand_enforcement.py",
        "skyyrose/elite_studio/tests/test_brand.py",
        "skyyrose/elite_studio/brand.py",
        # Corey's verbatim Signature founder-story quote ("I said luxury grows
        # from concrete — and I meant that literally") and its typographic
        # split; FOUNDER-authored, retained on 2026-10-06.
        "wordpress-theme/skyyrose-flagship/inc/collection-content.php",
        "wordpress-theme/skyyrose-flagship/data/collections/signature/copy.md",
        "wordpress-theme/skyyrose-flagship/data/collections/signature/index.html",
        # Kids Capsule insert card: the printed card is a physical product
        # fact, not generated copy.
        "wordpress-theme/skyyrose-flagship/data/collections/kids-capsule/copy.md",
        "wordpress-theme/skyyrose-flagship/data/collections/kids-capsule/index.html",
    }
)

# Directories to scan: every surface that renders copy or feeds a prompt.
_SCAN_DIRS = (
    "wordpress",
    "wordpress-theme",
    "frontend",
    "skyyrose",
    "scripts",
    "agents",
    "sdk",
    "hf-spaces",
    "orchestration",
    "services",
    "api",
    "integrations",
    "examples",
    "evaluation",
)

# File extensions to scan.
_SCAN_EXTS = frozenset(
    {".py", ".php", ".ts", ".tsx", ".js", ".jsx", ".yaml", ".yml", ".md", ".html"}
)


def _git_tracked_files() -> list[Path]:
    """Return all git-tracked files under _SCAN_DIRS with _SCAN_EXTS extensions."""
    try:
        result = subprocess.run(
            ["git", "-C", str(_REPO_ROOT), "ls-files", *_SCAN_DIRS],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        pytest.skip("git not available")
    if result.returncode != 0:
        pytest.skip(f"git ls-files failed: {result.stderr[:200]}")
    paths: list[Path] = []
    for line in result.stdout.splitlines():
        rel = line.strip()
        if not rel:
            continue
        rel_path = Path(rel)
        if rel_path.suffix.lower() not in _SCAN_EXTS:
            continue
        # Test files use retired phrases as negative fixtures.
        if "tests" in rel_path.parts or rel_path.name.startswith("test_"):
            continue
        paths.append(_REPO_ROOT / rel)
    return paths


# Words/phrases on the same line that mark an enforcement mention (allowed).
# If ANY of these co-occur with a retired phrase on the same line, it's
# documentation/assertion/rejection — not an actual usage.
_ENFORCEMENT_KEYWORDS = (
    "retired",
    "RETIRED",
    "never use",
    "Never use",
    "NEVER use",
    "NEVER",
    "is dead",
    "not the tagline",
    "do not use",
    "forbidden",
    "not in",
    "assert ",
    "retired_tagline",
    "DEPRECATED",
    "decommissioned",
    "banned",
)


def _is_enforcement_line(line: str) -> bool:
    """True if the line is declaring/rejecting the retired phrase, not using it."""
    return any(kw in line for kw in _ENFORCEMENT_KEYWORDS)


def test_retired_taglines_do_not_appear_as_actual_usage() -> None:
    brand = BrandConfig.load()
    retired = list(brand.retired_taglines)
    if not retired:
        pytest.skip("No retired taglines declared in brand.yaml")

    violations: list[tuple[str, str, int, str]] = []  # (rel_path, phrase, line_no, line)
    retired_folded = [(phrase, phrase.lower()) for phrase in retired]

    for path in _git_tracked_files():
        try:
            rel_path = str(path.relative_to(_REPO_ROOT))
        except ValueError:
            continue
        if rel_path in _ALLOWED_PATHS:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        content_folded = content.lower()
        for phrase, phrase_folded in retired_folded:
            if phrase_folded not in content_folded:
                continue
            for line_no, line in enumerate(content.splitlines(), start=1):
                if phrase_folded not in line.lower():
                    continue
                if _is_enforcement_line(line):
                    continue  # enforcement mention — allowed
                violations.append((rel_path, phrase, line_no, line.strip()[:120]))

    if violations:
        msg = "Retired tagline(s) used as actual content (must be migrated):\n"
        for rel_path, phrase, line_no, snippet in violations[:30]:
            msg += f"  {rel_path}:{line_no}  — {phrase!r}\n    {snippet}\n"
        if len(violations) > 30:
            msg += f"  ... {len(violations) - 30} more\n"
        msg += (
            "\nReplace with BrandConfig.load().tagline_active, or if this is an "
            "enforcement mention (instruction to NOT use the phrase), include one "
            "of the enforcement keywords (retired, NEVER, do not use, etc.) on "
            "the same line."
        )
        pytest.fail(msg)
