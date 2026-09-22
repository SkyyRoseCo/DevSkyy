"""Regression tests for source preservation and generated-output integrity."""

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

spec = importlib.util.spec_from_file_location(
    "card_renditions", Path(__file__).with_name("build-card-renditions.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RenditionIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.theme = Path(self.temp.name)
        (self.theme / "assets").mkdir()
        self.source = self.theme / "assets/front.webp"
        Image.new("RGB", (32, 48), (32, 44, 80)).save(self.source, "WEBP")
        self.original = self.source.read_bytes()
        self.manifest = self.theme / "approved.json"
        self.manifest.write_text(
            json.dumps(
                {
                    "products": {
                        "sg-005": {
                            "src": "assets/front.webp",
                            "width": 32,
                            "height": 48,
                            "sha256": hashlib.sha256(self.original).hexdigest(),
                        }
                    }
                }
            )
        )
        self.output = self.theme / "assets/derived/card-fronts"
        for name, value in [
            ("THEME", self.theme),
            ("MANIFEST", self.manifest),
            ("OUTPUT", self.output),
            ("WIDTHS", (8, 16)),
        ]:
            self.enterContext(patch.object(module, name, value))

    def test_repeat_generation_and_check_preserve_source(self):
        module.generate()
        first = {p.name: p.read_bytes() for p in self.output.iterdir()}
        module.generate()
        module.generate(check=True)
        self.assertEqual(first, {p.name: p.read_bytes() for p in self.output.iterdir()})
        self.assertEqual(self.original, self.source.read_bytes())

    def test_source_drift_rejected_before_delivery(self):
        self.source.write_bytes(self.original + b"drift")
        with self.assertRaisesRegex(ValueError, "source drift"):
            module.generate()
        self.assertFalse(self.output.exists())

    def test_rendition_symlink_cannot_overwrite_source(self):
        self.output.mkdir(parents=True)
        (self.output / "sg-005-8w.webp").symlink_to(self.source)
        with self.assertRaisesRegex(ValueError, "Symlink rendition"):
            module.generate()
        self.assertEqual(self.original, self.source.read_bytes())

    def test_output_directory_symlink_rejected(self):
        self.output.parent.mkdir(parents=True)
        self.output.symlink_to(self.theme / "assets", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlink output"):
            module.generate()
        self.assertEqual(self.original, self.source.read_bytes())

    def test_stale_derivative_check_rejects_without_repair(self):
        module.generate()
        target = self.output / "sg-005-8w.webp"
        target.write_bytes(b"not the verified derivative")
        with self.assertRaisesRegex(ValueError, "Stale rendition"):
            module.generate(check=True)
        self.assertEqual(b"not the verified derivative", target.read_bytes())


if __name__ == "__main__":
    unittest.main()
