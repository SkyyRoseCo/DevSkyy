"""Private WordPress bridge ingestion and authenticated storefront reporting."""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import time
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any, Literal
from urllib.parse import urlsplit
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.analytics.event_store import (
    BRIDGE_SOURCE,
    COMMERCE_SOURCE,
    EventConflictError,
    fingerprint,
    persist_events,
    read_summary,
    scoped_event_id,
)
from database.db import get_db
from security.jwt_oauth2_auth import TokenPayload, UserRole, get_current_user

router = APIRouter(prefix="/analytics", tags=["Storefront Analytics"])
MAX_BODY_BYTES = 65_536
TOKEN_PATTERN = r"^[A-Za-z0-9_/.-]{1,160}$"
EVENT_TYPES = {
    "page_view",
    "collection_view",
    "product_view",
    "product_click",
    "add_to_cart",
    "remove_from_cart",
    "begin_checkout",
    "lookbook_view",
    "hotspot_click",
    "search",
    "size_guide_open",
    "newsletter_signup",
    "scroll_depth",
    "next_world",
}
PROPERTY_KEYS = {
    "action",
    "depth",
    "sku",
    "product_id",
    "quantity",
    "position",
    "scene",
    "direction",
    "source",
    "variant",
    "route",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
}
Environment = Literal["staging", "production", "test"]


class AnalyticsSettings(BaseModel):
    site_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,80}$")
    environment: Environment
    secret: str = Field(min_length=32, repr=False)


def get_analytics_settings() -> AnalyticsSettings:
    try:
        return AnalyticsSettings(
            site_id=os.getenv("SKYYROSE_ANALYTICS_SITE_ID", ""),
            environment=os.getenv("SKYYROSE_ANALYTICS_ENVIRONMENT", ""),
            secret=os.getenv("SKYYROSE_ANALYTICS_SECRET", ""),
        )
    except ValidationError as exc:
        raise HTTPException(503, "Storefront analytics is not configured") from exc


def utc_timestamp(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError("Timestamps must include UTC timezone")
    return value.astimezone(UTC)


class BrowserEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, strict=True)

    event_id: UUID
    session_id: str = Field(min_length=16, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
    event_type: str
    occurred_at: datetime
    page_type: Literal[
        "home",
        "collection",
        "product",
        "shop",
        "cart",
        "checkout",
        "lookbook",
        "immersive",
        "search",
        "other",
    ]
    collection: str | None = Field(default=None, max_length=100, pattern=TOKEN_PATTERN)
    target: str | None = Field(default=None, pattern=TOKEN_PATTERN)
    value: float | None = Field(default=None, ge=0, le=1_000_000)
    properties: dict[str, str | float] = Field(default_factory=dict, max_length=16)
    synthetic: bool = False

    @field_validator("event_id", mode="before")
    @classmethod
    def canonical_event_id(cls, value: Any) -> str:
        if not isinstance(value, str) or value != str(UUID(value)):
            raise ValueError("Event identity must be a canonical UUID string")
        return value

    @field_validator("event_type")
    @classmethod
    def engagement_only(cls, value: str) -> str:
        if value not in EVENT_TYPES:
            raise ValueError("Unsupported browser event; purchases require verified WooCommerce")
        return value

    @field_validator("occurred_at")
    @classmethod
    def occurred_at_utc(cls, value: datetime) -> datetime:
        return utc_timestamp(value)

    @field_validator("properties")
    @classmethod
    def bounded_properties(cls, value: dict[str, str | float]) -> dict[str, str | float]:
        import math

        for key, item in value.items():
            if key not in PROPERTY_KEYS:
                raise ValueError("Unsupported event property")
            if isinstance(item, str) and not re.fullmatch(TOKEN_PATTERN, item):
                raise ValueError("Properties must be tokens without PII or query strings")
            if isinstance(item, float) and (not math.isfinite(item) or not 0 <= item <= 1_000_000):
                raise ValueError("Numeric properties must be finite and bounded")
        return value


class EventEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    schema_version: Literal[1]
    site_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,80}$")
    environment: Environment
    consent: Literal["accepted"]
    sent_at: datetime
    events: list[BrowserEvent] = Field(min_length=1, max_length=50)

    @field_validator("schema_version", mode="before")
    @classmethod
    def integer_version(cls, value: Any) -> int:
        if type(value) is not int or value != 1:
            raise ValueError("Unsupported integer schema version")
        return value

    @field_validator("sent_at")
    @classmethod
    def sent_at_utc(cls, value: datetime) -> datetime:
        return utc_timestamp(value)

    @model_validator(mode="after")
    def bounded_event_age(self) -> EventEnvelope:
        for event in self.events:
            if (
                not self.sent_at - timedelta(days=1)
                <= event.occurred_at
                <= self.sent_at + timedelta(seconds=60)
            ):
                raise ValueError("Event timestamp outside bounded collection window")
        return self


async def authenticated_envelope(
    request: Request, settings: AnalyticsSettings = Depends(get_analytics_settings)
) -> EventEnvelope:
    timestamp = request.headers.get("X-SkyyRose-Analytics-Timestamp", "")
    signature = request.headers.get("X-SkyyRose-Analytics-Signature", "")
    if not re.fullmatch(r"[0-9]{10,12}", timestamp) or abs(time.time() - int(timestamp)) > 300:
        raise HTTPException(401, "Invalid analytics signature timestamp")
    if not re.fullmatch(r"[0-9a-f]{64}", signature):
        raise HTTPException(401, "Invalid analytics signature")
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > MAX_BODY_BYTES:
            raise HTTPException(413, "Analytics batch exceeds size limit")
    expected = hmac.new(
        settings.secret.encode(), timestamp.encode() + b"." + body, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(401, "Invalid analytics signature")
    try:
        envelope = EventEnvelope.model_validate_json(bytes(body))
    except ValidationError as exc:
        raise HTTPException(422, "Invalid bounded analytics envelope") from exc
    if envelope.site_id != settings.site_id or envelope.environment != settings.environment:
        raise HTTPException(403, "Analytics site or environment does not match configured scope")
    if abs(envelope.sent_at.timestamp() - int(timestamp)) > 300:
        raise HTTPException(422, "Envelope timestamp does not match signed request window")
    return envelope


@router.post("/ingest")
async def ingest_events(
    envelope: EventEnvelope = Depends(authenticated_envelope),
    settings: AnalyticsSettings = Depends(get_analytics_settings),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    rows = []
    for event in envelope.events:
        data = event.model_dump(mode="json")
        synthetic = event.synthetic or settings.environment == "test"
        data["synthetic"] = synthetic
        session_hash = hmac.new(
            settings.secret.encode(),
            f"{settings.site_id}:{settings.environment}:{event.session_id}".encode(),
            hashlib.sha256,
        ).hexdigest()
        rows.append(
            {
                "id": scoped_event_id(settings.site_id, settings.environment, str(event.event_id)),
                "event_type": "storefront",
                "event_name": event.event_type,
                "source": BRIDGE_SOURCE,
                "session_id": session_hash,
                "properties": {
                    "site_id": settings.site_id,
                    "environment": settings.environment,
                    "consent": "accepted",
                    "synthetic": synthetic,
                    "page_type": event.page_type,
                    "collection": event.collection,
                    "target": event.target,
                    "details": event.properties,
                    "payload_hash": fingerprint(data),
                },
                "numeric_value": Decimal(str(event.value)) if event.value is not None else None,
                "event_timestamp": event.occurred_at,
            }
        )
    try:
        accepted, duplicates = await persist_events(db, rows)
    except EventConflictError as exc:
        raise HTTPException(409, str(exc)) from exc
    return {
        "status": "accepted",
        "accepted": accepted,
        "duplicates": duplicates,
        "event_ids": [str(event.event_id) for event in envelope.events],
        "site_id": settings.site_id,
        "environment": settings.environment,
    }


def require_analytics_reporter(user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
    if not user.has_any_role({UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.DEVELOPER}):
        raise HTTPException(403, "Analytics reporting requires administrator or developer access")
    return user


@router.get("/events/summary")
async def events_summary(
    site_id: str = Query(pattern=r"^[A-Za-z0-9_-]{1,80}$"),
    environment: Environment = Query(),
    days: int = Query(default=30, ge=1, le=90),
    user: TokenPayload = Depends(require_analytics_reporter),
    settings: AnalyticsSettings = Depends(get_analytics_settings),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    if site_id != settings.site_id or environment != settings.environment:
        raise HTTPException(403, "Analytics reporting scope does not match configuration")
    now = datetime.now(UTC)
    return await read_summary(db, site_id, environment, now - timedelta(days=days), now, days)


def canonical_site_origin(value: str) -> str | None:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
        or not re.fullmatch(r"[A-Za-z0-9.-]{1,253}", parsed.hostname)
    ):
        return None
    try:
        port = parsed.port
    except ValueError:
        return None
    return f"https://{parsed.hostname.lower()}" + (f":{port}" if port and port != 443 else "")


async def capture_paid_order(
    db: AsyncSession, order: dict[str, Any], source_url: str | None
) -> dict[str, Any]:
    """Called ONLY after WooCommerce HMAC verification, retaining no raw order or PII.

    The unsigned source header constrains identity; signature verification proves
    the configured webhook secret. Live account/secret qualification is separate.
    """
    try:
        settings = get_analytics_settings()
    except HTTPException:
        return {"status": "unavailable", "reason": "analytics_not_configured"}
    intended = canonical_site_origin(os.getenv("SKYYROSE_ANALYTICS_SITE_URL", ""))
    if not intended:
        return {"status": "unavailable", "reason": "analytics_site_url_not_configured"}
    if canonical_site_origin(source_url or "") != intended:
        return {"status": "unavailable", "reason": "webhook_site_mismatch"}
    paid_at = order.get("date_paid_gmt")
    if order.get("status") not in {"processing", "completed"} or not paid_at:
        return {"status": "skipped", "reason": "no_verified_paid_order"}
    try:
        order_id = order["id"]
        if isinstance(order_id, bool) or not isinstance(order_id, int) or order_id <= 0:
            raise ValueError("Invalid order identity")
        amount = Decimal(str(order["total"]))
        if not amount.is_finite() or not 0 <= amount <= 1_000_000:
            raise ValueError("Invalid paid order amount")
        durable_amount = amount.quantize(Decimal("0.000001"))
        if amount != durable_amount:
            raise ValueError("Payment precision exceeds durable schema")
        amount = durable_amount.normalize() if durable_amount else Decimal(0)
        currency = order["currency"]
        if not isinstance(currency, str) or not re.fullmatch(r"[A-Z]{3}", currency):
            raise ValueError("Invalid currency")
        timestamp = datetime.fromisoformat(paid_at.replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)  # WC's *_gmt field is explicitly UTC.
        timestamp = utc_timestamp(timestamp)
        if timestamp > datetime.now(UTC) + timedelta(seconds=60):
            raise ValueError("Future payment date")
    except (KeyError, ValueError, TypeError, AttributeError, InvalidOperation):
        return {"status": "skipped", "reason": "invalid_paid_order_fields"}
    synthetic = settings.environment == "test"
    identity = f"paid_order:{order_id}"
    data = {
        "order_id": order_id,
        "amount": str(amount),
        "currency": currency,
        "paid_at": timestamp.isoformat(),
        "synthetic": synthetic,
    }
    row = {
        "id": scoped_event_id(settings.site_id, settings.environment, identity),
        "event_type": "commerce",
        "event_name": "purchase",
        "source": COMMERCE_SOURCE,
        "numeric_value": amount,
        "event_timestamp": timestamp,
        "properties": {
            "site_id": settings.site_id,
            "environment": settings.environment,
            "order_identity": hashlib.sha256(identity.encode()).hexdigest(),
            "synthetic": synthetic,
            "currency": currency,
            "payment_provenance": "wc_hmac_verified_date_paid_gmt",
            "payload_hash": fingerprint(data),
        },
    }
    try:
        accepted, duplicates = await persist_events(db, [row])
    except EventConflictError:
        return {"status": "conflict", "reason": "paid_order_identity_changed"}
    return {"status": "accepted", "accepted": accepted, "duplicates": duplicates}
