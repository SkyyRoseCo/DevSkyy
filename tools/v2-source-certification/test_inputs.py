"""Current registry facts govern historical media receipt compatibility."""

import copy
import json
import unittest
from unittest.mock import patch

import inputs

from skyyrose.core.product import all_skus, get_product


class RegistryAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.manifest, _ = inputs.load_product_sot()

    def test_current_registry_supplies_every_garment_type(self):
        expected = {
            sku: get_product(sku)["catalog"]["garment_type_lock"].strip().lower()
            for sku in all_skus()
        }
        self.assertEqual(inputs.garment_types(self.manifest), expected)

    def test_founder_garment_correction_overrides_historical_receipt(self):
        sku = next(iter(self.manifest["products"]))
        corrected = copy.deepcopy(get_product(sku))
        corrected["catalog"]["garment_type_lock"] = "Synthetic test garment"
        with patch.object(
            inputs,
            "get_product",
            side_effect=lambda key: corrected if key == sku else get_product(key),
        ):
            self.assertEqual(inputs.garment_types(self.manifest)[sku], "synthetic test garment")

    def test_changed_current_commerce_requires_receipt_reconciliation(self):
        sku = next(iter(self.manifest["products"]))
        corrected = copy.deepcopy(get_product(sku))
        corrected["catalog"]["price"] = "99999.00"
        with patch.object(
            inputs,
            "get_product",
            side_effect=lambda key: corrected if key == sku else get_product(key),
        ):
            with self.assertRaisesRegex(ValueError, "requires media-binding reconciliation"):
                inputs.garment_types(self.manifest)

    def test_missing_receipt_product_fails_closed(self):
        self.manifest["products"].pop(next(iter(self.manifest["products"])))
        with self.assertRaisesRegex(ValueError, "SKU identity differs"):
            inputs.garment_types(self.manifest)

    def test_exact_current_registry_contract(self):
        inputs.verify_registry_binding(json.loads(inputs.CONTRACT.read_text()))

    def test_stale_sidecar_identity_fails_even_with_current_input_pin(self):
        contract = json.loads(inputs.CONTRACT.read_text())
        contract["current_registry_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "requires contract reconciliation"):
            inputs.verify_registry_binding(contract)

    def test_missing_input_pin_fails_even_with_current_sidecar_identity(self):
        contract = json.loads(inputs.CONTRACT.read_text())
        contract["input_hashes"].pop(contract["catalog_authority"])
        with self.assertRaisesRegex(ValueError, "requires contract reconciliation"):
            inputs.verify_registry_binding(contract)

    def test_alternate_authority_and_reader_fail_closed(self):
        for field, replacement in [
            ("catalog_authority", "stale-catalog.csv"),
            ("garment_source", "stale.reader"),
        ]:
            contract = json.loads(inputs.CONTRACT.read_text())
            contract[field] = replacement
            with self.assertRaisesRegex(ValueError, "differs from product entry point"):
                inputs.verify_registry_binding(contract)

    def test_registry_drift_during_product_reads_is_rejected(self):
        with patch.object(
            inputs,
            "verify_registry_binding",
            side_effect=[None, ValueError("registry changed during reads")],
        ) as check:
            with self.assertRaisesRegex(ValueError, "changed during reads"):
                inputs.garment_types(self.manifest)
            self.assertEqual(check.call_count, 2)


if __name__ == "__main__":
    unittest.main()
