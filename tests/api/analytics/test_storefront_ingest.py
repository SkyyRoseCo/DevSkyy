"""Offline synthetic fixtures prove transport, durable storage, and truth boundaries."""

import asyncio
import base64
import hashlib
import hmac
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from api.v1.analytics.business import router as business_router
from api.v1.analytics.event_store import StorefrontAnalyticsEvent, read_summary
from api.v1.analytics.ingest import canonical_site_origin, router
from api.v1.woocommerce_webhooks import router as webhook_router
from api.v1.wordpress_integration import WordPressSettings, get_settings
from database.db import get_db
from security.jwt_oauth2_auth import jwt_manager

SECRET = "offline-synthetic-analytics-secret-0000000000"
WC_SECRET = "offline-synthetic-wc-secret-000000000000"
SITE_URL = "https://synthetic.example.test"


@pytest.fixture
async def harness(tmp_path, monkeypatch):
    """Every event is synthetic and every request remains inside an ASGI test app."""
    monkeypatch.setenv("SKYYROSE_ANALYTICS_SITE_ID", "synthetic-site")
    monkeypatch.setenv("SKYYROSE_ANALYTICS_ENVIRONMENT", "test")
    monkeypatch.setenv("SKYYROSE_ANALYTICS_SECRET", SECRET)
    monkeypatch.setenv("SKYYROSE_ANALYTICS_SITE_URL", SITE_URL)
    monkeypatch.setattr(jwt_manager.config, "secret_key", "offline-synthetic-jwt-" + "0" * 64)
    db_path = tmp_path / "events.db"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
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
    app.include_router(business_router, prefix="/api/v1")
    app.include_router(webhook_router, prefix="/api/v1")
    app.dependency_overrides[get_db] = db_dependency
    app.dependency_overrides[get_settings] = lambda: WordPressSettings(
        site_url=SITE_URL, webhook_secret=WC_SECRET
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://offline.test"
    ) as client:
        yield client, sessions, db_path
    await engine.dispose()


def envelope(**changes):
    timestamp = datetime.now(UTC).isoformat()
    event = {
        "event_id": str(uuid4()),
        "session_id": "synthetic-session-00001",
        "event_type": "product_click",
        "occurred_at": timestamp,
        "page_type": "collection",
        "collection": "black-rose",
        "target": "/product/synthetic-sku",
        "properties": {"action": "product-click"},
        "synthetic": True,
    }
    value = {
        "schema_version": 1,
        "site_id": "synthetic-site",
        "environment": "test",
        "consent": "accepted",
        "sent_at": timestamp,
        "events": [event],
    }
    value.update(changes)
    return value


async def ingest(client, data, *, secret=SECRET, timestamp=None):
    body = json.dumps(data, separators=(",", ":"), allow_nan=True).encode()
    signed_at = str(timestamp if timestamp is not None else int(time.time()))
    signature = hmac.new(secret.encode(), signed_at.encode() + b"." + body, hashlib.sha256)
    return await client.post(
        "/api/v1/analytics/ingest",
        content=body,
        headers={
            "X-SkyyRose-Analytics-Timestamp": signed_at,
            "X-SkyyRose-Analytics-Signature": signature.hexdigest(),
        },
    )


def authorization(role="admin"):
    token = jwt_manager.create_access_token("offline-synthetic-user", [role])
    return {"Authorization": f"Bearer {token}"}


async def summary(client, **params):
    query = {"site_id": "synthetic-site", "environment": "test", "days": 7}
    query.update(params)
    return await client.get(
        "/api/v1/analytics/events/summary", params=query, headers=authorization()
    )


async def test_persists_before_ack_and_deduplicates_after_database_restart(harness):
    client, sessions, db_path = harness
    data = envelope()
    response = await ingest(client, data)
    assert response.status_code == 200
    assert response.json()["accepted"] == 1
    assert response.json()["event_ids"] == [data["events"][0]["event_id"]]
    # A new engine/session sees the committed row; no in-process ledger is consulted.
    restarted = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        execution_options={"schema_translate_map": {"public": None}},
    )
    async with async_sessionmaker(restarted)() as db:
        row = (await db.execute(select(StorefrontAnalyticsEvent))).scalar_one()
        assert row.properties["synthetic"] is True
        assert row.session_id != data["events"][0]["session_id"]
        assert row.ip_address is None and row.user_agent is None
    await restarted.dispose()
    retry = await ingest(client, data)
    assert retry.json()["accepted"] == 0 and retry.json()["duplicates"] == 1
    async with sessions() as db:
        assert (await db.execute(select(func.count(StorefrontAnalyticsEvent.id)))).scalar() == 1


async def test_identity_conflict_rolls_back_entire_batch(harness):
    client, sessions, _ = harness
    data = envelope()
    assert (await ingest(client, data)).status_code == 200
    data["events"][0]["target"] = "/changed-target"
    data["events"].append(envelope()["events"][0])
    assert (await ingest(client, data)).status_code == 409
    async with sessions() as db:
        assert (await db.execute(select(func.count(StorefrontAnalyticsEvent.id)))).scalar() == 1


@pytest.mark.parametrize(
    "change",
    [
        "purchase",
        "pii",
        "query",
        "nan",
        "bad_session",
        "non_utc",
        "future",
        "batch",
        "consent",
        "extra",
        "invalid_site",
        "boolean_version",
        "coerced_boolean",
        "over_bound",
        "noncanonical_uuid",
    ],
)
async def test_rejects_untrusted_or_unbounded_events(harness, change):
    client, _, _ = harness
    data = envelope()
    event = data["events"][0]
    if change == "purchase":
        event["event_type"] = "purchase"
    elif change == "pii":
        event["properties"] = {"email": "private@example.test"}
    elif change == "query":
        event["target"] = "/product?email=private@example.test"
    elif change == "nan":
        event["value"] = float("nan")
    elif change == "bad_session":
        event["session_id"] = "customer@example.test"
    elif change == "non_utc":
        event["occurred_at"] = "2026-01-01T01:00:00+01:00"
    elif change == "future":
        event["occurred_at"] = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
    elif change == "batch":
        data["events"] *= 51
    elif change == "consent":
        data["consent"] = "denied"
    elif change == "extra":
        event["order"] = {"total": 9000}
    elif change == "invalid_site":
        data["site_id"] = "https://example.test"
    elif change == "boolean_version":
        data["schema_version"] = True
    elif change == "coerced_boolean":
        event["synthetic"] = "false"
    elif change == "over_bound":
        event["value"] = 1_000_001
    elif change == "noncanonical_uuid":
        event["event_id"] = event["event_id"].upper()
    assert (await ingest(client, data)).status_code == 422


async def test_signature_replay_scope_and_body_size(harness):
    client, _, _ = harness
    assert (await ingest(client, envelope(), secret="forged")).status_code == 401
    assert (await ingest(client, envelope(), timestamp=int(time.time()) - 301)).status_code == 401
    assert (await ingest(client, envelope(site_id="different-site"))).status_code == 403
    assert (await ingest(client, envelope(environment="production"))).status_code == 403
    data = envelope()
    data["events"][0]["properties"]["route"] = "a" * 70_000
    assert (await ingest(client, data)).status_code == 413


async def test_configuration_and_reporting_auth_fail_closed(harness, monkeypatch):
    client, _, _ = harness
    path = "/api/v1/analytics/events/summary?site_id=synthetic-site&environment=test"
    assert (await client.get(path)).status_code == 401
    assert (await client.get(path, headers=authorization("read_only"))).status_code == 403
    assert (await summary(client, site_id="different-site")).status_code == 403
    assert (await summary(client, days=91)).status_code == 422
    monkeypatch.delenv("SKYYROSE_ANALYTICS_SECRET")
    assert (await ingest(client, envelope())).status_code == 503
    assert (await summary(client)).status_code == 503


@pytest.mark.parametrize("role", ["guest", "read_only", "api_user"])
async def test_legacy_funnel_cannot_bypass_private_reporting_roles(harness, role):
    client, _, _ = harness
    assert (await webhook(client, paid_order())).status_code == 200
    for path in (
        "/api/v1/analytics/business/funnel",
        "/api/v1/analytics/events/summary?site_id=synthetic-site&environment=test",
    ):
        denied = await client.get(path, headers=authorization(role))
        assert denied.status_code == 403
    allowed = await client.get("/api/v1/analytics/business/funnel", headers=authorization())
    assert allowed.status_code == 200


async def test_synthetic_events_do_not_become_real_engagement_or_revenue(harness):
    client, _, _ = harness
    data = envelope()
    # Even an omitted synthetic flag is forced true for configured test scope.
    del data["events"][0]["synthetic"]
    assert (await ingest(client, data)).status_code == 200
    result = (await summary(client)).json()
    assert result["coverage"]["synthetic_events_excluded"] == 1
    assert result["coverage"]["status"] == "unavailable"
    metrics = result["metrics"]
    assert metrics["event_count"] == 0
    assert metrics["product_clicks"] is None and metrics["add_to_cart"] is None
    assert metrics["verified_revenue"] is None and metrics["spend"] is None
    assert metrics["conversion_rate"] is None and metrics["roas"] is None


async def test_summary_scope_and_window_exclude_unrelated_events(harness):
    client, sessions, _ = harness
    assert (await ingest(client, envelope())).status_code == 200
    now = datetime.now(UTC)
    async with sessions() as db:
        out_of_window = await read_summary(
            db, "synthetic-site", "test", now - timedelta(days=8), now - timedelta(days=7), 1
        )
        wrong_site = await read_summary(db, "other", "test", now - timedelta(days=7), now, 7)
    assert out_of_window["coverage"]["synthetic_events_excluded"] == 0
    assert wrong_site["coverage"]["synthetic_events_excluded"] == 0
    assert out_of_window["metrics"]["page_views"] is None


def paid_order(**changes):
    value = {
        "id": 123,
        "status": "processing",
        "total": "123.45",
        "currency": "USD",
        "date_paid_gmt": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "billing": {"email": "discarded-private@example.test"},
    }
    value.update(changes)
    return value


async def webhook(client, order, *, source=SITE_URL, secret=WC_SECRET):
    body = json.dumps(order).encode()
    signature = base64.b64encode(hmac.new(secret.encode(), body, hashlib.sha256).digest()).decode()
    return await client.post(
        "/api/v1/woocommerce/webhooks/order",
        content=body,
        headers={"X-WC-Webhook-Signature": signature, "X-WC-Webhook-Source": source},
    )


async def test_verified_paid_order_is_durable_deduplicated_and_synthetic(harness):
    client, sessions, _ = harness
    order = paid_order()
    response = await webhook(client, order)
    assert response.json()["analytics"]["accepted"] == 1
    order["status"] = "completed"
    order["total"] = "123.450000"
    assert (await webhook(client, order)).json()["analytics"]["duplicates"] == 1
    result = (await summary(client)).json()
    assert result["coverage"]["synthetic_events_excluded"] == 1
    assert result["metrics"]["verified_revenue"] is None
    async with sessions() as db:
        row = (await db.execute(select(StorefrontAnalyticsEvent))).scalar_one()
    assert "discarded-private" not in json.dumps(row.properties)
    assert row.properties["payment_provenance"] == "wc_hmac_verified_date_paid_gmt"


async def test_wc_signature_site_payment_and_amount_cannot_be_forged(harness):
    client, sessions, _ = harness
    assert (await webhook(client, paid_order(), secret="forged")).status_code == 401
    for order in (
        paid_order(date_paid_gmt=None),
        paid_order(status="pending"),
        paid_order(status="refunded"),
        paid_order(total="NaN"),
        paid_order(total="1.000000000000000000000000000000001"),
        paid_order(id=True),
        paid_order(currency="<USD>"),
    ):
        assert (await webhook(client, order)).json()["analytics"]["status"] == "skipped"
    mismatch = await webhook(client, paid_order(), source="https://wrong.example.test")
    assert mismatch.status_code == 503
    assert mismatch.json()["detail"]["analytics"]["reason"] == "webhook_site_mismatch"
    async with sessions() as db:
        assert (await db.execute(select(func.count(StorefrontAnalyticsEvent.id)))).scalar() == 0


@pytest.mark.parametrize(
    "value",
    [
        "http://example.test",
        "https://user:pass@example.test",
        "https://example.test/path",
        "https://example.test?q=1",
        "https://example.test#fragment",
        "https://example.test:bad",
        "https://[",
        "https://bad host.example.test",
    ],
)
def test_site_origin_rejects_ambiguous_configuration(value):
    assert canonical_site_origin(value) is None


@pytest.mark.timeout(60)
async def test_database_deduplication_across_independent_processes(harness):
    """Independent processes race one synthetic event against the same file DB."""
    _, sessions, db_path = harness
    script = """import asyncio, sys
from datetime import UTC, datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from api.v1.analytics.event_store import persist_events
async def run():
    engine = create_async_engine("sqlite+aiosqlite:///" + sys.argv[1], execution_options={"schema_translate_map": {"public": None}})
    async with async_sessionmaker(engine)() as db:
        print(await persist_events(db, [{"id": UUID("00000000-0000-4000-8000-000000000001"),
          "event_type": "storefront", "event_name": "product_click", "source": "synthetic",
          "properties": {"synthetic": True, "payload_hash": "identical"},
          "event_timestamp": datetime(2026, 1, 1, tzinfo=UTC)}]))
    await engine.dispose()
asyncio.run(run())
"""
    process_env = os.environ.copy()
    process_env["PYTHONPATH"] = str(Path(__file__).resolve().parents[3])
    processes = [
        subprocess.Popen(
            [sys.executable, "-c", script, str(db_path)],
            env=process_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for _ in range(2)
    ]
    # CI cold interpreter/import startup exceeded the global 10-second limit.
    # Keep each child bounded to 30 seconds and always reap timed-out workers.
    try:
        outputs = await asyncio.gather(
            *[asyncio.to_thread(process.communicate, timeout=30) for process in processes],
            return_exceptions=True,
        )
        for output in outputs:
            if isinstance(output, BaseException):
                raise output
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
    assert all(process.returncode == 0 for process in processes), outputs
    assert sorted(output[0].strip() for output in outputs) == ["(0, 1)", "(1, 0)"]
    async with sessions() as db:
        assert (await db.execute(select(func.count(StorefrontAnalyticsEvent.id)))).scalar() == 1


async def test_paid_webhook_unavailable_retries_then_persists_once(harness, monkeypatch):
    client, sessions, _ = harness
    order = paid_order()
    monkeypatch.delenv("SKYYROSE_ANALYTICS_SITE_ID")
    response = await webhook(client, order)
    assert response.status_code == 503
    assert response.headers["retry-after"] == "60"
    assert response.json()["detail"]["analytics"]["status"] == "unavailable"
    monkeypatch.setenv("SKYYROSE_ANALYTICS_SITE_ID", "synthetic-site")
    assert (await webhook(client, order)).json()["analytics"]["accepted"] == 1
    assert (await webhook(client, order)).json()["analytics"]["duplicates"] == 1
    conflict = await webhook(client, {**order, "total": "1.00"})
    assert conflict.status_code == 503
    assert conflict.json()["detail"]["analytics"]["status"] == "conflict"
    async with sessions() as db:
        assert (await db.execute(select(func.count(StorefrontAnalyticsEvent.id)))).scalar() == 1


async def test_irrelevant_order_stays_skipped_without_analytics_configuration(harness, monkeypatch):
    client, _, _ = harness
    monkeypatch.delenv("SKYYROSE_ANALYTICS_SITE_ID")
    result = await webhook(client, paid_order(status="pending"))
    assert result.status_code == 200
    assert result.json()["analytics"]["status"] == "skipped"


async def test_duplicate_ids_inside_batch_are_counted_once(harness):
    """LOCAL SYNTHETIC: identical duplicates within one signed request."""
    client, sessions, _ = harness
    data = envelope()
    data["events"].append(dict(data["events"][0]))
    result = await ingest(client, data)
    assert result.status_code == 200
    assert result.json()["accepted"] == result.json()["duplicates"] == 1
    async with sessions() as db:
        assert (await db.execute(select(func.count(StorefrontAnalyticsEvent.id)))).scalar() == 1


async def test_conflicting_duplicate_ids_inside_batch_roll_back_all_rows(harness):
    client, sessions, _ = harness
    data = envelope()
    changed = dict(data["events"][0], target="/synthetic-changed-target")
    data["events"].extend([changed, envelope()["events"][0]])
    assert (await ingest(client, data)).status_code == 409
    async with sessions() as db:
        assert (await db.execute(select(func.count(StorefrontAnalyticsEvent.id)))).scalar() == 0
