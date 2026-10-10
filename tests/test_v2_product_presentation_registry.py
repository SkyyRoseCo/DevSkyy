"""Regression coverage for the generated V2 product-presentation adapter."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from skyyrose.core.product import all_skus, get_product, provenance

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "wordpress-theme/skyyrose-flagship-2/data/product-presentation-registry.json"


def _registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


class ProductPresentationTests(unittest.TestCase):
    def test_registry_covers_exact_current_registry_skus(self) -> None:
        self.assertEqual(set(_registry()["products"]), set(all_skus()))

    def test_registry_product_facts_come_from_unified_registry(self) -> None:
        registry = _registry()
        self.assertEqual(
            registry["generated_from"],
            "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        )
        self.assertEqual(
            registry["product_registry_sha256"], provenance()["sources"]["registry"]["sha256"]
        )
        for sku, presentation in registry["products"].items():
            with self.subTest(sku=sku):
                catalog = get_product(sku)["catalog"]
                self.assertIs(presentation["is_preorder"], catalog["is_preorder"].strip() == "1")
                self.assertEqual(presentation["collection"], catalog["collection"])
                self.assertEqual(
                    presentation["garment_type"], catalog["garment_type_lock"].strip().lower()
                )

    def test_jersey_presentation_preserves_membership_and_public_route(self) -> None:
        registry = _registry()
        jerseys = registry["supplements"]["jersey_series_skus"]
        expected = sorted(
            (get_product(sku)["merchandising"]["series_order"], sku)
            for sku in all_skus()
            if get_product(sku)["merchandising"]["series_slug"] == "jersey-series"
        )
        self.assertTrue(expected, "Existing Jersey Series membership must survive migration")
        self.assertEqual(jerseys, [sku for _order, sku in expected])
        orders = []
        for sku in jerseys:
            record = registry["products"][sku]
            self.assertEqual(record["collection"], "black-rose")
            self.assertEqual(record["presentation"], "jersey-series")
            self.assertEqual(record["route"], "/jersey-series/")
            self.assertTrue(record["series_region"])
            self.assertEqual(
                record["series_region"], get_product(sku)["merchandising"]["series_region"]
            )
            self.assertEqual(
                record["series_order"], get_product(sku)["merchandising"]["series_order"]
            )
            orders.append(record["series_order"])
        self.assertEqual(orders, sorted(set(orders)))


if __name__ == "__main__":
    unittest.main()
