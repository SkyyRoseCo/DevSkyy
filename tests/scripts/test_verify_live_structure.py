"""Tests for scripts/verify_live_structure.py -- target/slug resolution and the
Text-Domain-keyed page registries. Fetchers are fakes; nothing touches the
network."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify_live_structure.py"


@pytest.fixture(scope="module")
def vls():
    spec = importlib.util.spec_from_file_location("verify_live_structure", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    # dataclasses resolve cls.__module__ through sys.modules at class-creation
    # time, so the module must be registered before it executes.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, status=200, body=b"", counts=None):
        self.status = status
        self.body = body
        self.encoding = "utf-8"
        self._counts = counts or {}

    def css(self, selector):
        return [object()] * self._counts.get(selector, 0)


class FakeFetcher:
    def __init__(self, responses: dict[str, FakeResponse], error: Exception | None = None):
        self.responses = responses
        self.error = error
        self.calls: list[str] = []

    def get(self, url, timeout=None):
        self.calls.append(url)
        if self.error is not None:
            raise self.error
        path = "/" + url.split("://", 1)[1].split("/", 1)[1].split("?", 1)[0]
        return self.responses.get(path, FakeResponse(status=404))


V2_STYLE = (
    b"/*\nTheme Name: SkyyRose Flagship 2\nVersion: 2.4.4\nText Domain: skyyrose-flagship-2\n*/\n"
)
V1_STYLE = b"/*\nTheme Name:          SkyyRose\nVersion:             2.2.4\nText Domain:         skyyrose\n*/\n"


class TestParseTextDomain:
    def test_v1_padded_header(self, vls):
        assert vls.parse_text_domain(V1_STYLE.decode()) == "skyyrose"

    def test_v2_header(self, vls):
        assert vls.parse_text_domain(V2_STYLE.decode()) == "skyyrose-flagship-2"

    def test_missing_header(self, vls):
        assert vls.parse_text_domain("/*\nTheme Name: X\n*/") is None


class TestResolution:
    def test_base_url_prefers_cli(self, vls):
        assert (
            vls.resolve_base_url("https://a.example/?x=1", {"PUBLIC_URL": "https://b"})
            == "https://a.example"
        )

    def test_base_url_env_fallbacks(self, vls):
        assert vls.resolve_base_url(None, {"PUBLIC_URL": "https://p/"}) == "https://p"
        assert vls.resolve_base_url(None, {"WORDPRESS_URL": "https://w"}) == "https://w"

    def test_base_url_has_no_literal_default(self, vls):
        assert vls.resolve_base_url(None, {}) is None
        assert (
            "skyyrose.co"
            not in SCRIPT_PATH.read_text().split("def resolve_base_url")[1].split("def ")[0]
        )

    def test_theme_slug_fallbacks(self, vls):
        assert vls.resolve_theme_slug("x", {"THEME_SLUG": "y"}) == "x"
        assert vls.resolve_theme_slug(None, {"THEME_SLUG": "y"}) == "y"
        assert (
            vls.resolve_theme_slug(
                None, {"WP_THEME_PATH": "/h/wp-content/themes/skyyrose-flagship-2/"}
            )
            == "skyyrose-flagship-2"
        )
        assert vls.resolve_theme_slug(None, {}) is None


class TestRegistries:
    def test_v1_registry_routes(self, vls):
        reg = vls.select_registry("skyyrose", "skyyrose-flagship")
        assert reg.pages["black-rose"].path == "/collection-black-rose/"
        assert reg.pages["experience-black-rose"].path == "/experience-black-rose/"
        assert any(a.selector == "a.skip-link" for a in reg.global_assertions)
        assert any("skyyrose-flagship" in a.selector for a in reg.pages["home"].assertions)

    def test_v2_registry_routes(self, vls):
        reg = vls.select_registry("skyyrose-flagship-2", "skyyrose-flagship-2")
        assert reg.pages["black-rose"].path == "/collections/black-rose/"
        assert reg.pages["world-black-rose"].path == "/worlds/black-rose/"
        assert reg.pages["kids-capsule"].path == "/collections/kids-capsule/"
        assert reg.pages["about"].path == "/about/"
        assert reg.pages["preorder"].path == "/pre-order/"
        assert not any(a.selector == "a.skip-link" for a in reg.global_assertions)
        assert any(a.selector == "[data-skyyrose-error]" for a in reg.global_assertions)
        assert reg.pricing_checks == ()
        selectors = [a.selector for a in reg.pages["black-rose"].assertions]
        assert "main#primary.sr2-collection-world[data-collection='black-rose']" in selectors
        assert "link[href*='skyyrose-flagship-2']" in selectors

    def test_unknown_text_domain_raises(self, vls):
        with pytest.raises(ValueError, match="unrecognised text domain"):
            vls.select_registry("twentytwentyfive", "x")

    def test_theme_css_assertion_uses_slug(self, vls):
        assert vls.theme_css_assertion("abc").selector == "link[href*='abc']"


class TestLiveTextDomain:
    def test_reads_domain_from_live_style(self, vls):
        fetcher = FakeFetcher(
            {"/wp-content/themes/skyyrose-flagship-2/style.css": FakeResponse(200, V2_STYLE)}
        )
        domain, err = vls.fetch_live_text_domain(
            fetcher, "https://s.example", "skyyrose-flagship-2", 5, True
        )
        assert (domain, err) == ("skyyrose-flagship-2", None)
        assert fetcher.calls[0].startswith(
            "https://s.example/wp-content/themes/skyyrose-flagship-2/style.css?deploy_verify="
        )

    def test_404_fails_closed(self, vls):
        fetcher = FakeFetcher({})
        domain, err = vls.fetch_live_text_domain(fetcher, "https://s.example", "nope", 5, False)
        assert domain is None
        assert "HTTP 404" in err

    def test_unparseable_fails_closed(self, vls):
        fetcher = FakeFetcher(
            {"/wp-content/themes/t/style.css": FakeResponse(200, b"/* nothing */")}
        )
        domain, err = vls.fetch_live_text_domain(fetcher, "https://s.example", "t", 5, False)
        assert domain is None
        assert "no parseable Text Domain" in err

    def test_transport_error_fails_closed(self, vls, monkeypatch):
        monkeypatch.setattr(vls, "FETCH_RETRY_BACKOFF_SECONDS", 0)
        fetcher = FakeFetcher({}, error=OSError("boom"))
        domain, err = vls.fetch_live_text_domain(fetcher, "https://s.example", "t", 5, False)
        assert domain is None
        assert "fetch failed" in err


class TestCheckPage:
    def test_v2_collection_page_passes_with_markers(self, vls):
        reg = vls.select_registry("skyyrose-flagship-2", "skyyrose-flagship-2")
        page = reg.pages["black-rose"]
        counts = {
            "main#primary.sr2-collection-world[data-collection='black-rose']": 1,
            "link[href*='skyyrose-flagship-2']": 1,
            "[tabindex='-1']": 8,
            "img[loading='lazy']": 22,
        }
        fetcher = FakeFetcher({"/collections/black-rose/": FakeResponse(200, b"", counts)})
        report = vls.check_page(fetcher, page, reg, "https://s.example", 5, False)
        assert report.passed, [r.assertion.label for r in report.results if not r.passed]

    def test_v2_collection_page_fails_without_world_main(self, vls):
        reg = vls.select_registry("skyyrose-flagship-2", "skyyrose-flagship-2")
        page = reg.pages["black-rose"]
        counts = {
            "link[href*='skyyrose-flagship-2']": 1,
            "[tabindex='-1']": 1,
            "img[loading='lazy']": 1,
        }
        fetcher = FakeFetcher({"/collections/black-rose/": FakeResponse(200, b"", counts)})
        report = vls.check_page(fetcher, page, reg, "https://s.example", 5, False)
        assert not report.passed

    def test_error_beacon_fails_page(self, vls):
        reg = vls.select_registry("skyyrose-flagship-2", "skyyrose-flagship-2")
        page = reg.pages["about"]
        counts = {
            "main#primary.sr2-page--about": 1,
            "link[href*='skyyrose-flagship-2']": 1,
            "[tabindex='-1']": 1,
            "img[loading='lazy']": 1,
            "[data-skyyrose-error]": 1,
        }
        fetcher = FakeFetcher({"/about/": FakeResponse(200, b"", counts)})
        report = vls.check_page(fetcher, page, reg, "https://s.example", 5, False)
        assert not report.passed


class TestCli:
    def _run(self, *args, env_extra=None):
        env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("PUBLIC_URL", "WORDPRESS_URL", "THEME_SLUG", "WP_THEME_PATH")
        }
        env.update(env_extra or {})
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )

    def test_list_prints_both_registries(self):
        result = self._run("--list")
        assert result.returncode == 0
        assert "Registry for text domain: skyyrose\n" in result.stdout
        assert "Registry for text domain: skyyrose-flagship-2" in result.stdout
        assert "/collection-black-rose/" in result.stdout
        assert "/collections/black-rose/" in result.stdout

    def test_list_single_registry(self):
        result = self._run(
            "--list", "--text-domain", "skyyrose-flagship-2", "--theme-slug", "skyyrose-flagship-2"
        )
        assert result.returncode == 0
        assert "/collection-black-rose/" not in result.stdout
        assert (
            "link[href*='skyyrose-flagship-2']" not in result.stdout
        )  # labels, not selectors, are listed
        assert "(skyyrose-flagship-2 active)" in result.stdout

    def test_no_url_is_usage_error(self):
        result = self._run("--theme-slug", "x")
        assert result.returncode == 2
        assert "No target URL" in result.stderr

    def test_no_slug_is_usage_error(self):
        result = self._run("--url", "https://example.invalid")
        assert result.returncode == 2
        assert "No theme slug" in result.stderr

    def test_env_provides_url_and_slug(self):
        """With URL + slug from env the script gets past resolution; the next
        gate is the scrapling import (exit 3) or a fetch -- never a usage error."""
        result = self._run(
            "--text-domain",
            "skyyrose",
            env_extra={
                "PUBLIC_URL": "https://127.0.0.1:9/",
                "WP_THEME_PATH": "/x/skyyrose-flagship",
            },
        )
        assert result.returncode in (2, 3)
        assert "No target URL" not in result.stderr
        assert "No theme slug" not in result.stderr
