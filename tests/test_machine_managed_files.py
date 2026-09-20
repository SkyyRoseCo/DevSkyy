"""The formatter-ownership gate: one registry, checked against both configs.

Files with a program that owns their bytes (a serializer, a generator, a
minifier) must be invisible to every formatter. That knowledge used to live in
two hand-maintained places — `.prettierignore` and `lint-staged.config.mjs` —
with nothing tying them together, so a new generated file could be added to one,
the other, or neither. `.wolf/buglog.json` and `.wolf/anatomy.md` were in
neither, and prettier rewrote 1,643 lines of the bug log the first time it was
staged, after which the MCP server's serializer wrote it straight back.

`data/machine-managed-files.json` is now the one list. These checks need nothing
but Python, so they run in every job; `scripts/verify-formatter-ignores.mjs`
additionally asks prettier and lint-staged themselves, where node is available.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "data" / "machine-managed-files.json"
PRETTIERIGNORE_PATH = REPO_ROOT / ".prettierignore"
LINT_STAGED_PATH = REPO_ROOT / "lint-staged.config.mjs"

# A .prettierignore line that is deliberately NOT a machine-managed file. Keep
# this empty unless there is a real reason: every entry here is a line the
# registry no longer governs.
ALLOWED_UNREGISTERED_IGNORES: frozenset[str] = frozenset()


def _registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _ignore_lines() -> list[str]:
    return [
        line.strip()
        for line in PRETTIERIGNORE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


@pytest.fixture(scope="module")
def registry() -> dict:
    return _registry()


class TestRegistryShape:
    def test_registry_is_not_empty(self, registry: dict) -> None:
        """Every other check here iterates the entries, so an empty registry
        would pass all of them while proving nothing — the same vacuous pass
        that let the old two-list parity check go green after its input moved.
        The floor is a count, not just non-emptiness, so silent shrinkage
        (a truncated write, a bad merge resolution) fails too. Raise it when
        entries are added; lowering it needs a reason in the commit message.
        """
        entries = registry.get("entries")
        assert isinstance(entries, list), "registry.entries must be a list"
        assert len(entries) >= 14, (
            f"registry has {len(entries)} entries, expected at least 14 — "
            "entries were removed, or the file was truncated"
        )

    def test_every_entry_names_its_owner_and_reason(self, registry: dict) -> None:
        for entry in registry["entries"]:
            for field in ("pattern", "owner", "why"):
                assert entry.get(field), f"{entry.get('pattern', entry)!r}: {field} is required"
            assert entry.get("samples"), f"{entry['pattern']!r}: at least one sample path"

    def test_patterns_are_unique(self, registry: dict) -> None:
        patterns = [e["pattern"] for e in registry["entries"]]
        duplicates = sorted({p for p in patterns if patterns.count(p) > 1})
        assert not duplicates, f"duplicate patterns: {duplicates}"

    def test_samples_exist(self, registry: dict) -> None:
        """A registry pointing at deleted files stops proving anything.

        Worktrees are sparse (no assets/, renders/), so a sample is only
        checked when its top-level directory is present in this checkout.
        """
        missing = []
        for entry in registry["entries"]:
            for sample in entry["samples"]:
                top = REPO_ROOT / sample.split("/")[0]
                if top.exists() and not (REPO_ROOT / sample).exists():
                    missing.append(sample)
        assert not missing, f"registry samples no longer exist: {missing}"


class TestPrettierIgnoreCoversTheRegistry:
    def test_every_pattern_is_a_prettierignore_line(self, registry: dict) -> None:
        lines = set(_ignore_lines())
        missing = [e["pattern"] for e in registry["entries"] if e["pattern"] not in lines]
        assert not missing, (
            "machine-managed patterns absent from .prettierignore — prettier would "
            f"rewrite files a program owns: {missing}"
        )

    def test_no_unregistered_ignore_lines(self, registry: dict) -> None:
        """The registry is the list; .prettierignore is its projection."""
        patterns = {e["pattern"] for e in registry["entries"]}
        extra = [
            line
            for line in _ignore_lines()
            if line not in patterns and line not in ALLOWED_UNREGISTERED_IGNORES
        ]
        assert not extra, (
            "these .prettierignore lines are not in data/machine-managed-files.json — "
            f"add them there (with owner and reason) or to ALLOWED_UNREGISTERED_IGNORES: {extra}"
        )


class TestLintStagedReadsTheRegistry:
    def test_config_loads_the_registry_file(self) -> None:
        source = LINT_STAGED_PATH.read_text(encoding="utf-8")
        assert "machine-managed-files.json" in source, (
            "lint-staged.config.mjs must read data/machine-managed-files.json rather than "
            "carry its own copy of the list — a second list is what drifted before"
        )

    def test_config_is_reviewable_text(self) -> None:
        """A control byte in the source makes git treat the file as binary.

        The first version of the pattern matcher used a NUL byte as its "**"
        placeholder. It worked, and every gate passed — but git then rendered
        the file as `Bin 5778 -> 6796 bytes`, so the config that decides which
        files a formatter may rewrite had no reviewable line diff. Editors and
        `Read` display NUL as a space, which is what hid it.
        """
        raw = LINT_STAGED_PATH.read_bytes()
        control = {b for b in raw if b < 9 or 13 < b < 32}
        assert not control, (
            f"lint-staged.config.mjs contains control bytes {sorted(control)}; git treats "
            "the file as binary and its diff stops being reviewable"
        )

    def test_config_has_no_second_hardcoded_path_list(self) -> None:
        """The old `isByteStableOrManaged` inlined the paths as regexes."""
        source = LINT_STAGED_PATH.read_text(encoding="utf-8")
        for stale in ("Comfy/receipts", "fashion-theme-team", "logo-registry"):
            assert stale not in source, (
                f"{stale!r} is hardcoded in lint-staged.config.mjs; it belongs only in "
                "data/machine-managed-files.json"
            )
