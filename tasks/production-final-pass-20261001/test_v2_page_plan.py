"""Offline source/projection tests; no authenticated or remote execution."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "page_plan", Path(__file__).with_name("plan_v2_pages.py")
)
assert SPEC and SPEC.loader
pages = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pages)


def inventory() -> dict:
    records = {
        p: (
            None
            if p in pages.NEW_PATHS
            else {
                "ID": i + 1,
                "path": p,
                "post_type": "page",
                "post_status": "publish",
                "snapshot_sha256": "a" * 64,
                "template_values": ["skyyrose-canvas.php"],
            }
        )
        for i, p in enumerate(pages.PATHS)
    }
    return {
        "home": "https://skyyrose.co",
        "stylesheet": "skyyrose-flagship",
        "pages": records,
        "all_page_paths": [
            {
                "ID": r["ID"],
                "path": p,
                "post_name": p,
                "post_parent": 0,
                "post_status": "publish",
                "trashed_slug": "",
            }
            for p, r in records.items()
            if r is not None
        ],
    }


class ProjectionTests(unittest.TestCase):
    def test_exact_source_and_reviewed_hub(self):
        data = inventory()
        before = copy.deepcopy(data)
        plan = pages.make_plan(data, "release-pages-20261001")
        self.assertEqual(data, before)
        self.assertEqual([r["path"] for r in plan["changes"]], list(pages.NEW_PATHS))
        self.assertEqual(len(plan["changes"]), 10)
        self.assertEqual(len(plan["existing_guards"]), 6)
        self.assertEqual(pages.digest(plan["changes"][4]["content"].encode()), pages.WORLD_SHA)
        self.assertEqual(
            pages.digest(plan["changes"][-1]["content"].encode()),
            "62fa2ac6eda70f5d8119753ae2a62c3b1353c9ec01619741f03215d147d1dd4f",
        )
        self.assertTrue(all(r["before"] is None for r in plan["changes"]))
        self.assertEqual(plan, pages.make_plan(before, "release-pages-20261001"))

    def test_wrong_target(self):
        data = inventory()
        data["home"] = "https://other.example"
        with self.assertRaisesRegex(ValueError, "TARGET_MISMATCH"):
            pages.make_plan(data, "test")

    def test_absence_must_be_explicit(self):
        data = inventory()
        del data["pages"]["worlds"]
        with self.assertRaisesRegex(ValueError, "EXPLICIT_PATH"):
            pages.make_plan(data, "test")

    def test_collision_refused(self):
        data = inventory()
        data["pages"]["worlds"] = {**data["pages"]["collections"], "ID": 300, "path": "worlds"}
        with self.assertRaisesRegex(ValueError, "ALL_STATUS_PREIMAGE_CONFLICT"):
            pages.make_plan(data, "test")

    def test_duplicate_existing_id_refused(self):
        data = inventory()
        data["pages"]["cart"]["ID"] = data["pages"]["collections"]["ID"]
        with self.assertRaisesRegex(ValueError, "ALL_STATUS_PREIMAGE_CONFLICT"):
            pages.make_plan(data, "test")

    def test_existing_required_page_preserved(self):
        data = inventory()
        data["pages"]["cart"] = None
        with self.assertRaisesRegex(ValueError, "ALL_STATUS_ABSENCE_CONFLICT"):
            pages.make_plan(data, "test")

    def test_operation_restricts_path_and_control_characters(self):
        with self.assertRaisesRegex(ValueError, "OPERATION_INVALID"):
            pages.make_plan(inventory(), "../foreign\n")

    def test_preimage_requires_full_snapshot_hash(self):
        data = inventory()
        del data["pages"]["collections"]["snapshot_sha256"]
        with self.assertRaisesRegex(ValueError, "SNAPSHOT_REQUIRED"):
            pages.make_plan(data, "test")

    def test_verified_captured_source_used_without_mutable_reopen(self):
        captured = b"<?php function skyyrose2_marketplace_pages(){return ['x'=>['path'=>'verified-source']];}"
        with (
            patch.object(pages, "frozen_file", return_value=captured),
            patch.object(pages, "THEME", Path("/missing-mutable-source")),
        ):
            self.assertEqual(pages.definitions(), {"verified-source": {"path": "verified-source"}})

    def test_recorded_source_hash_is_from_same_captured_evaluation(self):
        original = pages.frozen_file
        captured = original("inc/presentation-registry.php")
        calls = []

        def capture(relative):
            if relative == "inc/presentation-registry.php":
                calls.append(relative)
                return captured if len(calls) == 1 else b"mutable second read"
            return original(relative)

        with patch.object(pages, "frozen_file", side_effect=capture):
            plan = pages.make_plan(inventory(), "test")
        self.assertEqual(len(calls), 1)
        self.assertEqual(
            plan["source_hashes"]["inc/presentation-registry.php"], pages.digest(captured)
        )

    def test_missing_complete_inventory(self):
        data = inventory()
        del data["all_page_paths"]
        with self.assertRaisesRegex(ValueError, "ALL_STATUS_INVENTORY_REQUIRED"):
            pages.make_plan(data, "test")

    def test_absence_conflicts_with_nonpublished_status(self):
        for status in ("draft", "pending", "private", "future", "auto-draft", "custom-status"):
            data = inventory()
            data["all_page_paths"].append(
                {
                    "ID": 999,
                    "path": "worlds",
                    "post_name": "worlds",
                    "post_parent": 0,
                    "post_status": status,
                    "trashed_slug": "",
                }
            )
            with self.assertRaisesRegex(ValueError, "ALL_STATUS_ABSENCE_CONFLICT"):
                pages.make_plan(data, "test")

    def test_trashed_and_suffixed_collisions(self):
        for path, status, desired in (
            ("worlds__trashed", "trash", "worlds"),
            ("worlds__trashed", "trash", ""),
            ("worlds-2", "draft", ""),
        ):
            data = inventory()
            data["all_page_paths"].append(
                {
                    "ID": 999,
                    "path": path,
                    "post_name": path,
                    "post_parent": 0,
                    "post_status": status,
                    "trashed_slug": desired,
                }
            )
            with self.assertRaisesRegex(ValueError, "ALL_STATUS_(TRASH|SUFFIX)_COLLISION"):
                pages.make_plan(data, "test")

    def test_complete_inventory_duplicate_and_mismatched_id(self):
        data = inventory()
        data["all_page_paths"].append({**data["all_page_paths"][0], "ID": 999})
        with self.assertRaisesRegex(ValueError, "ALL_STATUS_DUPLICATE_PATH"):
            pages.make_plan(data, "test")
        data = inventory()
        data["all_page_paths"][0]["ID"] = 999
        with self.assertRaisesRegex(ValueError, "ALL_STATUS_PREIMAGE_CONFLICT"):
            pages.make_plan(data, "test")

    def test_ascii_operation_and_boolean_id_match_php_contract(self):
        with self.assertRaisesRegex(ValueError, "OPERATION_INVALID"):
            pages.make_plan(inventory(), "é")
        data = inventory()
        data["pages"]["collections"]["ID"] = True
        with self.assertRaisesRegex(
            ValueError, "ALL_STATUS_PREIMAGE_CONFLICT|PAGE_PREIMAGE_INVALID"
        ):
            pages.make_plan(data, "test")


if __name__ == "__main__":
    unittest.main()
