"""Shipping placeholders must expose unknowns and preserve existing authority."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from skyyrose.core.product import get_product
from skyyrose.core.product_registry import initialize_shipping_records, load_registry


class ShippingRecordsTest(unittest.TestCase):
    def test_initializer_preserves_facts_and_is_idempotent(self):
        original = load_registry()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "registry.json"
            raw = copy.deepcopy(original)
            for product in raw["products"].values():
                product.pop("shipping", None)
            before = copy.deepcopy(raw)
            path.write_text(json.dumps(raw))
            self.assertEqual(len(initialize_shipping_records(path)), len(before["products"]))
            after = json.loads(path.read_text())
            for product in after["products"].values():
                shipping = product.pop("shipping")
                self.assertIsNone(shipping["item_weight"]["value"])
                self.assertEqual(shipping["item_weight"]["unit"], "g")
                self.assertEqual(shipping["packed_parcel"]["dimensions"]["unit"], "cm")
            self.assertEqual(before, after)
            previous = path.read_bytes()
            self.assertEqual(initialize_shipping_records(path), [])
            self.assertEqual(path.read_bytes(), previous)

    def test_existing_shipping_never_overwritten(self):
        raw = load_registry()
        raw["products"]["br-001"]["shipping"] = {"test_fixture": "preserve"}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "registry.json"
            path.write_text(json.dumps(raw))
            initialize_shipping_records(path)
            self.assertEqual(
                json.loads(path.read_text())["products"]["br-001"]["shipping"],
                {"test_fixture": "preserve"},
            )

    def product_with_shipping(self, shipping):
        fixture = copy.deepcopy(load_registry())
        fixture["products"]["br-001"]["shipping"] = shipping
        with patch("skyyrose.core.product.load_registry", return_value=fixture):
            return get_product("br-001")

    def test_unknown_fixture_measurements_named_in_public_gaps(self):
        from skyyrose.core.product_registry import empty_shipping_record

        product = self.product_with_shipping(empty_shipping_record())
        gaps = [gap for gap in product["gaps"] if gap.startswith("shipping.")]
        self.assertEqual(len(gaps), 6)
        self.assertIn("shipping.packed_parcel.dimensions.height", gaps)

    def test_populated_fixture_clears_only_shipping_gaps(self):
        from skyyrose.core.product_registry import empty_shipping_record

        shipping = empty_shipping_record()
        before = self.product_with_shipping(shipping)
        shipping["item_weight"]["value"] = 400
        shipping["packed_parcel"]["weight"]["value"] = 450
        shipping["packed_parcel"]["dimensions"].update(length=30, width=20, height=5)
        shipping["packed_parcel"]["packaging_reference"] = "synthetic-test-mailer"
        after = self.product_with_shipping(shipping)
        self.assertEqual(after["shipping"], shipping)
        self.assertEqual(
            after["gaps"], [g for g in before["gaps"] if not g.startswith("shipping.")]
        )
        for key in before.keys() - {"shipping", "gaps", "provenance"}:
            self.assertEqual(before[key], after[key])

    def test_invalid_measurements_and_units_fail_closed(self):
        from skyyrose.core.product_registry import empty_shipping_record

        for invalid in (0, -1, True, "400", float("nan"), float("inf")):
            for path in (
                ("item_weight", "value"),
                ("packed_parcel", "weight", "value"),
                ("packed_parcel", "dimensions", "length"),
                ("packed_parcel", "dimensions", "width"),
                ("packed_parcel", "dimensions", "height"),
            ):
                with self.subTest(invalid=invalid, path=path):
                    shipping = empty_shipping_record()
                    field = shipping
                    for key in path[:-1]:
                        field = field[key]
                    field[path[-1]] = invalid
                    with self.assertRaises(ValueError):
                        self.product_with_shipping(shipping)
        for key in ("item_weight", "packed_parcel"):
            shipping = empty_shipping_record()
            field = shipping[key] if key == "item_weight" else shipping[key]["dimensions"]
            field.pop("unit")
            with self.assertRaises(ValueError):
                self.product_with_shipping(shipping)
        shipping = empty_shipping_record()
        shipping["packed_parcel"]["dimensions"]["unit"] = "in"
        with self.assertRaises(ValueError):
            self.product_with_shipping(shipping)


if __name__ == "__main__":
    unittest.main()
