"""Offline generator guards; no authenticated provider operations."""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/sync-analytics.py"


class ProjectionGuards(unittest.TestCase):
    def setUp(self) -> None:
        spec = importlib.util.spec_from_file_location("analytics_projection", SCRIPT)
        assert spec is not None and spec.loader is not None
        self.module = importlib.util.module_from_spec(spec)
        with patch.object(Path, "write_text", side_effect=AssertionError("Import wrote files")):
            spec.loader.exec_module(self.module)

    def test_unknown_flag_rejected_before_writes(self) -> None:
        before = {p: p.read_bytes() for p in SCRIPT.parents[1].rglob("analytics-protocol.php")}
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--chek"], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("unrecognized arguments", result.stderr)
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_missing_anchor_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            self.module.checked_replace("changed source", "old selector", "new selector")

    def test_php_formatting_and_trailing_comma_are_neutral(self) -> None:
        self.assertEqual(
            self.module.canonical_php("<?php foo('value');"),
            self.module.canonical_php("<?php /* formatting */ foo(\n'value',\n);"),
        )

    def test_check_rejects_invalid_empty_call_without_rewriting(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            theme = Path(directory)
            protocol = theme / "inc/analytics-protocol.php"
            protocol.parent.mkdir()
            malformed = "<?php time(,);"
            protocol.write_text(malformed)
            with (
                patch.object(self.module, "THEME", theme),
                patch.object(self.module, "formatted", side_effect=lambda file, text: text),
                patch.object(sys, "argv", [str(SCRIPT), "--check"]),
                self.assertRaises(subprocess.CalledProcessError),
            ):
                self.module.main()
            self.assertEqual(protocol.read_text(), malformed)

    def test_php_changed_behavior_is_not_neutral(self) -> None:
        self.assertNotEqual(
            self.module.canonical_php("<?php foo('value');"),
            self.module.canonical_php("<?php foo('different');"),
        )


if __name__ == "__main__":
    unittest.main()
