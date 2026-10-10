"""Current registry facts govern historical media receipt compatibility."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import inputs

from skyyrose.core.product import all_skus, get_product


class RegistryAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.manifest, _ = inputs.load_product_sot()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

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

    def _with_corrections(self, entries):
        path = Path(self.tmp.name) / "receipt-corrections.json"
        path.write_text(
            json.dumps({"schema": "skyyrose.v2.receipt-corrections.v1", "corrections": entries})
        )
        return patch.object(inputs, "CORRECTIONS", path)

    def _kids_color(self, **overrides):
        entry = {
            "sku": "kids-002",
            "field": "colors",
            "receipt_value": ["Lavender/Purple"],
            "current_value": ["Purple/Black"],
            "founder_verbatim": "we never wrote lavender and light pink",
        }
        return {**entry, **overrides}

    def test_founder_color_correction_reconciles_receipt(self):
        with self._with_corrections([self._kids_color()]):
            self.assertIn("kids-002", inputs.garment_types(self.manifest))

    def test_correction_without_founder_verbatim_source_fails_closed(self):
        entry = self._kids_color(founder_verbatim="agent says the color is purple")
        with self._with_corrections([entry]):
            with self.assertRaisesRegex(ValueError, "lacks a founder-verbatim source"):
                inputs.garment_types(self.manifest)

    def test_correction_must_match_current_registry_value(self):
        with self._with_corrections([self._kids_color(current_value=["Purple"])]):
            with self.assertRaisesRegex(ValueError, "does not match the registry"):
                inputs.garment_types(self.manifest)

    def test_missing_correction_still_requires_reconciliation(self):
        with self._with_corrections([]):
            with self.assertRaisesRegex(ValueError, "requires media-binding reconciliation"):
                inputs.garment_types(self.manifest)

    def test_stale_correction_fails_closed(self):
        current = get_product("kids-002")
        reverted = copy.deepcopy(current)
        reverted["catalog"]["color"] = "Lavender/Purple"
        entry = self._kids_color(
            receipt_value=["Lavender/Purple"], current_value=["Lavender/Purple"]
        )
        with (
            self._with_corrections([entry]),
            patch.object(
                inputs,
                "get_product",
                side_effect=lambda key: reverted if key == "kids-002" else get_product(key),
            ),
        ):
            with self.assertRaisesRegex(ValueError, "stale"):
                inputs.garment_types(self.manifest)


if __name__ == "__main__":
    unittest.main()
