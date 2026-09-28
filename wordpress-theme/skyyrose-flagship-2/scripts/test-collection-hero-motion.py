#!/usr/bin/env python3
"""Regression tests for the homepage emitter approval boundaries."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("validate-collection-hero-motion.py")
SPEC = importlib.util.spec_from_file_location("hero_motion", SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class HomepageEmitterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        home = validator.THEME / "template-parts/home"
        cls.journal = (home / "editorial-journal.php").read_text()
        cls.collection = (home / "editorial-collection.php").read_text()

    def test_existing_journal_assets_are_hash_bound(self):
        validator.validate_home_journal(self.journal)

    def test_replaced_film_fails(self):
        changed = self.journal.replace("skyyrose-tour-around-the-bay.mp4", "other.mp4")
        with self.assertRaisesRegex(ValueError, "source binding drift"):
            validator.validate_home_journal(changed)

    def test_extra_video_fails(self):
        with self.assertRaisesRegex(ValueError, "exactly one"):
            validator.validate_home_journal(self.journal + "<VIDEO src='other.mp4'></VIDEO>")

    def test_direct_video_source_fails(self):
        with self.assertRaisesRegex(ValueError, "bypass"):
            validator.validate_home_journal(
                self.journal.replace("<video ", "<video src='other.mp4' ", 1)
            )

    def test_poster_removed_fails(self):
        with self.assertRaisesRegex(ValueError, "visible poster"):
            validator.validate_home_journal(
                self.journal.replace("skyyrose-tour-around-the-bay-poster.webp", "other.webp")
            )

    def test_asset_bytes_changed_fails(self):
        with patch.object(validator, "sha256", return_value="wrong"):
            with self.assertRaisesRegex(ValueError, "hash drift"):
                validator.validate_home_journal(self.journal)

    def test_collection_uses_destination_resolver(self):
        validator.validate_home_collection(self.collection)

    def test_collection_changed_resolver_source_fails(self):
        with self.assertRaisesRegex(ValueError, "destination hero"):
            validator.validate_home_collection(
                self.collection.replace("$collection['hero'] );", "'other.webp' );", 1)
            )

    def test_collection_extra_unclosed_video_fails(self):
        with self.assertRaisesRegex(ValueError, "exactly one video opening tag"):
            validator.validate_home_collection(
                self.collection + '<VIDEO src="other.mp4" autoplay muted>'
            )

    def test_collection_static_video_bypass_fails(self):
        with self.assertRaisesRegex(ValueError, "bypasses resolved"):
            validator.validate_home_collection(
                self.collection.replace("$chapter_motion['mp4']", "'other.mp4'")
            )


if __name__ == "__main__":
    unittest.main()
