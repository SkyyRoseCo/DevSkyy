"""Security regression tests for the auth-hardening pass (bug-252 sibling class).

Proves that endpoints which were unauthenticated (and in claude_sdk's case,
anonymous-RCE) now reject callers without valid credentials, and that the
WooCommerce webhook verifier fails closed when the secret is unset.

These are behavioral tests: mount each router on a minimal app and assert the
HTTP status a credential-less caller sees.
"""

from __future__ import annotations

import base64
import hashlib
import hmac

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

_UNAUTH = (401, 403)  # missing/invalid creds → Unauthorized or Forbidden


def _client(router, prefix: str = "") -> TestClient:
    app = FastAPI()
    if prefix:
        app.include_router(router, prefix=prefix)
    else:
        app.include_router(router)
    return TestClient(app, raise_server_exceptions=False)


class TestClaudeSdkNoAnonymousRce:
    """claude_sdk routes gave anonymous Bash-capable agents — now ADMIN-only."""

    def test_session_requires_auth(self):
        from api.v1.claude_sdk import router

        c = _client(router, prefix="/api/v1")
        r = c.post("/api/v1/claude-sdk/session", params={"action": "create"})
        assert r.status_code in _UNAUTH, r.status_code

    def test_excel_requires_auth(self):
        from api.v1.claude_sdk import router

        c = _client(router, prefix="/api/v1")
        r = c.post("/api/v1/claude-sdk/excel", params={"operation": "create", "description": "x"})
        assert r.status_code in _UNAUTH, r.status_code

    def test_dashboard_health_requires_auth(self):
        from api.v1.claude_sdk import router

        c = _client(router, prefix="/api/v1")
        r = c.get("/api/v1/claude-sdk/dashboard/health")
        assert r.status_code in _UNAUTH, r.status_code


class TestWordPressWritesRequireAuth:
    def test_content_sync_requires_auth(self):
        from api.v1.wordpress import router

        c = _client(router, prefix="/api/v1")
        r = c.post("/api/v1/wordpress/sync", json={"title": "x", "content": "y"})
        assert r.status_code in _UNAUTH, r.status_code

    def test_product_sync_requires_auth(self, monkeypatch):
        # Configure the site URL so the settings gate passes and auth becomes
        # the effective gate (else get_settings 503s before auth resolves).
        monkeypatch.setenv("WORDPRESS_SITE_URL", "https://skyyrose.co")

        from api.v1.wordpress_integration import router

        c = _client(router, prefix="/api/v1")
        # Send a plausible product body; auth must reject before any live write.
        r = c.post(
            "/api/v1/wordpress/products/sync",
            json={"sku": "test-001", "name": "Test", "price": 10, "collection": "signature"},
        )
        assert r.status_code in _UNAUTH, r.status_code


class TestFeatureFlagsAdminOnly:
    def test_upsert_flag_requires_auth(self):
        from api.v1.feature_flags import router

        c = _client(router)  # router already carries /api/v1/flags prefix
        r = c.put("/api/v1/flags/test-flag", json={"name": "test-flag", "enabled": True})
        assert r.status_code in _UNAUTH, r.status_code

    def test_delete_flag_requires_auth(self):
        from api.v1.feature_flags import router

        c = _client(router)
        r = c.delete("/api/v1/flags/test-flag")
        assert r.status_code in _UNAUTH, r.status_code


class TestWebhookFailsClosed:
    """An unset WC_WEBHOOK_SECRET must reject webhooks, not trust empty-key HMAC."""

    def test_empty_secret_rejects_webhook(self, monkeypatch):
        monkeypatch.delenv("WC_WEBHOOK_SECRET", raising=False)
        monkeypatch.setenv("WORDPRESS_SITE_URL", "https://skyyrose.co")

        from api.v1.woocommerce_webhooks import router

        app = FastAPI()
        app.include_router(router)
        client = TestClient(app, raise_server_exceptions=False)

        body = b'{"id": 1, "price": "1.00"}'
        # Forge the signature the way an attacker would with an empty key.
        forged = base64.b64encode(hmac.new(b"", body, hashlib.sha256).digest()).decode()
        r = client.post(
            "/woocommerce/webhooks/product",
            content=body,
            headers={"X-WC-Webhook-Signature": forged, "Content-Type": "application/json"},
        )
        assert r.status_code == 401, r.status_code


class TestBrandAssetSsrfGuard:
    """The bulk-ingest URL validator must reject internal / cloud-metadata targets
    regardless of scheme case. `HTTP://…` was a bypass: str.startswith(("http://",
    "https://")) is case-sensitive, but urlparse/httpx lowercase the scheme, so the
    raw URL reached httpx.get() unvalidated (169.254.169.254 → IAM credential theft).
    These assert the guard now runs unconditionally. All three targets are rejected
    BEFORE any DNS resolution (blocked-domain / protocol checks), so no network.
    """

    def test_lowercase_metadata_ip_rejected(self):
        from pydantic import ValidationError

        from api.v1.brand_assets import BrandAssetUpload

        with pytest.raises(ValidationError):
            BrandAssetUpload(url="http://169.254.169.254/latest/meta-data/", category="product")

    def test_uppercase_scheme_metadata_ip_rejected(self):
        # The regression: "HTTP://" skipped the case-sensitive startswith gate.
        from pydantic import ValidationError

        from api.v1.brand_assets import BrandAssetUpload

        with pytest.raises(ValidationError):
            BrandAssetUpload(
                url="HTTP://169.254.169.254/latest/meta-data/iam/security-credentials/",
                category="product",
            )

    def test_non_http_scheme_rejected(self):
        from pydantic import ValidationError

        from api.v1.brand_assets import BrandAssetUpload

        with pytest.raises(ValidationError):
            BrandAssetUpload(url="file:///etc/passwd", category="product")


class TestServiceTokenAuth:
    """/wordpress/sync accepts a machine-to-machine X-Service-Token (queue worker
    has no user session) as an alternative to a user JWT — constant-time matched,
    fails closed when the env token is unset. No user JWT is required for the
    service path, and no service path exists without the configured secret.
    """

    def test_valid_service_token_passes_auth(self, monkeypatch):
        monkeypatch.setenv("WORDPRESS_SYNC_SERVICE_TOKEN", "s3cr3t-worker-token")
        from api.v1.wordpress import router

        c = _client(router, prefix="/api/v1")
        r = c.post(
            "/api/v1/wordpress/sync",
            json={"title": "x", "content": "y"},
            headers={"X-Service-Token": "s3cr3t-worker-token"},
        )
        # Auth passed → NOT 401/403 (downstream may 503 on missing WP creds / 200).
        assert r.status_code not in _UNAUTH, r.status_code

    def test_wrong_service_token_rejected(self, monkeypatch):
        monkeypatch.setenv("WORDPRESS_SYNC_SERVICE_TOKEN", "s3cr3t-worker-token")
        from api.v1.wordpress import router

        c = _client(router, prefix="/api/v1")
        r = c.post(
            "/api/v1/wordpress/sync",
            json={"title": "x", "content": "y"},
            headers={"X-Service-Token": "WRONG"},
        )
        assert r.status_code in _UNAUTH, r.status_code

    def test_service_token_path_disabled_when_env_unset(self, monkeypatch):
        # No configured secret => the service-token path must not exist; a header
        # (even non-empty) can't authenticate. Fails closed.
        monkeypatch.delenv("WORDPRESS_SYNC_SERVICE_TOKEN", raising=False)
        from api.v1.wordpress import router

        c = _client(router, prefix="/api/v1")
        r = c.post(
            "/api/v1/wordpress/sync",
            json={"title": "x", "content": "y"},
            headers={"X-Service-Token": "anything"},
        )
        assert r.status_code in _UNAUTH, r.status_code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestTasksRequireAuth:
    """api/tasks.py ran agent work (paid LLM calls) for anonymous callers."""

    def test_list_requires_auth(self):
        from api.tasks import tasks_router

        r = _client(tasks_router, prefix="/api/v1").get("/api/v1/tasks")
        assert r.status_code in _UNAUTH, r.status_code

    def test_get_requires_auth(self):
        from api.tasks import tasks_router

        r = _client(tasks_router, prefix="/api/v1").get("/api/v1/tasks/x")
        assert r.status_code in _UNAUTH, r.status_code

    def test_submit_requires_auth(self):
        from api.tasks import tasks_router

        r = _client(tasks_router, prefix="/api/v1").post(
            "/api/v1/tasks", json={"agentType": "commerce", "prompt": "x"}
        )
        assert r.status_code in _UNAUTH, r.status_code

    def test_cancel_requires_auth(self):
        from api.tasks import tasks_router

        r = _client(tasks_router, prefix="/api/v1").post("/api/v1/tasks/x/cancel")
        assert r.status_code in _UNAUTH, r.status_code

    def test_submit_forbidden_for_api_user(self):
        from api.tasks import tasks_router
        from security.jwt_oauth2_auth import UserRole, jwt_manager

        token = jwt_manager.create_token_pair(user_id="u1", roles=[UserRole.API_USER.value])
        r = _client(tasks_router, prefix="/api/v1").post(
            "/api/v1/tasks",
            json={"agentType": "commerce", "prompt": "x"},
            headers={"Authorization": f"Bearer {token.access_token}"},
        )
        assert r.status_code == 403, r.status_code
