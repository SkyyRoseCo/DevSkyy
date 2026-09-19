"""stop-test-gate.sh fails CLOSED when no interpreter can run the suite.

A missing python must never read as "tests passed" (bug-230 class). The gate
reads ``{"cwd": ...}`` from stdin and looks only at that checkout's ``.venv``
and its primary worktree's ``.venv`` — PATH pythons are never used, so a tmp
repo without a venv is a checkout with no interpreter.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.hooks.conftest import FAKE_TOOL, HOOK_DIRS, add_worktree, init_repo, run_hook

HOOK = "stop-test-gate.sh"
NO_VENV_PATH = {"PATH": "/usr/bin:/bin"}  # git/sed/grep only; no python anywhere on PATH
MESSAGE = "Stop-gate: no python interpreter — tests NOT verified"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return init_repo(
        tmp_path / "repo", {"pkg/a.py": "x = 1\n", "tests/test_a.py": "def test_a():\n    pass\n"}
    )


def test_missing_interpreter_blocks_with_message(flavor: str, repo: Path) -> None:
    (repo / "pkg" / "a.py").write_text("x = 2\n")
    result = run_hook(HOOK_DIRS[flavor] / HOOK, {"cwd": str(repo)}, env=NO_VENV_PATH, cwd=repo)
    assert result.returncode == 2, result.stdout + result.stderr
    # On exit 2 Claude Code feeds STDERR to the model; plain stdout is dropped,
    # so a reason printed there blocks the Stop without telling Claude why.
    assert MESSAGE in result.stderr


def test_missing_interpreter_in_worktree_blocks(flavor: str, repo: Path, tmp_path: Path) -> None:
    wt = add_worktree(repo, tmp_path / "wt")
    (wt / "pkg" / "a.py").write_text("x = 3\n")
    result = run_hook(HOOK_DIRS[flavor] / HOOK, {"cwd": str(wt)}, env=NO_VENV_PATH, cwd=tmp_path)
    assert result.returncode == 2
    assert MESSAGE in result.stderr
    assert str(wt) in result.stderr  # gated the stopping session's own tree


FAILING_PYTHON = '#!/usr/bin/env bash\necho "FAILED tests/test_a.py::test_a"\nexit 1\n'


def test_reproduced_failure_blocks_with_reason_on_stderr(flavor: str, repo: Path) -> None:
    fake = repo / ".venv" / "bin" / "python"
    fake.parent.mkdir(parents=True)
    fake.write_text(FAILING_PYTHON)
    fake.chmod(0o755)
    (repo / "pkg" / "a.py").write_text("x = 5\n")
    result = run_hook(HOOK_DIRS[flavor] / HOOK, {"cwd": str(repo)}, env=NO_VENV_PATH, cwd=repo)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "failure reproduced on re-run — blocking Stop" in result.stderr
    assert "FAILED tests/test_a.py::test_a" in result.stderr


def test_no_python_change_is_silent(flavor: str, repo: Path) -> None:
    result = run_hook(HOOK_DIRS[flavor] / HOOK, {"cwd": str(repo)}, env=NO_VENV_PATH, cwd=repo)
    assert result.returncode == 0
    assert result.stdout == ""


def test_checkout_venv_is_used_when_present(flavor: str, repo: Path) -> None:
    fake = repo / ".venv" / "bin" / "python"
    fake.parent.mkdir(parents=True)
    fake.write_text(FAKE_TOOL)
    fake.chmod(0o755)
    (repo / "pkg" / "a.py").write_text("x = 4\n")
    result = run_hook(HOOK_DIRS[flavor] / HOOK, {"cwd": str(repo)}, env=NO_VENV_PATH, cwd=repo)
    assert result.returncode == 0, result.stdout
    invoked = (repo / ".venv" / "bin" / "python.log").read_text().split()
    assert invoked[:3] == ["-m", "pytest", "tests/"] and "-x" in invoked


def test_gate_keeps_scope_and_fail_fast() -> None:
    for flavor in HOOK_DIRS:
        text = (HOOK_DIRS[flavor] / HOOK).read_text()
        assert "pytest tests/ -x -q" in text, flavor
        assert (
            '[ -x "$PY" ] || exit 0' not in text
        ), f"{flavor}: silent fail-open on missing interpreter"
        assert "/Users/theceo/DevSkyy/.venv" not in text, f"{flavor}: hardcoded primary checkout"
