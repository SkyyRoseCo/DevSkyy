"""Shared helpers for the Claude Code / Codex hook tests.

Every test feeds a REAL hook payload (the JSON Claude Code writes to the hook's
stdin) to the shell script and asserts on exit code + output, so a regression
in parsing or matching fails the test rather than silently no-op'ing the hook.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
# Attribution (CLAUDE.md §3): point HOOKS_TREE at a `git archive` of a pristine
# commit to run this same suite against the old hooks and prove it goes RED.
HOOKS_TREE = Path(os.environ.get("HOOKS_TREE", REPO_ROOT)).resolve()
HOOK_DIRS = {
    "claude": HOOKS_TREE / ".claude" / "hooks",
    "codex": HOOKS_TREE / ".codex" / "hooks",
}
_HOOK_SWITCHES = frozenset(
    {
        "PAID_API_STOPGATE_DISABLE",
        "PY_FORMAT_ON_WRITE_DISABLE",
        "PHPCS_ON_WRITE_DISABLE",
        "CLAUDE_TOOL_INPUT_FILE_PATH",
    }
)
GIT = shutil.which("git") or "/usr/bin/git"
BASH = shutil.which("bash") or "/bin/bash"


def run_hook(
    script: Path,
    payload: dict,
    *,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run ``bash <script>`` with ``payload`` as JSON on stdin, like the harness.

    Switches a developer may have exported (hook kill-switches, the legacy
    file-path env the drift guard reads before stdin) are scrubbed so the
    caller's shell cannot flip an outcome; a test passes them via ``env``.
    """
    inherited = {k: v for k, v in os.environ.items() if k not in _HOOK_SWITCHES}
    full_env = {**inherited, **(env or {})}
    return subprocess.run(
        [BASH, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=full_env,
        cwd=str(cwd or REPO_ROOT),
        timeout=60,
    )


def git(repo: Path, *args: str) -> str:
    out = subprocess.run(
        [GIT, "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    return out.stdout.strip()


def init_repo(path: Path, files: dict[str, str], executables: frozenset[str] = frozenset()) -> Path:
    """Create a throwaway git repo at ``path`` with ``files`` committed.

    Hooks resolve the repo root from the edited file, so tests run them against
    a tmp repo (never the real checkout) — no generator can write tracked files.
    ``executables`` names the ``files`` keys that must carry the exec bit.
    """
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q", "-b", "main")
    git(path, "config", "user.email", "hooks-test@example.invalid")
    git(path, "config", "user.name", "hooks-test")
    git(path, "config", "commit.gpgsign", "false")
    for rel, content in files.items():
        target = path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        if rel in executables:
            target.chmod(0o755)
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", "init")
    return path


def add_worktree(repo: Path, path: Path, branch: str = "wt") -> Path:
    """Add a linked worktree of ``repo`` at ``path`` (shares repo's git common dir)."""
    git(repo, "worktree", "add", "-q", "-b", branch, str(path))
    return path


# The fake phpcs / python used where a test only needs to observe HOW the hook
# invoked the tool: it appends its argv to <self>.log and exits 0.
FAKE_TOOL = '#!/usr/bin/env bash\nprintf "%s\\n" "$@" >> "$0.log"\nexit 0\n'


def install_hook(repo: Path, name: str, flavor: str = "claude") -> Path:
    """Copy one hook (plus lib/) into ``repo`` so the script's own repo == repo."""
    src_dir = HOOK_DIRS[flavor]
    dst_dir = repo / ".claude" / "hooks"
    (dst_dir / "lib").mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_dir / name, dst_dir / name)
    for lib in (src_dir / "lib").glob("*.sh"):
        shutil.copy2(lib, dst_dir / "lib" / lib.name)
    return dst_dir / name


@pytest.fixture(params=["claude", "codex"])
def flavor(request: pytest.FixtureRequest) -> str:
    """Both hook trees are wired (settings.json / .codex/hooks.json); test both."""
    return request.param
