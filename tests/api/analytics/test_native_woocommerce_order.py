"""Bounded native WC fixture → HMAC webhook → durable synthetic analytics.

Run only with an explicit exported synthetic order; no external requests/payment.
The fixture's paid timestamp is assigned for this test, never gateway evidence.
"""

import json
import os
from pathlib import Path

import pytest
from sqlalchemy import func, select

from api.v1.analytics.event_store import StorefrontAnalyticsEvent, scoped_event_id
from tests.api.analytics.test_storefront_ingest import summary, webhook

pytest_plugins = ("tests.api.analytics.test_storefront_ingest",)


async def test_native_preorder_money_privacy_and_duplicate_identity(harness):
    artifact = os.environ.get("SKYYROSE_SYNTHETIC_NATIVE_ORDER")
    if not artifact:
        pytest.skip("Explicit isolated native WC order export not supplied")
    order = json.loads(Path(artifact).read_text())
    assert order["customer_note"] == "PRIVATE_SYNTHETIC_ONLY"
    assert order["total"] == "159.50"
    assert order["line_items"][0]["meta_data"][0]["key"] == "_skyyrose_preorder_snapshot"
    client, sessions, _ = harness
    assert (await webhook(client, order)).json()["analytics"]["accepted"] == 1
    order["status"] = "completed"
    order["customer_note"] = "PRIVATE_CHANGED_SYNTHETIC_ONLY"
    order["line_items"][0]["meta_data"][0]["value"] = {"private": "PRIVATE_CHANGED_PROMISE"}
    assert (await webhook(client, order)).json()["analytics"]["duplicates"] == 1
    async with sessions() as db:
        row = (await db.execute(select(StorefrontAnalyticsEvent))).scalar_one()
    assert row.id == scoped_event_id("synthetic-site", "test", f"paid_order:{order['id']}")
    assert "PRIVATE" not in json.dumps(row.properties)
    assert "preorder" not in json.dumps(row.properties)
    assert (await summary(client)).json()["coverage"]["synthetic_events_excluded"] == 1
    order["total"] = "159.51"
    conflict = await webhook(client, order)
    assert conflict.status_code == 503
    assert conflict.json()["detail"]["analytics"]["reason"] == "paid_order_identity_changed"
    async with sessions() as db:
        assert (await db.execute(select(func.count(StorefrontAnalyticsEvent.id)))).scalar() == 1
