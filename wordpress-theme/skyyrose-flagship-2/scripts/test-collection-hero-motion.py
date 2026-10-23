#!/usr/bin/env python3
"""Regression tests for the homepage emitter approval boundaries."""

import copy
import importlib.util
import json
import tempfile
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

    def test_journal_gallery_is_registry_source_bound(self):
        validator.validate_home_journal(self.journal)

    def test_rejected_film_fails(self):
        with self.assertRaisesRegex(ValueError, "rejected jersey film"):
            validator.validate_home_journal(
                self.journal + '<video src="skyyrose-tour-around-the-bay.mp4"></video>'
            )

    def test_gallery_removed_fails(self):
        with self.assertRaisesRegex(ValueError, "source-bound jersey gallery"):
            validator.validate_home_journal(
                self.journal.replace("template-parts/commerce/jersey-gallery", "other")
            )

    def test_card_bytes_changed_fails(self):
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


class FounderFilmTests(unittest.TestCase):
    """The 2026-10-08 films are admitted only through their founder receipt."""

    def setUp(self):
        manifest = json.loads(validator.MANIFEST.read_text(encoding="utf-8"))
        self.motion = manifest["collections"]["signature"]["ai_motion"]
        self.poster = manifest["collections"]["signature"]["source"]["file"]
        self.max_bytes = manifest["runtime"]["performance"]["max_web_asset_bytes"]
        self.receipt = validator.film_receipt("signature", self.poster)

    def check(self, motion=None, poster=None):
        validator.validate_founder_film(
            "signature", motion or self.motion, poster or self.poster, self.max_bytes
        )

    def test_current_film_passes(self):
        self.check()

    def test_missing_receipt_fails(self):
        with self.assertRaisesRegex(ValueError, "no founder authorization"):
            validator.film_receipt("signature", "assets/video/unknown.webp")

    def test_changed_decision_text_fails(self):
        changed = {**self.receipt, "decision_text": "wire them in"}
        with patch.object(
            validator.json,
            "loads",
            side_effect=[json.loads(validator.ELIGIBILITY.read_text(encoding="utf-8")), changed],
        ):
            with self.assertRaisesRegex(ValueError, "authorization drift"):
                validator.film_receipt("signature", self.poster)

    def test_other_collection_receipt_fails(self):
        with self.assertRaisesRegex(ValueError, "authorization drift"):
            validator.film_receipt("black-rose", self.poster)

    def test_master_hash_mismatch_fails(self):
        motion = copy.deepcopy(self.motion)
        motion["master"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "authorized master"):
            self.check(motion)

    def test_web_asset_outside_boundary_fails(self):
        motion = copy.deepcopy(self.motion)
        motion["web"][0]["file"] = motion["web"][0]["file"].replace("cinema-20261008", "other")
        with self.assertRaisesRegex(ValueError, "approval boundary"):
            self.check(motion)

    def test_changed_delivery_bytes_fail(self):
        motion = copy.deepcopy(self.motion)
        with patch.object(validator, "sha256", return_value="0" * 64):
            with self.assertRaisesRegex(ValueError, "hash drift"):
                self.check(motion)

    def test_non_object_web_entry_fails(self):
        motion = copy.deepcopy(self.motion)
        motion["web"][0] = motion["web"][0]["file"]
        with self.assertRaisesRegex(ValueError, "approval boundary"):
            self.check(motion)

    def test_eligibility_without_assets_fails(self):
        with patch.object(validator.json, "loads", return_value={}):
            with self.assertRaisesRegex(ValueError, "no founder authorization"):
                validator.film_receipt("signature", self.poster)


class NativeKidsTests(unittest.TestCase):
    def setUp(self):
        manifest = json.loads(validator.MANIFEST.read_text())
        self.motion = manifest["collections"]["kids-capsule"]["ai_motion"]
        self.poster = manifest["collections"]["kids-capsule"]["source"]["file"]
        self.budget = manifest["runtime"]["performance"]["max_web_asset_bytes"]

    def check(self, slug="kids-capsule"):
        validator.validate_native_kids(slug, self.motion, self.poster, self.budget)

    def test_current_native_receipt_passes_real_php_gate(self):
        self.check()

    def test_native_cannot_authorize_another_collection(self):
        with self.assertRaisesRegex(ValueError, "Kids boundary"):
            self.check("signature")

    def test_changed_native_master_refused(self):
        self.motion["master"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "master or directive"):
            self.check()

    def test_native_does_not_claim_ai_approval(self):
        self.motion["status"] = "founder_approved"
        with self.assertRaisesRegex(ValueError, "status drift"):
            self.check()

    def test_changed_native_directive_refused(self):
        self.motion["founder_approval_note"] = "unrelated authorization"
        with self.assertRaisesRegex(ValueError, "master or directive"):
            self.check()

    def test_native_missing_codec_refused(self):
        self.motion["web"].pop()
        with self.assertRaisesRegex(ValueError, "delivery boundary"):
            self.check()

    def test_native_byte_budget_enforced(self):
        self.budget = 1
        with self.assertRaisesRegex(ValueError, "byte budget"):
            self.check()

    def test_video_cannot_use_a_different_receipt(self):
        inventory = json.loads(validator.ELIGIBILITY.read_text())
        video = self.motion["web"][0]["file"]
        inventory["assets"][video]["authorization"] = inventory["assets"][video][
            "authorization"
        ] | {"path": "data/v2-media-reviews/other-valid-native-receipt.json"}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inventory.json"
            path.write_text(json.dumps(inventory))
            with patch.object(validator, "ELIGIBILITY", path):
                with self.assertRaisesRegex(ValueError, "coherent receipt"):
                    self.check()

    def test_native_runtime_gate_refusal_propagates(self):
        with patch.object(
            validator.subprocess, "run", return_value=validator.subprocess.CompletedProcess([], 1)
        ):
            with self.assertRaisesRegex(ValueError, "authorization gate refused"):
                self.check()

    def test_home_cannot_use_unscoped_cinema(self):
        source = (validator.THEME / "template-parts/home/editorial-collection.php").read_text()
        with self.assertRaisesRegex(ValueError, "Kids cinema"):
            validator.validate_home_collection(
                source.replace("'kids-capsule' === $slug ?", "true ?")
            )


class MediaGateExemptionTests(unittest.TestCase):
    """The media gate is exempt from the emitter scan only while it emits no video."""

    def setUp(self):
        self.source = (validator.THEME / validator.MEDIA_GATE).read_text(encoding="utf-8")

    def test_current_gate_is_exempt(self):
        self.assertTrue(validator.is_media_gate_filter(validator.MEDIA_GATE, self.source))

    def test_other_file_is_not_exempt(self):
        self.assertFalse(validator.is_media_gate_filter("functions.php", self.source))

    def test_added_video_in_gate_fails(self):
        with self.assertRaisesRegex(ValueError, "emits video outside its tag filter"):
            validator.is_media_gate_filter(
                validator.MEDIA_GATE, self.source + '<VIDEO src="other.mp4"></video>'
            )


if __name__ == "__main__":
    unittest.main()
