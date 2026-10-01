"""The combined replay never becomes live billing, acceptance or commerce evidence."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

import refresh_tracking as tracker


def fixture():
    return {
        "schema_version": 1,
        "captured_at": "2026-09-30T03:20:00Z",
        "evidence_class": "REPRODUCED_LOCAL_FIXTURES",
        "authentication": "SYNTHETIC_LOCAL",
        "checks": [{"name": "relay", "status": "PASS", "detail": "Local signed replay"}],
        "creative": {
            "job_id": "fixture-job",
            "contract_id": "a" * 64,
            "evidence_mode": "SIMULATED",
            "receipt_state": "VERIFIED",
            "artifact_count": 1,
            "technical_passes": 1,
            "owner_acceptance": "BLOCKED",
            "publication_authorized": False,
            "spend_authorized": False,
            "actual_spend": None,
            "current_provider_execution": None,
        },
        "governor": {
            "job_id": "fixture-job",
            "grant_id": "fixture-grant",
            "evidence_mode": "SIMULATED",
            "head_sequence": 6,
            "ledger_authenticated": True,
            "resources": {
                k: {"credits": "2.000000000000000001"}
                for k in ("authorized", "consumed", "held", "available", "unspent_authorization")
            },
            "operations_count": 1,
            "owner_acceptance": "UNVERIFIED",
            "actual_spend": None,
            "current_provider_execution": None,
        },
        "website": {
            "site_id": "synthetic-site",
            "environment": "test",
            "events": 2,
            "paid_orders": 1,
            "purchase_attribution": None,
        },
        "limitations": ["Fixtures are not production execution"],
    }


class IntegrationInputsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "integration.json"

    def read(self, value):
        self.path.write_text(json.dumps(value))
        return tracker.integration_evidence(self.path)

    def test_exact_record_preserves_failure_and_unknowns(self):
        value = fixture()
        value["checks"][0]["status"] = "FAIL"
        self.assertEqual(self.read(value), value)

    def test_missing_replay_stays_missing(self):
        self.assertIsNone(tracker.integration_evidence(self.path))

    def test_rejects_authority_upgrade_or_unbound_lineage(self):
        cases = (
            ("authentication", "AUTHENTICATED_LIVE"),
            ("schema_version", True),
            ("creative.evidence_mode", "LIVE"),
            ("creative.owner_acceptance", "APPROVED"),
            ("creative.publication_authorized", True),
            ("creative.spend_authorized", True),
            ("creative.actual_spend", 0),
            ("creative.contract_id", 123),
            ("creative.technical_passes", 2),
            ("governor.job_id", "different-job"),
            ("governor.actual_spend", "0"),
            ("governor.current_provider_execution", False),
            ("governor.ledger_authenticated", "true"),
            ("governor.head_sequence", True),
            ("website.environment", "production"),
            ("website.purchase_attribution", 0),
            ("website.events", -1),
        )
        for field, new in cases:
            value = copy.deepcopy(fixture())
            target = value
            parts = field.split(".")
            for part in parts[:-1]:
                target = target[part]
            target[parts[-1]] = new
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.read(value)

    def test_rejects_private_or_unbounded_metadata(self):
        for section in (None, "creative", "governor", "website"):
            value = fixture()
            (value[section] if section else value)["api_key"] = "private-example"
            with self.subTest(section=section), self.assertRaises(ValueError):
                self.read(value)
        for amount in ("NaN", "Infinity", "-1", "1e6", "0." + "1" * 19):
            value = fixture()
            value["governor"]["resources"]["held"]["credits"] = amount
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                self.read(value)

    def test_refresh_keeps_fixture_counts_out_of_live_metrics(self):
        self.read(fixture())
        config = self.root / "sources.json"
        config.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "components": [],
                    "repositories": [],
                    "integration_evidence_path": str(self.path),
                }
            )
        )
        (self.root / "dashboard-template.html").write_text("__TRACKING_DATA__")
        result = tracker.refresh(config, self.root, mcp_config=self.root / "missing.toml")
        self.assertEqual(result["integration"]["website"]["events"], 2)
        self.assertTrue(all(v is None for v in result["website"]["funnel"].values()))
        self.assertEqual(result["integration"]["creative"]["actual_spend"], None)
        events = [
            json.loads(v) for v in (self.root / "observed-events.jsonl").read_text().splitlines()
        ]
        self.assertIn("local_e2e_validation_snapshot", {v["kind"] for v in events})


if __name__ == "__main__":
    unittest.main()
