"""Shared fixtures for the two-target deploy tests (founder directive 2026-09-18).

Used by tests/scripts/test_deploy_targets.py (engine gates) and
tests/scripts/test_deploy_wrappers.py (staging/production wrappers). Nothing here
touches the network: curl is a route-driven PATH shim and every SSH-family tool on
PATH fails loudly (tests/scripts/deploy_shims.py); the real .env.wordpress* files
are never read.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from tests.scripts.deploy_shims import blocked_calls, install_shims, style_css

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = PROJECT_ROOT / "scripts"
ENGINE = SCRIPTS / "deploy-theme.sh"

STAGING_HOST = "staging-7e48-skyyrose.wpcomstaging.com"
V2_FOLDER = "skyyrose-flagship-2"
V1_FOLDER = "skyyrose-flagship"

# WP.com SSH accounts are "<first label of the public host>.wordpress.com"
# [repro 2026-09-19 against both real env files, values not printed].
PROD_SSH_USER = "skyyrose.wordpress.com"
STAGING_SSH_USER = "staging-7e48-skyyrose.wordpress.com"
REST_ROOT = ("/index.php", "200", '{"namespaces":["wp/v2"]}', "")

# Production's live style.css header as served on 2026-09-18 [live]: Flagship 2
# inside the V1-named folder. This is the state the identity gate exists for.
PROD_LIVE_STYLE = style_css("SkyyRose Flagship 2", V2_FOLDER, "2.3.1")

STUB_ENGINE = """#!/usr/bin/env bash
echo "STUB DEPLOY_TARGET=${DEPLOY_TARGET:-<unset>}"
echo "STUB ENV_FILE=${ENV_FILE:-<unset>}"
echo "STUB THEME_DIR_OVERRIDE=${THEME_DIR_OVERRIDE:-<unset>}"
echo "STUB ALLOW_NEW_THEME_FOLDER=${ALLOW_NEW_THEME_FOLDER:-<unset>}"
echo "STUB ALLOW_THEME_IDENTITY_CHANGE=${ALLOW_THEME_IDENTITY_CHANGE:-<unset>}"
echo "STUB ARGS=$*"
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _expected_ssh_user(url: str) -> str:
    """'<first label of the public host, leading www. removed>.wordpress.com'."""
    host = url.split("://", 1)[-1].split("/", 1)[0].split(":", 1)[0].lower()
    if host.startswith("www."):
        host = host[4:]
    return host.split(".", 1)[0] + ".wordpress.com"


def _env_text(
    *,
    public_url: str | None,
    theme_folder: str,
    wordpress_url: str | None = None,
    ssh_user: str | None = None,
    sftp_user: str | None = None,
) -> str:
    """A credentials file whose SSH_USER matches its public host by default
    (the real files do); pass ssh_user/sftp_user to model a mismatch."""
    site = public_url or wordpress_url or ""
    if ssh_user is None:
        ssh_user = _expected_ssh_user(site) if site else "unset.wordpress.com"
    if sftp_user is None:
        sftp_user = ssh_user
    lines = [
        "SSH_HOST=ssh.wp.com",
        "SSH_PORT=22",
        f"SSH_USER={ssh_user}",
        "SSH_PASS=fake-password",
        f"WP_THEME_PATH=/htdocs/wp-content/themes/{theme_folder}",
        "SFTP_HOST=ssh.wp.com",
        "SFTP_PORT=22",
        f"SFTP_USER={sftp_user}",
        "SFTP_PASS=fake-password",
    ]
    if public_url is not None:
        lines.append(f"PUBLIC_URL={public_url}")
    if wordpress_url is not None:
        lines.append(f"WORDPRESS_URL={wordpress_url}")
    return "\n".join(lines) + "\n"


def _write_theme(
    theme_dir: Path,
    *,
    theme_name: str = "SkyyRose",
    text_domain: str = "skyyrose",
    version_define: str = "SKYYROSE_VERSION",
    version: str = "1.0.0",
) -> None:
    """A gate-passing V1-shaped theme (see test_deploy_theme._make_deployable_theme)."""
    theme_dir.mkdir(parents=True, exist_ok=True)
    (theme_dir / "style.css").write_text(
        f"/*\nTheme Name:          {theme_name}\nVersion:             {version}\n"
        f"Text Domain:         {text_domain}\n*/\n"
    )
    (theme_dir / "functions.php").write_text(f"<?php\ndefine( '{version_define}', '{version}' );\n")
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


def _base_env(tmp_path: Path, routes) -> dict[str, str]:
    env = os.environ.copy()
    for key in INHERITED_KEYS:
        env.pop(key, None)
    pid = os.getpid()
    env["DEPLOY_LOCK_FILE"] = str(tmp_path / f"deploy-{pid}.lock")
    env["DEPLOY_LOG_FILE"] = str(tmp_path / f"deploy-{pid}.log")
    env.update(install_shims(tmp_path, routes))
    return env


def _run(cmd: list[str], env: dict[str, str]) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)
    assert "SHIM-BLOCKED" not in result.stderr, f"network tool invoked:\n{result.stderr}"
    assert blocked_calls(env) == [], f"network tool invoked (stderr hidden):\n{blocked_calls(env)}"
    return result


def _out(result: subprocess.CompletedProcess) -> str:
    return result.stdout + result.stderr


def _printed_as_token(value: str, out: str) -> bool:
    """True when `value` appears in `out` as a whole account name -- not as the
    tail of a longer one (staging-7e48-skyyrose.wordpress.com legitimately
    contains skyyrose.wordpress.com)."""
    return re.search(rf"(?<![\w.-]){re.escape(value)}(?![\w.-])", out) is not None


def _scratch_repo(tmp_path: Path, *, real_engine: bool = False) -> Path:
    """Copy the wrappers (+ stub or real engine) into a scratch repo layout."""
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    for name in ("deploy-staging.sh", "deploy-production.sh", "deploy-target-lib.sh"):
        shutil.copy(SCRIPTS / name, repo / "scripts" / name)
    engine = repo / "scripts" / "deploy-theme.sh"
    if real_engine:
        shutil.copy(ENGINE, engine)
    else:
        engine.write_text(STUB_ENGINE)
    engine.chmod(0o755)
    (repo / "wordpress-theme" / V2_FOLDER).mkdir(parents=True)
    return repo
