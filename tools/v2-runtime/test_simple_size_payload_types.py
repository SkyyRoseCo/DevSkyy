"""Offline modified retained-payload controls; no native database mutation."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "size_runner_types", Path(__file__).with_name("run_simple_size_native.py")
)
assert SPEC and SPEC.loader
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class NativePayloadTypes(unittest.TestCase):
    def setUp(self):
        reference = json.loads(
            Path(__file__)
            .with_name("fixtures")
            .joinpath("simple-size-typed-retained.json")
            .read_text()
        )
        original = reference["payload"]
        self.assertEqual(
            hashlib.sha256(runner.canonical(original).encode()).hexdigest(),
            reference["payload_sha256"],
        )
        # Full-source SHA and JSON pointer were checked when extracting this fixture;
        # portable controls do not claim to reexecute that historical native run.
        self.assertEqual(len(reference["source_sha256"]), 64)
        self.original = original

    def test_bool_and_fractional_integer_mutants_are_distinct(self):
        for field in ("boolean", "fractional"):
            with self.subTest(field=field):
                mutant = copy.deepcopy(self.original)
                mutant[field] = 1
                # Ordinary Python equality misses both observed-native-type mutants.
                self.assertEqual(self.original, mutant)
                self.assertNotEqual(runner.canonical(self.original), runner.canonical(mutant))

    def test_reordering_is_stable_and_nonfinite_values_refuse(self):
        reordered = dict(reversed(list(self.original.items())))
        self.assertEqual(runner.canonical(self.original), runner.canonical(reordered))
        with self.assertRaises(ValueError):
            runner.canonical({"invalid": float("nan")})


class NativePaymentAttribution(unittest.TestCase):
    """Illustrative local payload controls, not authenticated native executions."""

    def setUp(self):
        self.before = dict.fromkeys(
            ("items", "generation", "raw_size_rows", "raw_generation_rows", "fixture_order_meta"),
            [],
        )
        self.before.update(
            id=1,
            total="80.00",
            stock={"1": 120},
            stock_reduced=False,
            paid=False,
            paid_timestamp=None,
            transaction_id="",
            native_data={"payment_method": "", "payment_method_title": "", "date_modified": None},
        )
        self.after = copy.deepcopy(self.before)
        self.after["native_data"].update(
            payment_method="ss_offline",
            payment_method_title="Synthetic offline",
            date_modified="2026-10-19T12:00:01+00:00",
        )
        self.rows = [
            {"event": "native_pay_started", "data": {"id": 1, "label": "pay-1", "at": 1792411200}},
            {
                "event": "native_pay_order_saved",
                "data": {
                    "id": 1,
                    "label": "pay-1",
                    "at": 1792411201,
                    "values": copy.deepcopy(self.after["native_data"]),
                    "stack": [{"class": "WC_Form_Handler", "function": "pay_action"}],
                },
            },
            {"event": "native_pay_finished", "data": {"id": 1, "label": "pay-1", "at": 1792411202}},
        ]

    def test_exact_synthetic_gateway_and_observed_save_pass(self):
        with patch.object(runner, "events", return_value=self.rows):
            self.assertEqual(
                runner.payment_history_preserved(self.before, self.after, 0),
                ["date_modified", "payment_method", "payment_method_title"],
            )

    def test_wrong_gateway_title_date_and_unobserved_values_refuse(self):
        for field, value in (
            ("payment_method", "other"),
            ("payment_method_title", "Other title"),
            ("date_modified", "2026-10-18T12:00:01+00:00"),
        ):
            with self.subTest(field=field):
                after, rows = copy.deepcopy(self.after), copy.deepcopy(self.rows)
                after["native_data"][field] = value
                rows[1]["data"]["values"][field] = value
                with (
                    patch.object(runner, "events", return_value=rows),
                    self.assertRaises(AssertionError),
                ):
                    runner.payment_history_preserved(self.before, after, 0)
        rows = copy.deepcopy(self.rows)
        rows[1]["data"]["values"]["payment_method_title"] = "Not the persisted value"
        with patch.object(runner, "events", return_value=rows), self.assertRaises(AssertionError):
            runner.payment_history_preserved(self.before, self.after, 0)


if __name__ == "__main__":
    unittest.main()
