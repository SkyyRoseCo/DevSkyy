"""Tests for scripts/deploy-theme.sh -- subprocess-based verification.

Tests invoke the deploy script via subprocess and assert on exit codes,
stdout/stderr content, and script source patterns. Uses temporary directories
with fake .env.wordpress for controlled testing.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.scripts.deploy_shims import blocked_calls, install_shims, style_css

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "deploy-theme.sh"

# The fake target: a staging-shaped host (so DEPLOY_TARGET=staging agrees) and
# the V1 folder name. The curl shim answers its live style.css with the same
# identity the fake theme carries, so check_theme_identity passes by default.
# SSH_USER is the host's own WP.com account ("<first label>.wordpress.com") so
# the SSH-destination gate agrees too.
FAKE_PUBLIC_URL = "https://fake-staging.wpcomstaging.com/"
FAKE_SSH_USER = "fake-staging.wordpress.com"
FAKE_THEME_NAME = "Test"
FAKE_TEXT_DOMAIN = "skyyrose-test"
FAKE_LIVE_STYLE_PATH = "/wp-content/themes/skyyrose-flagship/style.css"


@pytest.fixture
def fake_env(tmp_path):
    """Create a fake .env.wordpress and theme directory for testing."""
    env_file = tmp_path / ".env.wordpress"
    env_file.write_text(
        "SSH_HOST=ssh.wp.com\n"
        "SSH_PORT=22\n"
        f"SSH_USER={FAKE_SSH_USER}\n"
        "SSH_PASS=fake-password\n"
        "WP_THEME_PATH=/htdocs/wp-content/themes/skyyrose-flagship\n"
        "SFTP_HOST=sftp.wp.com\n"
        "SFTP_PORT=22\n"
        f"SFTP_USER={FAKE_SSH_USER}\n"
        "SFTP_PASS=fake-password\n"
        f"PUBLIC_URL={FAKE_PUBLIC_URL}\n"
    )
    theme_dir = tmp_path / "wordpress-theme" / "skyyrose-flagship"
    _make_deployable_theme(theme_dir, version="1.0.0")
    return tmp_path, env_file, theme_dir


def _make_deployable_theme(theme_dir: Path, *, version: str = "1.0.0") -> None:
    """Write a minimal but *gate-passing* theme.

    preflight_completeness() requires a synced version triple + the
    critical-asset floor (>=3 emblem webp, >=10 woff2, skyy.glb). Transport/
    ordering/cache tests need a theme that clears the gate, not an exhaustive
    one — so this is the smallest tree that deploys. Kept in one helper so the
    floor's magic numbers live in a single place if they ever change.
    """
    theme_dir.mkdir(parents=True, exist_ok=True)
    (theme_dir / "style.css").write_text(
        f"/*\nTheme Name: {FAKE_THEME_NAME}\nVersion:             {version}\n"
        f"Text Domain:         {FAKE_TEXT_DOMAIN}\n*/\n"
    )
    (theme_dir / "functions.php").write_text(f"<?php\ndefine( 'SKYYROSE_VERSION', '{version}' );\n")
    (theme_dir / "readme.txt").write_text(f"Stable tag: {version}\n")
    emblems = theme_dir / "assets" / "images" / "emblems"
    emblems.mkdir(parents=True, exist_ok=True)
    for name in ("black-rose", "love-hurts", "signature"):
        (emblems / f"{name}-emblem.webp").write_bytes(b"")
    fonts = theme_dir / "assets" / "fonts"
    fonts.mkdir(parents=True, exist_ok=True)
    for i in range(10):
        (fonts / f"font-{i}-latin.woff2").write_bytes(b"")
    models = theme_dir / "assets" / "models"
    models.mkdir(parents=True, exist_ok=True)
    (models / "skyy.glb").write_bytes(b"")


INHERITED_KEYS = (
    "DEPLOY_TARGET",
    "ENV_FILE",
    "THEME_DIR_OVERRIDE",
    "PUBLIC_URL",
    "WORDPRESS_URL",
    "ALLOW_THEME_IDENTITY_CHANGE",
    "ALLOW_NEW_THEME_FOLDER",
    "PREFLIGHT_SKIP_COMPLETENESS",
    "STRUCTURE_CHECK_STRICT",
)


def run_script(*args, tmp_path: Path, env_overrides=None, deploy_target="staging"):
    """Run deploy-theme.sh with given arguments.

    Every run gets the PATH shims from tests/scripts/deploy_shims.py: curl is
    route-driven (the fake theme's live style.css answers with a matching
    identity) and ssh/scp/sftp/sshpass/lftp/rsync fail loudly and are logged.
    DEPLOY_TARGET defaults to staging because the engine refuses without one;
    pass deploy_target=None to test that refusal. Every per-test path (lock,
    log, shims) lives under tmp_path -- never a shared /tmp path (bug-231).
    """
    env = os.environ.copy()
    for key in INHERITED_KEYS:
        env.pop(key, None)
    # Isolate from real deploys: the script's concurrency lock and log default
    # to shared /tmp paths, so an in-flight production deploy would otherwise
    # fail these tests ("Another deploy is already running").
    env["DEPLOY_LOCK_FILE"] = str(tmp_path / "skyyrose-deploy-test.lock")
    env["DEPLOY_LOG_FILE"] = str(tmp_path / "skyyrose-deploy-test.log")
    env.update(
        install_shims(
            tmp_path,
            [(FAKE_LIVE_STYLE_PATH, "200", style_css(FAKE_THEME_NAME, FAKE_TEXT_DOMAIN), "")],
        )
    )
    if deploy_target is not None:
        env["DEPLOY_TARGET"] = deploy_target
    if env_overrides:
        env.update(env_overrides)
    result = subprocess.run(
        ["bash", str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    assert "SHIM-BLOCKED" not in result.stderr, f"network tool invoked:\n{result.stderr}"
    assert blocked_calls(env) == [], f"network tool invoked (stderr hidden):\n{blocked_calls(env)}"
    return result


class TestDryRun:
    """Test 1: --dry-run exits 0 and prints DRY RUN messages."""

    def test_dry_run_exits_zero(self, fake_env):
        tmp_path, env_file, theme_dir = fake_env
        result = run_script(
            "--dry-run",
            env_overrides={
                "ENV_FILE": str(env_file),
                "THEME_DIR_OVERRIDE": str(theme_dir),
            },
            tmp_path=tmp_path,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}\nstdout: {result.stdout}"

    def test_dry_run_prints_dry_run_label(self, fake_env):
        tmp_path, env_file, theme_dir = fake_env
        result = run_script(
            "--dry-run",
            env_overrides={
                "ENV_FILE": str(env_file),
                "THEME_DIR_OVERRIDE": str(theme_dir),
            },
            tmp_path=tmp_path,
        )
        assert "[DRY RUN]" in result.stdout

    def test_dry_run_mentions_maintenance_mode(self, fake_env):
        tmp_path, env_file, theme_dir = fake_env
        result = run_script(
            "--dry-run",
            env_overrides={
                "ENV_FILE": str(env_file),
                "THEME_DIR_OVERRIDE": str(theme_dir),
            },
            tmp_path=tmp_path,
        )
        assert "maintenance" in result.stdout.lower()

    def test_dry_run_mentions_file_transfer(self, fake_env):
        tmp_path, env_file, theme_dir = fake_env
        result = run_script(
            "--dry-run",
            env_overrides={
                "ENV_FILE": str(env_file),
                "THEME_DIR_OVERRIDE": str(theme_dir),
            },
            tmp_path=tmp_path,
        )
        output = result.stdout.lower()
        assert "transfer" in output or "rsync" in output or "lftp" in output

    def test_dry_run_mentions_cache_flush(self, fake_env):
        tmp_path, env_file, theme_dir = fake_env
        result = run_script(
            "--dry-run",
            env_overrides={
                "ENV_FILE": str(env_file),
                "THEME_DIR_OVERRIDE": str(theme_dir),
            },
            tmp_path=tmp_path,
        )
        assert "cache flush" in result.stdout.lower()


class TestHelp:
    """Test 2: --help exits 0 and prints usage."""

    def test_help_exits_zero(self, tmp_path):
        result = run_script("--help", tmp_path=tmp_path)
        assert result.returncode == 0

    def test_help_prints_usage(self, tmp_path):
        result = run_script("--help", tmp_path=tmp_path)
        output = result.stdout.lower()
        assert "usage" in output or "deploy" in output


class TestMissingEnv:
    """Test 3: Missing .env.wordpress causes non-zero exit."""

    def test_missing_env_exits_nonzero(self, tmp_path):
        result = run_script(
            env_overrides={"ENV_FILE": str(tmp_path / "nonexistent.env")},
            tmp_path=tmp_path,
        )
        assert result.returncode != 0

    def test_missing_env_prints_error(self, tmp_path):
        result = run_script(
            env_overrides={"ENV_FILE": str(tmp_path / "nonexistent.env")},
            tmp_path=tmp_path,
        )
        output = (result.stdout + result.stderr).lower()
        assert "credential file not found" in output


class TestTrapCleanup:
    """Test 4: Script contains trap cleanup EXIT and cleanup checks MAINTENANCE_ACTIVE."""

    def test_trap_cleanup_exit_registered(self):
        source = SCRIPT_PATH.read_text()
        assert "trap cleanup EXIT" in source or "trap cleanup EXIT INT TERM" in source

    def test_cleanup_checks_maintenance_active(self):
        source = SCRIPT_PATH.read_text()
        assert "MAINTENANCE_ACTIVE" in source
        # cleanup function should check the flag
        cleanup_match = re.search(
            r"cleanup\s*\(\)\s*\{[^}]+MAINTENANCE_ACTIVE[^}]+\}", source, re.DOTALL
        )
        assert cleanup_match is not None, "cleanup() must check MAINTENANCE_ACTIVE"

    def test_trap_before_maintenance_activation(self):
        """Trap must be registered BEFORE any maintenance mode activation."""
        source = SCRIPT_PATH.read_text()
        trap_pos = source.find("trap cleanup")
        activate_pos = source.find("maintenance-mode activate")
        assert trap_pos < activate_pos, "trap must be registered before maintenance-mode activate"


class TestCommandOrdering:
    """Test 5: In dry-run output, activate before transfer, deactivate after."""

    def test_maintenance_activates_before_file_transfer(self, fake_env):
        """Maintenance mode must activate before files are transferred (--with-maintenance path)."""
        tmp_path, env_file, theme_dir = fake_env
        result = run_script(
            "--dry-run",
            "--with-maintenance",
            env_overrides={
                "ENV_FILE": str(env_file),
                "THEME_DIR_OVERRIDE": str(theme_dir),
            },
            tmp_path=tmp_path,
        )
        output = result.stdout.lower()
        activate_pos = output.find("maintenance-mode activate")
        # Look for transfer indicators
        transfer_pos = min(
            (
                p
                for p in (
                    output.find("rsync"),
                    output.find("transfer"),
                    output.find("lftp"),
                    output.find("sftp"),
                    output.find("upload"),
                )
                if p != -1
            ),
            default=-1,
        )
        assert activate_pos != -1, "activate not found in output"
        assert transfer_pos != -1, "transfer not found in output"
        # Deploy script activates maintenance BEFORE transferring files
        assert (
            activate_pos < transfer_pos
        ), "maintenance-mode activate must appear before file transfer"

    def test_deactivate_after_transfer(self, fake_env):
        tmp_path, env_file, theme_dir = fake_env
        result = run_script(
            "--dry-run",
            "--with-maintenance",
            env_overrides={
                "ENV_FILE": str(env_file),
                "THEME_DIR_OVERRIDE": str(theme_dir),
            },
            tmp_path=tmp_path,
        )
        output = result.stdout.lower()
        transfer_pos = min(
            (
                p
                for p in (
                    output.find("rsync"),
                    output.find("transfer"),
                    output.find("lftp"),
                    output.find("sftp"),
                    output.find("upload"),
                )
                if p != -1
            ),
            default=-1,
        )
        deactivate_pos = output.find("maintenance-mode deactivate")
        assert transfer_pos != -1, "transfer not found"
        assert deactivate_pos != -1, "deactivate not found"
        assert transfer_pos < deactivate_pos


class TestCacheFlush:
    """Test 6: Cache flush commands appear after file transfer."""

    def test_cache_flush_in_output(self, fake_env):
        tmp_path, env_file, theme_dir = fake_env
        result = run_script(
            "--dry-run",
            env_overrides={
                "ENV_FILE": str(env_file),
                "THEME_DIR_OVERRIDE": str(theme_dir),
            },
            tmp_path=tmp_path,
        )
        output = result.stdout.lower()
        assert "cache flush" in output

    def test_transient_delete_in_output(self, fake_env):
        tmp_path, env_file, theme_dir = fake_env
        result = run_script(
            "--dry-run",
            env_overrides={
                "ENV_FILE": str(env_file),
                "THEME_DIR_OVERRIDE": str(theme_dir),
            },
            tmp_path=tmp_path,
        )
        output = result.stdout.lower()
        assert "transient delete" in output

    def test_rewrite_flush_in_output(self, fake_env):
        tmp_path, env_file, theme_dir = fake_env
        result = run_script(
            "--dry-run",
            env_overrides={
                "ENV_FILE": str(env_file),
                "THEME_DIR_OVERRIDE": str(theme_dir),
            },
            tmp_path=tmp_path,
        )
        output = result.stdout.lower()
        assert "rewrite flush" in output

    def test_cache_flush_after_transfer(self, fake_env):
        tmp_path, env_file, theme_dir = fake_env
        result = run_script(
            "--dry-run",
            env_overrides={
                "ENV_FILE": str(env_file),
                "THEME_DIR_OVERRIDE": str(theme_dir),
            },
            tmp_path=tmp_path,
        )
        output = result.stdout.lower()
        transfer_pos = min(
            (
                p
                for p in (
                    output.find("rsync"),
                    output.find("transfer"),
                    output.find("lftp"),
                    output.find("sftp"),
                    output.find("upload"),
                )
                if p != -1
            ),
            default=-1,
        )
        cache_pos = output.find("cache flush")
        assert transfer_pos < cache_pos


def _defs_only_script() -> str:
    """scripts/deploy-theme.sh with the trailing `main "$@"` call stripped, so
    sourcing it only defines functions/arrays and never executes a deploy."""
    lines = SCRIPT_PATH.read_text().splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    assert lines[-1].strip() == 'main "$@"', f"expected trailing main call, got: {lines[-1]!r}"
    return "\n".join(lines[:-1]) + "\n"


def _rendered_excludes() -> tuple[list[str], list[str]]:
    """The actual RSYNC_EXCLUDES / tar_excludes arrays as built at runtime --
    not a static grep of the source text, which breaks the moment the exclude
    lists move from literal arrays to any data-driven construction (as they
    did in the 2026-08-02 dedup refactor; see SKYY_EXCLUDE_COMMON_* +
    skyyrose_render_rsync_excludes/skyyrose_render_tar_excludes)."""
    script = (
        _defs_only_script()
        + '\nprintf "RSYNC:%s\\n" "${RSYNC_EXCLUDES[@]}"\n'
        + 'skyyrose_render_tar_excludes | sed "s/^/TAR:/"\n'
    )
    result = subprocess.run(
        ["bash", "-c", script], capture_output=True, text=True, timeout=15, check=True
    )
    lines = result.stdout.splitlines()
    rsync_excludes = [line[len("RSYNC:") :] for line in lines if line.startswith("RSYNC:")]
    tar_excludes = [line[len("TAR:") :] for line in lines if line.startswith("TAR:")]
    return rsync_excludes, tar_excludes


class TestExcludes:
    """Test 7: Rsync exclude list covers critical patterns."""

    def test_excludes_node_modules(self):
        source = SCRIPT_PATH.read_text()
        assert "node_modules" in source

    def test_excludes_git(self):
        rsync_excludes, tar_excludes = _rendered_excludes()
        assert "--exclude=.git" in rsync_excludes
        assert "--exclude=.git" in tar_excludes

    def test_excludes_env_files(self):
        source = SCRIPT_PATH.read_text()
        assert ".env" in source

    def test_excludes_map_files(self):
        source = SCRIPT_PATH.read_text()
        assert "*.map" in source

    def test_excludes_tests(self):
        rsync_excludes, tar_excludes = _rendered_excludes()
        assert "--exclude=tests/" in rsync_excludes
        assert "--exclude=tests" in tar_excludes

    def test_excludes_package_json(self):
        source = SCRIPT_PATH.read_text()
        assert "package.json" in source

    def test_excludes_package_lock(self):
        source = SCRIPT_PATH.read_text()
        assert "package-lock.json" in source


class TestShellcheck:
    """Test 8: shellcheck passes on the deploy script."""

    @pytest.mark.skipif(
        not shutil.which("shellcheck"),
        reason="shellcheck binary not installed",
    )
    def test_shellcheck_passes(self):
        result = subprocess.run(
            ["shellcheck", str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"shellcheck errors:\n{result.stdout}"


class TestCompletenessGate:
    """Test 9: preflight_completeness() fails CLOSED on an incomplete source
    tree (bug-252 gate) and never crashes with a raw awk/sed error (bug-253)."""

    def test_missing_version_file_fails_closed_cleanly(self, fake_env):
        """A missing readme.txt must exit non-zero with the gate's own clear
        message -- not a raw 'awk: can't open file' crash (regression bug-253)."""
        tmp_path, env_file, theme_dir = fake_env
        (theme_dir / "readme.txt").unlink()
        result = run_script(
            "--dry-run",
            env_overrides={"ENV_FILE": str(env_file), "THEME_DIR_OVERRIDE": str(theme_dir)},
            tmp_path=tmp_path,
        )
        assert result.returncode != 0
        combined = result.stdout + result.stderr
        assert "Version file missing" in combined, f"expected clean gate message, got: {combined}"
        assert (
            "can't open file" not in combined
        ), "raw awk crash leaked -- gate did not fail closed gracefully"

    def test_version_drift_fails_closed(self, fake_env):
        """A synced-but-mismatched version triple must block the deploy."""
        tmp_path, env_file, theme_dir = fake_env
        (theme_dir / "readme.txt").write_text("Stable tag: 9.9.9\n")
        result = run_script(
            "--dry-run",
            env_overrides={"ENV_FILE": str(env_file), "THEME_DIR_OVERRIDE": str(theme_dir)},
            tmp_path=tmp_path,
        )
        assert result.returncode != 0
        assert "DRIFT" in (result.stdout + result.stderr)

    def test_asset_floor_fails_closed(self, fake_env):
        """Dropping below the critical-asset floor (emblems) must block."""
        tmp_path, env_file, theme_dir = fake_env
        for webp in (theme_dir / "assets" / "images" / "emblems").glob("*.webp"):
            webp.unlink()
        result = run_script(
            "--dry-run",
            env_overrides={"ENV_FILE": str(env_file), "THEME_DIR_OVERRIDE": str(theme_dir)},
            tmp_path=tmp_path,
        )
        assert result.returncode != 0
        assert "Critical-asset floor" in (result.stdout + result.stderr)

    def test_skip_env_bypasses_gate(self, fake_env):
        """PREFLIGHT_SKIP_COMPLETENESS=1 must let an incomplete tree through
        the gate (emergency override) -- dry-run then reaches exit 0."""
        tmp_path, env_file, theme_dir = fake_env
        (theme_dir / "readme.txt").unlink()  # deliberately incomplete
        result = run_script(
            "--dry-run",
            env_overrides={
                "ENV_FILE": str(env_file),
                "THEME_DIR_OVERRIDE": str(theme_dir),
                "PREFLIGHT_SKIP_COMPLETENESS": "1",
            },
            tmp_path=tmp_path,
        )
        assert result.returncode == 0, f"skip override should pass; stderr: {result.stderr}"
        assert "SKIPPED" in result.stdout

    def test_git_error_fails_closed(self, fake_env):
        """A corrupt git index must fail the gate CLOSED with a clear message,
        never silently pass as '0/0 on disk' (bug-260 fail-open). Engages the
        tracked-file check by making the theme dir a real work tree, then
        corrupts .git/index so `git ls-files` errors while
        `rev-parse --is-inside-work-tree` still succeeds."""
        tmp_path, env_file, theme_dir = fake_env
        subprocess.run(["git", "init", "-q", str(theme_dir)], check=True)
        # `git add` creates the index; corrupting it (vs deleting) forces
        # ls-files to error rather than return an empty list.
        subprocess.run(["git", "-C", str(theme_dir), "add", "-A"], check=True)
        (theme_dir / ".git" / "index").write_bytes(b"garbage-not-a-git-index")
        result = run_script(
            "--dry-run",
            env_overrides={"ENV_FILE": str(env_file), "THEME_DIR_OVERRIDE": str(theme_dir)},
            tmp_path=tmp_path,
        )
        assert result.returncode != 0
        combined = result.stdout + result.stderr
        assert (
            "cannot verify tracked-file completeness" in combined
        ), f"expected clean fail-closed message, got: {combined}"
        assert (
            "0/0 on disk" not in combined
        ), "gate reported false completeness on a broken index (fail-open regression)"
