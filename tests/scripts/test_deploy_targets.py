"""Engine gates of scripts/deploy-theme.sh (founder directive 2026-09-18).

DEPLOY_TARGET gate, target-host and SSH-destination checks, the live theme
identity gate and the folder-name scope guard (skyyrose-flagship or
skyyrose-flagship-2 only). The staging/production wrappers are
covered by tests/scripts/test_deploy_wrappers.py; shared fixtures live in
tests/scripts/deploy_target_fixtures.py. Nothing here touches the network.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.scripts.deploy_shims import fetched_urls, style_css
from tests.scripts.deploy_target_fixtures import (
    ENGINE,
    PROD_LIVE_STYLE,
    PROD_SSH_USER,
    REST_ROOT,
    STAGING_HOST,
    STAGING_SSH_USER,
    V1_FOLDER,
    V2_FOLDER,
    _base_env,
    _env_text,
    _out,
    _printed_as_token,
    _run,
    _write_theme,
)

# ---------------------------------------------------------------------------
# Engine: DEPLOY_TARGET gate + banner
# ---------------------------------------------------------------------------


class TestEngineTargetGate:
    def _engine_env(self, tmp_path: Path, *, deploy_target: str | None, **env_kwargs):
        env_file = tmp_path / "env"
        env_file.write_text(
            _env_text(
                public_url=env_kwargs.pop("public_url", f"https://{STAGING_HOST}/"),
                theme_folder=env_kwargs.pop("theme_folder", V1_FOLDER),
                wordpress_url=env_kwargs.pop("wordpress_url", None),
                ssh_user=env_kwargs.pop("ssh_user", None),
                sftp_user=env_kwargs.pop("sftp_user", None),
            )
        )
        theme_dir = tmp_path / "src" / V1_FOLDER
        _write_theme(theme_dir)
        routes = env_kwargs.pop(
            "routes",
            [
                (
                    f"/wp-content/themes/{V1_FOLDER}/style.css",
                    "200",
                    style_css("SkyyRose", "skyyrose"),
                    "",
                )
            ],
        )
        env = _base_env(tmp_path, routes)
        env["ENV_FILE"] = str(env_file)
        env["THEME_DIR_OVERRIDE"] = str(theme_dir)
        if deploy_target is not None:
            env["DEPLOY_TARGET"] = deploy_target
        env.update(env_kwargs)
        return env, theme_dir

    def test_refuses_without_deploy_target(self, tmp_path):
        env, _ = self._engine_env(tmp_path, deploy_target=None)
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        assert "DEPLOY_TARGET is unset" in _out(result)
        assert "scripts/deploy-staging.sh or scripts/deploy-production.sh" in _out(result)
        # Refused before any lock/credential work -- nothing else ran.
        assert "Running preflight" not in result.stdout

    def test_refuses_unknown_deploy_target(self, tmp_path):
        env, _ = self._engine_env(tmp_path, deploy_target="prod")
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        assert "DEPLOY_TARGET='prod' is not one of {staging, production}" in _out(result)

    def test_help_works_without_target(self, tmp_path):
        env = _base_env(tmp_path, [])
        result = _run(["bash", str(ENGINE), "--help"], env)
        assert result.returncode == 0
        assert "DEPLOY_TARGET" in result.stdout
        assert "ALLOW_THEME_IDENTITY_CHANGE" in result.stdout

    def test_banner_names_target_host_and_folder(self, tmp_path):
        env, theme_dir = self._engine_env(tmp_path, deploy_target="staging")
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 0, _out(result)
        assert (
            f"TARGET staging: host {STAGING_HOST} | theme folder {V1_FOLDER} | source {V1_FOLDER}"
            in result.stdout
        )
        assert "target: staging" in result.stdout

    def test_production_target_refuses_staging_host(self, tmp_path):
        env, _ = self._engine_env(tmp_path, deploy_target="production")
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        assert f"DEPLOY_TARGET=production but PUBLIC_URL host is '{STAGING_HOST}'" in _out(result)

    def test_staging_target_refuses_production_host(self, tmp_path):
        env, _ = self._engine_env(
            tmp_path, deploy_target="staging", public_url="https://skyyrose.co/"
        )
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        assert "DEPLOY_TARGET=staging but PUBLIC_URL host is 'skyyrose.co'" in _out(result)

    def test_staging_target_refuses_non_staging_host(self, tmp_path):
        # Same allowlist as the wrapper: a direct engine run cannot aim "staging"
        # at an arbitrary host just because it is not a production one.
        env, _ = self._engine_env(
            tmp_path, deploy_target="staging", public_url="https://example.com/"
        )
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        assert "DEPLOY_TARGET=staging but PUBLIC_URL host is 'example.com'" in _out(result)
        assert "*.wpcomstaging.com" in _out(result)

    def test_refuses_when_no_site_url_in_env_file(self, tmp_path):
        env, _ = self._engine_env(tmp_path, deploy_target="staging", public_url=None)
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        assert "PUBLIC_URL (or WORDPRESS_URL) missing" in _out(result)

    def test_wordpress_url_fallback_is_accepted(self, tmp_path):
        env, _ = self._engine_env(
            tmp_path,
            deploy_target="staging",
            public_url=None,
            wordpress_url=f"https://{STAGING_HOST}",
        )
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 0, _out(result)
        assert f"host {STAGING_HOST}" in result.stdout

    # -- D4: userinfo in the URL authority ------------------------------------

    @pytest.mark.parametrize(
        "url",
        ["https://skyyrose.co:443@evil.invalid/", "https://skyyrose.co:@evil.invalid/"],
        ids=["port-userinfo", "empty-password"],
    )
    def test_production_url_with_userinfo_is_refused(self, tmp_path, url):
        env, _ = self._engine_env(
            tmp_path, deploy_target="production", public_url=url, ssh_user=PROD_SSH_USER
        )
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        assert "'@' in the authority" in _out(result)
        assert "evil.invalid" not in result.stdout  # never echoed as a host
        assert fetched_urls(env) == []

    def test_staging_url_with_userinfo_is_refused(self, tmp_path):
        env, _ = self._engine_env(
            tmp_path,
            deploy_target="staging",
            public_url=f"https://{STAGING_HOST}:443@evil.invalid/",
            ssh_user=STAGING_SSH_USER,
        )
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        assert "'@' in the authority" in _out(result)
        assert fetched_urls(env) == []


# ---------------------------------------------------------------------------
# Engine: SSH destination must belong to the target site (D1)
# ---------------------------------------------------------------------------


class TestEngineSshDestination:
    _engine_env = TestEngineTargetGate._engine_env

    def test_staging_url_with_production_ssh_user_is_refused(self, tmp_path):
        env, _ = self._engine_env(tmp_path, deploy_target="staging", ssh_user=PROD_SSH_USER)
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        out = _out(result)
        assert "SSH_USER" in out and f"expected '{STAGING_SSH_USER}'" in out
        assert not _printed_as_token(PROD_SSH_USER, out)  # offending value never printed
        assert fetched_urls(env) == []  # refused before the identity GET

    def test_production_url_with_staging_ssh_user_is_refused(self, tmp_path):
        env, _ = self._engine_env(
            tmp_path,
            deploy_target="production",
            public_url="https://www.skyyrose.co/",
            ssh_user=STAGING_SSH_USER,
        )
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        out = _out(result)
        assert "SSH_USER" in out and f"expected '{PROD_SSH_USER}'" in out
        assert STAGING_SSH_USER not in out
        assert fetched_urls(env) == []

    def test_matching_ssh_user_passes(self, tmp_path):
        env, _ = self._engine_env(tmp_path, deploy_target="staging", ssh_user=STAGING_SSH_USER)
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 0, _out(result)
        assert f"SSH destination belongs to {STAGING_HOST}: {STAGING_SSH_USER}" in result.stdout

    def test_sftp_user_mismatch_is_refused(self, tmp_path):
        env, _ = self._engine_env(
            tmp_path,
            deploy_target="staging",
            ssh_user=STAGING_SSH_USER,
            sftp_user="someone-else.wordpress.com",
        )
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        out = _out(result)
        assert "SFTP_USER" in out and "differs from SSH_USER" in out
        assert "someone-else" not in out
        assert fetched_urls(env) == []

    def test_offending_ssh_user_value_never_appears_in_output(self, tmp_path):
        leaked = "leaked-account-7f3a.wordpress.com"
        env, _ = self._engine_env(tmp_path, deploy_target="staging", ssh_user=leaked)
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        assert leaked not in _out(result)
        assert "leaked-account" not in _out(result)


# ---------------------------------------------------------------------------
# Engine: check_theme_identity
# ---------------------------------------------------------------------------


class TestThemeIdentityGate:
    LIVE_PATH = f"/wp-content/themes/{V1_FOLDER}/style.css"

    def _env(self, tmp_path: Path, routes, *, deploy_target="staging", **overrides):
        env_file = tmp_path / "env"
        public_url = (
            "https://skyyrose.co/" if deploy_target == "production" else f"https://{STAGING_HOST}/"
        )
        env_file.write_text(_env_text(public_url=public_url, theme_folder=V1_FOLDER))
        theme_dir = tmp_path / "src" / V1_FOLDER
        _write_theme(theme_dir)
        env = _base_env(tmp_path, routes)
        env.update(
            {
                "ENV_FILE": str(env_file),
                "THEME_DIR_OVERRIDE": str(theme_dir),
                "DEPLOY_TARGET": deploy_target,
            }
        )
        env.update(overrides)
        return env

    def test_match_passes_and_fetches_cache_busted_live_style(self, tmp_path):
        env = self._env(tmp_path, [(self.LIVE_PATH, "200", style_css("SkyyRose", "skyyrose"), "")])
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 0, _out(result)
        assert (
            "Live theme identity matches source: 'SkyyRose' / text domain 'skyyrose'"
            in result.stdout
        )
        urls = fetched_urls(env)
        assert len(urls) == 1, urls
        assert urls[0].startswith(f"https://{STAGING_HOST}{self.LIVE_PATH}?deploy_verify=")

    def test_v1_source_over_live_flagship2_is_refused(self, tmp_path):
        """Audit H3: the repo's V1 tree must not roll production back from Flagship 2."""
        env = self._env(
            tmp_path, [(self.LIVE_PATH, "200", PROD_LIVE_STYLE, "")], deploy_target="production"
        )
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        out = _out(result)
        assert "Live theme identity MISMATCH" in out
        assert "live='SkyyRose Flagship 2' / 'skyyrose-flagship-2'" in out
        assert "source='SkyyRose' / 'skyyrose'" in out
        assert "ALLOW_THEME_IDENTITY_CHANGE=1" in out
        assert "[DRY RUN] sftp upload" not in out  # never reached the transfer phase

    def test_mismatch_override_passes_with_loud_warning(self, tmp_path):
        env = self._env(
            tmp_path,
            [(self.LIVE_PATH, "200", PROD_LIVE_STYLE, "")],
            ALLOW_THEME_IDENTITY_CHANGE="1",
        )
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 0, _out(result)
        assert (
            "OVERRIDE ALLOW_THEME_IDENTITY_CHANGE=1: REPLACING live 'SkyyRose Flagship 2'"
            in result.stdout
        )

    def test_404_is_refused(self, tmp_path):
        env = self._env(tmp_path, [(self.LIVE_PATH, "404", "Not Found", "")])
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        assert f"Live theme folder '{V1_FOLDER}' is absent on {STAGING_HOST} (HTTP 404" in _out(
            result
        )
        assert "ALLOW_NEW_THEME_FOLDER=1" in _out(result)

    def test_404_override_passes_with_loud_warning(self, tmp_path):
        """D3: the override is honoured only once the REST root proves the
        PUBLIC_URL is a WordPress root (so the 404 really means 'folder absent')."""
        env = self._env(
            tmp_path,
            [(self.LIVE_PATH, "404", "Not Found", ""), REST_ROOT],
            ALLOW_NEW_THEME_FOLDER="1",
        )
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 0, _out(result)
        assert "OVERRIDE ALLOW_NEW_THEME_FOLDER=1" in result.stdout
        assert "FIRST deploy of this folder" in result.stdout
        urls = fetched_urls(env)
        assert len(urls) == 2, urls
        assert urls[1].startswith(f"https://{STAGING_HOST}/index.php?rest_route=/")

    @pytest.mark.parametrize(
        "rest_route",
        [("/index.php", "404", "Not Found", ""), ("/index.php", "200", "<html>parked</html>", "")],
        ids=["rest-404", "rest-200-without-namespaces"],
    )
    def test_404_override_refused_when_rest_root_is_not_wordpress(self, tmp_path, rest_route):
        env = self._env(
            tmp_path,
            [(self.LIVE_PATH, "404", "Not Found", ""), rest_route],
            ALLOW_NEW_THEME_FOLDER="1",
        )
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        out = _out(result)
        assert "cannot be trusted" in out and "folder absent" in out
        assert "FIRST deploy of this folder" not in out
        assert "[DRY RUN] sftp upload" not in out

    def test_curl_failure_is_refused(self, tmp_path):
        env = self._env(tmp_path, [(self.LIVE_PATH, "000", "", "")])
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        assert "Live theme identity fetch FAILED (HTTP 000" in _out(result)

    def test_server_error_is_refused_even_with_overrides(self, tmp_path):
        env = self._env(
            tmp_path,
            [(self.LIVE_PATH, "503", "maintenance", "")],
            ALLOW_NEW_THEME_FOLDER="1",
            ALLOW_THEME_IDENTITY_CHANGE="1",
        )
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        assert "fetch FAILED (HTTP 503" in _out(result)

    def test_unparseable_live_header_is_refused(self, tmp_path):
        env = self._env(tmp_path, [(self.LIVE_PATH, "200", "/* not a theme header */", "")])
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        assert "no parseable Theme Name/Text Domain" in _out(result)

    def test_name_match_but_domain_mismatch_is_refused(self, tmp_path):
        env = self._env(
            tmp_path, [(self.LIVE_PATH, "200", style_css("SkyyRose", "skyyrose-flagship-2"), "")]
        )
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        assert "MISMATCH" in _out(result)


# ---------------------------------------------------------------------------
# Engine: explicit refusal of a flagship-2 source
# ---------------------------------------------------------------------------


class TestEngineScopeGuard:
    @pytest.mark.parametrize(
        "kwargs",
        [
            {
                "version_define": "SKYYROSE2_VERSION",
                "theme_name": "SkyyRose Flagship 2",
                "text_domain": V2_FOLDER,
            },
            {"text_domain": V2_FOLDER},
            {"version_define": "SKYYROSE2_VERSION"},
        ],
        ids=["full-v2", "text-domain-only", "version-define-only"],
    )
    def test_unrecognized_folder_name_is_refused_regardless_of_content(self, tmp_path, kwargs):
        """The scope guard is folder-basename-driven, not content-driven: a
        source folder named neither skyyrose-flagship nor skyyrose-flagship-2
        is refused even when its style.css/functions.php carry V2 markers."""
        env_file = tmp_path / "env"
        env_file.write_text(
            _env_text(public_url=f"https://{STAGING_HOST}/", theme_folder=V2_FOLDER)
        )
        theme_dir = tmp_path / "src" / "some-source"
        _write_theme(theme_dir, **kwargs)
        env = _base_env(
            tmp_path,
            [
                (
                    f"/wp-content/themes/{V2_FOLDER}/style.css",
                    "200",
                    style_css("SkyyRose Flagship 2", V2_FOLDER),
                    "",
                )
            ],
        )
        env.update(
            {
                "ENV_FILE": str(env_file),
                "THEME_DIR_OVERRIDE": str(theme_dir),
                "DEPLOY_TARGET": "staging",
            }
        )
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        out = _out(result)
        assert "Deploy source folder is 'some-source'" in out
        assert "this engine only recognizes skyyrose-flagship or skyyrose-flagship-2" in out
        assert "Version triple unreadable" not in out

    def test_v2_named_folder_with_v1_content_is_treated_as_v1_and_still_gated(self, tmp_path):
        """A folder literally named skyyrose-flagship-2 now passes the
        basename-only scope guard, but V1-shaped content (no SKYYROSE2_VERSION
        define) makes skyyrose_is_v2_theme() classify it as V1 -- the V2 data/
        boundary gate is skipped, and it proceeds to the ordinary V1 checks and
        then the live theme identity gate, which is what actually catches it
        here (no live route configured for this folder -> 404 -> new-folder
        gate). Folder name alone no longer grants a free pass."""
        env_file = tmp_path / "env"
        env_file.write_text(
            _env_text(public_url=f"https://{STAGING_HOST}/", theme_folder=V2_FOLDER)
        )
        theme_dir = tmp_path / "src" / V2_FOLDER
        _write_theme(theme_dir)  # V1-shaped contents under the -2 folder name
        env = _base_env(tmp_path, [])
        env.update(
            {
                "ENV_FILE": str(env_file),
                "THEME_DIR_OVERRIDE": str(theme_dir),
                "DEPLOY_TARGET": "staging",
            }
        )
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        out = _out(result)
        assert f"Engine supports source: {V2_FOLDER}" in out
        assert "Version triple in sync: 1.0.0" in out
        assert f"is absent on {STAGING_HOST} (HTTP 404" in out
        assert "Deploying would create a new theme folder" in out
        assert "--allow-new-theme-folder" in out
        # Unlike the pre-support refusal, this now reaches the live identity
        # GET -- it is the gate that actually catches this case.
        assert len(fetched_urls(env)) == 1
        assert fetched_urls(env)[0].startswith(
            f"https://{STAGING_HOST}/wp-content/themes/{V2_FOLDER}/style.css"
        )

    def test_v1_source_under_another_basename_is_refused(self, tmp_path):
        """D2: the remote hot-swap moves the extracted archive under its own
        basename, so a source tree under any unrecognized folder name would
        extract to a path the swap never renames into place -- the scope
        guard refuses it up front regardless of content."""
        env_file = tmp_path / "env"
        env_file.write_text(
            _env_text(public_url=f"https://{STAGING_HOST}/", theme_folder=V1_FOLDER)
        )
        theme_dir = tmp_path / "src" / "skyyrose-flagship-copy"
        _write_theme(theme_dir)  # V1-shaped, wrong basename
        env = _base_env(tmp_path, [])
        env.update(
            {
                "ENV_FILE": str(env_file),
                "THEME_DIR_OVERRIDE": str(theme_dir),
                "DEPLOY_TARGET": "staging",
            }
        )
        result = _run(["bash", str(ENGINE), "--dry-run"], env)
        assert result.returncode == 1
        out = _out(result)
        assert "Deploy source folder is 'skyyrose-flagship-copy'" in out
        assert "this engine only recognizes skyyrose-flagship or skyyrose-flagship-2" in out
        assert fetched_urls(env) == []
