"""Negative tests exercise the hash and containment boundary, not product approval."""

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

spec = importlib.util.spec_from_file_location(
    "integrity", Path(__file__).with_name("check-integrity.py")
)
integrity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integrity)


class AssetBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        (self.root / "assets").mkdir()
        self.image = self.root / "assets/front.png"
        Image.new("RGB", (3, 5)).save(self.image)
        self.sha = hashlib.sha256(self.image.read_bytes()).hexdigest()
        self.binding = patch.object(integrity, "THEME", self.root)
        self.binding.start()

    def tearDown(self):
        self.binding.stop()
        self.directory.cleanup()

    def test_exact_hash_and_dimensions(self):
        integrity.asset("assets/front.png", self.sha, 3, 5)

    def test_rejects_changed_pixels(self):
        Image.new("RGB", (3, 5), "white").save(self.image)
        with self.assertRaises(ValueError):
            integrity.asset("assets/front.png", self.sha, 3, 5)

    def test_rejects_wrong_dimensions(self):
        with self.assertRaises(ValueError):
            integrity.asset("assets/front.png", self.sha, 5, 3)

    def test_rejects_traversal(self):
        with self.assertRaises(ValueError):
            integrity.asset("assets/../assets/front.png", self.sha)

    def test_rejects_symlink(self):
        (self.root / "assets/link.png").symlink_to(self.image)
        with self.assertRaises(ValueError):
            integrity.asset("assets/link.png", self.sha)
