#!/usr/bin/env python3
"""Precision cleanup: tidy only what an edit touched or orphaned, never the rest of the file.

Runs as a PostToolUse hook after Edit/MultiEdit/Write on Python files. The baseline is the
file as it was before the edit (the tool payload's ``originalFile``), so every change can be
attributed to the edit instead of to ``git diff HEAD`` (which in a shared checkout would
reformat other sessions' work as yours).

What it does, in order, each step best-effort and each guarded by a syntax check:

1. Removes an import the edit ORPHANED (it existed and was used before, and is unused now).
   An import the edit INTRODUCED is never removed: deleting ``import os`` between the edit that
   adds it and the edit that first uses it broke the second edit (tasks/lessons.md, 2026-06-22).
2. Re-sorts imports with isort, only when the edit touched imports and the baseline was already
   isort-clean, so any change is attributable to the edit.
3. Formats only the touched lines with ``black --line-ranges`` (CI enforces ``black --check``).
   A brand-new file is formatted whole.

It never touches vendored, generated or black-excluded paths, never reads a file it cannot
parse, never raises, and always exits 0: a formatter is not a gate.

Bypass: export PRECISION_CLEANUP_DISABLE=1
"""

from __future__ import annotations

import ast
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # python < 3.11: no black-exclude awareness, so skip, don't crash
    tomllib = None

MAX_BYTES = 512_000
_SKIP_PARTS = {"node_modules", "vendor", "dist", "build", ".next", "__pycache__"}
_GENERATED = re.compile(r"@generated|DO NOT EDIT", re.IGNORECASE)
_TIMEOUT = 5  # 5 tool calls worst case = 25s, inside the hook's 30s budget


def _tool(name: str, root: Path) -> str | None:
    """Resolve a tool from the project venv first, then PATH; None when absent."""
    local = root / ".venv" / "bin" / name
    if local.is_file() and os.access(local, os.X_OK):
        return str(local)
    return shutil.which(name)


def _run(cmd: list[str], text: str, root: Path) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            cmd, input=text, capture_output=True, text=True, cwd=root, timeout=_TIMEOUT, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None


def _black_config(root: Path) -> dict:
    if tomllib is None:
        return {}
    try:
        return tomllib.loads((root / "pyproject.toml").read_text()).get("tool", {}).get("black", {})
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def _excluded(rel: str, root: Path) -> bool:
    """Vendored trees, black's own excludes, and generated headers are never ours to touch."""
    parts = Path(rel).parts
    if any(p in _SKIP_PARTS or p.startswith(".venv") for p in parts):
        return True
    if tomllib is None:
        return True  # cannot read black's exclude list, so cannot prove the path is ours
    cfg = _black_config(root)
    for key in ("exclude", "extend-exclude", "force-exclude"):
        pattern = cfg.get(key)
        if not pattern:
            continue
        try:
            if re.compile(pattern, re.VERBOSE).search("/" + Path(rel).as_posix()):
                return True
        except re.error:
            continue
    return False


def _eligible(rel: str, current: str, root: Path) -> bool:
    if not rel.endswith(".py") or len(current.encode()) > MAX_BYTES:
        return False
    if _excluded(rel, root):
        return False
    if _GENERATED.search("\n".join(current.splitlines()[:5])):
        return False
    try:
        ast.parse(current)
    except (SyntaxError, ValueError):
        return False
    return True


def changed_ranges(baseline: str, current: str) -> list[tuple[int, int]]:
    """1-based inclusive line ranges of ``current`` that differ from ``baseline``."""
    a, b = baseline.splitlines(), current.splitlines()
    ranges = []
    for tag, _i1, _i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag in ("replace", "insert") and j2 > j1:
            ranges.append((j1 + 1, j2))
    return ranges


def _offsets(text: str) -> list[int]:
    starts, pos = [0], 0
    for line in text.splitlines(keepends=True):
        pos += len(line)
        starts.append(pos)
    return starts


def _ruff_f401(rel: str, text: str, root: Path) -> list[dict]:
    ruff = _tool("ruff", root)
    if not ruff or not text.strip():
        return []
    cmd = [ruff, "check", "--select", "F401", "--output-format", "json", "--no-cache"]
    cmd += ["--force-exclude", "--stdin-filename", rel, "-"]
    proc = _run(cmd, text, root)
    if proc is None or proc.returncode not in (0, 1):
        return []
    try:
        return json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        return []


def _drop_orphaned_imports(rel: str, baseline: str, text: str, root: Path, notes: list[str]) -> str:
    now = _ruff_f401(rel, text, root)
    if not now:
        return text
    before = Counter(f["message"] for f in _ruff_f401(rel, baseline, root))
    seen: Counter = Counter()
    starts = _offsets(text)
    edits = []
    for finding in now:
        seen[finding["message"]] += 1
        if seen[finding["message"]] <= before[finding["message"]]:
            continue  # legacy finding: not this edit's debt
        fix = finding.get("fix") or {}
        if fix.get("applicability") != "safe":
            continue
        for e in fix["edits"]:
            lo = starts[e["location"]["row"] - 1] + e["location"]["column"] - 1
            hi = starts[e["end_location"]["row"] - 1] + e["end_location"]["column"] - 1
            region = text[lo:hi]
            # Orphaned = the statement was already there (and used) before the edit.
            if region.strip() and region in baseline:
                edits.append((lo, hi, e["content"], finding["message"]))
    for lo, hi, content, message in sorted(edits, reverse=True):
        text = text[:lo] + content + text[hi:]
        notes.append(f"removed orphaned import: {message}")
    return text


def _import_lines(text: str) -> set[int]:
    lines: set[int] = set()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return lines
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            lines.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))
    return lines


def _sort_touched_imports(rel: str, baseline: str, text: str, root: Path, notes: list[str]) -> str:
    isort = _tool("isort", root)
    if not isort:
        return text
    touched = {n for lo, hi in changed_ranges(baseline, text) for n in range(lo, hi + 1)}
    if not touched & _import_lines(text):
        return text
    if baseline.strip():
        # No --filename: with one, isort applies its skip settings to the (virtual) path and
        # silently echoes the input back unchanged, which looks exactly like "already sorted".
        # Exclusions are handled by _eligible, so stdin + --settings-path is the honest call.
        check = _run([isort, "--check-only", "--settings-path", str(root), "-"], baseline, root)
        if check is None or check.returncode != 0:
            return text  # baseline already unsorted: any diff would not be this edit's
    done = _run([isort, "--settings-path", str(root), "-"], text, root)
    if done is None or done.returncode != 0 or not done.stdout:
        return text
    if done.stdout != text:
        notes.append("sorted imports")
    return done.stdout


def _black_touched(rel: str, baseline: str, text: str, root: Path, notes: list[str]) -> str:
    black = _tool("black", root)
    if not black:
        return text
    cmd = [black, "-q", "--stdin-filename", rel]
    if baseline.strip():
        ranges = changed_ranges(baseline, text)
        if not ranges:
            return text
        for lo, hi in ranges:
            cmd += ["--line-ranges", f"{lo}-{hi}"]
    proc = _run([*cmd, "-"], text, root)
    if proc is None or proc.returncode != 0 or not proc.stdout:
        return text
    if proc.stdout != text:
        notes.append("formatted touched lines")
    return proc.stdout


def cleanup_text(rel: str, baseline: str | None, current: str, root: Path) -> tuple[str, list[str]]:
    """Return ``(cleaned, notes)``. ``baseline`` is None when unknown, "" for a new file."""
    notes: list[str] = []
    if baseline is None or not _eligible(rel, current, root):
        return current, notes
    text = _drop_orphaned_imports(rel, baseline, current, root, notes)
    text = _sort_touched_imports(rel, baseline, text, root, notes)
    text = _black_touched(rel, baseline, text, root, notes)
    try:
        ast.parse(text)
    except SyntaxError:
        return current, ["reverted: cleanup produced invalid syntax"]
    return text, notes


def _write_atomic(path: Path, content: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        shutil.copymode(path, tmp)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def _baseline_from(payload: dict) -> str | None:
    """The pre-edit file text from the tool payload; None when it cannot be known."""
    response = payload.get("tool_response")
    if not isinstance(response, dict):
        return None
    if response.get("type") == "create":
        return ""
    original = response.get("originalFile")
    return original if isinstance(original, str) else None


def _repo_root(path: Path) -> Path:
    forced = os.environ.get("PRECISION_CLEANUP_ROOT")
    if forced:
        return Path(forced).resolve()
    proc = _run(["git", "rev-parse", "--show-toplevel"], "", path.parent)
    if proc is not None and proc.returncode == 0 and proc.stdout.strip():
        return Path(proc.stdout.strip()).resolve()
    return path.parent.resolve()


def main() -> int:
    if os.environ.get("PRECISION_CLEANUP_DISABLE") == "1":
        return 0
    try:
        payload = json.load(sys.stdin)
        file_path = (payload.get("tool_input") or {}).get("file_path")
        if not isinstance(file_path, str) or not file_path.endswith(".py"):
            return 0
        path = Path(file_path).resolve()
        if not path.is_file():
            return 0
        root = _repo_root(path)
        if root not in path.parents:
            return 0
        current = path.read_text(encoding="utf-8")
        cleaned, notes = cleanup_text(
            path.relative_to(root).as_posix(), _baseline_from(payload), current, root
        )
        if cleaned != current:
            _write_atomic(path, cleaned)
            print(f"[precision-cleanup] {path.name}: {'; '.join(notes)}", file=sys.stderr)
    except Exception as exc:  # a formatter must never fail the edit it follows
        print(f"[precision-cleanup] skipped: {type(exc).__name__}: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
