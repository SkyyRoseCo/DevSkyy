"""Tests for scripts/env_import.sh — batch import of KEY=VALUE lines into an env file.

The script is driven as a real subprocess against a tmp_path target, so nothing
touches the repo's own .env.local. Secret-shaped values are asserted to stay out
of stdout and stderr.
"""

import stat
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "env_import.sh"
SECRET = "id-abc:secret-xyz"


def run(target, *args, stdin=None):
    return subprocess.run(
        ["bash", str(SCRIPT), "--target", str(target), "--force", *args],
        input=stdin,
        capture_output=True,
        text=True,
        timeout=30,
    )


def source_file(tmp_path, text):
    path = tmp_path / "incoming.env"
    path.write_text(text)
    return path


def test_script_is_executable_and_parses():
    assert SCRIPT.exists()
    assert subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True).returncode == 0


def test_mktemp_template_is_portable():
    """`mktemp -t NAME` works on BSD/macOS but GNU coreutils rejects it.

    The suite runs on macOS locally and Linux in CI, and the Linux failure mode is
    "mktemp: too few X's in template" on every write path, so pin the portable form.
    """
    text = SCRIPT.read_text()
    code = [line for line in text.splitlines() if not line.lstrip().startswith("#")]
    assert not [line for line in code if "mktemp -t " in line]
    assert text.count('mktemp "${TMPDIR:-/tmp}/env_import.XXXXXX"') == 2


def test_imports_multiple_keys_from_a_file(tmp_path):
    target = tmp_path / ".env.local"
    src = source_file(tmp_path, f"HF_KEY={SECRET}\nFAL_KEY=fal-1\nOTHER=3\n")

    result = run(target, "--file", str(src))

    assert result.returncode == 0, result.stderr
    assert target.read_text() == f"HF_KEY={SECRET}\nFAL_KEY=fal-1\nOTHER=3\n"
    assert "HF_KEY" in result.stdout
    assert "FAL_KEY" in result.stdout
    assert SECRET not in result.stdout + result.stderr


def test_reads_stdin_and_sets_owner_only_permissions(tmp_path):
    target = tmp_path / ".env.local"

    result = run(target, "--file", "-", stdin=f"HF_KEY={SECRET}\n")

    assert result.returncode == 0, result.stderr
    assert stat.S_IMODE(target.stat().st_mode) == 0o600
    assert SECRET not in result.stdout + result.stderr


def test_merges_into_existing_file_with_last_value_winning(tmp_path):
    target = tmp_path / ".env.local"
    target.write_text("HF_KEY=stale\nKEEP=kept\n")
    src = source_file(tmp_path, f"HF_KEY={SECRET}\nNEW=n\n")

    result = run(target, "--file", str(src))

    assert result.returncode == 0, result.stderr
    assert target.read_text() == f"HF_KEY={SECRET}\nKEEP=kept\nNEW=n\n"
    assert "new this run" in result.stdout
    assert "NEW" in result.stdout
    assert "KEEP" not in result.stdout.split("new this run")[1]


def test_drops_empty_values_and_counts_unparseable_lines(tmp_path):
    target = tmp_path / ".env.local"
    src = source_file(
        tmp_path,
        f"cd /Users/theceo/DevSkyy && pbpaste\nEMPTY=\nHF_KEY={SECRET}\n\n# comment\n",
    )

    result = run(target, "--file", str(src))

    assert result.returncode == 0, result.stderr
    assert target.read_text() == f"HF_KEY={SECRET}\n"
    assert "skipped 3 unparseable line(s)" in result.stdout


@pytest.mark.parametrize("text", ["", "\n\n", "cd /Users/theceo/DevSkyy && pbpaste\n", "EMPTY=\n"])
def test_refuses_to_write_when_source_has_no_key(tmp_path, text):
    target = tmp_path / ".env.local"
    target.write_text("HF_KEY=untouched\n")

    result = run(target, "--file", str(source_file(tmp_path, text)))

    assert result.returncode == 3
    assert target.read_text() == "HF_KEY=untouched\n"
    assert "nothing written" in result.stderr


def test_refuses_a_target_git_does_not_ignore(tmp_path):
    target = tmp_path / "tracked.env"
    src = source_file(tmp_path, f"HF_KEY={SECRET}\n")

    result = subprocess.run(
        ["bash", str(SCRIPT), "--target", str(target), "--file", str(src)],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 5
    assert not target.exists()
    assert "not ignored by git" in result.stderr


def test_unreadable_source_reports_and_writes_nothing(tmp_path):
    target = tmp_path / ".env.local"

    result = run(target, "--file", str(tmp_path / "absent.env"))

    assert result.returncode == 4
    assert not target.exists()
    assert "cannot read" in result.stderr


def test_clipboard_is_the_default_source(tmp_path, monkeypatch):
    target = tmp_path / ".env.local"
    fake_clipboard = tmp_path / "fakepaste"
    fake_clipboard.write_text(f"#!/bin/sh\nprintf 'HF_KEY={SECRET}\\n'\n")
    fake_clipboard.chmod(0o755)

    result = subprocess.run(
        ["bash", str(SCRIPT), "--target", str(target), "--force"],
        capture_output=True,
        text=True,
        timeout=30,
        env={"PATH": f"{tmp_path}:/usr/bin:/bin", "ENV_IMPORT_CLIPBOARD": "fakepaste"},
    )

    assert result.returncode == 0, result.stderr
    assert target.read_text() == f"HF_KEY={SECRET}\n"
    assert SECRET not in result.stdout + result.stderr


def test_missing_clipboard_command_fails_closed(tmp_path):
    target = tmp_path / ".env.local"

    result = subprocess.run(
        ["bash", str(SCRIPT), "--target", str(target), "--force"],
        capture_output=True,
        text=True,
        timeout=30,
        env={"PATH": "/usr/bin:/bin", "ENV_IMPORT_CLIPBOARD": "definitely-not-a-command"},
    )

    assert result.returncode == 4
    assert not target.exists()
    assert "not found" in result.stderr
