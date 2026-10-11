"""Tests for .wolf/hooks/handoff-gate.sh — the session handoff log gate.

The gate is shared by Claude Code and Codex, so each case drives it with the
JSON those harnesses send on stdin, against a throwaway git repo and memory file.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / ".wolf" / "hooks" / "handoff-gate.sh"
SID = "abcd1234-0000-4000-8000-000000000000"
SID8 = SID[:8]

pytestmark = pytest.mark.skipif(
    shutil.which("jq") is None or shutil.which("git") is None,
    reason="handoff gate needs jq and git",
)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / ".wolf").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "feat/x", str(root)], check=True)
    (root / ".wolf" / "memory.md").write_text("# Memory\n\n| 00:00 | old row | — | — | — |\n")
    return root


def run(repo: Path, tmp_path: Path, payload: dict, agent: str = "claude-code") -> str:
    env = {
        "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
        "HOME": str(tmp_path),
        "WOLF_HANDOFF_STATE_DIR": str(tmp_path / "state"),
        "WOLF_HANDOFF_NOW": "2026-10-11 12:00",
    }
    payload = {"session_id": SID, "cwd": str(repo), **payload}
    out = subprocess.run(
        ["bash", str(SCRIPT), "--agent", agent],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        timeout=20,
    )
    assert out.returncode == 0, out.stderr
    return out.stdout.strip()


def edit(repo: Path, tmp_path: Path, rel: str = "app.py") -> None:
    payload = {
        "hook_event_name": "PostToolUse",
        "tool_name": "Edit",
        "tool_input": {"file_path": str(repo / rel)},
    }
    run(repo, tmp_path, payload)


def stop(repo: Path, tmp_path: Path, active: bool = False, agent: str = "claude-code") -> str:
    return run(repo, tmp_path, {"hook_event_name": "Stop", "stop_hook_active": active}, agent)


def log_row(repo: Path, note: str = "did x") -> None:
    with (repo / ".wolf" / "memory.md").open("a") as fh:
        fh.write(
            f"| 2026-10-11 12:01 | claude-code @ feat/x sid:{SID8} | {note} | app.py | done | ~1k |\n"
        )


def prompt(repo: Path, tmp_path: Path) -> str:
    return run(repo, tmp_path, {"hook_event_name": "UserPromptSubmit", "prompt": "next"})


def test_read_only_turn_does_not_block(repo: Path, tmp_path: Path) -> None:
    assert stop(repo, tmp_path) == ""


def test_edit_without_log_row_blocks_with_prefilled_row(repo: Path, tmp_path: Path) -> None:
    edit(repo, tmp_path)
    out = json.loads(stop(repo, tmp_path))
    assert out["decision"] == "block"
    assert f"| 2026-10-11 12:00 | claude-code @ feat/x sid:{SID8} |" in out["reason"]
    assert str(repo / ".wolf" / "memory.md") in out["reason"]


def test_log_row_clears_the_gate(repo: Path, tmp_path: Path) -> None:
    edit(repo, tmp_path)
    log_row(repo)
    assert stop(repo, tmp_path) == ""
    # Marker cleared: a later read-only turn passes too.
    assert stop(repo, tmp_path) == ""


def test_more_work_after_logging_needs_a_new_row(repo: Path, tmp_path: Path) -> None:
    edit(repo, tmp_path)
    log_row(repo)
    assert stop(repo, tmp_path) == ""
    edit(repo, tmp_path, "other.py")
    assert json.loads(stop(repo, tmp_path))["decision"] == "block"


def test_auto_session_rows_and_other_sessions_do_not_count(repo: Path, tmp_path: Path) -> None:
    edit(repo, tmp_path)
    with (repo / ".wolf" / "memory.md").open("a") as fh:
        fh.write(
            f"| 12:00 | session end (exit) — {SID8} on feat/x @abc · uncommitted: 1 | — | closed | — |\n"
        )
        fh.write(
            "| 2026-10-11 12:01 | codex @ main sid:ffffffff | other agent | x | done | ~1k |\n"
        )
    assert json.loads(stop(repo, tmp_path))["decision"] == "block"


def test_reentry_lets_the_turn_end(repo: Path, tmp_path: Path) -> None:
    edit(repo, tmp_path)
    assert stop(repo, tmp_path, active=True) == ""


def test_blocks_only_once_per_session_then_reminds(repo: Path, tmp_path: Path) -> None:
    """Soft mode: the first unlogged turn blocks; later ones only remind the user."""
    edit(repo, tmp_path)
    assert json.loads(stop(repo, tmp_path))["decision"] == "block"
    # Agent ignored it; next turn's Stop is non-blocking.
    edit(repo, tmp_path, "other.py")
    out = json.loads(stop(repo, tmp_path))
    assert "decision" not in out
    assert f"sid:{SID8}" in out["systemMessage"]


def test_user_prompt_reminds_the_model_while_unlogged(repo: Path, tmp_path: Path) -> None:
    edit(repo, tmp_path)
    out = json.loads(prompt(repo, tmp_path))
    ctx = out["hookSpecificOutput"]
    assert ctx["hookEventName"] == "UserPromptSubmit"
    assert f"claude-code @ feat/x sid:{SID8}" in ctx["additionalContext"]
    log_row(repo)
    assert prompt(repo, tmp_path) == ""


def test_rotation_archiving_the_old_row_is_not_a_new_row(repo: Path, tmp_path: Path) -> None:
    """A session row moved to the archive must not count as freshly logged."""
    memory = repo / ".wolf" / "memory.md"
    log_row(repo, "earlier work")
    edit(repo, tmp_path)
    memory.write_text("# Memory\n\n| 00:00 | unrelated | — | — | — |\n")  # rotated away
    assert json.loads(stop(repo, tmp_path))["decision"] == "block"
    log_row(repo, "new work")
    assert stop(repo, tmp_path) == ""


def test_writing_the_memory_file_is_not_work(repo: Path, tmp_path: Path) -> None:
    edit(repo, tmp_path, ".wolf/memory.md")
    assert stop(repo, tmp_path) == ""


def test_edits_outside_the_repo_are_ignored(repo: Path, tmp_path: Path) -> None:
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    payload = {
        "hook_event_name": "PostToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": str(scratch / "notes.txt")},
    }
    run(repo, tmp_path, payload)
    assert stop(repo, tmp_path) == ""


@pytest.mark.parametrize(
    "cmd",
    [
        "git commit -m 'fix: x'",
        "git -C /x push origin feat/x",
        "rm -rf build",
        "echo hi > out.txt",
        "cd frontend && npm run build",
        "sed -i '' 's/a/b/' f.py",
    ],
)
def test_mutating_shell_commands_mark_dirty(repo: Path, tmp_path: Path, cmd: str) -> None:
    run(
        repo,
        tmp_path,
        {"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": {"command": cmd}},
    )
    assert json.loads(stop(repo, tmp_path))["decision"] == "block"


@pytest.mark.parametrize(
    "cmd",
    [
        "git status --short",
        "git diff -- CLAUDE.md 2>/dev/null",
        "grep -rn foo src 2>&1 | head",
        "ls -la",
        "printf '| row |\\n' >> .wolf/memory.md",
    ],
)
def test_read_only_and_logging_shell_commands_do_not(repo: Path, tmp_path: Path, cmd: str) -> None:
    run(
        repo,
        tmp_path,
        {"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": {"command": cmd}},
    )
    assert stop(repo, tmp_path) == ""


def test_codex_apply_patch(repo: Path, tmp_path: Path) -> None:
    patch = "*** Begin Patch\n*** Update File: app.py\n@@\n-a\n+b\n*** End Patch\n"
    run(
        repo,
        tmp_path,
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "apply_patch",
            "tool_input": {"command": patch},
        },
    )
    out = json.loads(stop(repo, tmp_path, agent="codex"))
    assert f"codex @ feat/x sid:{SID8}" in out["reason"]


def test_codex_patch_touching_only_the_log_is_exempt(repo: Path, tmp_path: Path) -> None:
    patch = "*** Begin Patch\n*** Update File: .wolf/memory.md\n@@\n+| row |\n*** End Patch\n"
    run(
        repo,
        tmp_path,
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "apply_patch",
            "tool_input": {"command": patch},
        },
    )
    assert stop(repo, tmp_path, agent="codex") == ""


def test_worktree_logs_to_main_checkout(repo: Path, tmp_path: Path) -> None:
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=t",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "init",
        ],
        check=True,
    )
    wt = tmp_path / "wt"
    subprocess.run(
        ["git", "-C", str(repo), "worktree", "add", "-q", "-b", "feat/wt", str(wt)], check=True
    )
    run(
        wt,
        tmp_path,
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Edit",
            "tool_input": {"file_path": str(wt / "app.py")},
        },
    )
    out = json.loads(run(wt, tmp_path, {"hook_event_name": "Stop", "stop_hook_active": False}))
    assert str(repo / ".wolf" / "memory.md") in out["reason"]
    assert "@ feat/wt sid:" in out["reason"]


COMMIT_CMD = "git " + "commit -m 'fix: x'"


def test_cwd_outside_repo_still_gates_edits_inside_it(repo: Path, tmp_path: Path) -> None:
    """The shell may have wandered off; the edited path decides, and Stop still fires."""
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    payload = {
        "hook_event_name": "PostToolUse",
        "cwd": str(elsewhere),
        "tool_name": "Edit",
        "tool_input": {"file_path": str(repo / "app.py")},
    }
    run(repo, tmp_path, payload)
    out = json.loads(run(repo, tmp_path, {"hook_event_name": "Stop", "cwd": str(elsewhere)}))
    assert out["decision"] == "block"
    assert str(repo / ".wolf" / "memory.md") in out["reason"]
    assert "@ feat/x sid:" in out["reason"]


def test_shell_cd_into_repo_from_outside_is_gated(repo: Path, tmp_path: Path) -> None:
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    payload = {
        "hook_event_name": "PostToolUse",
        "cwd": str(elsewhere),
        "tool_name": "Bash",
        "tool_input": {"command": f"cd {repo} && {COMMIT_CMD}"},
    }
    run(repo, tmp_path, payload)
    assert json.loads(stop(repo, tmp_path))["decision"] == "block"


def test_codex_argv_array_command(repo: Path, tmp_path: Path) -> None:
    argv = ["bash", "-lc", COMMIT_CMD]
    run(
        repo,
        tmp_path,
        {"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": {"command": argv}},
    )
    assert json.loads(stop(repo, tmp_path, agent="codex"))["decision"] == "block"


def test_codex_argv_array_read_only(repo: Path, tmp_path: Path) -> None:
    argv = ["bash", "-lc", "git status --short"]
    run(
        repo,
        tmp_path,
        {"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": {"command": argv}},
    )
    assert stop(repo, tmp_path, agent="codex") == ""
