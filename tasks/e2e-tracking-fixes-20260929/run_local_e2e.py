"""Reproduce the consent-relay/storage and receipt/ledger paths without external I/O.

All credentials, orders, pixels and accounting units here are synthetic fixtures.
This runner does not start the enterprise app or acquire provider transports.
"""

import argparse
import asyncio
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from api.v1.analytics.event_store import StorefrontAnalyticsEvent  # noqa: E402
from api.v1.analytics.ingest import router  # noqa: E402
from api.v1.woocommerce_webhooks import router as webhook_router  # noqa: E402
from api.v1.wordpress_integration import WordPressSettings, get_settings  # noqa: E402
from database.db import get_db  # noqa: E402
from security.jwt_oauth2_auth import jwt_manager  # noqa: E402
from skyyrose.elite_studio.creative.governor_reporting import ReadOnlyLedger  # noqa: E402
from skyyrose.elite_studio.creative.receipt_reader import read_receipt_run  # noqa: E402
from skyyrose.elite_studio.creative.reporting_app import (  # noqa: E402
    ReportConfig,
    create_reporting_app,
    report_signature,
)
from tests.api.analytics.test_storefront_ingest import paid_order, webhook  # noqa: E402
from tests.test_creative_reporting import (  # noqa: E402
    build_accounting_fixture,
    build_local_fixture,
)


async def website_replay(directory: Path, checks: list) -> dict:
    os.environ.update(
        {
            "SKYYROSE_ANALYTICS_SITE_ID": "fixture-site",
            "SKYYROSE_ANALYTICS_ENVIRONMENT": "test",
            "SKYYROSE_ANALYTICS_SECRET": "fixture-only-private-signing-secret-00001",
            "SKYYROSE_ANALYTICS_SITE_URL": "https://synthetic.example.test",
        }
    )
    jwt_manager.config.secret_key = "offline-synthetic-jwt-" + "0" * 64
    php = shutil.which("php")
    if php is None:
        raise RuntimeError("PHP is required for the offline signed WordPress relay replay")
    signed = json.loads(
        subprocess.check_output(
            [
                php,
                str(ROOT / "wordpress-theme/skyyrose-flagship/tests/analytics/signed-envelope.php"),
            ],
            text=True,
            cwd=ROOT,
        )
    )
    database = directory / "events.sqlite"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{database}",
        execution_options={"schema_translate_map": {"public": None}},
    )
    async with engine.begin() as connection:
        await connection.run_sync(StorefrontAnalyticsEvent.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)

    async def db_dependency():
        async with sessions() as session:
            yield session

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.include_router(webhook_router, prefix="/api/v1")
    app.dependency_overrides[get_db] = db_dependency
    app.dependency_overrides[get_settings] = lambda: WordPressSettings(
        site_url="https://synthetic.example.test",
        webhook_secret="offline-synthetic-wc-secret-000000000000",
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app), base_url="http://fixture.test"
    ) as client:
        response = await client.post(
            "/api/v1/analytics/ingest", content=signed["body"], headers=signed["headers"]
        )
        assert response.status_code == 200 and response.json()["accepted"] == 1
        repeated = await client.post(
            "/api/v1/analytics/ingest", content=signed["body"], headers=signed["headers"]
        )
        assert repeated.json()["accepted"] == 0 and repeated.json()["duplicates"] == 1
        tampered = await client.post(
            "/api/v1/analytics/ingest", content=signed["body"] + " ", headers=signed["headers"]
        )
        assert tampered.status_code == 401
        order = paid_order()
        captured = await webhook(client, order)
        assert captured.status_code == 200
        duplicate_order = await webhook(client, order)
        assert duplicate_order.status_code == 200
        path = "/api/v1/analytics/events/summary?site_id=fixture-site&environment=test&days=7"
        assert (await client.get(path)).status_code == 401
        token = jwt_manager.create_access_token("offline-synthetic-user", ["admin"])
        summary = await client.get(path, headers={"Authorization": f"Bearer {token}"})
        assert summary.status_code == 200
        value = summary.json()
        assert value["coverage"]["synthetic_events_excluded"] == 2
        assert value["metrics"]["verified_revenue"] is None
        assert value["metrics"]["conversion_rate"] is None
        (directory / "website-summary.json").write_text(json.dumps(value, indent=2) + "\n")
        async with sessions() as db:
            rows = (await db.execute(select(StorefrontAnalyticsEvent))).scalars().all()
            assert len(rows) == 2
            assert all(row.properties["synthetic"] is True for row in rows)
            assert "discarded-private" not in json.dumps([row.properties for row in rows])
            paid = sum(row.source == "skyyrose.woocommerce_paid_order" for row in rows)
    await engine.dispose()
    code = """
import asyncio
import sys
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from api.v1.analytics.event_store import StorefrontAnalyticsEvent

async def read():
    engine = create_async_engine(
        "sqlite+aiosqlite:///" + sys.argv[1],
        execution_options={"schema_translate_map": {"public": None}},
    )
    try:
        async with async_sessionmaker(engine)() as session:
            result = await session.execute(select(func.count(StorefrontAnalyticsEvent.id)))
            print(result.scalar())
    finally:
        await engine.dispose()

asyncio.run(read())
"""
    count = subprocess.check_output(
        [sys.executable, "-c", code, str(database)],
        cwd=ROOT,
        text=True,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
    )
    assert count.strip() == "2"
    checks.append(
        {
            "name": "PHP relay → API → durable restart → protected summary",
            "status": "PASS",
            "detail": "Actual PHP HMAC accepted once; duplicate retry safe; raw-byte tamper and anonymous report rejected; two synthetic rows reopened in a separate Python process.",
        }
    )
    checks.append(
        {
            "name": "Purchase and fixture authority",
            "status": "PASS",
            "detail": "Signed WooCommerce paid order is separate from browser engagement; duplicate order retained once; both test rows excluded from actual revenue, conversion and attribution.",
        }
    )
    return {
        "site_id": "fixture-site",
        "environment": "test",
        "events": 2,
        "paid_orders": paid,
        "purchase_attribution": None,
    }


def creative_replay(directory: Path, checks: list) -> tuple[dict, dict]:
    job, run, _ = build_local_fixture(directory / "creative")
    receipt = read_receipt_run(ROOT, run)
    assert receipt["owner_acceptance"] == "BLOCKED"
    assert receipt["evidence_mode"] == "SIMULATED"
    ledger, authority, integrity, database, reserve = build_accounting_fixture(
        directory / "accounting",
        job_id=job.job_id,
        contract_id=job.contract_id,
    )
    reserve("fixture-operation")
    held = ReadOnlyLedger(
        database, authority.public_key, integrity, minimum_checkpoint=ledger.checkpoint()
    ).report(job_id=job.job_id, grant_id="fixture-grant")
    assert held["resources"]["held"]["credits"] == "4"
    ledger.mark_submitted("fixture-operation", "synthetic-task")
    ledger.record_outcome("fixture-operation", "FAILED")
    ledger.reconcile(
        "fixture-operation", {"usd": "1.000000000000000001", "credits": "2"}, "SYNTHETIC_BILLING"
    )
    ledger.record_review(
        "fixture-operation", {"decision": "REJECT", "reviewer": "synthetic-reviewer"}
    )
    checkpoint = ledger.checkpoint()
    digest = hashlib.sha256(database.read_bytes()).hexdigest()
    key = b"synthetic-report-authentication-32bytes!!"
    config = ReportConfig(
        database,
        authority.public_key,
        integrity,
        checkpoint,
        key,
        "fixture-site",
        frozenset({(job.job_id, "fixture-grant")}),
    )
    path = f"/v1/governor/report/{job.job_id}/fixture-grant"
    stamp = str(int(time.time()))
    with TestClient(create_reporting_app(config)) as client:
        assert client.get(path).status_code == 401
        response = client.get(
            path,
            headers={
                "X-Report-Timestamp": stamp,
                "X-Report-Site": "fixture-site",
                "X-Report-Signature": report_signature(
                    key, timestamp=stamp, path=path, site_id="fixture-site"
                ),
            },
        )
        assert response.status_code == 200 and response.headers["Cache-Control"] == "no-store"
        report = response.json()
    assert hashlib.sha256(database.read_bytes()).hexdigest() == digest
    assert report["operations"][0]["contract_id"] == job.contract_id
    assert report["actual_spend"] is None and report["current_provider_execution"] is None
    assert report["evidence_mode"] == "SIMULATED" and report["owner_acceptance"] == "UNVERIFIED"
    for name, value in (("creative-receipt.json", receipt), ("governor-report.json", report)):
        (directory / name).write_text(json.dumps(value, indent=2) + "\n")
    checks.append(
        {
            "name": "Creative context → pixels → receipt → Governor report",
            "status": "PASS",
            "detail": "Current non-SKU job produced local synthetic pixels; execution/audit/context/artifact hashes verified and bound to exact job/contract in signed accounting records.",
        }
    )
    checks.append(
        {
            "name": "Read-only reporting and authority isolation",
            "status": "PASS",
            "detail": "Anonymous read rejected; signed allowlisted read succeeded without ledger byte changes; held/reconciled/rejected fixture state preserved; owner acceptance, actual spend, provider execution and release remain unapproved or unknown.",
        }
    )
    creative = {
        "job_id": receipt["job_id"],
        "contract_id": receipt["contract_id"],
        "evidence_mode": receipt["evidence_mode"],
        "receipt_state": receipt["receipt_state"],
        "artifact_count": len(receipt["artifacts"]),
        "technical_passes": sum(a["technical_status"] == "PASS" for a in receipt["artifacts"]),
        **{
            k: receipt[k]
            for k in (
                "owner_acceptance",
                "publication_authorized",
                "spend_authorized",
                "actual_spend",
                "current_provider_execution",
            )
        },
    }
    governor = {
        "job_id": report["job_id"],
        "grant_id": report["grant_id"],
        "evidence_mode": report["evidence_mode"],
        "head_sequence": report["ledger"]["head_sequence"],
        "ledger_authenticated": report["ledger_authenticated"],
        "resources": report["resources"],
        "operations_count": len(report["operations"]),
        **{
            k: report[k] for k in ("owner_acceptance", "actual_spend", "current_provider_execution")
        },
    }
    return creative, governor


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture-directory", default="tasks/e2e-tracking-fixes-20260929/fixtures/combined-replay"
    )
    parser.add_argument(
        "--record", default="tasks/e2e-tracking-fixes-20260929/integration-evidence.json"
    )
    args = parser.parse_args()
    directory = (ROOT / args.fixture_directory).resolve()
    output = (ROOT / args.record).resolve()
    allowed_roots = (ROOT, Path(tempfile.gettempdir()).resolve(), Path("/tmp").resolve())
    if not all(
        any(path.is_relative_to(root) for root in allowed_roots) for path in (directory, output)
    ):
        raise SystemExit(
            "Fixture and record paths must remain inside the candidate or temporary root"
        )
    if output.exists():
        raise SystemExit("Use a fresh record path; prior replay evidence is preserved")
    if directory.exists():
        raise SystemExit("Use a fresh fixture directory; prior replay evidence is preserved")
    directory.mkdir(parents=True)
    checks = []
    website = asyncio.run(website_replay(directory, checks))
    creative, governor = creative_replay(directory, checks)
    record = {
        "schema_version": 1,
        "captured_at": datetime.now(UTC).isoformat(),
        "evidence_class": "REPRODUCED_LOCAL_FIXTURES",
        "authentication": "SYNTHETIC_LOCAL",
        "checks": checks,
        "creative": creative,
        "governor": governor,
        "website": website,
        "limitations": [
            "Local synthetic execution only; no customer data, paid generation or live provider transaction.",
            "Fixture totals are excluded from actual website metrics and actual spend.",
            "Live database capacity, stopped runtime, site secrets, migrations, production persistence and release remain separate gates.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(record, indent=2) + "\n")
    print(
        json.dumps(
            {
                "record": str(output),
                "checks": len(checks),
                "status": "PASS",
                "evidence": "REPRODUCED_LOCAL_FIXTURES",
            }
        )
    )


if __name__ == "__main__":
    main()
