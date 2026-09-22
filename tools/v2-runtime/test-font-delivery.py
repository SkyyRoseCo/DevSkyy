"""Check font delivery determinism and fail-closed filesystem/source behavior."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "font_delivery", Path(__file__).with_name("build-font-delivery.py")
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
RAW = (MODULE.THEME / MODULE.SOURCE).read_bytes()


class FontDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.theme = Path(self.temporary.name)
        self.source = self.theme / MODULE.SOURCE
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(RAW)
        self.context = patch.object(MODULE, "THEME", self.theme)
        self.context.start()
        self.addCleanup(self.context.stop)

    def test_deterministic_and_read_only_check(self):
        self.assertEqual(MODULE.derive(RAW), MODULE.derive(RAW))
        MODULE.generate()
        before = {
            p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.theme.rglob("*") if p.is_file()
        }
        MODULE.generate(True)
        self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in before})
        self.assertEqual(self.source.read_bytes(), RAW)

    def test_missing_and_stale_output_fail_without_repair(self):
        with self.assertRaisesRegex(ValueError, "Stale"):
            MODULE.generate(True)
        self.assertFalse((self.theme / MODULE.DESTINATION).parent.exists())
        MODULE.generate()
        for relative in (MODULE.DESTINATION, "assets/derived/fonts/manifest.json"):
            output = self.theme / relative
            original = output.read_bytes()
            output.write_bytes(b"stale")
            with self.assertRaisesRegex(ValueError, "Stale"):
                MODULE.generate(True)
            self.assertEqual(output.read_bytes(), b"stale")
            output.write_bytes(original)

    def test_source_and_versions_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "source drift"):
            MODULE.derive(RAW + b"tamper")
        with (
            patch.object(MODULE, "version", return_value="wrong"),
            self.assertRaisesRegex(ValueError, "Unpinned"),
        ):
            MODULE.derive(RAW)
        with patch.object(MODULE, "AXES", []), self.assertRaisesRegex(ValueError, "axes"):
            MODULE.derive(RAW)
        self.assertEqual(self.source.read_bytes(), RAW)

    def test_actual_encoder_mismatch_fails_closed(self):
        with (
            patch.object(MODULE.woff2, "brotli", object()),
            self.assertRaisesRegex(ValueError, "selected WOFF2"),
        ):
            MODULE.derive(RAW)

    def test_output_symlink_cannot_overwrite_source(self):
        output = self.theme / MODULE.DESTINATION
        output.parent.mkdir(parents=True)
        output.symlink_to(self.source)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            MODULE.generate()
        self.assertEqual(self.source.read_bytes(), RAW)

    def test_ancestor_symlink_rejected(self):
        outside = self.theme / "outside"
        outside.mkdir()
        (self.theme / "assets/derived").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            MODULE.generate()
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
