"""Tests for scripts/verify-deploy.sh -- subprocess-based verification.

Tests invoke the verification script via subprocess and assert on exit codes,
stdout/stderr content, and script source patterns. Validates deep content
verification for post-deploy health checks.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.scripts.deploy_shims import blocked_calls, fetched_urls, install_shims, style_css

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify-deploy.sh"

SITE = "https://fake-site.wpcomstaging.com"
INHERITED_KEYS = (
    "WORDPRESS_URL",
    "PUBLIC_URL",
    "WP_THEME_PATH",
    "THEME_SLUG",
    "ALLOW_THEME_IDENTITY_CHANGE",
    "ALLOW_NEW_THEME_FOLDER",
    "PREFLIGHT_SKIP_COMPLETENESS",
    "STRUCTURE_CHECK_STRICT",
)


def run_script(*args, env_overrides=None):
    """Run verify-deploy.sh with given arguments (no target env by default)."""
    env = os.environ.copy()
    for key in INHERITED_KEYS:
        env.pop(key, None)
    if env_overrides:
        env.update(env_overrides)
    result = subprocess.run(
        ["bash", str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    return result


def _v1_routes():
    pages = {
        "/": "<title>SKYY ROSE</title>",
        "/index.php": '{"namespaces":[]}',
        "/collection-black-rose/": "Black Rose",
        "/collection-love-hurts/": "Love Hurts",
        "/collection-signature/": "Signature",
        "/about/": "SkyyRose",
        "/experience-black-rose/": "immersive-black-rose",
        "/experience-love-hurts/": "immersive-love-hurts",
        "/experience-signature/": "immersive-signature",
        "/pre-order/": "pre-order",
        "/experience/": "Immersive Experiences",
    }
    routes = [
        (
            "/wp-content/themes/skyyrose-flagship/style.css",
            "200",
            style_css("SkyyRose", "skyyrose"),
            "",
        )
    ]
    routes += [(path, "200", body, "") for path, body in pages.items()]
    return routes


def _v2_routes(*, legacy_status="302", legacy_target=None, redirect_site=SITE):
    pages = {
        "/": "SkyyRose",
        "/index.php": '{"namespaces":[]}',
        "/collections/black-rose/": "Black Rose",
        "/collections/love-hurts/": "Love Hurts",
        "/collections/signature/": "Signature",
        "/collections/kids-capsule/": "Kids Capsule",
        "/about/": "SkyyRose",
        "/worlds/black-rose/": "page-template-template-immersive-black-rose",
        "/worlds/love-hurts/": "page-template-template-immersive-love-hurts",
        "/worlds/signature/": "page-template-template-immersive-signature",
        "/pre-order/": "Pre-Order",
    }
    legacy = {
        "/collection-black-rose/": "/collections/black-rose/",
        "/collection-love-hurts/": "/collections/love-hurts/",
        "/collection-signature/": "/collections/signature/",
        "/collection-kids-capsule/": "/collections/kids-capsule/",
        "/experience-black-rose/": "/worlds/black-rose/",
        "/experience-love-hurts/": "/worlds/love-hurts/",
        "/experience-signature/": "/worlds/signature/",
    }
    routes = [
        (
            "/wp-content/themes/skyyrose-flagship-2/style.css",
            "200",
            style_css("SkyyRose Flagship 2", "skyyrose-flagship-2"),
            "",
        )
    ]
    routes += [(path, "200", body, "") for path, body in pages.items()]
    for path, target in legacy.items():
        routes.append(
            (path, legacy_status, "legacy body", f"{redirect_site}{legacy_target or target}")
        )
    return routes


def run_shimmed(tmp_path, routes, *args, env_overrides=None):
    env = install_shims(tmp_path, routes)
    if env_overrides:
        env.update(env_overrides)
    result = run_script(*args, env_overrides=env)
    assert "SHIM-BLOCKED" not in result.stderr
    assert blocked_calls(env) == [], f"network tool invoked (stderr hidden):\n{blocked_calls(env)}"
    return result, env


class TestHelp:
    """Test 1: --help exits 0 and prints usage information."""

    def test_help_exits_zero(self):
        result = run_script("--help")
        assert result.returncode == 0

    def test_help_prints_usage(self):
        result = run_script("--help")
        output = result.stdout.lower()
        assert "usage" in output


class TestScriptStructure:
    """Test 2-3: Script source contains verify_page function with curl + content grep."""

    def test_verify_page_function_exists(self):
        source = SCRIPT_PATH.read_text()
        assert "verify_page()" in source or "verify_page ()" in source

    def test_uses_curl_with_http_code(self):
        source = SCRIPT_PATH.read_text()
        assert "curl" in source
        assert "http_code" in source

    def test_checks_content_marker(self):
        """Script checks HTTP status code AND content marker (not just status)."""
        source = SCRIPT_PATH.read_text()
        assert "grep -qi" in source or "grep -q" in source


class TestContentVerification:
    """Test 4: Script contains all required health check pages."""

    def test_checks_homepage(self):
        source = SCRIPT_PATH.read_text()
        assert "Homepage" in source

    def test_checks_rest_api(self):
        source = SCRIPT_PATH.read_text()
        assert "REST API" in source
        assert "rest_route" in source

    def test_checks_black_rose(self):
        source = SCRIPT_PATH.read_text()
        assert "Black Rose" in source
        assert "collection-black-rose" in source

    def test_checks_love_hurts(self):
        source = SCRIPT_PATH.read_text()
        assert "Love Hurts" in source
        assert "collection-love-hurts" in source

    def test_checks_signature(self):
        source = SCRIPT_PATH.read_text()
        assert "Signature" in source
        assert "collection-signature" in source

    def test_checks_about(self):
        source = SCRIPT_PATH.read_text()
        assert "About" in source
        assert "/about/" in source


class TestCacheBusting:
    """Test 5: Script uses cache-busting query parameter."""

    def test_uses_cache_busting_param(self):
        source = SCRIPT_PATH.read_text()
        assert "_verify=" in source or "nocache=" in source

    def test_uses_timestamp_for_cache_busting(self):
        source = SCRIPT_PATH.read_text()
        assert "TIMESTAMP" in source

    def test_rest_api_uses_ampersand_separator(self):
        """REST API URL already has '?' so cache bust must use '&'."""
        source = SCRIPT_PATH.read_text()
        assert "&_verify=" in source or "&_verify=" in source


class TestFailureCollection:
    """Test 6: Script collects all failures before exiting."""

    def test_has_failures_counter(self):
        source = SCRIPT_PATH.read_text()
        assert "FAILURES" in source

    def test_does_not_exit_on_first_failure(self):
        """verify_page calls use || true to continue on failure."""
        source = SCRIPT_PATH.read_text()
        assert "|| true" in source

    def test_exits_nonzero_on_failure(self):
        """Script exits with non-zero when FAILURES > 0."""
        source = SCRIPT_PATH.read_text()
        # Accept both quoted and unquoted forms
        assert (
            "FAILURES -eq 0" in source
            or "FAILURES -gt 0" in source
            or '"$FAILURES" -eq 0' in source
            or '"$FAILURES" -gt 0' in source
        )


class TestEnvironmentVariable:
    """Test 7: Script uses WORDPRESS_URL environment variable."""

    def test_uses_wordpress_url_env(self):
        source = SCRIPT_PATH.read_text()
        assert "WORDPRESS_URL" in source

    def test_not_hardcoded_url(self):
        """SITE_URL comes from env var, not hardcoded."""
        source = SCRIPT_PATH.read_text()
        assert "${WORDPRESS_URL:-" in source
        assert "WORDPRESS_URL:-https://skyyrose.co" not in source

    def test_refuses_without_target_url(self):
        result = run_script("--theme", "skyyrose-flagship-2")
        assert result.returncode == 1
        assert "No target URL" in result.stdout + result.stderr

    def test_refuses_without_theme_slug(self):
        result = run_script("--url", "https://example.invalid")
        assert result.returncode == 1
        assert "No theme slug" in result.stdout + result.stderr

    def test_env_file_supplies_url_and_slug(self, tmp_path):
        env_file = tmp_path / "env"
        env_file.write_text(
            "SSH_PASS=do-not-print\nPUBLIC_URL=https://from-env.wpcomstaging.com/\n"
            "WP_THEME_PATH=/htdocs/wp-content/themes/skyyrose-flagship-2\n"
        )
        result = run_script("--env-file", str(env_file), "--list")
        assert result.returncode == 0
        assert "https://from-env.wpcomstaging.com/collections/black-rose/" in result.stdout
        assert "do-not-print" not in result.stdout + result.stderr


class TestTextDomainRouting:
    """The route table is chosen by the LIVE theme's Text Domain -- fail closed."""

    def test_v1_theme_runs_v1_routes(self, tmp_path):
        result, env = run_shimmed(
            tmp_path,
            _v1_routes(),
            env_overrides={"WORDPRESS_URL": SITE, "WP_THEME_PATH": "/x/themes/skyyrose-flagship"},
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert "text domain 'skyyrose'" in result.stdout
        urls = fetched_urls(env)
        assert any("/collection-black-rose/?_verify=" in u for u in urls)
        assert not any("/collections/" in u for u in urls)
        assert "All 11 checks verified" in result.stdout

    def test_v2_theme_runs_v2_routes_and_redirects(self, tmp_path):
        result, env = run_shimmed(
            tmp_path,
            _v2_routes(),
            env_overrides={"WORDPRESS_URL": SITE, "WP_THEME_PATH": "/x/themes/skyyrose-flagship-2"},
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert "text domain 'skyyrose-flagship-2'" in result.stdout
        urls = fetched_urls(env)
        assert urls[0].startswith(
            f"{SITE}/wp-content/themes/skyyrose-flagship-2/style.css?_verify="
        )
        assert any("/collections/black-rose/?_verify=" in u for u in urls)
        assert any("/worlds/signature/?_verify=" in u for u in urls)
        assert any("/collection-black-rose/?_verify=" in u for u in urls)
        assert "Legacy experience: Signature: HTTP 302 -> /worlds/signature/" in result.stdout
        assert "All 18 checks verified" in result.stdout

    def test_v2_legacy_route_answering_200_fails(self, tmp_path):
        result, _ = run_shimmed(
            tmp_path,
            _v2_routes(legacy_status="200"),
            env_overrides={"WORDPRESS_URL": SITE, "WP_THEME_PATH": "/x/themes/skyyrose-flagship-2"},
        )
        assert result.returncode == 1
        assert "Legacy collection: Black Rose: HTTP 200 (expected 301/302" in result.stdout
        assert "7 of 18 checks failed" in result.stdout

    def test_v2_redirect_to_wrong_target_fails(self, tmp_path):
        result, _ = run_shimmed(
            tmp_path,
            _v2_routes(legacy_target="/"),
            env_overrides={"WORDPRESS_URL": SITE, "WP_THEME_PATH": "/x/themes/skyyrose-flagship-2"},
        )
        assert result.returncode == 1
        assert "redirects to" in result.stdout

    # -- D6a: the Location must equal SITE_URL + expected path EXACTLY ---------

    def test_v2_redirect_to_evil_host_fails(self, tmp_path):
        """A redirect whose path merely ENDS with the expected path is not a
        pass: https://evil.invalid/collections/black-rose/ must fail."""
        result, _ = run_shimmed(
            tmp_path,
            _v2_routes(redirect_site="https://evil.invalid"),
            env_overrides={"WORDPRESS_URL": SITE, "WP_THEME_PATH": "/x/themes/skyyrose-flagship-2"},
        )
        assert result.returncode == 1
        assert "redirects to 'https://evil.invalid/collections/black-rose/'" in result.stdout
        assert "7 of 18 checks failed" in result.stdout

    def test_v2_redirect_with_path_prefix_fails(self, tmp_path):
        """.../es/collections/black-rose/ ends with the expected path but is a
        different route on the same host -- exact match only."""
        result, _ = run_shimmed(
            tmp_path,
            _v2_routes(redirect_site=f"{SITE}/es"),
            env_overrides={"WORDPRESS_URL": SITE, "WP_THEME_PATH": "/x/themes/skyyrose-flagship-2"},
        )
        assert result.returncode == 1
        assert f"redirects to '{SITE}/es/collections/black-rose/'" in result.stdout
        assert "7 of 18 checks failed" in result.stdout

    # -- D6b: PUBLIC_URL wins over WORDPRESS_URL (matches wrapper/engine) ------

    def test_public_url_takes_precedence_over_wordpress_url(self, tmp_path):
        result, env = run_shimmed(
            tmp_path,
            _v2_routes(),
            env_overrides={
                "PUBLIC_URL": SITE,
                "WORDPRESS_URL": "https://other-site.invalid",
                "WP_THEME_PATH": "/x/themes/skyyrose-flagship-2",
            },
        )
        assert result.returncode == 0, result.stdout + result.stderr
        urls = fetched_urls(env)
        assert urls and all(u.startswith(f"{SITE}/") for u in urls), urls
        assert "other-site.invalid" not in result.stdout + result.stderr

    # -- D6c: a ?query on the site URL is stripped and never printed ----------

    @pytest.mark.parametrize("via", ["env", "flag", "env-file"])
    def test_site_url_query_is_stripped_and_never_printed(self, tmp_path, via):
        secret_url = f"{SITE}/?bypass-coming-soon=SECRET-TOKEN-9c1e"
        args: list[str] = []
        overrides = {"WP_THEME_PATH": "/x/themes/skyyrose-flagship-2"}
        if via == "env":
            overrides["WORDPRESS_URL"] = secret_url
        elif via == "flag":
            args = ["--url", secret_url]
        else:
            env_file = tmp_path / "env"
            env_file.write_text(
                f"PUBLIC_URL={secret_url}\nWP_THEME_PATH=/x/themes/skyyrose-flagship-2\n"
            )
            args = ["--env-file", str(env_file)]
        result, env = run_shimmed(tmp_path, _v2_routes(), *args, env_overrides=overrides)
        assert result.returncode == 0, result.stdout + result.stderr
        out = result.stdout + result.stderr
        assert "SECRET-TOKEN" not in out and "bypass-coming-soon" not in out
        urls = fetched_urls(env)
        assert urls[0].startswith(
            f"{SITE}/wp-content/themes/skyyrose-flagship-2/style.css?_verify="
        )
        assert not any("bypass-coming-soon" in u for u in urls), urls

    def test_list_never_prints_site_url_query(self):
        result = run_script(
            "--list",
            env_overrides={
                "WORDPRESS_URL": f"{SITE}/?bypass-coming-soon=SECRET-TOKEN-9c1e",
                "WP_THEME_PATH": "/x/themes/skyyrose-flagship-2",
            },
        )
        assert result.returncode == 0
        assert "SECRET-TOKEN" not in result.stdout + result.stderr
        assert f"{SITE}/collections/black-rose/" in result.stdout

    def test_missing_marker_fails(self, tmp_path):
        routes = [
            r if r[0] != "/collections/love-hurts/" else (r[0], "200", "wrong page", "")
            for r in _v2_routes()
        ]
        result, _ = run_shimmed(
            tmp_path,
            routes,
            "--url",
            SITE,
            "--theme",
            "skyyrose-flagship-2",
        )
        assert result.returncode == 1
        assert "Collection: Love Hurts: Content marker 'Love Hurts' not found" in result.stdout

    def test_unknown_text_domain_refuses(self, tmp_path):
        routes = [
            ("/wp-content/themes/other/style.css", "200", style_css("Other", "other-theme"), "")
        ]
        result, env = run_shimmed(tmp_path, routes, "--url", SITE, "--theme", "other")
        assert result.returncode == 1
        assert "unrecognised text domain 'other-theme'" in result.stdout
        assert len(fetched_urls(env)) == 1  # no page was guessed at

    def test_style_css_without_text_domain_refuses_with_reason(self, tmp_path):
        # pipefail + grep no-match must not kill the script before it can say why.
        routes = [
            (
                "/wp-content/themes/skyyrose-flagship-2/style.css",
                "200",
                "/*\nTheme Name: SkyyRose Flagship 2\n*/\n",
                "",
            )
        ]
        result, env = run_shimmed(tmp_path, routes, "--url", SITE, "--theme", "skyyrose-flagship-2")
        assert result.returncode == 1
        assert "unrecognised text domain '<none>'" in result.stdout
        assert len(fetched_urls(env)) == 1

    def test_unreadable_style_css_refuses(self, tmp_path):
        result, env = run_shimmed(tmp_path, [], "--url", SITE, "--theme", "skyyrose-flagship-2")
        assert result.returncode == 1
        assert "Live theme style.css unreadable (HTTP 404)" in result.stdout
        assert len(fetched_urls(env)) == 1

    def test_curl_failure_refuses(self, tmp_path):
        routes = [("/wp-content/themes/skyyrose-flagship-2/style.css", "000", "", "")]
        result, _ = run_shimmed(tmp_path, routes, "--url", SITE, "--theme", "skyyrose-flagship-2")
        assert result.returncode == 1
        assert "unreadable (HTTP 000)" in result.stdout


class TestShellcheck:
    """Test 8: shellcheck passes on verify-deploy.sh."""

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


class TestListMode:
    """Test 9: --list exits 0 and prints health check list without HTTP requests."""

    def test_list_exits_zero(self):
        result = run_script("--list")
        assert result.returncode == 0

    def test_list_prints_pages(self):
        result = run_script("--list")
        output = result.stdout
        assert "Homepage" in output
        assert "REST API" in output
        assert "Black Rose" in output
        assert "Love Hurts" in output
        assert "Signature" in output
        assert "About" in output

    def test_list_shows_six_entries(self):
        """List mode should show exactly 6 health check entries."""
        result = run_script("--list")
        lines = [
            line
            for line in result.stdout.strip().splitlines()
            if line.strip() and not line.startswith("=") and "Health" not in line
        ]
        # At least 6 entries (one per health check)
        assert len(lines) >= 6
