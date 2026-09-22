"""Current registry facts govern historical media receipt compatibility."""

import copy
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


if __name__ == "__main__":
    unittest.main()
