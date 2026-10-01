"""Tests for WooCommerce Webhooks API (api/v1/woocommerce_webhooks.py).

Signature verification is delegated to api.v1.wordpress_integration.verify_webhook
(HMAC-SHA256 over X-WC-Webhook-Signature). No network, no DB, no paid APIs.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

SECRET = "test-wc-webhook-secret"


def _sign(body: bytes, secret: str = SECRET) -> str:
    # WooCommerce sends X-WC-Webhook-Signature base64-encoded (not hex).
    return base64.b64encode(hmac.new(secret.encode(), body, hashlib.sha256).digest()).decode()


@pytest.fixture
def wc_app(monkeypatch):
    """Minimal FastAPI app carrying only the woocommerce_webhooks router
    (mirrors the pattern documented in tests/test_api_v2.py's module docstring:
    "minimal FastAPI app fixture to avoid importing the full main_enterprise stack").
    """
    monkeypatch.setenv("WORDPRESS_SITE_URL", "https://test.example.com")
    monkeypatch.setenv("WC_WEBHOOK_SECRET", SECRET)

    from api.v1.woocommerce_webhooks import router
    from api.v1.wordpress_integration import WordPressSettings, get_settings
    from database.db import get_db

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = lambda: None
    app.dependency_overrides[get_settings] = lambda: WordPressSettings(
        site_url="https://test.example.com", webhook_secret=SECRET
    )
    return TestClient(app)


class TestOrderWebhook:
    def test_valid_signature_returns_200(self, wc_app, monkeypatch):
        capture = AsyncMock(return_value={"status": "accepted", "accepted": 1, "duplicates": 0})
        monkeypatch.setattr("api.v1.woocommerce_webhooks.capture_paid_order", capture)
        body = json.dumps({"id": 501, "status": "completed"}).encode()
        r = wc_app.post(
            "/woocommerce/webhooks/order",
            content=body,
            headers={"X-WC-Webhook-Signature": _sign(body), "Content-Type": "application/json"},
        )
        assert r.status_code == 200
        assert r.json() == {
            "status": "received",
            "analytics": {"status": "accepted", "accepted": 1, "duplicates": 0},
        }
        capture.assert_awaited_once()

    def test_invalid_signature_returns_401(self, wc_app):
        body = json.dumps({"id": 501}).encode()
        r = wc_app.post(
            "/woocommerce/webhooks/order",
            content=body,
            headers={"X-WC-Webhook-Signature": "0" * 64, "Content-Type": "application/json"},
        )
        assert r.status_code == 401

    def test_missing_signature_header_rejected(self, wc_app):
        # verify_webhook declares the header via Header(...) with no default —
        # FastAPI's own request validation rejects this BEFORE the handler or
        # verify_webhook body ever runs (empirically confirmed: a bare POST with
        # no signature header returns 422, not 401). Fail-closed either way (no
        # processing occurs). Do not force a 401 here by modifying the shared
        # verify_webhook dependency — it is also used by wordpress_integration.py's
        # already-mounted, already-live production webhook endpoints.
        body = json.dumps({"id": 501}).encode()
        r = wc_app.post(
            "/woocommerce/webhooks/order",
            content=body,
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 422

    def test_malformed_json_payload_returns_400(self, wc_app):
        body = b"{not valid json"
        r = wc_app.post(
            "/woocommerce/webhooks/order",
            content=body,
            headers={"X-WC-Webhook-Signature": _sign(body), "Content-Type": "application/json"},
        )
        assert r.status_code == 400


class TestProductWebhook:
    def test_valid_signature_returns_200(self, wc_app):
        body = json.dumps({"id": 77, "name": "Black Rose Hoodie"}).encode()
        r = wc_app.post(
            "/woocommerce/webhooks/product",
            content=body,
            headers={"X-WC-Webhook-Signature": _sign(body), "Content-Type": "application/json"},
        )
        assert r.status_code == 200
        assert r.json() == {"status": "received"}

    def test_invalid_signature_returns_401(self, wc_app):
        body = json.dumps({"id": 77}).encode()
        r = wc_app.post(
            "/woocommerce/webhooks/product",
            content=body,
            headers={"X-WC-Webhook-Signature": "bad", "Content-Type": "application/json"},
        )
        assert r.status_code == 401

    def test_malformed_json_payload_returns_400(self, wc_app):
        body = b"[[[not json"
        r = wc_app.post(
            "/woocommerce/webhooks/product",
            content=body,
            headers={"X-WC-Webhook-Signature": _sign(body), "Content-Type": "application/json"},
        )
        assert r.status_code == 400


class TestMountedInApp:
    def test_route_registered_in_main_enterprise(self):
        """Proves the router is actually mounted at /api/v1, not just importable standalone.

        Uses app.openapi()["paths"] (the stable public API) rather than walking
        app.routes directly — this FastAPI version wraps included routers in an
        internal fastapi.routing._IncludedRouter with no .path attribute, so a
        naive `route.path for route in app.routes` misses lazily-resolved routes.
        """
        from main_enterprise import app

        paths = set(app.openapi()["paths"].keys())
        assert "/api/v1/woocommerce/webhooks/order" in paths
        assert "/api/v1/woocommerce/webhooks/product" in paths

    @pytest.mark.asyncio
    async def test_end_to_end_through_full_app(self, client, monkeypatch):
        from database.db import get_db
        from main_enterprise import app

        # The shared ASGI client does not run lifespan/database initialization.
        # This unpaid-order route check needs no SQL; paid persistence is covered
        # through the real SQLite harness in test_storefront_ingest.py.
        monkeypatch.setitem(app.dependency_overrides, get_db, lambda: None)
        monkeypatch.setenv("WORDPRESS_SITE_URL", "https://test.example.com")
        monkeypatch.setenv("WC_WEBHOOK_SECRET", SECRET)
        body = json.dumps({"id": 900, "status": "processing"}).encode()
        r = await client.post(
            "/api/v1/woocommerce/webhooks/order",
            content=body,
            headers={"X-WC-Webhook-Signature": _sign(body), "Content-Type": "application/json"},
        )
        assert r.status_code == 200
