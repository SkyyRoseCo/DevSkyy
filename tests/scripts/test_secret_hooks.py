"""The gitleaks gate in .husky/pre-commit and .husky/pre-push fails closed.

Wraps scripts/test-secret-hooks.sh, which installs the real hooks,
scripts/secret-scan.sh and .gitleaks.toml into throwaway repos wired like
production (core.hooksPath -> .husky/_) and proves: a planted credential is
blocked at pre-commit (before lint-staged) and at pre-push (new branch and
existing range); clean commit/push pass; a missing gitleaks binary, a missing
config and a corrupt config all block; SECRETS_SCAN_SKIP=1 passes with a loud
warning; a deletion push passes; and no transcript ever contains the credential.

Skips (does not silently pass) when gitleaks is not installed: the Python CI
job has no gitleaks, so the gate's own behaviour is proven locally
(`brew install gitleaks`), while the Secrets Scan CI job pins the same version.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "test-secret-hooks.sh"


@pytest.mark.timeout(240)
def test_secret_hooks_end_to_end() -> None:
    if shutil.which("gitleaks") is None:
        pytest.skip("gitleaks not installed (brew install gitleaks)")
    assert SCRIPT.is_file(), SCRIPT
    result = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    transcript = result.stdout + result.stderr
    assert result.returncode == 0, transcript
    assert "0 failed" in transcript, transcript
    assert "FAIL" not in transcript, transcript


def test_pinned_gitleaks_version_matches_ci() -> None:
    """scripts/secret-scan.sh and security-gate.yml must pin the same version."""
    script = (REPO_ROOT / "scripts" / "secret-scan.sh").read_text(encoding="utf-8")
    workflow = (REPO_ROOT / ".github" / "workflows" / "security-gate.yml").read_text(
        encoding="utf-8"
    )
    pins = [
        line.split("=", 1)[1].strip().strip('"')
        for line in script.splitlines()
        if line.startswith("GITLEAKS_VERSION=")
    ]
    assert len(pins) == 1, pins
    assert f"gitleaks/releases/download/v{pins[0]}/gitleaks_{pins[0]}_linux_x64" in workflow


def test_gitleaks_config_extends_default_rules() -> None:
    """A config without [extend] useDefault carries zero rules and passes vacuously."""
    config = (REPO_ROOT / ".gitleaks.toml").read_text(encoding="utf-8")
    assert "[extend]" in config
    assert "useDefault = true" in config
