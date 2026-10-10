"""
Enterprise API v2 — Webhook Registration

Expanded webhook system wrapping the existing WebhookManager from
api/v1/elite_studio_webhooks.py. Adds auto-generated secrets, a test
fire endpoint, and full CRUD over registered webhooks.

Prefix: /api/v2/webhooks
Auth:   X-API-Key header (matches v1 pattern)
"""

from __future__ import annotations

import json
import logging
import os
import secrets
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from api.v1.elite_studio_webhooks import VALID_EVENTS, WebhookManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks v2"])

_KEY_PREFIX = "elite_studio:webhooks"


# ---------------------------------------------------------------------------
# Auth dependency (mirrors v1)
# ---------------------------------------------------------------------------


def _get_api_key_dependency():
    async def _check_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        expected = os.getenv("API_KEY", "")
        if not expected:
            # Fail closed outside dev — a missing API_KEY must not allow through.
            if os.getenv("ENVIRONMENT", "").lower() in ("development", "dev", "local", "test"):
                return None
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="API_KEY not configured",
            )
        if x_api_key != expected:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing X-API-Key header",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        return x_api_key

    return _check_api_key


_api_key_dep = _get_api_key_dependency()

# Shared WebhookManager instance (lazy Redis)
_manager = WebhookManager()


# ---------------------------------------------------------------------------
# Pydantic V2 models
# ---------------------------------------------------------------------------


class RegisterWebhookRequest(BaseModel):
    model_config = {"str_strip_whitespace": True}

    url: str
    events: list[str] = Field(min_length=1)
    secret: str = ""  # auto-generated if empty
    description: str = ""

    @field_validator("url")
    @classmethod
    def _validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("url must start with http:// or https://")
        return v

    @field_validator("events")
    @classmethod
    def _validate_events(cls, v: list[str]) -> list[str]:
        invalid = set(v) - VALID_EVENTS
        if invalid:
            raise ValueError(f"Unknown events: {sorted(invalid)}. Valid: {sorted(VALID_EVENTS)}")
        return v


class WebhookResponse(BaseModel):
    webhook_id: str
    url: str
    events: list[str]
    active: bool
    description: str = ""
    created_at: str


class WebhookListResponse(BaseModel):
    webhooks: list[WebhookResponse]
    total: int


class TestWebhookResponse(BaseModel):
    webhook_id: str
    event_fired: str
    delivery_attempted: bool
    url: str


# ---------------------------------------------------------------------------
# Redis helpers (read raw webhook records not exposed by WebhookManager)
# ---------------------------------------------------------------------------


def _get_redis() -> Any | None:
    return _manager._get_redis()


def _require_redis() -> Any:
    r = _get_redis()
    if r is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis unavailable — cannot process request",
        )
    return r


def _fetch_webhook_record(r: Any, webhook_id: str) -> dict | None:
    """Fetch raw webhook hash from Redis."""
    key = f"{_KEY_PREFIX}:{webhook_id}"
    try:
        data = r.hgetall(key)
        return data if data else None
    except Exception as exc:
        logger.warning("Failed to fetch webhook %s: %s", webhook_id, exc)
        return None


def _list_webhook_records(r: Any) -> list[dict]:
    """Return all webhook records from Redis."""
    records: list[dict] = []
    try:
        keys = r.keys(f"{_KEY_PREFIX}:*")
        for key in keys:
            data = r.hgetall(key)
            if data:
                records.append(data)
    except Exception as exc:
        logger.warning("Failed to list webhooks: %s", exc)
    return records


def _raw_to_response(data: dict) -> WebhookResponse:
    """Convert a raw Redis hash to WebhookResponse."""
    events_raw = data.get("events", "[]")
    try:
        events = json.loads(events_raw)
    except Exception:
        events = []
    return WebhookResponse(
        webhook_id=data.get("webhook_id", ""),
        url=data.get("url", ""),
        events=events,
        active=data.get("active", "true").lower() == "true",
        description=data.get("description", ""),
        created_at=data.get("registered_at", datetime.now(UTC).isoformat()),
    )


def _delete_webhook_record(r: Any, webhook_id: str) -> bool:
    """Delete a webhook record. Returns True if deleted."""
    key = f"{_KEY_PREFIX}:{webhook_id}"
    try:
        deleted = r.delete(key)
        return bool(deleted)
    except Exception as exc:
        logger.warning("Failed to delete webhook %s: %s", webhook_id, exc)
        return False


def _store_extra_fields(r: Any, webhook_id: str, description: str, active: bool = True) -> None:
    """Store extra fields (description, active) not stored by WebhookManager.register."""
    key = f"{_KEY_PREFIX}:{webhook_id}"
    try:
        r.hset(key, mapping={"description": description, "active": str(active).lower()})
    except Exception as exc:
        logger.warning("Failed to store extra webhook fields for %s: %s", webhook_id, exc)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=WebhookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a webhook endpoint",
)
async def register_webhook(
    body: RegisterWebhookRequest,
    _auth=Depends(_api_key_dep),
):
    """Register a webhook endpoint for one or more events.

    If ``secret`` is omitted, a 32-byte hex secret is auto-generated.
    The secret is stored in Redis for HMAC signing — store it securely
    on your side; it is not returned after registration.
    """
    effective_secret = body.secret or secrets.token_hex(32)

    try:
        webhook_id = _manager.register(
            url=body.url,
            events=body.events,
            secret=effective_secret,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    r = _get_redis()
    if r is not None:
        _store_extra_fields(r, webhook_id, description=body.description)

    return WebhookResponse(
        webhook_id=webhook_id,
        url=body.url,
        events=body.events,
        active=True,
        description=body.description,
        created_at=datetime.now(UTC).isoformat(),
    )


@router.get(
    "",
    response_model=WebhookListResponse,
    summary="List all registered webhooks",
)
async def list_webhooks(
    _auth=Depends(_api_key_dep),
):
    """Return all registered webhooks."""
    r = _require_redis()
    records = _list_webhook_records(r)
    webhooks = [_raw_to_response(rec) for rec in records]
    webhooks.sort(key=lambda w: w.created_at, reverse=True)
    return WebhookListResponse(webhooks=webhooks, total=len(webhooks))


@router.get(
    "/{webhook_id}",
    response_model=WebhookResponse,
    summary="Get a webhook by ID",
)
async def get_webhook(
    webhook_id: str,
    _auth=Depends(_api_key_dep),
):
    """Retrieve a registered webhook by its ID."""
    r = _require_redis()
    data = _fetch_webhook_record(r, webhook_id)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook not found: {webhook_id}",
        )
    return _raw_to_response(data)


@router.delete(
    "/{webhook_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a webhook",
)
async def delete_webhook(
    webhook_id: str,
    _auth=Depends(_api_key_dep),
):
    """Permanently remove a webhook registration."""
    r = _require_redis()
    deleted = _delete_webhook_record(r, webhook_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook not found: {webhook_id}",
        )
    return None


@router.post(
    "/{webhook_id}/test",
    response_model=TestWebhookResponse,
    status_code=status.HTTP_200_OK,
    summary="Fire a test event to a webhook URL",
)
async def test_webhook(
    webhook_id: str,
    _auth=Depends(_api_key_dep),
):
    """Send a test ``webhook.test`` event to the registered URL.

    This fires a real HTTP POST so you can verify your endpoint receives
    and validates the HMAC signature correctly.
    Delivery failures are logged but do not cause a non-2xx response here.
    """
    r = _require_redis()
    data = _fetch_webhook_record(r, webhook_id)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook not found: {webhook_id}",
        )

    url = data.get("url", "")
    secret = data.get("secret", "")
    test_payload = {
        "webhook_id": webhook_id,
        "test": True,
        "timestamp": datetime.now(UTC).isoformat(),
        "message": "SkyyRose webhook test",
    }

    # Fire delivery directly (bypasses event subscription check for test)
    from api.v1.elite_studio_webhooks import _deliver

    await _deliver(
        registration={"url": url, "secret": secret},
        event="webhook.test",
        payload=test_payload,
    )

    return TestWebhookResponse(
        webhook_id=webhook_id,
        event_fired="webhook.test",
        delivery_attempted=True,
        url=url,
    )
