"""The write-time formatters resolve the checkout from the edited file, so they
work in every worktree of this repo (and only this repo):

* python-format-on-write.sh — isort/ruff/black on one .py
* phpcs-on-write.sh        — the edited THEME's own ruleset (PHPCS lookup order), never a sibling's
* inline tsc hook          — .claude/settings.json / .codex/hooks.json PostToolUse

Each test copies the hook into a throwaway repo (so "the hook's own repo" is
that repo) and edits files in it, in a linked worktree of it, or in a foreign
repo — asserting on what changed on disk / what the tool was invoked with.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.hooks.conftest import (
    BASH,
    FAKE_TOOL,
    HOOK_DIRS,
    HOOKS_TREE,
    REPO_ROOT,
    add_worktree,
    init_repo,
    install_hook,
    run_hook,
)

PY_HOOK = "python-format-on-write.sh"
PHP_HOOK = "phpcs-on-write.sh"
FORMATTER_PATH = {"PATH": f"{Path(sys.executable).parent}:{os.environ.get('PATH', '')}"}
PYPROJECT = '[tool.black]\nline-length = 100\n[tool.ruff]\nline-length = 100\n[tool.isort]\nprofile = "black"\n'


def _edit(path: Path) -> dict:
    return {"tool_name": "Write", "tool_input": {"file_path": str(path), "content": ""}}


# ── python-format-on-write.sh ───────────────────────────────────────────────


@pytest.fixture
def py_repo(tmp_path: Path) -> Path:
    return init_repo(tmp_path / "repo", {"pyproject.toml": PYPROJECT, "pkg/a.py": "x = 1\n"})


def test_py_in_worktree_is_formatted(flavor: str, py_repo: Path, tmp_path: Path) -> None:
    hook = install_hook(py_repo, PY_HOOK, flavor)
    wt = add_worktree(py_repo, tmp_path / "wt")
    target = wt / "pkg" / "a.py"
    target.write_text("x=1\n")
    result = run_hook(hook, _edit(target), env=FORMATTER_PATH, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert target.read_text() == "x = 1\n"


def test_py_in_main_checkout_is_formatted(flavor: str, py_repo: Path) -> None:
    hook = install_hook(py_repo, PY_HOOK, flavor)
    target = py_repo / "pkg" / "a.py"
    target.write_text("x=1\n")
    result = run_hook(hook, _edit(target), env=FORMATTER_PATH, cwd=py_repo)
    assert result.returncode == 0, result.stderr
    assert target.read_text() == "x = 1\n"


def test_py_in_foreign_repo_is_left_alone(flavor: str, py_repo: Path, tmp_path: Path) -> None:
    hook = install_hook(py_repo, PY_HOOK, flavor)
    other = init_repo(tmp_path / "other", {"pyproject.toml": PYPROJECT, "b.py": "y=1\n"})
    target = other / "b.py"
    result = run_hook(hook, _edit(target), env=FORMATTER_PATH, cwd=other)
    assert result.returncode == 0
    assert target.read_text() == "y=1\n"


def test_py_hook_no_longer_skips_worktrees() -> None:
    for flavor in HOOK_DIRS:
        assert (
            ".claude/worktrees/*) exit 0" not in (HOOK_DIRS[flavor] / PY_HOOK).read_text()
        ), flavor


# ── phpcs-on-write.sh ───────────────────────────────────────────────────────

THEMES = "wordpress-theme"
V1 = f"{THEMES}/skyyrose-flagship"
V2 = f"{THEMES}/skyyrose-flagship-2"
PHP_FILES = {
    f"{V1}/.phpcs.xml": '<ruleset name="v1"/>\n',
    f"{V1}/vendor/bin/phpcs": FAKE_TOOL,
    f"{V1}/inc/a.php": "<?php\n",
    f"{V2}/inc/b.php": "<?php\n",
}


@pytest.fixture
def php_repo(tmp_path: Path) -> Path:
    return init_repo(
        tmp_path / "repo", PHP_FILES, executables=frozenset({f"{V1}/vendor/bin/phpcs"})
    )


def test_theme_without_ruleset_gets_notice_not_sibling_standard(
    flavor: str, php_repo: Path
) -> None:
    hook = install_hook(php_repo, PHP_HOOK, flavor)
    result = run_hook(hook, _edit(php_repo / V2 / "inc" / "b.php"), cwd=php_repo)
    assert result.returncode == 0
    assert "skyyrose-flagship-2 has no ruleset" in result.stderr
    assert not (
        php_repo / V1 / "vendor" / "bin" / "phpcs.log"
    ).exists()  # v1 standard never applied


def test_flagship_2_selects_its_own_phpcs_xml(flavor: str, php_repo: Path) -> None:
    """flagship-2 ships a tracked `phpcs.xml` (no dot-file); it must be picked."""
    hook = install_hook(php_repo, PHP_HOOK, flavor)
    (php_repo / V2 / "phpcs.xml").write_text('<ruleset name="v2"/>\n')
    result = run_hook(hook, _edit(php_repo / V2 / "inc" / "b.php"), cwd=php_repo)
    assert result.returncode == 0, result.stderr
    argv = (php_repo / V1 / "vendor" / "bin" / "phpcs.log").read_text().split("\n")
    assert f"--standard={php_repo / V2 / 'phpcs.xml'}" in argv
    assert f"--standard={php_repo / V1 / '.phpcs.xml'}" not in argv


@pytest.mark.parametrize(
    ("present", "expected"),
    [
        pytest.param([".phpcs.xml", "phpcs.xml"], ".phpcs.xml", id="dot-file-wins"),
        pytest.param(["phpcs.xml", ".phpcs.xml.dist"], "phpcs.xml", id="phpcs-xml-before-dist"),
        pytest.param([".phpcs.xml.dist", "phpcs.xml.dist"], ".phpcs.xml.dist", id="dot-dist"),
        pytest.param(["phpcs.xml.dist"], "phpcs.xml.dist", id="dist-only"),
    ],
)
def test_ruleset_lookup_follows_phpcs_order(
    flavor: str, php_repo: Path, present: list[str], expected: str
) -> None:
    hook = install_hook(php_repo, PHP_HOOK, flavor)
    for name in present:
        (php_repo / V2 / name).write_text(f'<ruleset name="{name}"/>\n')
    result = run_hook(hook, _edit(php_repo / V2 / "inc" / "b.php"), cwd=php_repo)
    assert result.returncode == 0, result.stderr
    argv = (php_repo / V1 / "vendor" / "bin" / "phpcs.log").read_text().split("\n")
    assert f"--standard={php_repo / V2 / expected}" in argv


def test_real_flagship_2_ruleset_is_phpcs_xml() -> None:
    """This checkout: flagship-2 has phpcs.xml and no .phpcs.xml (lead directive)."""
    theme = REPO_ROOT / V2
    assert (theme / "phpcs.xml").is_file()
    assert not (theme / ".phpcs.xml").exists()


def test_flagship_in_worktree_uses_worktree_standard(
    flavor: str, php_repo: Path, tmp_path: Path
) -> None:
    hook = install_hook(php_repo, PHP_HOOK, flavor)
    wt = add_worktree(php_repo, tmp_path / "wt")
    result = run_hook(hook, _edit(wt / V1 / "inc" / "a.php"), cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    argv = (wt / V1 / "vendor" / "bin" / "phpcs.log").read_text().split("\n")
    assert f"--standard={wt / V1 / '.phpcs.xml'}" in argv


def test_php_in_foreign_repo_is_skipped(flavor: str, php_repo: Path, tmp_path: Path) -> None:
    hook = install_hook(php_repo, PHP_HOOK, flavor)
    other = init_repo(
        tmp_path / "other", PHP_FILES, executables=frozenset({f"{V1}/vendor/bin/phpcs"})
    )
    result = run_hook(hook, _edit(other / V1 / "inc" / "a.php"), cwd=other)
    assert result.returncode == 0
    assert result.stderr == ""
    assert not (other / V1 / "vendor" / "bin" / "phpcs.log").exists()


@pytest.mark.timeout(90)
def test_real_flagship_file_runs_real_phpcs() -> None:
    """End-to-end on this checkout: the V1 ruleset and vendor phpcs resolve."""
    theme = REPO_ROOT / V1
    phpcs = theme / "vendor" / "bin" / "phpcs"
    if not phpcs.exists():
        pytest.skip("vendor/bin/phpcs not installed in this checkout")
    target = min((theme / "inc").glob("*.php"), key=lambda p: p.stat().st_size)
    result = run_hook(HOOK_DIRS["claude"] / PHP_HOOK, _edit(target), cwd=REPO_ROOT)
    assert result.returncode in (0, 2), result.stderr
    if result.returncode == 2:
        assert f"skyyrose-flagship standard: {theme / '.phpcs.xml'}" in result.stderr


# ── inline tsc hook ─────────────────────────────────────────────────────────


def _tsc_command(settings_file: Path) -> str:
    hooks = json.loads(settings_file.read_text())["hooks"]["PostToolUse"]
    commands = [
        h["command"] for entry in hooks for h in entry["hooks"] if "tsc-on-write" in h["command"]
    ]
    assert len(commands) == 1, f"expected exactly one tsc-on-write hook in {settings_file}"
    return commands[0]


TSC_SETTINGS = {
    "claude": HOOKS_TREE / ".claude" / "settings.json",
    "codex": HOOKS_TREE / ".codex" / "hooks.json",
}


def _run_tsc_hook(
    flavor: str, payload: dict, project_dir: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [BASH, "-c", _tsc_command(TSC_SETTINGS[flavor])],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)},
        cwd=str(project_dir),
        timeout=60,
    )


@pytest.fixture
def ts_repo(tmp_path: Path) -> Path:
    return init_repo(
        tmp_path / "repo",
        {"frontend/package.json": "{}\n", "frontend/a.ts": "export const a = 1;\n"},
    )


def test_tsc_hook_resolves_worktree_frontend(flavor: str, ts_repo: Path, tmp_path: Path) -> None:
    wt = add_worktree(ts_repo, tmp_path / "wt")
    result = _run_tsc_hook(flavor, _edit(wt / "frontend" / "a.ts"), ts_repo)
    assert result.returncode == 0, result.stderr
    assert f"[tsc-on-write] {wt / 'frontend' / 'node_modules'} missing" in result.stdout


def test_tsc_hook_ignores_non_frontend_files(flavor: str, ts_repo: Path) -> None:
    result = _run_tsc_hook(flavor, _edit(ts_repo / "a.py"), ts_repo)
    assert result.returncode == 0
    assert result.stdout == ""


def test_tsc_hook_skips_foreign_repo(flavor: str, ts_repo: Path, tmp_path: Path) -> None:
    other = init_repo(
        tmp_path / "other", {"frontend/package.json": "{}\n", "frontend/a.ts": "export {};\n"}
    )
    result = _run_tsc_hook(flavor, _edit(other / "frontend" / "a.ts"), ts_repo)
    assert result.returncode == 0
    assert result.stdout == ""


def test_codex_mirrors_are_identical() -> None:
    for name in (PY_HOOK, PHP_HOOK):
        assert (HOOK_DIRS["claude"] / name).read_bytes() == (
            HOOK_DIRS["codex"] / name
        ).read_bytes(), name
