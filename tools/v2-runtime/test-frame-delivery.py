"""Regression coverage for deterministic, authority-preserving frame delivery."""

import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

SPEC = importlib.util.spec_from_file_location(
    "frame_delivery", Path(__file__).with_name("build-frame-delivery.py")
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FrameDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.theme = Path(self.temp.name).resolve()
        self.source = (
            self.theme / "assets/sot/images/product-card-portals/signature-portal-statue-640w.webp"
        )
        self.source.parent.mkdir(parents=True)
        image = Image.new("RGBA", (16, 24), (30, 50, 70, 255))
        image.putpixel((8, 12), (200, 80, 10, 0))
        image.save(self.source, "WEBP", lossless=True, exact=True)
        self.raw = self.source.read_bytes()
        self.expected = (MODULE.digest(self.raw), 16, 24)
        self.enterContext(patch.object(MODULE, "THEME", self.theme))
        self.enterContext(patch.object(MODULE, "WIDTH", 8))
        self.enterContext(patch.object(MODULE, "SOURCES", {"signature": self.expected}))
        self.output = self.theme / MODULE.OUTPUT

    def snapshot(self):
        return {
            str(p.relative_to(self.theme)): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in self.theme.rglob("*")
            if p.is_file()
        }

    def test_deterministic_generation_and_check_never_mutate(self):
        MODULE.generate()
        first = {p.name: p.read_bytes() for p in self.output.iterdir()}
        MODULE.generate()
        self.assertEqual(first, {p.name: p.read_bytes() for p in self.output.iterdir()})
        snapshot = self.snapshot()
        MODULE.generate(check=True)
        self.assertEqual(snapshot, self.snapshot())
        self.assertEqual(self.raw, self.source.read_bytes())

    def test_narrow_variant_supplements_wider_source_with_matching_recipe(self):
        with patch.object(MODULE, "WIDTH", 384):
            manifest = MODULE.generate()
            row = manifest["collections"]["signature"]
            self.assertEqual(row["rendition"]["width"], 384)
            self.assertEqual(row["narrow_rendition"]["width"], 360)
            self.assertEqual(manifest["recipe"]["quality"], MODULE.QUALITY)
            candidate = self.theme / row["narrow_rendition"]["src"]
            self.assertEqual(
                MODULE.digest(candidate.read_bytes()), row["narrow_rendition"]["sha256"]
            )
            before = self.snapshot()
            MODULE.generate(check=True)
            self.assertEqual(before, self.snapshot())
            candidate.write_bytes(b"stale")
            before = self.snapshot()
            with self.assertRaisesRegex(ValueError, "Stale frame"):
                MODULE.generate(check=True)
            self.assertEqual(before, self.snapshot())

    def test_missing_check_never_creates_output_directory(self):
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "Stale frame"):
            MODULE.generate(check=True)
        self.assertFalse(self.output.exists())
        self.assertEqual(before, self.snapshot())

    def test_source_drift_and_dimensions_fail_before_output(self):
        self.source.write_bytes(self.raw + b"drift")
        with self.assertRaisesRegex(ValueError, "source drift"):
            MODULE.generate()
        self.assertFalse(self.output.exists())
        self.source.write_bytes(self.raw)
        with patch.object(MODULE, "SOURCES", {"signature": (self.expected[0], 17, 24)}):
            with self.assertRaisesRegex(ValueError, "dimensions"):
                MODULE.generate()
        self.assertFalse(self.output.exists())

    def test_stale_rendition_and_manifest_fail_readonly(self):
        MODULE.generate()
        for name in ("signature-8w.webp", "manifest.json"):
            target = self.output / name
            original = target.read_bytes()
            target.write_bytes(original + b"stale")
            before = self.snapshot()
            with self.assertRaisesRegex(ValueError, "Stale frame"):
                MODULE.generate(check=True)
            self.assertEqual(before, self.snapshot())
            target.write_bytes(original)

    def test_alpha_and_dimensions_are_checked_after_decode(self):
        reference = Image.new("RGBA", (8, 12), (30, 40, 50, 120))
        changed = reference.copy()
        changed.putpixel((0, 0), (30, 40, 50, 121))
        stream = io.BytesIO()
        changed.save(stream, "PNG")
        with self.assertRaisesRegex(ValueError, "alpha differs"):
            MODULE.validate_decoded(stream.getvalue(), reference, {})
        with self.assertRaisesRegex(ValueError, "dimensions"):
            MODULE.validate_decoded(stream.getvalue(), reference.resize((7, 12)), {})

    def test_reject_source_output_and_manifest_symlinks(self):
        original = self.source.with_suffix(".original")
        self.source.rename(original)
        self.source.symlink_to(original)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            MODULE.generate()
        self.source.unlink()
        original.rename(self.source)
        self.output.parent.mkdir(parents=True)
        self.output.symlink_to(self.source.parent, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            MODULE.generate()
        self.output.unlink()
        self.output.mkdir()
        for name in ("signature-8w.webp", "manifest.json"):
            link = self.output / name
            link.symlink_to(self.source)
            with self.assertRaisesRegex(ValueError, "Symlink"):
                MODULE.generate()
            self.assertEqual(self.raw, self.source.read_bytes())
            link.unlink()

    def test_reject_traversal_and_unpinned_codec(self):
        for relative in ("../outside", "/tmp/outside"):
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                MODULE.safe_path(relative)
        with patch.object(MODULE.features, "version", return_value="wrong"):
            with self.assertRaisesRegex(ValueError, "Unpinned"):
                MODULE.generate()
        self.assertFalse(self.output.exists())

    def test_atomic_failure_preserves_existing_target_and_cleans_temp(self):
        MODULE.generate()
        before = self.snapshot()
        with patch.object(MODULE.os, "replace", side_effect=OSError("simulated failure")):
            with self.assertRaises(OSError):
                MODULE.write_atomic(f"{MODULE.OUTPUT}/signature-8w.webp", b"bad")
        self.assertEqual(before, self.snapshot())


if __name__ == "__main__":
    unittest.main()
