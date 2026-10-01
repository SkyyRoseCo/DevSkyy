"""Focused offline tests of observation integrity, privacy and evidence scope."""

import json
import subprocess
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import refresh_tracking as tracker


class TrackingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / "sources.json"
        self.mcp = self.root / "config.toml"
        self.mcp.write_text("[mcp_servers.example]\nurl='https://example.org/mcp'\n")
        (self.root / "dashboard-template.html").write_text(
            '<script type="application/json" id="data">__TRACKING_DATA__</script>'
        )
        self.cfg = {
            "schema_version": 1,
            "components": [
                {
                    "id": "creative",
                    "category": "Creative OS",
                    "name": "Creative jobs",
                    "status": "OFFLINE_VERIFIED",
                    "evidence_class": "SOURCE_REPORTED_HISTORY",
                    "summary": "Historical tests passed.",
                    "source_paths": [],
                    "next_action": "Run authorized job.",
                    "owner": "Owner",
                }
            ],
            "repositories": [],
        }
        self.config.write_text(json.dumps(self.cfg))

    def refresh(self):
        return tracker.refresh(self.config, self.root, mcp_config=self.mcp)

    def test_relative_sources_bind_to_checkout_not_working_directory(self):
        repo = (self.root / "checkout").resolve()
        repo.mkdir()
        (repo / "evidence.json").write_text("{}")
        self.cfg["components"][0]["source_paths"] = ["evidence.json"]
        self.cfg["repositories"] = ["."]
        for key in (
            "manifest_path",
            "e2e_state_path",
            "connector_observations_path",
            "website_observations_path",
            "integration_evidence_path",
        ):
            self.cfg[key] = "evidence.json"
        self.config.write_text(json.dumps(self.cfg))
        with patch.object(tracker, "REPOSITORY_ROOT", repo):
            parsed = tracker.config_read(self.config)
        self.assertEqual(parsed["components"][0]["source_paths"], [str(repo / "evidence.json")])
        self.assertEqual(parsed["repositories"], [str(repo)])
        for key in (
            "manifest_path",
            "e2e_state_path",
            "connector_observations_path",
            "website_observations_path",
            "integration_evidence_path",
        ):
            self.assertEqual(parsed[key], str(repo / "evidence.json"))

    def test_relative_source_cannot_escape_checkout(self):
        with patch.object(tracker, "REPOSITORY_ROOT", self.root):
            with self.assertRaisesRegex(ValueError, "escapes repository"):
                tracker.source_path("../outside")
            (self.root / "escape").symlink_to(self.root.parent, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "escapes repository"):
                tracker.source_path("escape/outside")

    def test_shipped_config_is_portable_and_does_not_claim_execution(self):
        shipped = json.loads(Path(tracker.__file__).with_name("sources.json").read_text())
        self.assertEqual(shipped["repositories"], ["."])
        for component in shipped["components"]:
            self.assertEqual(component["evidence_class"], "SOURCE_INVENTORY_ONLY")
            for path in component["source_paths"]:
                self.assertFalse(Path(path).is_absolute())
                self.assertTrue((tracker.REPOSITORY_ROOT / path).is_file())

    def test_offline_cannot_contact_network(self):
        self.cfg["live_targets"] = [{"id": "site", "url": "https://skyyrose.co", "kind": "website"}]
        self.config.write_text(json.dumps(self.cfg))
        with patch.object(
            tracker, "observe_http", side_effect=AssertionError("Offline made request")
        ):
            result = self.refresh()
        self.assertEqual(result["live_observations"], [])
        self.assertEqual(result["mode"], "offline")

    def test_mcp_allowlist_drops_auth_args_and_uri_credentials(self):
        self.mcp.write_text(
            "[mcp_servers.test]\nurl='https://user:uri-secret@example.org/mcp?access_token=query-secret#fragment-secret'\ncommand='secret-command'\nargs=['arg-secret']\n[mcp_servers.test.http_headers]\nAuthorization='header-secret'\n[mcp_servers.test.env]\nPRIVATE_SECRET='env-secret'\n"
        )
        result = tracker.mcp_inventory(self.mcp)
        self.assertEqual(
            result,
            [
                {
                    "name": "test",
                    "url": "https://example.org",
                    "url_scope": "configured_origin",
                    "enabled": True,
                    "transport": "streamable_http",
                }
            ],
        )
        self.assertNotIn("secret", json.dumps(result))

    def test_hash_chain_refuses_value_tampering(self):
        self.refresh()
        path = self.root / "observed-events.jsonl"
        lines = path.read_text().splitlines()
        event = json.loads(lines[0])
        event["data"]["servers"] = []
        lines[0] = json.dumps(event)
        path.write_text("\n".join(lines) + "\n")
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            self.refresh()
        self.assertEqual(path.read_bytes(), before)

    def test_hash_chain_refuses_partial_and_complete_line_truncation(self):
        self.refresh()
        path = self.root / "observed-events.jsonl"
        original = path.read_bytes()
        for truncated in (original[:-3], original.rsplit(b"\n", 2)[0] + b"\n", b""):
            path.write_bytes(truncated)
            with self.subTest(length=len(truncated)), self.assertRaises(ValueError):
                self.refresh()
            self.assertEqual(path.read_bytes(), truncated)

    def test_hash_chain_refuses_missing_checkpoint(self):
        self.refresh()
        (self.root / ".observed-events.checkpoint.json").unlink()
        with self.assertRaises(ValueError):
            self.refresh()

    def test_append_only_observations_have_valid_unique_ids(self):
        first = self.refresh()
        original = (self.root / "observed-events.jsonl").read_bytes()
        second = self.refresh()
        self.assertEqual(second["history"]["event_count"], 2 * first["history"]["event_count"])
        body = (self.root / "observed-events.jsonl").read_bytes()
        self.assertTrue(body.startswith(original))
        ids = [json.loads(line)["observation_id"] for line in body.splitlines()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_script_injection_escaped_before_embedding(self):
        self.cfg["components"][0]["summary"] = "</script><script>alert('x')</script>&"
        self.config.write_text(json.dumps(self.cfg))
        (self.root / "dashboard-template.html").write_text(
            '<script type="application/json" id="data">__TRACKING_DATA__</script>'
        )
        self.refresh()
        html = (self.root / "dashboard.html").read_text()
        self.assertEqual(html.count("</script>"), 1)
        self.assertNotIn("<script>alert", html)
        self.assertIn("\\u003c/script\\u003e", html)
        self.assertIn("\\u0026", html)

    def test_no_synthetic_metrics_or_evidence_upgrade(self):
        result = self.refresh()
        self.assertEqual(result["components"], self.cfg["components"])
        self.assertTrue(all(v is None for v in result["website"]["funnel"].values()))
        self.assertEqual(result["website"]["captured_at"], None)
        self.assertEqual(result["website"]["evidence_class"], "unknown")
        self.assertNotIn("revenue", json.dumps(result))
        self.assertNotIn("provider_execution_enabled", result)

    def test_monthly_views_are_separate_source_dated_measurements(self):
        source = {
            "captured_at": "2026-09-28T10:00:00Z",
            "evidence_class": "AUTHENTICATED_LIVE_AGGREGATE_READ",
            "sites": [
                {
                    "site_id": 1,
                    "url": "https://skyyrose.co",
                    "primary_domain": "skyyrose.co",
                    "environment": "Staging",
                    "theme": "theme",
                    "monthly_views": 22,
                    "window_definition": "Exact dates unknown",
                }
            ],
            "funnel": dict.fromkeys(
                ("page_view", "view_item", "add_to_cart", "begin_checkout", "purchase")
            ),
            "limitations": ["Views are not unique visitors"],
        }
        path = self.root / "website-observations.json"
        path.write_text(json.dumps(source))
        result = self.refresh()["website"]
        self.assertEqual(result["captured_at"], source["captured_at"])
        self.assertEqual(result["sites"][0]["monthly_views"], 22)
        self.assertTrue(all(v is None for v in result["funnel"].values()))

    def test_known_redirect_boundary_rejects_external_and_credentials(self):
        self.assertTrue(
            tracker.redirect_allowed("https://skyyrose.co/", "https://skyyrose.wpcomstaging.com/")
        )
        self.assertTrue(
            tracker.redirect_allowed(
                "https://skyyrose.co/", "https://staging-7e48-skyyrose.wpcomstaging.com/"
            )
        )
        for bad in (
            "https://skyyrose.co.evil.example/",
            "https://evil.example/",
            "http://skyyrose.co/",
            "https://user:pass@skyyrose.co/",
            "https://skyyrose.co/?token=secret",
            "https://skyyrose.co:8443/",
        ):
            self.assertFalse(tracker.redirect_allowed("https://skyyrose.co/", bad), bad)

    def test_health_projection_does_not_accept_unlisted_truth(self):
        class Response:
            status = 200
            url = "https://example.fly.dev/health"

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def read(self, _):
                return b'{"status":"ok","service":"governor","version":"1.2.3","dry_run_enabled":false,"provider_execution_enabled":false,"release_ready":true,"api_key":"never-display"}'

        with patch.object(tracker.request, "build_opener") as opened:
            opened.return_value.open.return_value = Response()
            result = tracker.observe_http({"id": "health", "kind": "service", "url": Response.url})
        self.assertEqual(
            result["health"],
            {
                "status": "ok",
                "service": "governor",
                "version": "1.2.3",
                "dry_run_enabled": False,
                "provider_execution_enabled": False,
            },
        )
        self.assertNotIn("never-display", json.dumps(result))
        self.assertNotIn("release_ready", result["health"])

    def test_e2e_discards_unlisted_secret_fields(self):
        path = self.root / "e2e.json"
        path.write_text(
            json.dumps(
                {
                    "date": "2026-09-28",
                    "overall_status": "INCOMPLETE",
                    "password": "never-display",
                    "gates": {
                        "image": {
                            "status": "PASS",
                            "report": "/public/report.md",
                            "api_key": "never-display",
                            "required_for_os_e2e": False,
                        }
                    },
                }
            )
        )
        result = tracker.e2e_gates(path)
        self.assertNotIn("never-display", json.dumps(result))
        self.assertEqual(result["evidence_class"], "source_reported_historical")

    def test_strict_schema_rejects_embedded_secret_field(self):
        self.cfg["components"][0]["api_key"] = "never-display"
        self.config.write_text(json.dumps(self.cfg))
        with self.assertRaises(ValueError) as caught:
            self.refresh()
        self.assertNotIn("never-display", str(caught.exception))
        self.assertFalse((self.root / "observed-events.jsonl").exists())

    def test_ga4_identifiers_are_case_sensitive(self):
        html = "CSS-like g-deadbeef00 ; valid G-AB12CD3456 ; lowercase g-ab12cd3456"
        self.assertEqual(tracker.re.findall(r"\bG-[A-Z0-9]{6,}\b", html), ["G-AB12CD3456"])

    def test_manifest_detects_drift_and_escape(self):
        artifact = self.root / "artifact.txt"
        artifact.write_text("approved")
        source = {
            "candidate_root": str(self.root),
            "readiness": "CLEAN_CANDIDATE_VERIFIED",
            "files": [
                {"path": "artifact.txt", "candidate_sha256": tracker.file_state(artifact)["sha256"]}
            ],
        }
        path = self.root / "manifest.json"
        path.write_text(json.dumps(source))
        self.assertEqual(tracker.manifest_integrity(path)["status"], "MATCH")
        artifact.write_text("changed")
        self.assertEqual(tracker.manifest_integrity(path)["status"], "DRIFT")
        source["files"][0]["path"] = "../outside"
        path.write_text(json.dumps(source))
        with self.assertRaises(ValueError):
            tracker.manifest_integrity(path)

    def test_repository_counts_preserve_leading_status_space(self):
        outputs = iter(["a" * 40 + "\n", "main\n", " M file\0M  other\0?? new\0"])
        with patch.object(
            tracker.subprocess,
            "run",
            side_effect=lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout=next(outputs)),
        ):
            result = tracker.repository_state(self.root)
        self.assertEqual(
            (result["staged_count"], result["dirty_count"], result["untracked_count"]), (1, 1, 1)
        )

    def test_mcp_url_path_token_is_never_exported(self):
        self.mcp.write_text(
            "[mcp_servers.example]\nurl='https://example.org/mcp/private-token-0123456789abcdef'\n"
        )
        result = self.refresh()
        self.assertEqual(result["mcp_inventory"][0]["url"], "https://example.org")
        for name in ("snapshot.json", "observed-events.jsonl"):
            self.assertNotIn("private-token", (self.root / name).read_text())

    def test_source_config_and_collector_are_fingerprinted(self):
        for key in (
            "manifest_path",
            "e2e_state_path",
            "connector_observations_path",
            "website_observations_path",
        ):
            self.cfg[key] = str(self.root / (key + ".json"))
        self.config.write_text(json.dumps(self.cfg))
        result = self.refresh()
        paths = {str(Path(item["path"]).resolve()) for item in result["source_files"]}
        expected = {
            str(path.resolve())
            for path in (
                self.config,
                Path(tracker.__file__),
                *[Path(self.cfg[k]) for k in self.cfg if k.endswith("_path")],
            )
        }
        self.assertLessEqual(expected, paths)
        self.assertEqual(result["config_sha256"], tracker.file_state(self.config)["sha256"])
        self.assertEqual(
            result["collector_sha256"], tracker.file_state(Path(tracker.__file__))["sha256"]
        )

    def test_concurrent_refreshes_serialize_gather_and_projection(self):
        entered, release, second_read = threading.Event(), threading.Event(), threading.Event()
        actual_read = tracker.config_read
        calls = []

        def ordered_read(path):
            calls.append(len(calls) + 1)
            if len(calls) == 1:
                entered.set()
                self.assertTrue(release.wait(2))
            else:
                second_read.set()
            result = actual_read(path)
            result["components"][0]["summary"] = f"Capture {len(calls)}"
            return result

        with (
            patch.object(tracker, "config_read", side_effect=ordered_read),
            ThreadPoolExecutor(max_workers=2) as pool,
        ):
            first = pool.submit(self.refresh)
            self.assertTrue(entered.wait(2))
            second = pool.submit(self.refresh)
            self.assertFalse(second_read.wait(0.05))
            release.set()
            first.result(timeout=3)
            second.result(timeout=3)
        saved = json.loads((self.root / "snapshot.json").read_text())
        self.assertEqual(saved["components"][0]["summary"], "Capture 2")
        self.assertEqual(saved["history"]["event_count"], 12)

    def test_invalid_health_shape_becomes_error_observation(self):
        class Response:
            status = 200
            url = "https://example.fly.dev/health"

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def read(self, _):
                return b'["status", "secret-token"]'

        with patch.object(tracker.request, "build_opener") as opened:
            opened.return_value.open.return_value = Response()
            result = tracker.observe_http({"id": "health", "kind": "service", "url": Response.url})
        self.assertIn("error", result)
        self.assertNotIn("secret-token", json.dumps(result))
        self.assertNotIn("health", result)
        tracker.timestamp(result["captured_at"])

    def test_manifest_rejects_empty_invalid_and_duplicate_entries(self):
        path = self.root / "manifest.json"
        artifact = self.root / "artifact.txt"
        artifact.write_text("artifact")
        entry = {"path": "artifact.txt", "candidate_sha256": tracker.file_state(artifact)["sha256"]}
        for entries in ([], None, {}, ["invalid"], [entry, {**entry, "path": "./artifact.txt"}]):
            path.write_text(json.dumps({"candidate_root": str(self.root), "files": entries}))
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                tracker.manifest_integrity(path)

    def test_manifest_rejects_declared_file_count_mismatch(self):
        path = self.root / "manifest.json"
        artifact = self.root / "artifact.txt"
        artifact.write_text("artifact")
        source = {
            "candidate_root": str(self.root),
            "candidate_file_count_excluding_manifest": 2,
            "files": [
                {"path": "artifact.txt", "candidate_sha256": tracker.file_state(artifact)["sha256"]}
            ],
        }
        path.write_text(json.dumps(source))
        with self.assertRaises(ValueError):
            tracker.manifest_integrity(path)

    def test_missing_or_invalid_template_refused_before_event_append(self):
        path = self.root / "dashboard-template.html"
        path.unlink()
        with self.assertRaises(ValueError):
            self.refresh()
        self.assertFalse((self.root / "observed-events.jsonl").exists())
        path.write_text("No marker")
        with self.assertRaises(ValueError):
            self.refresh()
        self.assertFalse((self.root / "observed-events.jsonl").exists())

    def test_config_replaced_after_parse_refuses_mismatched_provenance(self):
        actual_read = tracker.config_read

        def replace_after_read(path):
            result = actual_read(path)
            replacement = json.loads(json.dumps(result))
            replacement["components"][0]["summary"] = "Changed configuration"
            path.write_text(json.dumps(replacement))
            return result

        with (
            patch.object(tracker, "config_read", side_effect=replace_after_read),
            self.assertRaises(ValueError),
        ):
            self.refresh()
        self.assertFalse((self.root / "observed-events.jsonl").exists())

    def test_manual_observation_replaced_after_parse_refuses_batch(self):
        path = self.root / "connector-observations.json"
        path.write_text(
            json.dumps(
                {
                    "captured_at": "2026-09-28T10:00:00Z",
                    "evidence_class": "AUTHENTICATED_LIVE_READ_ONLY",
                    "connectors": [],
                }
            )
        )
        actual_read = tracker.manual_observations

        def replace_after_read(source_path, kind):
            result = actual_read(source_path, kind)
            if kind == "connectors":
                replacement = json.loads(json.dumps(result))
                replacement["captured_at"] = "2026-09-28T11:00:00Z"
                source_path.write_text(json.dumps(replacement))
            return result

        with (
            patch.object(tracker, "manual_observations", side_effect=replace_after_read),
            self.assertRaises(ValueError),
        ):
            self.refresh()
        self.assertFalse((self.root / "observed-events.jsonl").exists())

    def test_source_directory_presence_is_separate_from_file_receipt_verification(self):
        directory = self.root / "artifacts"
        directory.mkdir()
        present = tracker.file_state(directory)
        absent = tracker.file_state(directory / "missing")
        self.assertEqual((present["exists"], present["kind"]), (True, "directory"))
        self.assertIsNone(present["bytes"])
        self.assertIsNone(present["sha256"])
        self.assertEqual((absent["exists"], absent["kind"]), (False, "missing"))
        self.assertIsNone(absent["bytes"])
        self.assertIsNone(absent["sha256"])
        self.assertIsNone(absent["modified_at"])


if __name__ == "__main__":
    unittest.main()
