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
THEME = f"{HOST}/wp-content/themes/skyyrose-flagship-2"
JS = b"console.log('theme');"
CSS = b".a{color:red}.b{background:url(../img/x.webp)}"


def sha12(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]


def page(*tags: str) -> bytes:
    return ("<html><head>" + "".join(tags) + "</head><body></body></html>").encode()


def script(rel: str, ver: str) -> str:
    return f"<script src='{THEME}/{rel}?ver={ver}' id='x'></script>"


class Repo:
    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "assets/js").mkdir(parents=True)
        (self.root / "assets/css").mkdir(parents=True)
        (self.root / "assets/js/theme.min.js").write_bytes(JS)
        (self.root / "assets/css/theme.min.css").write_bytes(CSS)

    def close(self) -> None:
        self.tmp.cleanup()


class ParityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Repo()
        self.site: dict[str, tuple[int, bytes]] = {}

    def tearDown(self) -> None:
        self.repo.close()

    def fetch(self, url: str) -> tuple[int, bytes]:
        # A real server ignores ?cb= / ?ver= queries; Boost bundles are keyed by their ?? path.
        base = url if "/_jb_static/" in url else url.split("?")[0]
        if base not in self.site:
            return 404, b""
        return self.site[base]

    def run_pages(self, *pages: str, rea=None):
        return vp.verify(
            HOST, list(pages), self.repo.root, "skyyrose-flagship-2", self.fetch, rea_runner=rea
        )

    def test_matching_script_passes(self) -> None:
        self.site[f"{HOST}/"] = (200, page(script("assets/js/theme.min.js", f"2.5.2-{sha12(JS)}")))
        self.site[f"{THEME}/assets/js/theme.min.js"] = (200, JS)
        report = self.run_pages("/")
        self.assertEqual(report["status"], "PASS", report)
        self.assertEqual(report["verified"][0]["asset"], "assets/js/theme.min.js")

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
        self.site[f"{HOST}/"] = (200, page(script("assets/js/theme.min.js", "2.5.2-000000000000")))
        self.site[f"{THEME}/assets/js/theme.min.js"] = (200, JS)
        report = self.run_pages("/")
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("?ver= hash", report["findings"][0]["detail"])

    def test_asset_missing_from_repo_is_finding(self) -> None:
        self.site[f"{HOST}/"] = (200, page(script("assets/js/gone.min.js", "2.5.2")))
        self.site[f"{THEME}/assets/js/gone.min.js"] = (200, b"x")
        report = self.run_pages("/")
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("not in repo", report["findings"][0]["detail"])

    def test_non_200_page_is_incomplete_not_pass(self) -> None:
        report = self.run_pages("/missing/")
        self.assertEqual(report["status"], "INCOMPLETE")

    def test_page_without_theme_assets_is_incomplete(self) -> None:
        self.site[f"{HOST}/"] = (200, page("<script src='/wp-includes/js/jquery.js'></script>"))
        report = self.run_pages("/")
        self.assertEqual(report["status"], "INCOMPLETE")

    def test_concatenated_css_verified_by_containment(self) -> None:
        bundle = b"/*other*/" + CSS.replace(b"../img", f"{THEME}/assets/img".encode())
        self.site[f"{HOST}/"] = (
            200,
            page(
                f"<link rel='stylesheet' href='{HOST}/_jb_static/??abc' />",
                script("assets/js/theme.min.js", f"2.5.2-{sha12(JS)}"),
            ),
        )
        self.site[f"{THEME}/assets/js/theme.min.js"] = (200, JS)
        self.site[f"{HOST}/_jb_static/??abc"] = (200, bundle)
        report = self.run_pages("/")
        self.assertEqual(report["status"], "PASS", report)
        css = [v for v in report["verified"] if v["asset"] == "assets/css/theme.min.css"]
        self.assertEqual(css[0]["method"], "concat-url-normalized")

    def test_font_cdn_and_cut_family_are_policy_findings(self) -> None:
        self.site[f"{HOST}/"] = (
            200,
            page(
                "<link rel='stylesheet' href='https://fonts-api.wp.com/css?family=Playfair+Display:400' />",
                script("assets/js/theme.min.js", f"2.5.2-{sha12(JS)}"),
            ),
        )
        self.site[f"{THEME}/assets/js/theme.min.js"] = (200, JS)
        report = self.run_pages("/")
        self.assertEqual(report["status"], "FAIL")
        kinds = {f["kind"] for f in report["findings"]}
        self.assertEqual(kinds, {"font-cdn", "cut-font"})

    def test_rea_executed_script_drift_is_finding(self) -> None:
        self.site[f"{HOST}/"] = (200, page(script("assets/js/theme.min.js", f"2.5.2-{sha12(JS)}")))
        self.site[f"{THEME}/assets/js/theme.min.js"] = (200, JS)

        def rea(url: str) -> dict:
            return {
                "normalized_result": {
                    "completeness": {"status": "complete"},
                    "observations": {
                        "chunks": {
                            "nodes": [
                                {
                                    "url": f"{THEME}/assets/js/theme.min.js?ver=2.5.0",
                                    "artifact_sha256": hashlib.sha256(b"older").hexdigest(),
                                }
                            ]
                        }
                    },
                }
            }

        report = self.run_pages("/", rea=rea)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["findings"][0]["kind"], "runtime-drift")

    def test_rea_error_is_incomplete_never_pass(self) -> None:
        self.site[f"{HOST}/"] = (200, page(script("assets/js/theme.min.js", f"2.5.2-{sha12(JS)}")))
        self.site[f"{THEME}/assets/js/theme.min.js"] = (200, JS)
        report = self.run_pages("/", rea=lambda url: {"error": "Browser observation failed"})
        self.assertEqual(report["status"], "INCOMPLETE")

    def test_rea_capture_with_no_theme_scripts_is_incomplete(self) -> None:
        self.site[f"{HOST}/"] = (200, page(script("assets/js/theme.min.js", f"2.5.2-{sha12(JS)}")))
        self.site[f"{THEME}/assets/js/theme.min.js"] = (200, JS)
        empty = {
            "normalized_result": {
                "completeness": {"status": "complete"},
                "observations": {"chunks": {"nodes": []}},
            }
        }
        report = self.run_pages("/", rea=lambda url: empty)
        self.assertEqual(report["status"], "INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
