#!/usr/bin/env python3
"""Render real Home chapters through the production gate, including media loss.

Usage: python3 tools/v2-runtime/test-home-editorial-media.py [theme-directory]
WordPress request APIs are stubbed by the existing collection renderer. Theme
resolvers, inventory pins, file hashes, output gate and templates are real.
Negative cases modify only a disposable copy; the supplied theme is read-only.
"""

import errno
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser

THEME = (
    Path(sys.argv[1]).resolve()
    if len(sys.argv) > 1
    else Path(__file__).resolve().parents[2] / "wordpress-theme/skyyrose-flagship-2"
)
RENDERER = Path(__file__).with_name("render-collection-imagery.php")
SLUGS = ["signature", "black-rose", "love-hurts", "kids-capsule"]


class Chapters(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.chapters = {}
        self.current = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section" and "sr2-chapter" in attrs.get("class", "").split():
            self.current = []
            self.chapters[attrs["data-collection"]] = self.current
        if self.current is not None:
            self.current.append((tag, attrs))

    def handle_endtag(self, tag):
        if tag == "section":
            self.current = None


def render(theme):
    # This fixture uses core PHP only; exclude host debugger/profiler extensions.
    with tempfile.TemporaryFile(mode="w+") as output, tempfile.TemporaryFile(mode="w+") as errors:
        subprocess.run(
            ["php", "-n", str(RENDERER), "home", str(theme)],
            stdout=output,
            stderr=errors,
            check=True,
            timeout=30,
        )
        output.seek(0)
        errors.seek(0)
        html, stderr = output.read(), errors.read()
    if stderr or any(word in html for word in ["Fatal error:", "Warning:", "Deprecated:"]):
        raise AssertionError(stderr + html)
    return Chapters(html).chapters


def tags(chapter, name):
    return [attrs for tag, attrs in chapter if tag == name]


class HomeEditorialMedia(unittest.TestCase):
    def assert_navigation(self, chapters):
        self.assertEqual(list(chapters), SLUGS)
        for slug, chapter in chapters.items():
            self.assertEqual(len(tags(chapter, "h2")), 1, slug)
            self.assertTrue(tags(chapter, "a"), slug)

    def test_current_release_media(self):
        chapters = render(THEME)
        self.assert_navigation(chapters)
        for slug, chapter in chapters.items():
            self.assertEqual(len(tags(chapter, "picture")), 1, slug)
            images = tags(chapter, "img")
            self.assertTrue(images and images[0].get("src"), slug)
            if slug == "kids-capsule":
                self.assertEqual(images[0].get("data-media-role"), "collection_hero")
                self.assertEqual(images[0].get("style"), "object-fit: contain")
                registry = json.loads(
                    (THEME / "data/product-presentation-registry.json").read_text()
                )
                self.assertEqual(
                    images[0].get("data-media-sku"),
                    registry["collections"][slug]["imagery"]["collection_hero"]["sku"],
                )
                self.assertFalse(tags(chapter, "video"))
                self.assertFalse(tags(chapter, "button"))
            else:
                prefix = f"assets/video/collection-heroes/approved/{slug}/cinema-20261008/"
                self.assertIn(prefix + "poster.webp?v=", images[0]["src"])
                self.assertEqual(len(tags(chapter, "video")), 1)
                video = tags(chapter, "video")[0]
                self.assertEqual(video["preload"], "none")
                self.assertNotIn("src", video)
                self.assertNotIn("autoplay", video)
                self.assertEqual(
                    [s["type"] for s in tags(chapter, "source")], ["video/webm", "video/mp4"]
                )
                for source in tags(chapter, "source"):
                    self.assertIn(prefix + "hero.", source["data-src"])
                    self.assertNotIn("src", source)
                self.assertEqual(tags(chapter, "button")[0]["aria-controls"], video["id"])
            for tag, attrs in chapter:
                for name in ["src", "data-src"]:
                    if name not in attrs:
                        continue
                    url = attrs[name]
                    relative, sha = url.split("/skyyrose-flagship-2/", 1)[1].split("?v=")
                    self.assertEqual(
                        hashlib.sha256((THEME / relative).read_bytes()).hexdigest(), sha
                    )

    def test_missing_media_fails_closed_with_navigation(self):
        with tempfile.TemporaryDirectory(prefix="sr2-home-media-") as temp:
            fixture = Path(temp) / "theme"

            def copy_fixture(src, dst):
                # Tests only unlink assets; share immutable bytes without copying
                # the entire packaged film archive. Policy/config files are copied
                # independently because the inventory-negative case edits one.
                if "assets" in Path(src).relative_to(THEME).parts:
                    try:
                        return os.link(src, dst)
                    except OSError as error:
                        if error.errno != errno.EXDEV:
                            raise
                return shutil.copy2(src, dst)

            shutil.copytree(THEME, fixture, copy_function=copy_fixture)
            manifest = json.loads((fixture / "data/collection-hero-motion.json").read_text())
            webm = next(
                a["file"]
                for a in manifest["collections"]["signature"]["ai_motion"]["web"]
                if a["file"].endswith(".webm")
            )
            (fixture / webm).unlink()
            chapters = render(fixture)
            self.assert_navigation(chapters)
            signature = chapters["signature"]
            self.assertTrue(tags(signature, "img"))
            self.assertFalse(tags(signature, "video"))
            self.assertFalse(tags(signature, "button"))
            self.assertFalse(tags(signature, "source"))

            registry = json.loads((fixture / "data/product-presentation-registry.json").read_text())
            (
                fixture
                / registry["collections"]["kids-capsule"]["imagery"]["collection_hero"]["src"]
            ).unlink()
            chapters = render(fixture)
            self.assert_navigation(chapters)
            self.assertFalse(tags(chapters["kids-capsule"], "figure"))
            self.assertFalse(tags(chapters["kids-capsule"], "button"))

            # A changed runtime inventory must not fall back to legacy imagery.
            with (fixture / "data/runtime-media.json").open("a") as handle:
                handle.write("\n")
            chapters = render(fixture)
            self.assert_navigation(chapters)
            for chapter in chapters.values():
                self.assertFalse(tags(chapter, "figure"))
                self.assertFalse(tags(chapter, "picture"))
                self.assertFalse(tags(chapter, "video"))
                self.assertFalse(tags(chapter, "source"))
                self.assertFalse(tags(chapter, "button"))


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]])
