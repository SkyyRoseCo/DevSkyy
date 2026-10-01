"""Immutable source bytes + owned overlay, never a blanket hash reblessing."""

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "299f694702ac2dcc61a0f30aa34e4b3ef12f9118"
THEME = "wordpress-theme/skyyrose-flagship-2/"
OVERLAY = {
    "tools/v2-source-certification/inputs.py",
    "tools/v2-source-certification/package-boundary.json",
    "tools/v2-source-certification/generated-outputs.json",
    "tools/v2-source-certification/runtime-php-baseline.json",
}


def source_bytes(relative):
    return subprocess.check_output(["git", "show", SOURCE + ":" + relative], cwd=ROOT)


def verify_pins(contract, reader):
    for relative, expected in contract["input_hashes"].items():
        if hashlib.sha256(reader(relative)).hexdigest() != expected:
            raise ValueError("Unreviewed source drift: " + relative)


class ReviewedSourceTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads((HERE / "build-inputs.json").read_text())

    def combined_bytes(self, relative):
        return (ROOT / relative).read_bytes() if relative in OVERLAY else source_bytes(relative)

    def test_exact_reviewed_source_and_guarded_overlay(self):
        self.assertEqual(self.contract["reviewed_source_revision"], SOURCE)
        verify_pins(self.contract, self.combined_bytes)

    def test_changed_hash_is_not_blessed(self):
        for target in (
            THEME + "assets/js/home-experience.js",
            THEME + "assets/js/product-glb-init.mjs",
            THEME + "inc/product-glb.php",
            THEME + "scripts/build-product-presentation-registry.py",
        ):
            with (
                self.subTest(target=target),
                self.assertRaisesRegex(ValueError, "Unreviewed source drift"),
            ):
                verify_pins(
                    self.contract,
                    lambda p, target=target: self.combined_bytes(p)
                    + (b"changed" if p == target else b""),
                )

    def test_package_census_and_generated_provenance(self):
        files = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", SOURCE, "--", THEME], cwd=ROOT, text=True
        ).splitlines()
        boundary = json.loads((HERE / "package-boundary.json").read_text())["files"]
        self.assertEqual({p[len(THEME) :] for p in files}, set(boundary))
        self.assertIs(boundary["scripts/test-collection-hero-motion.py"]["release"], False)
        for relative in (
            "assets/js/product-glb-init.mjs",
            "assets/js/product-glb-viewer.mjs",
            "assets/js/product-glb-three.mjs",
            "assets/css/product-glb.css",
            "assets/css/product-glb.min.css",
            "inc/product-glb.php",
            "inc/product-glb-links.php",
            "inc/woocommerce-compat.php",
        ):
            self.assertIs(boundary[relative]["release"], True, relative)
        for relative in (
            "tests/commerce/bootstrap.php",
            "tests/commerce/preorder.php",
            "tests/commerce/run-local-matrix.sh",
            "tests/commerce/verify-bootstrap.php",
            "tests/commerce/verify-glb-runtime.php",
        ):
            self.assertIs(boundary[relative]["release"], False, relative)
        generated = json.loads((HERE / "generated-outputs.json").read_text())
        for stem in (
            "css/home-art-direction",
            "css/home-experience",
            "js/home-experience",
            "js/house-motion",
            "css/product-glb",
        ):
            extension = stem.split("/")[0]
            self.assertEqual(
                generated[f"assets/{stem}.min.{extension}"]["source"], f"assets/{stem}.{extension}"
            )

    def test_reviewed_php_bytes(self):
        baseline = json.loads((HERE / "runtime-php-baseline.json").read_text())
        for relative, digest in baseline.items():
            self.assertEqual(
                hashlib.sha256(source_bytes(THEME + relative)).hexdigest(), digest, relative
            )

    def test_product_blocks_and_historical_approvals_retained(self):
        registry = json.loads(
            source_bytes("wordpress-theme/skyyrose-flagship/data/logo-registry.json")
        )
        fronts = json.loads(source_bytes(THEME + "data/approved-card-fronts.json"))
        for sku in ("br-001", "br-004", "br-007"):
            self.assertEqual(
                fronts["products"][sku]["current_fidelity_status"], "BLOCKED_PRODUCT_MISMATCH"
            )
        for sku, binding in fronts["products"].items():
            self.assertEqual(binding, registry["products"][sku]["images"]["card_front"])
        self.assertEqual(len(fronts["products"]), 33)
        self.assertTrue(
            all(
                "accepted_glb_runtime" not in product.get("asset_library", {})
                for product in registry["products"].values()
            ),
            "A newly accepted asset requires a separate reviewed approval contract",
        )


if __name__ == "__main__":
    unittest.main()
