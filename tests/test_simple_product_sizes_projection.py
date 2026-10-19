"""Exact canonical strings, coherent membership and read-only drift detection."""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from skyyrose.core import simple_product_sizes as projection


class SimpleProductSizeProjectionTest(unittest.TestCase):
    def test_every_record_comes_from_get_product_without_size_coercion(self):
        payload = projection.build()
        self.assertEqual(sorted(payload["products"]), sorted(projection.product.all_skus()))
        for sku, record in payload["products"].items():
            self.assertEqual(
                record["sizes"], projection.product.get_product(sku)["garment"]["available_sizes"]
            )
            self.assertTrue(all(type(value) is str for value in record["sizes"]))
        self.assertEqual(
            payload["products_sha256"],
            hashlib.sha256(projection.encoded(payload["products"])).hexdigest(),
        )

    def test_numeric_array_empty_and_duplicate_canonical_sizes_are_refused(self):
        original = projection.product.get_product
        for invalid in ([5], [["S"]], [], ["S", "S"]):

            def reader(sku, invalid_sizes=invalid):
                record = copy.deepcopy(original(sku))
                if sku == "kids-002":
                    record["garment"]["available_sizes"] = invalid_sizes
                return record

            with (
                self.subTest(invalid=invalid),
                patch.object(projection.product, "get_product", side_effect=reader),
            ):
                with self.assertRaisesRegex(ValueError, "Canonical size strings"):
                    projection.build()

    def test_omitted_product_is_not_a_complete_projection(self):
        with patch.object(projection.product, "all_skus", return_value=["br-001"]):
            with self.assertRaisesRegex(ValueError, "membership differs"):
                projection.build()

    def test_check_reports_missing_and_modified_projection_without_repair(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder).resolve() / "sizes.json"
            self.assertEqual(projection.reconcile(True, output), [str(output)])
            self.assertFalse(output.exists())
            self.assertEqual(projection.reconcile(False, output), [str(output)])
            self.assertEqual(projection.reconcile(True, output), [])
            modified = json.loads(output.read_bytes())
            del modified["products"]["kids-002"]
            output.write_text(json.dumps(modified))
            before = output.read_bytes()
            self.assertEqual(projection.reconcile(True, output), [str(output)])
            self.assertEqual(output.read_bytes(), before)

    def test_symlink_output_is_refused_without_touching_its_target(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            target = root / "preserved.txt"
            target.write_text("preserved")
            output = root / "sizes.json"
            output.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "symlink"):
                projection.reconcile(False, output)
            self.assertEqual(target.read_text(), "preserved")


if __name__ == "__main__":
    unittest.main()
