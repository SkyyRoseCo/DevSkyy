"""Offline public permission gates; isolated fixtures and blocked network tools."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "public_permissions", ROOT / "scripts/check-public-release-permissions.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


@pytest.fixture
def public_fixture(tmp_path):
    theme = tmp_path / "theme"
    (theme / "assets/derived/cards").mkdir(parents=True)
    public = theme / "assets/derived/cards/a.webp"
    public.write_bytes(b"exact fixture bytes")
    public.chmod(0o644)
    for directory in (theme, theme / "assets", theme / "assets/derived", public.parent):
        directory.chmod(0o755)
    private = theme / "assets/private.env"
    private.write_bytes(b"do not inspect")
    private.chmod(0o600)
    boundary = tmp_path / "boundary.json"
    boundary.write_text(
        json.dumps(
            {
                "files": {
                    "assets/derived/cards/a.webp": {"release": True},
                    "assets/private.env": {"release": False},
                    "data/private.json": {"release": False},
                }
            }
        )
    )
    return theme, public, private, boundary


def test_only_release_assets_are_inspected_and_no_bytes_or_modes_change(
    public_fixture, monkeypatch
):
    theme, public, private, boundary = public_fixture
    before = [(p.stat().st_mode, p.stat().st_mtime_ns, p.read_bytes()) for p in (public, private)]
    original = Path.read_bytes

    def reject_asset_reads(path):
        if path.is_relative_to(theme):
            pytest.fail("Permission gate read public/private asset content")
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", reject_asset_reads)
    assert MODULE.check_permissions(theme, boundary) == 1
    monkeypatch.undo()
    assert before == [
        (p.stat().st_mode, p.stat().st_mtime_ns, p.read_bytes()) for p in (public, private)
    ]


@pytest.mark.parametrize("mode", [0o600, 0o640, 0o666, 0o755])
def test_file_modes_fail_without_repair(public_fixture, mode):
    theme, public, _, boundary = public_fixture
    public.chmod(mode)
    with pytest.raises(ValueError, match="0644"):
        MODULE.check_permissions(theme, boundary)
    assert public.stat().st_mode & 0o777 == mode


@pytest.mark.parametrize("mode", [0o700, 0o750, 0o777])
def test_directory_modes_fail_without_repair(public_fixture, mode):
    theme, public, _, boundary = public_fixture
    public.parent.chmod(mode)
    with pytest.raises(ValueError, match="0755"):
        MODULE.check_permissions(theme, boundary)
    assert public.parent.stat().st_mode & 0o777 == mode


@pytest.mark.parametrize("mode", [0o700, 0o750, 0o777])
def test_theme_root_modes_fail_without_repair(public_fixture, mode):
    theme, _, _, boundary = public_fixture
    theme.chmod(mode)
    with pytest.raises(ValueError, match="Public theme directory requires 0755"):
        MODULE.check_permissions(theme, boundary)
    assert theme.stat().st_mode & 0o777 == mode


def test_restrictive_umask_requires_explicit_public_theme_root(tmp_path):
    old_mask = os.umask(0o077)
    try:
        theme = tmp_path / "theme"
        assets = theme / "assets"
        assets.mkdir(parents=True)
        public = assets / "a.webp"
        public.write_bytes(b"synthetic public delivery")
        public.chmod(0o644)
        assets.chmod(0o755)
        boundary = tmp_path / "boundary.json"
        boundary.write_text(json.dumps({"files": {"assets/a.webp": {"release": True}}}))
        assert theme.stat().st_mode & 0o777 == 0o700
        with pytest.raises(ValueError, match="Public theme directory requires 0755"):
            MODULE.check_permissions(theme, boundary)
        theme.chmod(0o755)
        assert MODULE.check_permissions(theme, boundary) == 1
    finally:
        os.umask(old_mask)


@pytest.mark.parametrize(
    "relative",
    [
        "assets/../secret.webp",
        "assets/.env",
        "assets/public.env",
        "assets/a\\b.webp",
        "assets/._a.webp",
    ],
)
def test_unsafe_release_paths_fail_closed(public_fixture, relative):
    theme, _, _, boundary = public_fixture
    boundary.write_text(json.dumps({"files": {relative: {"release": True}}}))
    with pytest.raises(ValueError):
        MODULE.check_permissions(theme, boundary)


def test_symlink_asset_and_parent_are_rejected(public_fixture, tmp_path):
    theme, public, _, boundary = public_fixture
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    replacement = elsewhere / "a.webp"
    public.rename(replacement)
    public.symlink_to(replacement)
    with pytest.raises(ValueError, match="Unsafe/missing public file"):
        MODULE.check_permissions(theme, boundary)
    public.unlink()
    public.parent.rmdir()
    public.parent.symlink_to(elsewhere, target_is_directory=True)
    with pytest.raises(ValueError, match="Unsafe/missing public directory"):
        MODULE.check_permissions(theme, boundary)


def test_empty_public_release_fails(public_fixture):
    theme, _, _, boundary = public_fixture
    boundary.write_text('{"files": {"assets/private.env": {"release": false}}}')
    with pytest.raises(ValueError, match="no releasable"):
        MODULE.check_permissions(theme, boundary)


@pytest.mark.parametrize("private_public", [False, True])
def test_actual_preflight_function_blocks_private_modes_before_network(
    public_fixture, tmp_path, private_public
):
    theme, public, _, boundary = public_fixture
    if private_public:
        public.chmod(0o600)
    project = tmp_path / "project"
    (project / "scripts").mkdir(parents=True)
    (project / "tools/v2-source-certification").mkdir(parents=True)
    shutil.copyfile(
        ROOT / "scripts/check-public-release-permissions.py",
        project / "scripts/check-public-release-permissions.py",
    )
    shutil.copyfile(boundary, project / "tools/v2-source-certification/package-boundary.json")
    script = (ROOT / "scripts/deploy-theme.sh").read_text()
    function = script.split("check_v2_public_asset_permissions() {", 1)[1].split("\n}\n", 1)[0]
    gate = "check_v2_public_asset_permissions() {" + function + "\n}\n"
    preflight = script.split("preflight() {", 1)[1].split("\n}\n", 1)[0]
    assert preflight.index("check_v2_public_asset_permissions") < preflight.index(
        "check_theme_identity"
    )
    deny = tmp_path / "deny"
    deny.mkdir()
    network_log = tmp_path / "network.log"
    for tool in ("ssh", "scp", "sftp", "curl", "wget"):
        wrapper = deny / tool
        wrapper.write_text('#!/bin/sh\nprintf "blocked\\n" >> "$NETWORK_LOG"\nexit 97\n')
        wrapper.chmod(0o755)
    env = {
        **os.environ,
        "PROJECT_ROOT": str(project),
        "THEME_DIR": str(theme),
        "PATH": f"{deny}:{os.environ['PATH']}",
        "NETWORK_LOG": str(network_log),
    }
    result = subprocess.run(
        [
            "/bin/bash",
            "-c",
            'skyyrose_is_v2_theme() { return 0; }\nlog_error() { echo "$*" >&2; }\nlog_success() { echo "$*"; }\n'
            + gate
            + "check_v2_public_asset_permissions\n",
        ],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == (1 if private_public else 0), result.stdout + result.stderr
    assert not network_log.exists()
