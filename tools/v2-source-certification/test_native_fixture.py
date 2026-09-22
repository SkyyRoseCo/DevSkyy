"""Reject untrusted native fixture bytes before creating an executable PHP fixture."""

import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "native_fixture", Path(__file__).with_name("prepare-native-fixture.py")
)
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


class NativeFixtureTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.destination = self.root / "wordpress"
        self.payload = b"<?php /* test fixture only */"
        self.pins = json.loads(fixture.PINS.read_text())
        self.pins["files"] = {
            name: hashlib.sha256(self.payload).hexdigest() for name in fixture.SOURCES
        }
        self.manifest = self.root / "pins.json"
        self.manifest.write_text(json.dumps(self.pins))
        binding = patch.object(fixture, "PINS", self.manifest)
        binding.start()
        self.addCleanup(binding.stop)

    def test_fetches_and_writes_only_exact_pinned_files(self):
        with patch.object(
            fixture, "urlopen", side_effect=lambda *args, **kwargs: io.BytesIO(self.payload)
        ) as fetch:
            fixture.prepare(self.destination)
        self.assertEqual(fetch.call_count, 7)
        files = {str(p.relative_to(self.destination)) for p in self.destination.rglob("*.php")}
        self.assertEqual(files, set(fixture.SOURCES))
        for relative in files:
            self.assertEqual((self.destination / relative).read_bytes(), self.payload)

    def test_changed_bytes_do_not_create_partial_fixture(self):
        with patch.object(fixture, "urlopen", return_value=io.BytesIO(b"changed")):
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                fixture.prepare(self.destination)
        self.assertFalse(self.destination.exists())

    def test_rejects_extra_manifest_path_before_network(self):
        self.pins["files"]["../outside.php"] = "0" * 64
        self.manifest.write_text(json.dumps(self.pins))
        with patch.object(fixture, "urlopen") as fetch:
            with self.assertRaisesRegex(ValueError, "manifest differs"):
                fixture.prepare(self.destination)
        fetch.assert_not_called()
        self.assertFalse(self.destination.exists())

    def test_does_not_overwrite_existing_destination(self):
        self.destination.mkdir()
        marker = self.destination / "keep.txt"
        marker.write_text("preserve")
        with patch.object(fixture, "urlopen") as fetch:
            with self.assertRaisesRegex(ValueError, "must not already exist"):
                fixture.prepare(self.destination)
        fetch.assert_not_called()
        self.assertEqual(marker.read_text(), "preserve")
