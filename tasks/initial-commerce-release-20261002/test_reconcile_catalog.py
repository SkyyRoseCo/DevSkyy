"""Offline catalog reconciliation rejects ambiguous identities before producing evidence."""

import copy
import json
import unittest
from pathlib import Path

from reconcile_catalog import reconcile


class CatalogEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads(
            (Path(__file__).parent / "evidence/staging-catalog.json").read_text()
        )

    def test_parent_only_identity_allows_existing_child_skus(self):
        result = reconcile(self.snapshot)
        self.assertEqual(result["counts"]["canonical_skus"], 33)
        self.assertEqual(result["missing_canonical_skus"], [])
        self.assertTrue(all(p["price_matches"] for p in result["products"]))
        self.assertTrue(all(p["preorder_matches"] for p in result["products"]))
        self.assertTrue(all(p["card_front"]["local_hash_matches"] for p in result["products"]))

    def test_foreign_target_rejected(self):
        self.snapshot["home"] = "https://unverified.invalid"
        with self.assertRaisesRegex(ValueError, "UNVERIFIED_TARGET"):
            reconcile(self.snapshot)

    def test_duplicate_record_id_rejected(self):
        self.snapshot["records"].append(copy.deepcopy(self.snapshot["records"][0]))
        with self.assertRaisesRegex(ValueError, "DUPLICATE_RECORD_ID"):
            reconcile(self.snapshot)

    def test_duplicate_published_parent_sku_rejected(self):
        parent = next(r for r in self.snapshot["records"] if not r["parent_id"])
        duplicate = copy.deepcopy(parent)
        duplicate["id"] = max(r["id"] for r in self.snapshot["records"]) + 1
        self.snapshot["records"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "AMBIGUOUS_PUBLISHED_SKU"):
            reconcile(self.snapshot)


if __name__ == "__main__":
    unittest.main()
