"""Check font delivery determinism and fail-closed filesystem/source behavior."""

import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fontTools.ttLib import TTFont

SPEC = importlib.util.spec_from_file_location(
    "font_delivery", Path(__file__).with_name("build-font-delivery.py")
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
RAW = {job.source: (MODULE.THEME / job.source).read_bytes() for job in MODULE.JOBS}
FIRST = MODULE.JOBS[0]


class FontDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.theme = Path(self.temporary.name)
        for relative, raw in RAW.items():
            source = self.theme / relative
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(raw)
        self.context = patch.object(MODULE, "THEME", self.theme)
        self.context.start()
        self.addCleanup(self.context.stop)

    def sources_unchanged(self):
        for relative, raw in RAW.items():
            self.assertEqual((self.theme / relative).read_bytes(), raw)

    def test_deterministic_and_read_only_check(self):
        for job in MODULE.JOBS:
            self.assertEqual(
                MODULE.derive(RAW[job.source], job), MODULE.derive(RAW[job.source], job)
            )
        MODULE.generate()
        before = {
            p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.theme.rglob("*") if p.is_file()
        }
        MODULE.generate(True)
        self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in before})
        self.sources_unchanged()

    def test_every_delivery_fixes_only_its_width(self):
        MODULE.generate()
        manifest = json.loads((self.theme / MODULE.MANIFEST).read_text())
        self.assertEqual(
            [entry["output"] for entry in manifest["deliveries"]],
            [job.destination for job in MODULE.JOBS],
        )
        for job in MODULE.JOBS:
            font = TTFont(io.BytesIO((self.theme / job.destination).read_bytes()))
            self.assertEqual(MODULE.axes(font), MODULE.retained(job))
            self.assertNotIn("wdth", [axis[0] for axis in MODULE.axes(font)])
            self.assertIn("wght", [axis[0] for axis in MODULE.axes(font)])

    def test_missing_and_stale_output_fail_without_repair(self):
        with self.assertRaisesRegex(ValueError, "Stale"):
            MODULE.generate(True)
        self.assertFalse((self.theme / FIRST.destination).parent.exists())
        MODULE.generate()
        for relative in (*(job.destination for job in MODULE.JOBS), MODULE.MANIFEST):
            output = self.theme / relative
            original = output.read_bytes()
            output.write_bytes(b"stale")
            with self.assertRaisesRegex(ValueError, "Stale"):
                MODULE.generate(True)
            self.assertEqual(output.read_bytes(), b"stale")
            output.write_bytes(original)

    def test_source_and_versions_fail_closed(self):
        for job in MODULE.JOBS:
            with self.assertRaisesRegex(ValueError, "source drift"):
                MODULE.derive(RAW[job.source] + b"tamper", job)
            with self.assertRaisesRegex(ValueError, "axes"):
                MODULE.derive(RAW[job.source], job._replace(axes=[]))
        with (
            patch.object(MODULE, "version", return_value="wrong"),
            self.assertRaisesRegex(ValueError, "Unpinned"),
        ):
            MODULE.derive(RAW[FIRST.source], FIRST)
        self.sources_unchanged()

    def test_actual_encoder_mismatch_fails_closed(self):
        with (
            patch.object(MODULE.woff2, "brotli", object()),
            self.assertRaisesRegex(ValueError, "selected WOFF2"),
        ):
            MODULE.derive(RAW[FIRST.source], FIRST)

    def test_output_symlink_cannot_overwrite_source(self):
        output = self.theme / FIRST.destination
        output.parent.mkdir(parents=True)
        output.symlink_to(self.theme / FIRST.source)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            MODULE.generate()
        self.sources_unchanged()

    def test_ancestor_symlink_rejected(self):
        outside = self.theme / "outside"
        outside.mkdir()
        (self.theme / "assets/derived").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            MODULE.generate()
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
