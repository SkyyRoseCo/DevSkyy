#!/usr/bin/env python3
"""Offline tests for scripts/verify-live-parity.py. Run: python3 scripts/test-verify-live-parity.py

fetch() and the REA runner are replaced with in-memory fakes, so nothing touches the network.
"""

from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "verify_live_parity", Path(__file__).with_name("verify-live-parity.py")
)
vp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vp)

HOST = "https://skyyrose.co"
FOLDER = "skyyrose-flagship-2"
THEME = f"{HOST}/wp-content/themes/{FOLDER}"
JS = b"console.log('theme');"
OTHER_JS = b"console.log('other module');"
CSS = b'.sr2-a{color:red}.sr2-b{background:url("../img/x.webp")}'
# What Jetpack Boost emits for CSS: url() made root-relative to the stylesheet, quotes dropped.
BOOSTED_CSS = CSS.replace(
    b'url("../img/x.webp")', f"url(/wp-content/themes/{FOLDER}/assets/css/../img/x.webp)".encode()
)
CRITICAL = b".sr2-hero{background:url(__SKYYROSE2_ASSETS__/img/h.webp)}"
HERO_JS = b"window.sr2Hero=1;"


def sha12(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]


def page(*tags: str) -> bytes:
    return ("<html><head>" + "".join(tags) + "</head><body></body></html>").encode()


def script(rel: str, ver: str) -> str:
    return f"<script src='{THEME}/{rel}?ver={ver}' id='x'></script>"


THEME_JS_TAG = script("assets/js/theme.min.js", f"2.5.2-{sha12(JS)}")


def bundle_link(key: str = "abc") -> str:
    return f"<link rel='stylesheet' href='{HOST}/_jb_static/??{key}' />"


def rea_nodes(*nodes: dict) -> dict:
    return {
        "normalized_result": {
            "completeness": {"status": "complete"},
            "observations": {"chunks": {"nodes": list(nodes)}},
        }
    }


class Repo:
    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel, data in {
            "assets/js/theme.min.js": JS,
            "assets/js/other.min.js": OTHER_JS,
            "assets/js/visual-recovery.min.js": HERO_JS,
            "assets/css/theme.min.css": CSS,
            "assets/css/critical/home.min.css": CRITICAL,
        }.items():
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_bytes(data)

    def close(self) -> None:
        self.tmp.cleanup()


class ParityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Repo()
        self.site: dict[str, tuple[int, bytes]] = {}
        self.queries: list[str] = []

    def tearDown(self) -> None:
        self.repo.close()

    def fetch(self, url: str) -> tuple[int, bytes]:
        # A real server ignores ?ver= queries; Boost bundles are keyed by their ?? path.
        self.queries.append(url)
        base = url if "/_jb_static/" in url else url.split("?")[0]
        return self.site.get(base, (404, b""))

    def run_pages(self, *pages: str, rea=None, inline=None):
        return vp.verify(
            HOST,
            list(pages),
            self.repo.root,
            FOLDER,
            self.fetch,
            rea_runner=rea,
            inline_required=inline,
        )

    def home(self, *tags: str) -> None:
        self.site[f"{HOST}/"] = (200, page(*tags))
        self.site[f"{THEME}/assets/js/theme.min.js"] = (200, JS)

    def kinds(self, report: dict) -> set[str]:
        return {f["kind"] for f in report["findings"]}

    # --- served bytes and ?ver= ---

    def test_matching_script_passes(self) -> None:
        self.home(THEME_JS_TAG)
        report = self.run_pages("/")
        self.assertEqual(report["status"], "PASS", report)
        self.assertEqual(report["verified"][0]["asset"], "assets/js/theme.min.js")

    def test_page_is_fetched_bare_like_a_visitor(self) -> None:
        self.home(THEME_JS_TAG)
        self.run_pages("/")
        self.assertIn(f"{HOST}/", self.queries)
        self.assertFalse(any("cb=" in q for q in self.queries))

    def test_served_bytes_differ_from_repo_is_drift(self) -> None:
        stale = b"console.log('old');"
        self.site[f"{HOST}/"] = (
            200,
            page(script("assets/js/theme.min.js", f"2.5.2-{sha12(stale)}")),
        )
        self.site[f"{THEME}/assets/js/theme.min.js"] = (200, stale)
        report = self.run_pages("/")
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("served bytes differ from repo", report["findings"][0]["detail"])

    def test_ver_hash_not_matching_served_bytes_is_finding(self) -> None:
        self.home(script("assets/js/theme.min.js", "2.5.2-000000000000"))
        report = self.run_pages("/")
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("?ver= hash", report["findings"][0]["detail"])

    def test_unhashed_ver_on_hash_sized_asset_is_drift(self) -> None:
        self.home(script("assets/js/theme.min.js", "2.5.3"))
        report = self.run_pages("/")
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("no content hash", report["findings"][0]["detail"])

    def test_every_distinct_query_for_a_path_is_checked(self) -> None:
        self.home(script("assets/js/theme.min.js", "2.5.0-000000000000"), THEME_JS_TAG)
        report = self.run_pages("/")
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(
            len([v for v in report["verified"] if v["asset"] == "assets/js/theme.min.js"]), 1
        )

    def test_asset_missing_from_repo_is_finding(self) -> None:
        self.home(script("assets/js/gone.min.js", "2.5.2"))
        self.site[f"{THEME}/assets/js/gone.min.js"] = (200, b"x")
        report = self.run_pages("/")
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("not in repo", report["findings"][0]["detail"])

    # --- pages that cannot be verified ---

    def test_non_200_page_is_incomplete_not_pass(self) -> None:
        self.assertEqual(self.run_pages("/missing/")["status"], "INCOMPLETE")

    def test_redirected_page_is_incomplete(self) -> None:
        self.site[f"{HOST}/product/gone/"] = (301, b"")
        self.assertEqual(self.run_pages("/product/gone/")["status"], "INCOMPLETE")

    def test_page_without_theme_assets_is_incomplete(self) -> None:
        self.site[f"{HOST}/"] = (200, page("<script src='/wp-includes/js/jquery.js'></script>"))
        self.assertEqual(self.run_pages("/")["status"], "INCOMPLETE")

    # --- Jetpack Boost CSS bundles ---

    def test_boost_rewritten_css_is_verified_exactly(self) -> None:
        self.home(bundle_link(), THEME_JS_TAG)
        self.site[f"{HOST}/_jb_static/??abc"] = (200, b"/*other*/" + BOOSTED_CSS)
        report = self.run_pages("/")
        self.assertEqual(report["status"], "PASS", report)
        css = [v for v in report["verified"] if v["asset"] == "assets/css/theme.min.css"]
        self.assertEqual(css[0]["method"], "concat-boost-url")

    def test_bundle_with_a_different_url_target_is_drift(self) -> None:
        self.home(bundle_link(), THEME_JS_TAG)
        swapped = BOOSTED_CSS.replace(b"x.webp", b"y.webp")
        self.site[f"{HOST}/_jb_static/??abc"] = (200, swapped)
        report = self.run_pages("/")
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("unmatched-theme-css", self.kinds(report))

    def test_stale_theme_css_beside_matching_css_is_drift(self) -> None:
        self.home(bundle_link(), THEME_JS_TAG)
        self.site[f"{HOST}/_jb_static/??abc"] = (200, BOOSTED_CSS + b".sr2-old{color:blue}")
        report = self.run_pages("/")
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("unmatched-theme-css", self.kinds(report))

    def test_js_bundle_with_exact_repo_scripts_passes(self) -> None:
        self.home(
            f"<script type='text/javascript' src='{HOST}/_jb_static/??def'></script>", THEME_JS_TAG
        )
        self.site[f"{HOST}/_jb_static/??def"] = (200, b"/*wp*/" + OTHER_JS + b";" + JS)
        report = self.run_pages("/")
        self.assertEqual(report["status"], "PASS", report)
        bundled = {v["asset"] for v in report["verified"] if v["method"] == "concat-exact"}
        self.assertEqual(bundled, {"assets/js/other.min.js", "assets/js/theme.min.js"})

    def test_stale_theme_js_in_bundle_is_drift(self) -> None:
        self.home(
            f"<script type='text/javascript' src='{HOST}/_jb_static/??def'></script>", THEME_JS_TAG
        )
        stale = b'document.querySelector(".sr2-search-dialog__old")'
        self.site[f"{HOST}/_jb_static/??def"] = (200, JS + stale)
        report = self.run_pages("/")
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("unmatched-theme-js", self.kinds(report))

    # --- homepage inline blocks ---

    def inline_home(self, css: bytes, js: bytes) -> None:
        self.home(
            f'<style id="skyyrose2-critical-home">{css.decode()}</style>',
            f'<script id="skyyrose2-visual-recovery-early" data-jetpack-boost="ignore">{js.decode()}</script>',
            THEME_JS_TAG,
        )

    def test_inline_critical_blocks_matching_repo_pass(self) -> None:
        live_css = CRITICAL.replace(b"__SKYYROSE2_ASSETS__", f"{THEME}/assets".encode())
        self.inline_home(live_css, HERO_JS)
        report = self.run_pages("/", inline=vp.HOME_INLINE)
        self.assertEqual(report["status"], "PASS", report)
        self.assertEqual({v["method"] for v in report["verified"]} >= {"inline-exact"}, True)

    def test_stale_inline_hero_script_is_drift(self) -> None:
        live_css = CRITICAL.replace(b"__SKYYROSE2_ASSETS__", f"{THEME}/assets".encode())
        self.inline_home(live_css, b"window.sr2Hero=0;")
        report = self.run_pages("/", inline=vp.HOME_INLINE)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("inline-drift", self.kinds(report))

    def test_missing_required_inline_block_is_incomplete(self) -> None:
        self.home(THEME_JS_TAG)
        self.assertEqual(self.run_pages("/", inline=vp.HOME_INLINE)["status"], "INCOMPLETE")

    # --- font policy ---

    def test_font_cdn_and_cut_family_are_policy_findings(self) -> None:
        self.home(
            "<link rel='stylesheet' href='https://fonts-api.wp.com/css?family=Playfair+Display:400' />",
            THEME_JS_TAG,
        )
        report = self.run_pages("/")
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(self.kinds(report), {"font-cdn", "cut-font"})

    def test_cut_family_in_inline_css_is_policy_finding(self) -> None:
        self.home('<style>h1{font-family:"Playfair Display",serif}</style>', THEME_JS_TAG)
        report = self.run_pages("/")
        self.assertEqual(self.kinds(report), {"cut-font"})

    def test_cut_family_in_bundle_css_is_policy_finding(self) -> None:
        self.home(bundle_link(), THEME_JS_TAG)
        self.site[f"{HOST}/_jb_static/??abc"] = (
            200,
            BOOSTED_CSS + b".plugin-x{font-family:'Bebas Neue',sans-serif}",
        )
        self.assertEqual(self.kinds(self.run_pages("/")), {"cut-font"})

    # --- REA runtime evidence ---

    def test_rea_executed_script_drift_is_finding(self) -> None:
        self.home(THEME_JS_TAG)
        node = {
            "url": f"{THEME}/assets/js/theme.min.js?ver=2.5.0",
            "artifact_sha256": hashlib.sha256(b"older").hexdigest(),
        }
        report = self.run_pages("/", rea=lambda url: rea_nodes(node))
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["findings"][0]["kind"], "runtime-drift")

    def test_rea_script_serving_another_modules_bytes_is_drift(self) -> None:
        self.home(THEME_JS_TAG)
        node = {
            "url": f"{THEME}/assets/js/theme.min.js",
            "artifact_sha256": hashlib.sha256(OTHER_JS).hexdigest(),
        }
        report = self.run_pages("/", rea=lambda url: rea_nodes(node))
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("runtime-drift", self.kinds(report))

    def test_rea_error_is_incomplete_never_pass(self) -> None:
        self.home(THEME_JS_TAG)
        report = self.run_pages("/", rea=lambda url: {"error": "Browser observation failed"})
        self.assertEqual(report["status"], "INCOMPLETE")

    def test_rea_runner_exception_is_incomplete_never_traceback(self) -> None:
        self.home(THEME_JS_TAG)

        def boom(url: str) -> dict:
            raise TimeoutError("CDP endpoint unreachable")

        report = self.run_pages("/", rea=boom)
        self.assertEqual(report["status"], "INCOMPLETE")
        self.assertIn("CDP endpoint unreachable", report["incomplete"][0])

    def test_rea_capture_with_no_theme_scripts_is_incomplete(self) -> None:
        self.home(THEME_JS_TAG)
        self.assertEqual(self.run_pages("/", rea=lambda url: rea_nodes())["status"], "INCOMPLETE")


class FetchTests(unittest.TestCase):
    def test_truncated_body_is_reported_as_unreachable(self) -> None:
        import http.client
        from unittest import mock

        class Truncated:
            status = 200

            def read(self) -> bytes:
                raise http.client.IncompleteRead(b"partial", 100)

            def __enter__(self):
                return self

            def __exit__(self, *exc) -> None:
                return None

        with mock.patch.object(vp.OPENER, "open", return_value=Truncated()):
            self.assertEqual(vp.fetch("https://skyyrose.co/"), (0, b""))


if __name__ == "__main__":
    unittest.main()
