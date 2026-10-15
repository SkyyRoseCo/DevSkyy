"""Regression tests for source preservation and generated-output integrity."""

import hashlib
import importlib.util
import json
import os
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
        (self.theme / "assets/v2-original/products").mkdir(parents=True)
        self.source = self.theme / "assets/v2-original/products/sg-005.png"
        Image.new("RGB", (32, 48), (32, 44, 80)).save(self.source, "PNG")
        self.original = self.source.read_bytes()
        self.manifest = self.theme / "approved.json"
        receipt = self.theme / "data/v2-media-reviews/fixture.json"
        receipt.parent.mkdir(parents=True)
        evidence = {
            "asset_sha256": hashlib.sha256(self.original).hexdigest(),
            "roles": ["card_front", "pdp_on_model_front"],
            "skus": ["sg-005"],
            "collections": ["signature"],
            "production_id": "synthetic-contract-only",
            "producer": "fixture-maker",
            "reviewer": "fixture-reviewer",
            "verdict": "PASS",
            "v2_originality_pass": True,
            "product_fidelity_pass": True,
        }
        receipt.write_text(json.dumps(evidence))
        self.inventory = {
            "schema": "skyyrose.v2.media-eligibility.v1",
            "disallowed_legacy_sha256": [],
            "assets": {
                "assets/v2-original/products/sg-005.png": {
                    "kind": "photograph",
                    "status": "INDEPENDENT_VISUAL_PASS",
                    "origin": "V2_ORIGINAL_20261002",
                    "sha256": evidence["asset_sha256"],
                    **{
                        key: evidence[key]
                        for key in ("roles", "skus", "collections", "production_id", "producer")
                    },
                    "review": {
                        "path": "data/v2-media-reviews/fixture.json",
                        "sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
                        "reviewer": "fixture-reviewer",
                        "verdict": "PASS",
                    },
                }
            },
        }
        self.manifest.write_text(json.dumps(self.inventory))
        self.enterContext(
            patch.object(
                module,
                "get_product",
                return_value={
                    "collection": "signature",
                    "images": {
                        "card_front": {
                            "path": "assets/v2-original/products/sg-005.png",
                            "sha256": evidence["asset_sha256"],
                            "source_sha256": evidence["asset_sha256"],
                            "review": self.inventory["assets"][
                                "assets/v2-original/products/sg-005.png"
                            ]["review"],
                            "current_fidelity_status": "INDEPENDENT_VISUAL_PASS",
                        }
                    },
                },
            )
        )
        # The builder selects sources through the shared admission module.
        # Restore its theme after each fixture so later package tests retain
        # their real source-bound policy and canonical media paths.
        self.enterContext(patch.object(module.admission, "THEME", self.theme))
        self.output = self.theme / "assets/derived/card-fronts"
        for name, value in [
            ("THEME", self.theme),
            ("MANIFEST", self.manifest),
            ("OUTPUT", self.output),
            ("WIDTHS", (8, 16)),
        ]:
            self.enterContext(patch.object(module, name, value))

    @unittest.skipUnless(os.name == "posix", "POSIX publication permissions")
    def test_completed_temp_remains_private_until_publication(self):
        original_fchmod = module.os.fchmod
        checked = []

        def observe(fd, mode):
            current = os.fstat(fd)
            self.assertEqual(current.st_mode & 0o777, 0o600)
            self.assertGreater(current.st_size, 0)
            self.assertEqual(len(os.pread(fd, current.st_size, 0)), current.st_size)
            self.assertEqual(mode, 0o644)
            checked.append(fd)
            original_fchmod(fd, mode)

        with patch.object(module.os, "fchmod", side_effect=observe):
            module.generate()
        self.assertTrue(checked)

    @unittest.skipUnless(os.name == "posix", "POSIX public-directory permissions")
    def test_private_existing_directory_fails_without_permission_repair(self):
        module.generate()
        root = self.theme / "assets/derived"
        directory = next(path for path in root.iterdir() if path.is_dir())
        before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
        directory.chmod(0o700)
        for check in (True, False):
            with self.subTest(check=check):
                with self.assertRaisesRegex(ValueError, "Inaccessible public"):
                    module.generate(check=check)
                self.assertEqual(directory.stat().st_mode & 0o777, 0o700)
                self.assertEqual(
                    before, {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
                )

    @unittest.skipUnless(os.name == "posix", "POSIX public-file permissions")
    def test_failed_atomic_permission_step_preserves_destination_and_cleans_temp(self):
        module.generate()
        derived = self.theme / "assets/derived"
        before = {path: path.read_bytes() for path in derived.rglob("*") if path.is_file()}
        with patch.object(module.os, "fchmod", side_effect=OSError("permission failure")):
            with self.assertRaisesRegex(OSError, "permission failure"):
                module.generate()
        self.assertEqual(
            before, {path: path.read_bytes() for path in derived.rglob("*") if path.is_file()}
        )

    @unittest.skipUnless(os.name == "posix", "POSIX public-file permissions")
    def test_public_artifacts_are_readable_under_restrictive_umask(self):
        previous_umask = os.umask(0o077)
        try:
            module.generate()
        finally:
            os.umask(previous_umask)
        generated = list((self.theme / "assets/derived").rglob("*"))
        files = [path for path in generated if path.is_file()]
        self.assertTrue(files)
        for path in generated:
            if path.is_dir():
                self.assertEqual(path.stat().st_mode & 0o777, 0o755)
        original = {path: path.read_bytes() for path in files}
        for path in files:
            self.assertEqual(path.stat().st_mode & 0o777, 0o644)
            path.chmod(0o600)
        with self.assertRaisesRegex(ValueError, "Stale"):
            module.generate(check=True)
        for path in files:
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        module.generate()
        for path in files:
            self.assertEqual(path.stat().st_mode & 0o777, 0o644)
            self.assertEqual(path.read_bytes(), original[path])

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

    def test_derivative_projection_binds_bytes_and_source_without_visual_pass(self):
        records = module.generate()
        manifest_hash = hashlib.sha256((self.output / "manifest.json").read_bytes()).hexdigest()
        self.assertEqual(len(records), 3)
        self.assertEqual(sorted(record["width"] for record in records.values()), [8, 16, 32])
        native = records["assets/derived/card-fronts/sg-005-32w.webp"]
        self.assertEqual((native["width"], native["height"]), (32, 48))
        self.assertEqual(self.source.read_bytes(), self.original)
        for relative, record in records.items():
            self.assertEqual(record["status"], "DELIVERY_DERIVATIVE")
            self.assertEqual(record["source_sha256"], hashlib.sha256(self.original).hexdigest())
            self.assertEqual(record["delivery_manifest"]["sha256"], manifest_hash)
            self.assertEqual(
                record["sha256"], hashlib.sha256((self.theme / relative).read_bytes()).hexdigest()
            )
            self.assertNotIn("review", record)
            self.assertNotIn("verdict", record)

    def test_legacy_manifest_is_not_an_approval_source(self):
        self.manifest.write_text(json.dumps({"products": {"sg-005": {}}}))
        with self.assertRaisesRegex(ValueError, "eligibility schema"):
            module.generate()
        self.assertFalse(self.output.exists())

    def test_review_drift_rejected_before_encoding(self):
        receipt = self.theme / "data/v2-media-reviews/fixture.json"
        receipt.write_text(receipt.read_text() + " ")
        with self.assertRaisesRegex(ValueError, "invalid review"):
            module.generate()
        self.assertFalse(self.output.exists())

    def test_legacy_bytes_rejected_even_with_visual_pass(self):
        self.inventory["disallowed_legacy_sha256"] = [hashlib.sha256(self.original).hexdigest()]
        self.manifest.write_text(json.dumps(self.inventory))
        with self.assertRaisesRegex(ValueError, "invalid review"):
            module.generate()
        self.assertFalse(self.output.exists())

    def test_duplicate_master_is_not_arbitrarily_selected(self):
        self.inventory["assets"]["assets/other.webp"] = self.inventory["assets"][
            "assets/v2-original/products/sg-005.png"
        ]
        (self.theme / "assets/other.webp").write_bytes(self.original)
        self.manifest.write_text(json.dumps(self.inventory))
        with self.assertRaisesRegex(ValueError, "Competing approved"):
            module.generate()
        self.assertFalse(self.output.exists())

    def test_delivery_receipt_preserves_exact_roles_without_new_visual_claim(self):
        module.generate()
        product = json.loads((self.output / "manifest.json").read_text())["products"]["sg-005"]
        self.assertEqual(product["roles"], ["card_front", "pdp_on_model_front"])
        self.assertEqual(
            product["source_review"],
            self.inventory["assets"]["assets/v2-original/products/sg-005.png"]["review"],
        )
        self.assertNotIn("verdict", product)
        self.assertFalse(product["encoding"]["crop"])
        self.assertFalse(product["encoding"]["upscale"])

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

    def test_inventory_sync_updates_only_delivery_bindings(self):
        records = module.generate()
        target = self.theme / "data/v2-media-eligibility.json"
        target.write_text(json.dumps(self.inventory))
        expected = target.read_bytes()
        module.sync_delivery_inventory(records, expected)
        current = json.loads(target.read_text())
        self.assertEqual(
            current["assets"]["assets/v2-original/products/sg-005.png"],
            self.inventory["assets"]["assets/v2-original/products/sg-005.png"],
        )
        for path, record in records.items():
            self.assertEqual(current["assets"][path], record)
            self.assertEqual(
                record["delivery_manifest"]["sha256"],
                hashlib.sha256((self.output / "manifest.json").read_bytes()).hexdigest(),
            )

    def test_inventory_sync_preserves_concurrent_owner_change(self):
        records = module.generate()
        target = self.theme / "data/v2-media-eligibility.json"
        target.write_text(json.dumps(self.inventory))
        expected = target.read_bytes()
        changed = {**self.inventory, "coverage_status": "owner changed inventory"}
        target.write_text(json.dumps(changed))
        with self.assertRaisesRegex(ValueError, "inventory changed"):
            module.sync_delivery_inventory(records, expected)
        self.assertEqual(json.loads(target.read_text()), changed)

    def test_inventory_sync_rejects_partial_delivery_and_master_edits(self):
        records = module.generate()
        target = self.theme / "data/v2-media-eligibility.json"
        target.write_text(json.dumps(self.inventory))
        expected = target.read_bytes()
        wrong = {**records, "assets/v2-original/products/sg-005.png": {"status": "invented"}}
        for data in ({}, wrong):
            with self.assertRaisesRegex(ValueError, "exact complete derivative"):
                module.sync_delivery_inventory(data, expected)
            self.assertEqual(target.read_bytes(), expected)


if __name__ == "__main__":
    unittest.main()
