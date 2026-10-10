#!/usr/bin/env python3
"""Offline tests for scripts/validate-sitemap.py. Run: python3 scripts/test-validate-sitemap.py

fetch() is replaced with an in-memory site, so nothing touches the network.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "validate_sitemap", Path(__file__).with_name("validate-sitemap.py")
)
vs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vs)

SM = "http://www.sitemaps.org/schemas/sitemap/0.9"
IMG = "http://www.google.com/schemas/sitemap-image/1.1"
HOST = "https://skyyrose.co"


def urlset(*locs: str, image: bool = False) -> bytes:
    extra = f' xmlns:image="{IMG}"' if image else ""
    body = "".join(
        f"<url><loc>{loc}</loc>"
        + (
            "<image:image><image:loc>https://skyyrose.co/a.webp</image:loc></image:image>"
            if image
            else ""
        )
        + "</url>"
        for loc in locs
    )
    return f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="{SM}"{extra}>{body}</urlset>'.encode()


def index(*locs: str) -> bytes:
    body = "".join(f"<sitemap><loc>{loc}</loc></sitemap>" for loc in locs)
    return f'<?xml version="1.0" encoding="UTF-8"?><sitemapindex xmlns="{SM}">{body}</sitemapindex>'.encode()


def page(url: str, head: str = "") -> bytes:
    return f"<html><head>{head or f'<link rel=canonical href={chr(34)}{url}{chr(34)}>'}</head></html>".encode()


class Site:
    def __init__(self, files: dict[str, tuple[int, bytes]]):
        self.files = files
        self.requested: list[str] = []

    def fetch(self, url: str, cache_bust: bool):
        self.requested.append(url)
        status, body = self.files.get(url, (404, b""))
        return status, {}, body


class ValidatorTests(unittest.TestCase):
    def run_site(self, files, root=f"{HOST}/sitemap.xml", max_urls=2000):
        site = Site(files)
        vs.fetch = site.fetch
        failures, listed, probed = vs.validate(root, max_urls, sleep=0)
        return site, failures, listed, probed

    def test_same_loc_allowed_in_page_and_image_sitemaps(self):
        a = f"{HOST}/a/"
        files = {
            f"{HOST}/sitemap.xml": (200, index(f"{HOST}/s1.xml", f"{HOST}/s1-image.xml")),
            f"{HOST}/s1.xml": (200, urlset(a)),
            f"{HOST}/s1-image.xml": (200, urlset(a, image=True)),
            a: (200, page(a)),
        }
        _, failures, listed, probed = self.run_site(files)
        self.assertEqual([], failures)
        self.assertEqual((1, 1), (listed, probed))

    def test_duplicate_within_one_kind_fails(self):
        a = f"{HOST}/a/"
        files = {
            f"{HOST}/sitemap.xml": (200, urlset(a, a)),
            a: (200, page(a)),
        }
        _, failures, _, _ = self.run_site(files)
        self.assertTrue(any("listed more than once in the page" in f for f in failures))

    def test_truncated_probe_is_not_a_pass(self):
        urls = [f"{HOST}/p{i}/" for i in range(3)]
        files = {f"{HOST}/sitemap.xml": (200, urlset(*urls))}
        files.update({u: (200, page(u)) for u in urls})
        _, failures, listed, probed = self.run_site(files, max_urls=2)
        self.assertEqual([], failures)
        self.assertEqual((3, 2), (listed, probed))
        self.assertLess(probed, listed)  # main() exits 2 / prints INCOMPLETE for this case

    def test_main_exit_codes(self):
        urls = [f"{HOST}/p{i}/" for i in range(3)]
        files = {f"{HOST}/sitemap.xml": (200, urlset(*urls))}
        files.update({u: (200, page(u)) for u in urls})
        vs.fetch = Site(files).fetch
        vs.SLEEP = 0
        import contextlib
        import io
        import sys

        def run(*argv):
            out = io.StringIO()
            old = sys.argv
            sys.argv = ["validate-sitemap.py", *argv]
            real_validate = vs.validate
            vs.validate = lambda s, m, sleep=0: real_validate(s, m, 0)
            try:
                with contextlib.redirect_stdout(out):
                    return vs.main(), out.getvalue()
            finally:
                vs.validate = real_validate
                sys.argv = old

        code, text = run(f"{HOST}/sitemap.xml", "--max-urls", "2")
        self.assertEqual(2, code)
        self.assertIn("INCOMPLETE", text)
        self.assertNotIn("PASS", text)
        code, text = run(f"{HOST}/sitemap.xml", "--max-urls", "3")
        self.assertEqual(0, code)
        self.assertIn("PASS", text)

    def test_googlebot_meta_noindex_detected(self):
        a = f"{HOST}/a/"
        for name in ("googlebot", "robots"):
            head = (
                f'<meta name="{name}" content="noindex, follow"><link rel="canonical" href="{a}">'
            )
            files = {f"{HOST}/sitemap.xml": (200, urlset(a)), a: (200, page(a, head))}
            _, failures, _, _ = self.run_site(files)
            self.assertTrue(any(f"{name} meta noindex" in f for f in failures), name)

    def test_canonical_attribute_order_and_quotes(self):
        a = f"{HOST}/a/"
        for head, expect_fail in (
            (f'<link href="{HOST}/other/" rel="canonical">', True),
            (f"<link href='{HOST}/other/' rel='canonical'>", True),
            (f'<link href="{a}" rel="canonical">', False),
            (f'<link rel="canonical" href="{a}?utm=x">', False),
            ('<link href="https://x.test/o/" rel="stylesheet">', False),
        ):
            files = {f"{HOST}/sitemap.xml": (200, urlset(a)), a: (200, page(a, head))}
            _, failures, _, _ = self.run_site(files)
            self.assertEqual(
                expect_fail, any("canonical points elsewhere" in f for f in failures), head
            )

    def test_foreign_child_sitemap_rejected_and_not_fetched(self):
        foreign = "https://evil.test/sitemap-child.xml"
        files = {
            f"{HOST}/sitemap.xml": (200, index(foreign)),
            foreign: (200, urlset("https://evil.test/x/")),
        }
        site, failures, listed, _ = self.run_site(files)
        self.assertNotIn(foreign, site.requested)
        self.assertEqual(0, listed)
        self.assertTrue(
            any("child sitemap is not an https URL on skyyrose.co" in f for f in failures)
        )

    def test_child_urls_keep_root_host(self):
        files = {
            f"{HOST}/sitemap.xml": (200, index(f"{HOST}/s1.xml")),
            f"{HOST}/s1.xml": (200, urlset("https://other.test/a/")),
        }
        _, failures, _, _ = self.run_site(files)
        self.assertTrue(any("not an absolute https URL on skyyrose.co" in f for f in failures))


if __name__ == "__main__":
    unittest.main()
