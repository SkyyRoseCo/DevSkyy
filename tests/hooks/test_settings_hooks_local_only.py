"""Project hooks run on the founder's machine only, never inside CI review bots.

claude-code-action loads `.claude/settings.json` (settingSources include
"project"), so without a guard every PR's review bot would run the session
audit, prompt router, pytest stop-gate and format-on-edit hooks.
FOUNDER_CONFIRMED 2026-10-11: hooks are local-only.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SETTINGS = ROOT / ".claude" / "settings.json"
GUARD = '[ -n "${GITHUB_ACTIONS:-}" ] && exit 0; '
BASH = shutil.which("bash") or "/bin/bash"


def _commands() -> list[str]:
    hooks = json.loads(SETTINGS.read_text())["hooks"]
    return [
        h["command"]
        for entries in hooks.values()
        for entry in entries
        for h in entry["hooks"]
        if h.get("type") == "command"
    ]


def test_every_hook_command_is_guarded() -> None:
    unguarded = [c for c in _commands() if not c.startswith(GUARD)]
    assert _commands(), "no hook commands found"
    assert not unguarded, unguarded


def test_no_hook_command_hardcodes_a_home_path() -> None:
    assert not [
        c
        for c in _commands()
        if "/Users/" in c.replace("${CLAUDE_PROJECT_DIR:-/Users/theceo/DevSkyy}", "")
    ]


@pytest.mark.parametrize("command", _commands())
def test_real_hook_command_is_a_no_op_under_github_actions(command: str, tmp_path: Path) -> None:
    # CLAUDE_PROJECT_DIR points at an empty dir: any hook body that runs fails or
    # writes output, so a clean, silent exit proves the guard short-circuited it.
    env = {**os.environ, "GITHUB_ACTIONS": "true", "CLAUDE_PROJECT_DIR": str(tmp_path)}
    result = subprocess.run(
        [BASH, "-c", command],
        input="{}",
        env=env,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert (result.returncode, result.stdout, result.stderr) == (0, "", ""), result
