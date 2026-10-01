"""Durable, scope-bound storefront analytics using the existing analytics schema."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import (
    DECIMAL,
    JSON,
    TIMESTAMP,
    Column,
    ForeignKey,
    Index,
    String,
    Table,
    Text,
    TypeDecorator,
    Uuid,
    func,
    select,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.functions import FunctionElement

BRIDGE_SOURCE = "skyyrose.wordpress_bridge"
COMMERCE_SOURCE = "skyyrose.woocommerce_paid_order"


class _UUIDDefault(FunctionElement[UUID]):
    inherit_cache = True


@compiles(_UUIDDefault)
def _uuid_default(element: Any, compiler: Any, **kwargs: Any) -> str:
    return "gen_random_uuid()"


@compiles(_UUIDDefault, "sqlite")
def _sqlite_uuid_default(element: Any, compiler: Any, **kwargs: Any) -> str:
    return "lower(hex(randomblob(16)))"


class _UserIdString(TypeDecorator[str]):
    """Store legacy string user identifiers without coercing UUID objects badly."""

    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> str | None:
        return None if value is None else str(value)


class _EmptyJSONDefault(FunctionElement[dict[str, Any]]):
    inherit_cache = True


@compiles(_EmptyJSONDefault)
def _empty_json_default(element: Any, compiler: Any, **kwargs: Any) -> str:
    return "'{}'::jsonb"


@compiles(_EmptyJSONDefault, "sqlite")
def _sqlite_empty_json_default(element: Any, compiler: Any, **kwargs: Any) -> str:
    return "'{}'"


class _AnalyticsBase(DeclarativeBase):
    """Analytics metadata, isolated from the application-wide create_all path."""


# Reference-only anchor for the migration's FK. This is not a second user ORM
# model or a schema to bootstrap; production users remain owned by the existing application schema.
Table(
    "users",
    _AnalyticsBase.metadata,
    Column("id", _UserIdString(), primary_key=True),
    schema="public",
)


class StorefrontAnalyticsEvent(_AnalyticsBase):
    """Map the isolated legacy-compatible analytics migration."""

    __tablename__ = "analytics_events"

    id: Mapped[UUID] = mapped_column(
        Uuid().with_variant(PostgreSQLUUID(as_uuid=True), "postgresql"),
        primary_key=True,
        server_default=_UUIDDefault(),
    )
    event_type: Mapped[str] = mapped_column(String(100))
    event_name: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(100))
    user_id: Mapped[str | None] = mapped_column(
        _UserIdString(),
        ForeignKey("public.users.id", ondelete="SET NULL"),
        nullable=True,
    )
    session_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    properties: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB(astext_type=Text()), "postgresql"),
        nullable=True,
        server_default=_EmptyJSONDefault(),
    )
    numeric_value: Mapped[Decimal | None] = mapped_column(DECIMAL(20, 6), nullable=True)
    string_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    geo_country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    geo_region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    event_timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    )
    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        Index("ix_analytics_events_event_type", "event_type"),
        Index("ix_analytics_events_event_name", "event_name"),
        Index("ix_analytics_events_source", "source"),
        Index("ix_analytics_events_user_id", "user_id"),
        Index("ix_analytics_events_session_id", "session_id"),
        Index("ix_analytics_events_correlation_id", "correlation_id"),
        Index("ix_analytics_events_event_timestamp", "event_timestamp"),
        Index("ix_analytics_events_type_timestamp", "event_type", "event_timestamp"),
        {"schema": "public"},
    )


class EventConflictError(ValueError):
    """An event identity was reused for different data."""


def scoped_event_id(site_id: str, environment: str, event_id: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"skyyrose:{site_id}:{environment}:{event_id}")


async def persist_events(db: AsyncSession, rows: list[dict[str, Any]]) -> tuple[int, int]:
    """Atomically insert or deduplicate, rejecting changed identities before commit.

    A database primary key and ON CONFLICT make retries safe across processes.
    Every row, including duplicates, must match its recorded fingerprint.
    """
    dialect = db.get_bind().dialect.name
    if dialect not in {"sqlite", "postgresql"}:
        raise RuntimeError("Storefront analytics requires SQLite or PostgreSQL")
    insert = sqlite_insert if dialect == "sqlite" else postgres_insert
    try:
        statement = insert(StorefrontAnalyticsEvent).values(rows)
        statement = statement.on_conflict_do_nothing(index_elements=["id"])
        result = await db.execute(statement.returning(StorefrontAnalyticsEvent.id))
        inserted = len(result.scalars().all())
        stored = await db.execute(
            select(StorefrontAnalyticsEvent.id, StorefrontAnalyticsEvent.properties).where(
                StorefrontAnalyticsEvent.id.in_([row["id"] for row in rows])
            )
        )
        fingerprints = {row.id: row.properties["payload_hash"] for row in stored}
        if any(fingerprints[row["id"]] != row["properties"]["payload_hash"] for row in rows):
            raise EventConflictError("Event identity already contains different data")
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    return inserted, len(rows) - inserted


def fingerprint(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


async def read_summary(
    db: AsyncSession, site_id: str, environment: str, start: datetime, end: datetime, days: int
) -> dict[str, Any]:
    scope = (
        StorefrontAnalyticsEvent.source.in_([BRIDGE_SOURCE, COMMERCE_SOURCE]),
        StorefrontAnalyticsEvent.properties["site_id"].as_string() == site_id,
        StorefrontAnalyticsEvent.properties["environment"].as_string() == environment,
        StorefrontAnalyticsEvent.event_timestamp >= start,
        StorefrontAnalyticsEvent.event_timestamp <= end,
    )
    synthetic_flag = StorefrontAnalyticsEvent.properties["synthetic"].as_boolean()
    currency_field = StorefrontAnalyticsEvent.properties["currency"].as_string()
    scoped = (
        select(
            StorefrontAnalyticsEvent.id,
            StorefrontAnalyticsEvent.source,
            StorefrontAnalyticsEvent.event_name,
            StorefrontAnalyticsEvent.session_id,
            StorefrontAnalyticsEvent.numeric_value,
            synthetic_flag.label("synthetic"),
            currency_field.label("currency"),
        )
        .where(*scope)
        .cte("scoped_events")
    )
    session_count = (
        select(func.count(func.distinct(scoped.c.session_id)))
        .where(scoped.c.source == BRIDGE_SOURCE, scoped.c.synthetic.is_(False))
        .correlate(None)
        .scalar_subquery()
    )
    # The grouped counts and session count share one statement snapshot. Only
    # bounded dimension groups leave the database, never the full event log.
    result = await db.execute(
        select(
            scoped.c.source,
            scoped.c.event_name,
            scoped.c.synthetic,
            scoped.c.currency,
            func.count(scoped.c.id).label("event_count"),
            func.sum(scoped.c.numeric_value).label("amount"),
            session_count.label("session_count"),
        ).group_by(
            scoped.c.source,
            scoped.c.event_name,
            scoped.c.synthetic,
            scoped.c.currency,
        )
    )
    rows = result.all()
    synthetic = sum(row.event_count for row in rows if row.synthetic is True)
    # Missing provenance flags fail closed instead of joining the live totals.
    actual = [row for row in rows if row.synthetic is False]
    telemetry = [row for row in actual if row.source == BRIDGE_SOURCE]
    commerce = [row for row in actual if row.source == COMMERCE_SOURCE]
    counts: dict[str, int] = {}
    for row in telemetry:
        counts[row.event_name] = counts.get(row.event_name, 0) + row.event_count
    sessions = telemetry[0].session_count if telemetry else None
    revenue: dict[str, Decimal] = {}
    for row in commerce:
        revenue[row.currency] = revenue.get(row.currency, Decimal(0)) + (row.amount or Decimal(0))
    currency = next(iter(revenue)) if len(revenue) == 1 else None
    missing = ["purchase_session_attribution", "ad_spend", "continuous_collection_coverage"]
    if not telemetry:
        missing.append("consented_storefront_events")
    if not commerce:
        missing.append("verified_paid_orders")
    return {
        "site_id": site_id,
        "environment": environment,
        "window": {"start": start.isoformat(), "end": end.isoformat(), "days": days},
        "coverage": {
            "status": "partial" if actual else "unavailable",
            "telemetry": "observed" if telemetry else "unavailable",
            "commerce": "observed" if commerce else "unavailable",
            "consent": "accepted_only",
            "synthetic_events_excluded": synthetic,
            "missing": missing,
        },
        "metrics": {
            "event_count": sum(counts.values()),
            "page_views": counts.get("page_view"),
            "sessions": sessions,
            "product_views": counts.get("product_view"),
            "product_clicks": counts.get("product_click"),
            "add_to_cart": counts.get("add_to_cart"),
            "checkout_started": counts.get("begin_checkout"),
            "consented_purchases": None,
            "conversion_rate": None,
            "verified_purchases": sum(row.event_count for row in commerce) if commerce else None,
            "verified_revenue": float(revenue[currency]) if currency else None,
            "currency": currency,
            "spend": None,
            "roas": None,
        },
        "event_counts": counts,
        "revenue_by_currency": {key: float(value) for key, value in revenue.items()},
        "provenance": {
            "telemetry": "hmac_authenticated_wordpress_bridge",
            "commerce": "signature_verified_woocommerce_paid_order",
            "attribution": "unavailable",
            "revenue_basis": "paid_order_gross_not_refund_adjusted",
        },
    }
