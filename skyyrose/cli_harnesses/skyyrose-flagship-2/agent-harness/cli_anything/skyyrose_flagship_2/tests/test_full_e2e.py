"""
End-to-end tests against the real flagship-2 theme and God Mode X's real checker.

Opt-in: set SKYYROSE2_E2E=1. One test briefly edits a tracked theme file in the
checkout under test, so these must never run by accident in a shared checkout;
use a dedicated worktree. Once opted in, nothing skips:

Hard requirements (tests FAIL, never skip, when missing):
  - the checkout that contains this harness, with theme node_modules installed
  - SKYYROSE2_NODE_BIN_DIR -> Node 22.23.2 + npm 10.9.8; python3 3.12.12; php
  - a God Mode X clone (GOD_MODE_X_ROOT or ~/god-mode-x)

Run the installed command with CLI_ANYTHING_FORCE_INSTALLED=1.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from cli_anything.skyyrose_flagship_2.utils.backend import THEME_REL, sha256_file

pytestmark = [
    pytest.mark.skipif(
        os.environ.get("SKYYROSE2_E2E", "").strip() != "1",
        reason="opt-in: SKYYROSE2_E2E=1 (edits a tracked file in the checkout under test)",
    ),
    pytest.mark.timeout(600),  # real npm gates; the repo-wide 10s default flakes under load
]

CLI_NAME = "cli-anything-skyyrose-flagship-2"
MODULE = "cli_anything.skyyrose_flagship_2.skyyrose_flagship_2_cli"
REPO = Path(__file__).resolve().parents[7]
FAST_GATES = ["check:registry", "check:i18n", "check:tokens", "check:source-integrity"]


def _resolve_cli(name: str) -> list[str]:
    """Installed command, or `python -m` for dev; CLI_ANYTHING_FORCE_INSTALLED=1 requires installed."""
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name) or shutil.which(name, path=str(Path(sys.executable).parent))
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {MODULE}")
    return [sys.executable, "-m", MODULE]


CLI = _resolve_cli(CLI_NAME)


@pytest.fixture(scope="session")
def wp_fixture(tmp_path_factory: pytest.TempPathFactory) -> str:
    """The pinned native WP/Woo fixture, built once per test session through the CLI."""
    if os.environ.get("V2_WP_FIXTURE"):
        return os.environ["V2_WP_FIXTURE"]
    home = tmp_path_factory.mktemp("fixture-home")
    env = {**os.environ, "SKYYROSE2_CLI_HOME": str(home), "SKYYROSE2_REPO_ROOT": str(REPO)}
    proc = subprocess.run(
        [*CLI, "--json", "fixture", "prepare"], capture_output=True, text=True, env=env, timeout=300
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return json.loads(proc.stdout)["path"]


@pytest.fixture()
def run(tmp_path: Path, wp_fixture: str):
    env = {
        **os.environ,
        "SKYYROSE2_CLI_HOME": str(tmp_path / "clihome"),
        "SKYYROSE2_REPO_ROOT": str(REPO),
        "V2_WP_FIXTURE": wp_fixture,
    }

    def _run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        proc = subprocess.run([*CLI, *args], capture_output=True, text=True, env=env, timeout=900)
        if check and proc.returncode != 0:
            raise AssertionError(
                f"{args} exited {proc.returncode}\nstdout:{proc.stdout}\nstderr:{proc.stderr}"
            )
        return proc

    return _run


def _tracked_state() -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), "status", "--porcelain", "--untracked-files=no"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def test_doctor_is_healthy(run) -> None:
    report = json.loads(run("--json", "doctor").stdout)
    assert report["ok"] is True, report
    assert report["toolchain"]["node"] == report["toolchain"]["pins"]["node"]
    assert report["god_mode_x_checker"]


def test_help_and_introspection(run) -> None:
    assert "evidence" in run("--help").stdout
    info = json.loads(run("--json", "info").stdout)
    assert info["candidate"]["artifact"].startswith(THEME_REL + "@tree:")
    ver = json.loads(run("--json", "version", "check").stdout)
    assert ver["consistent"] is True and ver["version"]
    pin = json.loads(run("--json", "pin", "status").stdout)
    assert pin["in_sync"] is True


def test_every_package_script_is_classified(run) -> None:
    listing = json.loads(run("--json", "scripts", "list").stdout)
    pkg = json.loads((REPO / THEME_REL / "package.json").read_text())["scripts"]
    assert {row["name"] for row in listing["scripts"]} == set(pkg)
    unclassified = [row["name"] for row in listing["scripts"] if row["kind"] == "unclassified"]
    assert unclassified == [], f"classify these in core/gates.py: {unclassified}"


def test_gates_to_god_mode_x_pass(run, tmp_path: Path) -> None:
    before = _tracked_state()
    result = json.loads(run("--json", "check", "run", *FAST_GATES).stdout)
    assert result["ok"] is True and [r["gate_id"] for r in result["runs"]] == FAST_GATES
    assert all(r["changed_paths"] == [] for r in result["runs"])
    out = tmp_path / "evidence"
    exported = run("--json", "evidence", "export", "-o", str(out), check=False)
    payload = json.loads(exported.stdout)
    record = json.loads((out / "task-evidence.json").read_text())
    for artifact in record["artifacts"]:
        assert sha256_file(out / artifact["path"]) == artifact["sha256"]
    print(f"\n  record: {out / 'task-evidence.json'}")
    if (
        before
    ):  # the checkout itself has tracked edits: evidence must say partial, and GMX must refuse
        assert record["claim"] == "partial" and payload["god_mode_x"]["gate"] == "FAIL"
    else:
        assert exported.returncode == 0, exported.stdout
        assert record["claim"] == "verified" and payload["god_mode_x"]["gate"] == "PASS"
        validated = json.loads(
            run("--json", "evidence", "validate", str(out / "task-evidence.json")).stdout
        )
        assert validated["gate"] == "PASS" and validated["exit_code"] == 0
        assert payload["fashion_theme_team"] == "BLOCKED"
    assert _tracked_state() == before


def test_ftt_review_requires_independent_reviewer(run, tmp_path: Path) -> None:
    run("check", "run", "check:tokens")
    owner = subprocess.run(
        ["git", "config", "user.name"], capture_output=True, text=True
    ).stdout.strip()
    refused = run(
        "--json",
        "evidence",
        "review",
        "--reviewer",
        owner or "unknown-owner",
        "--disposition",
        "PASS",
        "--note",
        "self",
        check=False,
    )
    assert refused.returncode != 0 and "independent" in refused.stdout
    run(
        "evidence",
        "review",
        "--reviewer",
        "theme-release-engineer",
        "--disposition",
        "PASS",
        "--note",
        "read the check:tokens log and record",
    )
    payload = json.loads(
        run("--json", "evidence", "export", "-o", str(tmp_path / "e"), check=False).stdout
    )
    expected = "BLOCKED" if _tracked_state() else "PASS"
    assert payload["fashion_theme_team"] == expected


def test_edit_makes_old_runs_stale_and_dirty_is_partial(run, tmp_path: Path) -> None:
    target = REPO / THEME_REL / "readme.txt"
    original = target.read_bytes()
    run("check", "run", "check:tokens")
    try:
        target.write_bytes(original + b"\n")
        stale = run("--json", "evidence", "export", "-o", str(tmp_path / "s"), check=False)
        assert stale.returncode != 0 and "No gate runs recorded" in stale.stdout
        run("check", "run", "check:tokens")
        dirty = run("--json", "evidence", "export", "-o", str(tmp_path / "d"), check=False)
        payload = json.loads(dirty.stdout)
        assert payload["claim"] == "partial"
        assert payload["god_mode_x"]["gate"] == "FAIL" and dirty.returncode == 3
    finally:
        target.write_bytes(original)


@pytest.mark.parametrize(
    "name", ["render:commerce-scenes", "certify:image-generation-preflight", "nope:script"]
)
def test_refusals_run_nothing(run, name: str) -> None:
    proc = run("--json", "check", "run", name, check=False)
    assert proc.returncode == 1 and "Refusing" in proc.stdout
    sessions = json.loads(run("--json", "session", "list").stdout)["sessions"]
    assert all(s.get("runs", 0) == 0 for s in sessions)


def test_build_plan_does_not_run(run) -> None:
    before = _tracked_state()
    plan = json.loads(run("--json", "build", "run", "build:registry", "--plan").stdout)
    assert plan["plan"] is True and plan["gate"]["kind"] == "build"
    assert _tracked_state() == before
