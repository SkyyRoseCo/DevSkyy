"""Synthetic local jobs and signed accounting fixtures; no provider or owner approval."""

import hashlib
import json
import shutil
import socket
import sqlite3
import struct
import subprocess
import sys
import threading
import time
import zlib
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import HTTPException
from fastapi.testclient import TestClient
from PIL import Image
from starlette.requests import Request

from skyyrose.core.context_resolver import ResolutionRequest, SourceReference
from skyyrose.core.creative_job import (
    GATES,
    JobPlan,
    VerificationRecord,
    audit_bundle,
    build_job,
    execution_bundle,
)
from skyyrose.core.paths import REPO_ROOT
from skyyrose.elite_studio.creative.editorial import (
    Direction,
    ResolvedEditorial,
    run_editorial,
)
from skyyrose.elite_studio.creative.governor_reporting import ReadOnlyLedger
from skyyrose.elite_studio.creative.local_composite import AssetRef, LocalCompositeGrant, Placement
from skyyrose.elite_studio.creative.receipt_reader import ReceiptError, _read, read_receipt_run
from skyyrose.elite_studio.creative.reporting_app import (
    ReportConfig,
    create_reporting_app,
    report_signature,
)
from skyyrose.elite_studio.creative.spend_ledger import (
    LedgerError,
    SpendAuthority,
    SpendDenied,
    SpendGrant,
    SpendLedger,
)


@pytest.fixture(autouse=True)
def forbid_network(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("Network/provider execution forbidden in local report tests")

    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket, "create_connection", denied)


def asset(path: Path) -> AssetRef:
    return AssetRef(str(path.relative_to(REPO_ROOT)), hashlib.sha256(path.read_bytes()).hexdigest())


def build_local_fixture(directory: Path):
    """Reusable synthetic replay builder. Directory must be inside REPO_ROOT."""
    directory = directory.resolve()
    directory.relative_to(REPO_ROOT)
    directory.mkdir(parents=True, exist_ok=True)
    source = directory / "source.png"
    mask = directory / "mask.png"
    background = directory / "background.png"
    Image.new("RGB", (4, 4), (30, 70, 90)).save(source)
    Image.new("L", (4, 4), 255).save(mask)
    Image.new("RGB", (8, 8), (110, 130, 160)).save(background)
    bound_source = asset(source)
    request = ResolutionRequest.model_validate_json(
        (REPO_ROOT / "docs/examples/context-resolver-abstract.json").read_text()
    ).model_copy(update={"job_id": f"synthetic-local-{directory.name}", "place_relevant": False})
    plan = JobPlan(
        deliverables=["Synthetic fixture PNG"],
        experience_outcome="Test bounded receipt flow",
        authored_meaning="Synthetic internal fixture only",
        production_method={
            "technique": "SOURCE_COMPOSITE",
            "rationale": "Synthetic source preservation",
            "inputs": [{"path": bound_source.path, "sha256": bound_source.sha256}],
            "feasibility_evidence": [],
        },
        success_evidence=["Independent local pixel checks"],
        channel_requirements=["Internal fixture"],
        approval_requirements=["Owner review"],
        novelty_dimensions=[],
        major_initiative=False,
        accessibility_applicable=False,
        accessibility_reason="Internal test fixture",
        commerce_applicable=False,
        commerce_reason="No commerce action",
    )
    job = build_job(request, plan)
    assert not job.blockers

    class Adapter:
        def resolve(self):
            return ResolvedEditorial(execution_bundle(job), audit_bundle(job), bound_source)

    run = directory / "run"
    direction = Direction(
        "test",
        "Synthetic fixture",
        "Synthetic fixture",
        "Synthetic fixture",
        "Synthetic fixture",
        "Synthetic non-product pixels",
        "Synthetic fixture",
        "Synthetic fixture",
        "Synthetic fixture",
        asset(background),
        asset(mask),
        Placement(2, 2),
    )
    production = run_editorial(
        Adapter(),
        [direction],
        root=REPO_ROOT,
        output_dir=run,
        grant=LocalCompositeGrant(
            job.job_id,
            bound_source.sha256,
            str(directory.relative_to(REPO_ROOT)),
            "synthetic-local-test",
        ),
        simulated=True,
    )
    return job, run, production


@pytest.fixture
def local_run():
    with TemporaryDirectory(prefix="creative-report-fixture-", dir=REPO_ROOT) as folder:
        yield build_local_fixture(Path(folder))


def test_real_non_sku_job_local_pixels_receipt_projection(local_run):
    job, run, production = local_run
    report = read_receipt_run(REPO_ROOT, run)
    assert report["job_id"] == job.job_id
    assert report["contract_id"] == job.contract_id
    assert report["evidence_mode"] == "SIMULATED"
    assert (
        report["artifacts"][0]["artifact_sha256"]
        == production["candidates"][0]["receipt"]["output_sha256"]
    )
    assert report["artifacts"][0]["technical_status"] == "PASS"
    assert report["artifacts"][0]["review_state"] == "MISSING"
    assert report["owner_acceptance"] == "BLOCKED"
    assert report["actual_spend"] is report["current_provider_execution"] is None
    assert not report["publication_authorized"] and not report["spend_authorized"]
    assert "Synthetic fixture" not in json.dumps(report)
    assert "raw_product_snapshots" not in json.dumps(report)


def test_json_read_is_bounded_even_when_initial_stat_changes(tmp_path, monkeypatch):
    from io import BytesIO

    path = tmp_path / "small.json"
    path.write_text("{}")
    requested = []

    class GrowingFile(BytesIO):
        def read(self, size=-1):
            requested.append(size)
            return super().read(size)

    monkeypatch.setattr(Path, "open", lambda *a, **k: GrowingFile(b"x" * 1000))
    with pytest.raises(ReceiptError, match="bounded"):
        _read(tmp_path, path, 100)
    assert requested == [101]


def test_oversized_png_header_is_normalized_as_receipt_error(local_run, monkeypatch):
    job, run, production = local_run
    ref = production["candidates"][0]["receipt"]["request"]["source"]
    ihdr = struct.pack(">IIBBBBB", 20000, 20000, 8, 2, 0, 0, 0)

    def chunk(kind, data):
        return (
            struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
        )

    # Tiny hostile header fixture, no large image allocation or generation.
    (REPO_ROOT / ref["path"]).write_bytes(
        b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IEND", b"")
    )
    # Preserve source hash during fresh job rebuild to reach image preflight itself.
    monkeypatch.setattr(
        "skyyrose.elite_studio.creative.receipt_reader.build_job", lambda *a, **k: job
    )
    with pytest.raises(ReceiptError) as caught:
        read_receipt_run(REPO_ROOT, run)
    assert isinstance(caught.value.__cause__, Image.DecompressionBombError)


def test_caller_review_owner_name_does_not_authenticate_acceptance(local_run):
    job, run, production = local_run
    receipt = production["candidates"][0]["receipt"]
    artifact = SourceReference(path=receipt["output_path"], sha256=receipt["output_sha256"])
    records = []
    for gate in GATES:
        applicable = gate not in {"PRODUCT_FIDELITY", "ACCESSIBILITY", "COMMERCE_INTEGRITY"}
        records.append(
            VerificationRecord(
                gate=gate,
                contract_id=job.contract_id,
                artifact=artifact,
                applicable=applicable,
                applicability_reason="Synthetic fixture",
                result="PASS" if applicable else None,
                reviewer="Corey",
                method="Untrusted caller string",
                recorded_at="2026-09-29T00:00:00Z",
                observations="Caller text cannot prove owner identity",
                evidence=[artifact],
            ).model_dump()
        )
    (run / "review.json").write_text(json.dumps({"records": records}))
    report = read_receipt_run(REPO_ROOT, run)
    assert report["artifacts"][0]["review_state"] == "BLOCKED_OR_STALE"
    assert report["owner_acceptance"] == "BLOCKED"
    assert "Corey" not in json.dumps(report)


@pytest.mark.parametrize(
    "record", ["execution.json", "audit.json", "context-link.json", "production.json"]
)
def test_changed_cross_record_hash_or_contract_refused(local_run, record):
    _, run, _ = local_run
    path = run / record
    value = json.loads(path.read_text())
    value["job_id"] = "different-job"
    path.write_text(json.dumps(value))
    with pytest.raises(ReceiptError):
        read_receipt_run(REPO_ROOT, run)


def test_changed_pixels_and_receipt_symlink_escape_refused(local_run, tmp_path):
    _, run, _ = local_run
    frame = run / "test.png"
    frame.write_bytes(b"changed")
    with pytest.raises(ReceiptError):
        read_receipt_run(REPO_ROOT, run)
    frame.unlink()
    escaped = tmp_path / "escaped.png"
    escaped.write_bytes(b"secret")
    frame.symlink_to(escaped)
    with pytest.raises(ReceiptError, match="escapes"):
        read_receipt_run(REPO_ROOT, run)


def test_receipt_bounded_json_file_count_and_missing_files(local_run):
    _, run, _ = local_run
    with pytest.raises(ReceiptError, match="file count"):
        read_receipt_run(REPO_ROOT, run, max_files=2)
    with pytest.raises(ReceiptError, match="JSON"):
        read_receipt_run(REPO_ROOT, run, max_json_bytes=10)
    (run / "audit.json").unlink()
    with pytest.raises(ReceiptError):
        read_receipt_run(REPO_ROOT, run)


def build_accounting_fixture(
    directory: Path, *, job_id="fixture-job", grant_id="fixture-grant", contract_id="a" * 64
):
    """Reusable signed SIMULATED ledger builder; never submits a provider call."""
    directory.mkdir(parents=True, exist_ok=True)
    authority = SpendAuthority(Ed25519PrivateKey.generate())
    integrity = b"synthetic-integrity-key-32-bytes!!"
    database = directory / "fixture.sqlite"
    ledger = SpendLedger(database, authority.public_key, integrity)
    signed = authority.issue(
        SpendGrant(
            grant_id,
            job_id,
            ("synthetic-provider",),
            ("fixture",),
            {"usd": "10.000000000000000001", "credits": "20"},
            {"usd": "3", "credits": "5"},
            "2099-01-01T00:00:00Z",
        )
    )
    ledger.install_grant(signed)

    def reserve(operation):
        return ledger.reserve(
            operation,
            grant_id=grant_id,
            job_id=job_id,
            provider="synthetic-provider",
            purpose="fixture",
            direction="test",
            stage="fixture",
            maximum={"usd": "2.000000000000000001", "credits": "4"},
            reason="Synthetic fixture only",
            contract_digest=contract_id,
            metadata={
                "simulated": True,
                "prompt": "MUST NOT LEAK",
                "url": "https://example.test/private",
                "arbitrary": "hidden",
            },
        )

    return ledger, authority, integrity, database, reserve


@pytest.fixture
def accounting(tmp_path):
    return build_accounting_fixture(tmp_path)


def readonly(accounting, checkpoint=None):
    ledger, authority, integrity, database, _ = accounting
    return ReadOnlyLedger(
        database,
        authority.public_key,
        integrity,
        minimum_checkpoint=checkpoint or ledger.checkpoint(),
    )


def test_synchronous_ledger_report_runs_outside_asgi_event_loop(accounting, monkeypatch):
    ledger, authority, integrity, database, reserve = accounting
    reserve("fixture-operation-1")
    key = b"synthetic-report-authentication-32bytes!!"
    app = create_reporting_app(
        ReportConfig(
            database,
            authority.public_key,
            integrity,
            ledger.checkpoint(),
            key,
            "fixture-site",
            frozenset({("fixture-job", "fixture-grant")}),
        )
    )
    loop_threads = []
    report_threads = []

    @app.middleware("http")
    async def remember_loop_thread(request, call_next):
        loop_threads.append(threading.get_ident())
        return await call_next(request)

    original = ReadOnlyLedger.report

    def inspected_report(self, **kwargs):
        report_threads.append(threading.get_ident())
        return original(self, **kwargs)

    monkeypatch.setattr(ReadOnlyLedger, "report", inspected_report)
    path = "/v1/governor/report/fixture-job/fixture-grant"
    # Assert execution threads rather than a flaky elapsed-time threshold.
    stamp = str(int(time.time()))
    with TestClient(app) as client:
        response = client.get(
            path,
            headers={
                "X-Report-Site": "fixture-site",
                "X-Report-Timestamp": stamp,
                "X-Report-Signature": report_signature(
                    key, timestamp=stamp, path=path, site_id="fixture-site"
                ),
            },
        )
    assert response.status_code == 200
    assert loop_threads and report_threads
    assert report_threads[0] != loop_threads[0]


def test_non_ascii_report_signature_is_denied_instead_of_crashing(accounting):
    ledger, authority, integrity, database, _ = accounting
    app = create_reporting_app(
        ReportConfig(
            database,
            authority.public_key,
            integrity,
            ledger.checkpoint(),
            b"synthetic-report-authentication-32bytes!!",
            "fixture-site",
            frozenset({("fixture-job", "fixture-grant")}),
        ),
        clock=lambda: 1234567890,
    )
    route = next(
        r
        for r in app.routes
        if getattr(r, "path", None) == "/v1/governor/report/{job_id}/{grant_id}"
    )
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/v1/governor/report/fixture-job/fixture-grant",
            "query_string": b"",
            "headers": [
                (b"x-report-timestamp", b"1234567890"),
                (b"x-report-site", b"fixture-site"),
                (b"x-report-signature", b"\xff" * 64),
            ],
        }
    )
    with pytest.raises(HTTPException) as denied:
        route.endpoint(request, "fixture-job", "fixture-grant")
    assert denied.value.status_code == 401


def test_signed_held_reconciled_rejected_record_projection_identity(accounting):
    ledger, _, _, _, reserve = accounting
    reserve("fixture-operation-1")
    held = readonly(accounting).report(job_id="fixture-job", grant_id="fixture-grant")
    assert held["resources"]["held"]["usd"] == "2.000000000000000001"
    assert held["resources"]["available"]["usd"] == "8.000000000000000000"
    assert held["operations"][0]["billing_unknown"]
    with pytest.raises(SpendDenied, match="Unresolved"):
        reserve("fixture-operation-2")
    ledger.mark_submitted("fixture-operation-1", "synthetic-task-1")
    ledger.record_outcome("fixture-operation-1", "FAILED")
    assert (
        readonly(accounting).report(job_id="fixture-job", grant_id="fixture-grant")["resources"][
            "held"
        ]["credits"]
        == "4"
    )
    ledger.reconcile(
        "fixture-operation-1", {"usd": "1.000000000000000001", "credits": "2"}, "SYNTHETIC_BILLING"
    )
    ledger.record_review("fixture-operation-1", {"decision": "REJECT", "reviewer": "Corey"})
    report = readonly(accounting).report(job_id="fixture-job", grant_id="fixture-grant")
    assert report["ledger"]["head_sequence"] == ledger.checkpoint()["sequence"]
    operation = report["operations"][0]
    assert operation["operation_id"] == "fixture-operation-1"
    assert operation["job_id"] == "fixture-job" and operation["grant_id"] == "fixture-grant"
    assert operation["contract_id"] == "a" * 64 and operation["task_id"] == "synthetic-task-1"
    assert operation["state"] == "FAILED" and operation["review_state"] == "RECORDED"
    assert not operation["billing_unknown"]
    assert report["resources"]["consumed"]["usd"] == "1.000000000000000001"
    assert report["resources"]["held"]["usd"] == "0"
    assert report["evidence_mode"] == "SIMULATED"
    assert report["owner_acceptance"] == "UNVERIFIED"
    assert report["actual_spend"] is report["current_provider_execution"] is None
    for secret in ("MUST NOT LEAK", "example.test", "signature", "issued_by", "Corey", "arbitrary"):
        assert secret not in json.dumps(report)


def test_read_only_snapshot_never_constructs_writable_ledger_or_changes_bytes(
    accounting, monkeypatch
):
    _, _, _, database, reserve = accounting
    reserve("fixture-operation-1")
    reader = readonly(accounting)
    before = database.read_bytes()
    monkeypatch.setattr(
        SpendLedger, "__init__", lambda *a, **k: pytest.fail("Writable ledger constructed")
    )
    reader.report(job_id="fixture-job", grant_id="fixture-grant")
    assert database.read_bytes() == before
    assert not hasattr(reader, "reserve") and not hasattr(reader, "install_grant")
    with reader._connect() as connection:
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            connection.execute("UPDATE ledger_head SET sequence=0")
    assert database.read_bytes() == before


def test_report_uses_one_consistent_snapshot_during_concurrent_writer(accounting, monkeypatch):
    ledger, _, _, database, reserve = accounting
    with sqlite3.connect(database) as writer:
        writer.execute("PRAGMA journal_mode=WAL")
    reader = readonly(accounting)
    prior_sequence = ledger.checkpoint()["sequence"]
    load = reader._load

    def append_after_snapshot(connection):
        reserve("fixture-concurrent-operation")
        return load(connection)

    monkeypatch.setattr(reader, "_load", append_after_snapshot)
    projection = reader.report(job_id="fixture-job", grant_id="fixture-grant")
    assert projection["ledger"]["head_sequence"] == prior_sequence
    assert projection["operations"] == []
    fresh = readonly(accounting).report(job_id="fixture-job", grant_id="fixture-grant")
    assert fresh["ledger"]["head_sequence"] > prior_sequence
    assert fresh["operations"][0]["operation_id"] == "fixture-concurrent-operation"


def test_report_non_simulated_record_label_does_not_manufacture_execution(accounting):
    ledger, _, _, _, _ = accounting
    ledger.reserve(
        "unclassified-operation",
        grant_id="fixture-grant",
        job_id="fixture-job",
        provider="synthetic-provider",
        purpose="fixture",
        direction="test",
        stage="fixture",
        maximum={"usd": "1", "credits": "1"},
        reason="Unclassified ledger record",
        contract_digest="a" * 64,
        metadata={
            "evidence_mode": "AUTHENTICATED",
            "owner_approved": True,
            "actual_spend": "1",
            "current_provider_execution": "live",
        },
    )
    report = readonly(accounting).report(job_id="fixture-job", grant_id="fixture-grant")
    assert report["evidence_mode"] == "LEDGER_RECORDS_ONLY"
    assert report["actual_spend"] is report["current_provider_execution"] is None
    assert report["owner_acceptance"] == "UNVERIFIED"


def test_signature_hmac_tamper_and_whole_database_rollback_refused(accounting, tmp_path):
    ledger, authority, integrity, database, reserve = accounting
    prior = tmp_path / "prior.sqlite"
    shutil.copyfile(database, prior)
    reserve("fixture-operation-1")
    checkpoint = ledger.checkpoint()
    with pytest.raises(LedgerError, match="rollback"):
        ReadOnlyLedger(
            prior, authority.public_key, integrity, minimum_checkpoint=checkpoint
        ).report(job_id="fixture-job", grant_id="fixture-grant")
    with sqlite3.connect(database) as connection:
        connection.execute("DROP TRIGGER no_event_update")
        connection.execute("UPDATE economic_events SET event_hash=? WHERE sequence=1", ("f" * 64,))
    with pytest.raises(LedgerError, match="integrity"):
        readonly(accounting, checkpoint).report(job_id="fixture-job", grant_id="fixture-grant")


def test_authority_key_mismatch_refused(accounting):
    ledger, _, integrity, database, reserve = accounting
    reserve("fixture-operation-1")
    other = SpendAuthority(Ed25519PrivateKey.generate())
    with pytest.raises(SpendDenied, match="signature"):
        ReadOnlyLedger(
            database, other.public_key, integrity, minimum_checkpoint=ledger.checkpoint()
        ).report(job_id="fixture-job", grant_id="fixture-grant")


def report_client(accounting):
    ledger, authority, integrity, database, _ = accounting
    config = ReportConfig(
        database,
        authority.public_key,
        integrity,
        ledger.checkpoint(),
        b"synthetic-read-auth-key-32-bytes!!",
        "fixture-site",
        frozenset({("fixture-job", "fixture-grant")}),
    )
    instant = datetime(2026, 9, 29, tzinfo=UTC).timestamp()
    client = TestClient(create_reporting_app(config, clock=lambda: instant))
    path = "/v1/governor/report/fixture-job/fixture-grant"
    timestamp = str(int(instant))
    headers = {
        "X-Report-Timestamp": timestamp,
        "X-Report-Site": config.site_id,
        "X-Report-Signature": report_signature(
            config.authentication_key, timestamp=timestamp, path=path, site_id=config.site_id
        ),
    }
    return client, path, headers, config


def test_app_authenticated_scoped_read_no_store_and_no_writable_construction(
    accounting, monkeypatch
):
    _, _, _, database, reserve = accounting
    reserve("fixture-operation-1")
    client, path, headers, _ = report_client(accounting)
    before = database.read_bytes()
    monkeypatch.setattr(
        SpendLedger, "__init__", lambda *a, **k: pytest.fail("Writable ledger constructed")
    )
    response = client.get(path, headers=headers)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["evidence_mode"] == "SIMULATED"
    assert response.json()["actual_spend"] is response.json()["current_provider_execution"] is None
    assert database.read_bytes() == before


@pytest.mark.parametrize(
    "failure",
    ["missing", "wrong-site", "old-timestamp", "wrong-signature", "wrong-route", "mode-spoof"],
)
def test_report_auth_route_timestamp_site_and_mode_negatives(accounting, failure):
    _, _, _, _, reserve = accounting
    reserve("fixture-operation-1")
    client, path, headers, _ = report_client(accounting)
    expected = 401
    if failure == "missing":
        headers = {}
    elif failure == "wrong-site":
        headers["X-Report-Site"] = "different-site"
    elif failure == "old-timestamp":
        headers["X-Report-Timestamp"] = "1"
    elif failure == "wrong-signature":
        headers["X-Report-Signature"] = "0" * 64
    elif failure == "wrong-route":
        path = path.replace("fixture-grant", "different-grant")
    else:
        path += "?evidence_mode=AUTHENTICATED&owner_accepted=true"
        expected = 400
    response = client.get(path, headers=headers)
    assert response.status_code == expected
    assert response.headers["cache-control"] == "no-store"
    assert "signature" not in response.text.lower()


def test_report_missing_configuration_fail_closed_and_mutations_absent():
    client = TestClient(create_reporting_app())
    path = "/v1/governor/report/fixture-job/fixture-grant"
    response = client.get(path)
    assert response.status_code == 503 and response.headers["cache-control"] == "no-store"
    assert client.post(path, json={"spend": "1"}).status_code == 405
    assert client.get("/openapi.json").status_code == 404


@pytest.mark.parametrize("failure", ["missing-database", "corrupt-database", "wrong-checkpoint"])
def test_report_evidence_failures_are_closed_503(accounting, failure):
    _, _, _, database, reserve = accounting
    reserve("fixture-operation-1")
    client, path, headers, config = report_client(accounting)
    if failure == "missing-database":
        database.unlink()
    elif failure == "corrupt-database":
        database.write_bytes(b"invalid SQLite")
    else:
        config.minimum_checkpoint["hash"] = "f" * 64
    response = client.get(path, headers=headers)
    assert response.status_code == 503
    assert response.headers["cache-control"] == "no-store"


def test_isolated_report_app_import_has_no_api_runtime_sdk_or_network():
    script = """
import importlib.abc
import socket
import sys
class Forbid(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in {"api", "openai", "anthropic", "runwayml", "langgraph"}:
            raise AssertionError("Forbidden import: " + fullname)
sys.meta_path.insert(0, Forbid())
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(AssertionError("Network"))
from skyyrose.elite_studio.creative.reporting_app import create_reporting_app
from skyyrose.elite_studio.creative.spend_ledger import SpendLedger
SpendLedger.__init__ = lambda *a, **k: (_ for _ in ()).throw(AssertionError("Writable ledger"))
app = create_reporting_app()
assert "skyyrose.elite_studio.creative.runner" not in sys.modules
assert "skyyrose.elite_studio.creative.router" not in sys.modules
assert "skyyrose.elite_studio.creative.runway_paid_transport" not in sys.modules
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=REPO_ROOT,
        env={"PYTHONPATH": str(REPO_ROOT)},
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("headers_mode", ["missing", "invalid"])
def test_unauthenticated_report_cannot_discover_allowed_scopes(
    accounting, monkeypatch, headers_mode
):
    client, allowed, headers, _ = report_client(accounting)
    monkeypatch.setattr(
        ReadOnlyLedger, "__init__", lambda *a, **k: pytest.fail("Unauthenticated ledger read")
    )
    headers = {} if headers_mode == "missing" else {**headers, "X-Report-Signature": "0" * 64}
    known = client.get(allowed, headers=headers)
    unknown = client.get(allowed.replace("fixture-grant", "unknown-grant"), headers=headers)
    assert known.status_code == unknown.status_code == 401
    assert known.json() == unknown.json()


def test_authenticated_report_still_denies_ungranted_scope(accounting, monkeypatch):
    client, path, headers, config = report_client(accounting)
    path = path.replace("fixture-grant", "unknown-grant")
    headers["X-Report-Signature"] = report_signature(
        config.authentication_key,
        timestamp=headers["X-Report-Timestamp"],
        path=path,
        site_id=config.site_id,
    )
    monkeypatch.setattr(
        ReadOnlyLedger, "__init__", lambda *a, **k: pytest.fail("Unauthorized ledger read")
    )
    response = client.get(path, headers=headers)
    assert response.status_code == 403
    assert response.json() == {"detail": "Report scope denied"}
