"""scripts/deploy-staging.sh and scripts/deploy-production.sh (via deploy-target-lib.sh).

Env-file validation, inherited-variable refusal, one-shot override flags, and the
handoff to the engine. The wrappers run from a copied scratch repo so their env-file
paths resolve inside tmp_path -- the real .env.wordpress* files are never read.
Engine gates: tests/scripts/test_deploy_targets.py.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.scripts.deploy_shims import fetched_urls
from tests.scripts.deploy_target_fixtures import (
    ENGINE,
    PROD_SSH_USER,
    SCRIPTS,
    STAGING_HOST,
    STAGING_SSH_USER,
    V1_FOLDER,
    V2_FOLDER,
    _base_env,
    _env_text,
    _out,
    _printed_as_token,
    _run,
    _scratch_repo,
    _write_theme,
)

# ---------------------------------------------------------------------------
# Wrappers
# ---------------------------------------------------------------------------


class TestStagingWrapper:
    def _run_wrapper(self, repo: Path, env: dict[str, str], *args):
        return _run(["bash", str(repo / "scripts" / "deploy-staging.sh"), *args], env)

    def test_valid_env_execs_engine_with_pinned_target(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress.staging").write_text(
            _env_text(public_url=f"https://{STAGING_HOST}/", theme_folder=V2_FOLDER)
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []), "--dry-run")
        assert result.returncode == 0, _out(result)
        assert "STUB DEPLOY_TARGET=staging" in result.stdout
        assert f"STUB ENV_FILE={repo / '.env.wordpress.staging'}" in result.stdout
        assert f"STUB THEME_DIR_OVERRIDE={repo / 'wordpress-theme' / V2_FOLDER}" in result.stdout
        assert "STUB ARGS=--dry-run" in result.stdout
        assert f"Target staging: host {STAGING_HOST} | theme folder {V2_FOLDER}" in result.stdout

    def test_wordpress_url_fallback(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress.staging").write_text(
            _env_text(
                public_url=None, theme_folder=V2_FOLDER, wordpress_url=f"https://{STAGING_HOST}"
            )
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []))
        assert result.returncode == 0, _out(result)
        assert "STUB DEPLOY_TARGET=staging" in result.stdout

    def test_missing_env_file_refuses(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        result = self._run_wrapper(repo, _base_env(tmp_path, []), "--dry-run")
        assert result.returncode == 1
        assert "Env file missing" in _out(result)
        assert "STUB" not in result.stdout

    def test_production_host_refuses(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress.staging").write_text(
            _env_text(public_url="https://skyyrose.co/", theme_folder=V2_FOLDER)
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []))
        assert result.returncode == 1
        assert "host 'skyyrose.co' is not a *.wpcomstaging.com staging host" in _out(result)
        assert "STUB" not in result.stdout

    def test_nonresolving_custom_staging_host_refuses(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress.staging").write_text(
            _env_text(public_url="https://staging.skyyrose.co/", theme_folder=V2_FOLDER)
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []))
        assert result.returncode == 1
        assert "host 'staging.skyyrose.co' is not a *.wpcomstaging.com" in _out(result)

    def test_wrong_theme_basename_refuses(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress.staging").write_text(
            _env_text(public_url=f"https://{STAGING_HOST}/", theme_folder=V1_FOLDER)
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []))
        assert result.returncode == 1
        assert f"ends in '{V1_FOLDER}' -- expected 'skyyrose-flagship-2'" in _out(result)
        assert "STUB" not in result.stdout

    def test_missing_site_url_refuses(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress.staging").write_text(
            _env_text(public_url=None, theme_folder=V2_FOLDER)
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []))
        assert result.returncode == 1
        assert "no PUBLIC_URL (or WORDPRESS_URL)" in _out(result)

    @pytest.mark.parametrize(
        "var",
        [
            "ENV_FILE",
            "THEME_DIR_OVERRIDE",
            "DEPLOY_TARGET",
            "PUBLIC_URL",
            "WORDPRESS_URL",
            "ALLOW_THEME_IDENTITY_CHANGE",
            "ALLOW_NEW_THEME_FOLDER",
            "PREFLIGHT_SKIP_COMPLETENESS",
        ],
    )
    def test_inherited_selection_variable_is_rejected(self, tmp_path, var):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress.staging").write_text(
            _env_text(public_url=f"https://{STAGING_HOST}/", theme_folder=V2_FOLDER)
        )
        env = _base_env(tmp_path, [])
        env[var] = "1"
        result = self._run_wrapper(repo, env, "--dry-run")
        assert result.returncode == 1
        assert f"{var} is already set in the environment" in _out(result)
        assert "STUB" not in result.stdout

    # -- D5: one-shot override flags are consumed by the wrapper ---------------

    def test_allow_new_theme_folder_flag_reaches_engine_as_env_only(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress.staging").write_text(
            _env_text(public_url=f"https://{STAGING_HOST}/", theme_folder=V2_FOLDER)
        )
        result = self._run_wrapper(
            repo, _base_env(tmp_path, []), "--allow-new-theme-folder", "--dry-run"
        )
        assert result.returncode == 0, _out(result)
        assert "STUB ALLOW_NEW_THEME_FOLDER=1" in result.stdout
        assert "STUB ALLOW_THEME_IDENTITY_CHANGE=<unset>" in result.stdout
        assert "STUB ARGS=--dry-run" in result.stdout  # flag never reaches parse_args

    def test_allow_theme_identity_change_flag_reaches_engine_as_env_only(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress.staging").write_text(
            _env_text(public_url=f"https://{STAGING_HOST}/", theme_folder=V2_FOLDER)
        )
        result = self._run_wrapper(
            repo, _base_env(tmp_path, []), "--dry-run", "--allow-theme-identity-change"
        )
        assert result.returncode == 0, _out(result)
        assert "STUB ALLOW_THEME_IDENTITY_CHANGE=1" in result.stdout
        assert "STUB ALLOW_NEW_THEME_FOLDER=<unset>" in result.stdout
        assert "STUB ARGS=--dry-run" in result.stdout

    def test_both_flags_with_passthrough_args(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress.staging").write_text(
            _env_text(public_url=f"https://{STAGING_HOST}/", theme_folder=V2_FOLDER)
        )
        result = self._run_wrapper(
            repo,
            _base_env(tmp_path, []),
            "--allow-new-theme-folder",
            "--dry-run",
            "--allow-theme-identity-change",
            "--with-maintenance",
        )
        assert result.returncode == 0, _out(result)
        assert "STUB ALLOW_NEW_THEME_FOLDER=1" in result.stdout
        assert "STUB ALLOW_THEME_IDENTITY_CHANGE=1" in result.stdout
        assert "STUB ARGS=--dry-run --with-maintenance" in result.stdout

    def test_flags_named_in_help(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        result = self._run_wrapper(repo, _base_env(tmp_path, []), "--help")
        assert result.returncode == 0
        assert "--allow-new-theme-folder" in result.stdout
        assert "--allow-theme-identity-change" in result.stdout

    # -- D1: SSH destination must belong to the staging host -------------------

    def test_production_ssh_user_refuses(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress.staging").write_text(
            _env_text(
                public_url=f"https://{STAGING_HOST}/",
                theme_folder=V2_FOLDER,
                ssh_user=PROD_SSH_USER,
            )
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []), "--dry-run")
        assert result.returncode == 1
        out = _out(result)
        assert "SSH_USER" in out and f"expected '{STAGING_SSH_USER}'" in out
        assert not _printed_as_token(PROD_SSH_USER, out)
        assert "STUB" not in result.stdout

    def test_sftp_user_mismatch_refuses(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress.staging").write_text(
            _env_text(
                public_url=f"https://{STAGING_HOST}/",
                theme_folder=V2_FOLDER,
                sftp_user="someone-else.wordpress.com",
            )
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []), "--dry-run")
        assert result.returncode == 1
        out = _out(result)
        assert "SFTP_USER" in out and "differs from SSH_USER" in out
        assert "someone-else" not in out
        assert "STUB" not in result.stdout

    def test_ssh_user_value_never_printed(self, tmp_path):
        leaked = "leaked-account-7f3a.wordpress.com"
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress.staging").write_text(
            _env_text(
                public_url=f"https://{STAGING_HOST}/", theme_folder=V2_FOLDER, ssh_user=leaked
            )
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []), "--dry-run")
        assert result.returncode == 1
        assert "leaked-account" not in _out(result)

    # -- D4: userinfo in the URL authority --------------------------------------

    def test_url_with_userinfo_refuses(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress.staging").write_text(
            _env_text(
                public_url=f"https://{STAGING_HOST}:443@evil.invalid/",
                theme_folder=V2_FOLDER,
                ssh_user=STAGING_SSH_USER,
            )
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []), "--dry-run")
        assert result.returncode == 1
        assert "'@' in the authority" in _out(result)
        assert "evil.invalid" not in result.stdout
        assert "STUB" not in result.stdout

    def test_help_needs_no_env_file(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        result = self._run_wrapper(repo, _base_env(tmp_path, []), "--help")
        assert result.returncode == 0
        assert "deploy-staging.sh" in result.stdout
        assert "STUB" not in result.stdout

    def test_secret_values_never_printed(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress.staging").write_text(
            _env_text(public_url=f"https://{STAGING_HOST}/", theme_folder=V2_FOLDER)
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []))
        assert "fake-password" not in _out(result)

    def test_end_to_end_real_engine_refuses_flagship2_source_explicitly(self, tmp_path):
        """Wrapper -> real engine: today the chain must stop at the scope guard,
        with the explicit PR #918 message, before any transfer or SSH."""
        repo = _scratch_repo(tmp_path, real_engine=True)
        (repo / ".env.wordpress.staging").write_text(
            _env_text(public_url=f"https://{STAGING_HOST}/", theme_folder=V2_FOLDER)
        )
        _write_theme(
            repo / "wordpress-theme" / V2_FOLDER,
            theme_name="SkyyRose Flagship 2",
            text_domain=V2_FOLDER,
            version_define="SKYYROSE2_VERSION",
        )
        env = _base_env(tmp_path, [])
        result = self._run_wrapper(repo, env, "--dry-run")
        assert result.returncode == 1
        out = _out(result)
        assert "target: staging" in out
        assert (
            f"TARGET staging: host {STAGING_HOST} | theme folder {V2_FOLDER} | source {V2_FOLDER}"
            in out
        )
        assert "engine lacks skyyrose-flagship-2 support" in out
        assert fetched_urls(env) == []


class TestProductionWrapper:
    def _run_wrapper(self, repo: Path, env: dict[str, str], *args):
        return _run(["bash", str(repo / "scripts" / "deploy-production.sh"), *args], env)

    @pytest.mark.parametrize(
        "url", ["https://skyyrose.co/", "https://www.skyyrose.co", "HTTPS://SkyyRose.co/"]
    )
    def test_post_cutover_env_execs_engine(self, tmp_path, url):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress").write_text(_env_text(public_url=url, theme_folder=V2_FOLDER))
        result = self._run_wrapper(repo, _base_env(tmp_path, []), "--dry-run")
        assert result.returncode == 0, _out(result)
        assert "STUB DEPLOY_TARGET=production" in result.stdout
        assert f"STUB ENV_FILE={repo / '.env.wordpress'}" in result.stdout
        assert f"STUB THEME_DIR_OVERRIDE={repo / 'wordpress-theme' / V2_FOLDER}" in result.stdout

    def test_pre_cutover_env_refuses_with_plain_reason(self, tmp_path):
        """Today's .env.wordpress still names the V1 folder -> intended refusal."""
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress").write_text(
            _env_text(public_url="https://skyyrose.co/", theme_folder=V1_FOLDER)
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []), "--dry-run")
        assert result.returncode == 1
        out = _out(result)
        assert f"ends in '{V1_FOLDER}' -- expected 'skyyrose-flagship-2'" in out
        assert "pre-cutover folder" in out
        assert "founder-approved env switch" in out
        assert "STUB" not in result.stdout

    def test_staging_host_refuses(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress").write_text(
            _env_text(public_url=f"https://{STAGING_HOST}/", theme_folder=V2_FOLDER)
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []))
        assert result.returncode == 1
        assert f"host '{STAGING_HOST}' is not skyyrose.co" in _out(result)
        assert "STUB" not in result.stdout

    def test_lookalike_host_refuses(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress").write_text(
            _env_text(public_url="https://skyyrose.com/", theme_folder=V2_FOLDER)
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []))
        assert result.returncode == 1
        assert "host 'skyyrose.com' is not skyyrose.co" in _out(result)

    def test_missing_env_file_refuses(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        result = self._run_wrapper(repo, _base_env(tmp_path, []))
        assert result.returncode == 1
        assert "Env file missing" in _out(result)

    def test_inherited_env_file_is_rejected(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress").write_text(
            _env_text(public_url="https://skyyrose.co/", theme_folder=V2_FOLDER)
        )
        env = _base_env(tmp_path, [])
        env["ENV_FILE"] = str(tmp_path / "staging-creds")
        result = self._run_wrapper(repo, env)
        assert result.returncode == 1
        assert "ENV_FILE is already set" in _out(result)
        assert "STUB" not in result.stdout

    @pytest.mark.parametrize("var", ["ALLOW_THEME_IDENTITY_CHANGE", "ALLOW_NEW_THEME_FOLDER"])
    def test_inherited_override_variable_is_rejected(self, tmp_path, var):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress").write_text(
            _env_text(public_url="https://skyyrose.co/", theme_folder=V2_FOLDER)
        )
        env = _base_env(tmp_path, [])
        env[var] = "1"
        result = self._run_wrapper(repo, env, "--dry-run")
        assert result.returncode == 1
        assert f"{var} is already set in the environment" in _out(result)
        assert "STUB" not in result.stdout

    # -- D1: SSH destination must belong to skyyrose.co -------------------------

    @pytest.mark.parametrize("url", ["https://skyyrose.co/", "https://www.skyyrose.co/"])
    def test_staging_ssh_user_refuses(self, tmp_path, url):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress").write_text(
            _env_text(public_url=url, theme_folder=V2_FOLDER, ssh_user=STAGING_SSH_USER)
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []), "--dry-run")
        assert result.returncode == 1
        out = _out(result)
        assert "SSH_USER" in out and f"expected '{PROD_SSH_USER}'" in out
        assert STAGING_SSH_USER not in out
        assert "STUB" not in result.stdout

    def test_matching_ssh_user_passes(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress").write_text(
            _env_text(
                public_url="https://www.skyyrose.co/",
                theme_folder=V2_FOLDER,
                ssh_user=PROD_SSH_USER,
                sftp_user=PROD_SSH_USER,
            )
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []), "--dry-run")
        assert result.returncode == 0, _out(result)
        assert "STUB DEPLOY_TARGET=production" in result.stdout

    def test_sftp_user_mismatch_refuses(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress").write_text(
            _env_text(
                public_url="https://skyyrose.co/",
                theme_folder=V2_FOLDER,
                sftp_user="someone-else.wordpress.com",
            )
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []), "--dry-run")
        assert result.returncode == 1
        out = _out(result)
        assert "SFTP_USER" in out and "differs from SSH_USER" in out
        assert "someone-else" not in out
        assert "STUB" not in result.stdout

    # -- D4: userinfo in the URL authority --------------------------------------

    @pytest.mark.parametrize(
        "url",
        ["https://skyyrose.co:443@evil.invalid/", "https://skyyrose.co:@evil.invalid/"],
        ids=["port-userinfo", "empty-password"],
    )
    def test_url_with_userinfo_refuses(self, tmp_path, url):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress").write_text(
            _env_text(public_url=url, theme_folder=V2_FOLDER, ssh_user=PROD_SSH_USER)
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []), "--dry-run")
        assert result.returncode == 1
        assert "'@' in the authority" in _out(result)
        assert "evil.invalid" not in result.stdout
        assert "STUB" not in result.stdout

    def test_wordpress_url_with_userinfo_refuses(self, tmp_path):
        repo = _scratch_repo(tmp_path)
        (repo / ".env.wordpress").write_text(
            _env_text(
                public_url=None,
                theme_folder=V2_FOLDER,
                wordpress_url="https://skyyrose.co:443@evil.invalid/",
                ssh_user=PROD_SSH_USER,
            )
        )
        result = self._run_wrapper(repo, _base_env(tmp_path, []), "--dry-run")
        assert result.returncode == 1
        assert "'@' in the authority" in _out(result)
        assert "STUB" not in result.stdout


# ---------------------------------------------------------------------------
# Static checks
# ---------------------------------------------------------------------------


class TestShellcheck:
    @pytest.mark.skipif(not shutil.which("shellcheck"), reason="shellcheck binary not installed")
    @pytest.mark.parametrize(
        "script",
        ["deploy-staging.sh", "deploy-production.sh", "deploy-target-lib.sh", "verify-deploy.sh"],
    )
    def test_shellcheck_passes(self, script):
        result = subprocess.run(
            ["shellcheck", "-x", str(SCRIPTS / script)], capture_output=True, text=True, timeout=30
        )
        assert result.returncode == 0, f"shellcheck errors:\n{result.stdout}"

    def test_wrappers_are_executable(self):
        for script in ("deploy-staging.sh", "deploy-production.sh"):
            assert os.access(SCRIPTS / script, os.X_OK), f"{script} is not executable"

    def test_engine_has_no_literal_production_default(self):
        source = ENGINE.read_text()
        assert "PUBLIC_URL:-https://skyyrose.co" not in source
