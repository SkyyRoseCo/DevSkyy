"""Offline migration parity and summary snapshot regressions for analytics."""

from __future__ import annotations

import importlib.util
import re
import sqlite3
from contextlib import closing
from datetime import UTC, datetime, timedelta
from io import StringIO
from pathlib import Path
from uuid import uuid4

from sqlalchemy import delete, insert, select, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.schema import CreateIndex, CreateTable

from alembic.migration import MigrationContext
from alembic.operations import Operations
from api.v1.analytics.event_store import (
    BRIDGE_SOURCE,
    COMMERCE_SOURCE,
    StorefrontAnalyticsEvent,
    persist_events,
    read_summary,
)
from database.db import Base


def _sql(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().rstrip(";")


def test_legacy_postgresql_schema_matches_isolated_analytics_migration(monkeypatch):
    """Compare the legacy identity model with its isolated analytics Alembic track."""
    migration_path = (
        Path(__file__).resolve().parents[3]
        / "alembic/storefront_migrations/versions/001_create_storefront_analytics.py"
    )
    spec = importlib.util.spec_from_file_location("analytics_migration_003", migration_path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    output = StringIO()
    context = MigrationContext.configure(
        dialect_name="postgresql", opts={"as_sql": True, "output_buffer": output}
    )
    monkeypatch.setattr(migration, "op", Operations(context))
    migration.upgrade()
    emitted = output.getvalue()
    # Exercise the emitted catalog predicate against a synthetic schema catalog.
    # An unrelated tenant/archive table must not block creation in public.
    catalog_guard = re.search(
        r"SELECT 1 FROM pg_catalog\.pg_tables\s+WHERE[^;]+?(?=\s*\) THEN)", emitted
    )
    assert catalog_guard is not None
    with closing(sqlite3.connect(":memory:")) as catalog:
        catalog.execute("ATTACH DATABASE ':memory:' AS pg_catalog")
        catalog.execute("CREATE TABLE pg_catalog.pg_tables (schemaname TEXT, tablename TEXT)")
        catalog.execute("INSERT INTO pg_catalog.pg_tables VALUES ('archive', 'analytics_events')")
        assert catalog.execute(catalog_guard.group()).fetchone() is None
        catalog.execute("INSERT INTO pg_catalog.pg_tables VALUES ('public', 'analytics_events')")
        assert catalog.execute(catalog_guard.group()).fetchone() == (1,)
    migration_table = re.search(r"CREATE TABLE public\.analytics_events \(.*?\n\);", emitted, re.S)
    assert migration_table is not None
    table = StorefrontAnalyticsEvent.__table__
    assert _sql(str(CreateTable(table).compile(dialect=postgresql.dialect()))) == _sql(
        migration_table.group()
    )
    actual_indexes = {
        _sql(value)
        for value in re.findall(
            r"CREATE INDEX [^;]+ ON public\.analytics_events \([^;]+\);", emitted
        )
    }
    assert len(actual_indexes) == 8
    assert {
        _sql(str(CreateIndex(index).compile(dialect=postgresql.dialect())))
        for index in table.indexes
    } == actual_indexes


def test_migration_bound_analytics_is_not_created_by_divergent_base_bootstrap():
    table = StorefrontAnalyticsEvent.__table__
    assert table.metadata is not Base.metadata
    assert "analytics_events" not in Base.metadata.tables
    # The existing bootstrap remains unchanged. Analytics preserves its
    # VARCHAR(36) user identity rather than converting it to UUID.
    assert str(Base.metadata.tables["users"].c.id.type) == "VARCHAR(36)"
    foreign_key = next(iter(table.c.user_id.foreign_keys))
    assert foreign_key.target_fullname == "public.users.id"
    assert foreign_key.ondelete == "SET NULL"
    assert str(foreign_key.column.type.compile(dialect=postgresql.dialect())) == "VARCHAR(36)"


async def test_sqlite_defaults_nullable_columns_and_set_null_foreign_key(tmp_path):
    """A local compatibility schema exercises the migration's actual semantics."""
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{tmp_path / 'schema.db'}",
        execution_options={"schema_translate_map": {"public": None}},
    )
    table = StorefrontAnalyticsEvent.__table__
    users = table.metadata.tables["public.users"]
    user_id = uuid4()
    try:
        async with engine.begin() as connection:
            await connection.execute(text("PRAGMA foreign_keys=ON"))
            await connection.run_sync(users.create)
            await connection.run_sync(table.create)
            await connection.execute(insert(users).values(id=user_id))
            row = (
                await connection.execute(
                    insert(table)
                    .values(
                        event_type="storefront",
                        event_name="page_view",
                        source=BRIDGE_SOURCE,
                        user_id=user_id,
                    )
                    .returning(
                        table.c.id, table.c.properties, table.c.event_timestamp, table.c.created_at
                    )
                )
            ).one()
            assert row.id is not None and row.properties == {}
            assert row.event_timestamp is not None and row.created_at is not None
            await connection.execute(delete(users).where(users.c.id == user_id))
            assert (await connection.execute(select(table.c.user_id))).scalar_one() is None
            await connection.execute(
                insert(table).values(
                    event_type="storefront",
                    event_name="product_view",
                    source=BRIDGE_SOURCE,
                    properties=text("NULL"),
                    created_at=None,
                )
            )
            nullable_row = (
                await connection.execute(
                    select(table.c.properties, table.c.created_at).where(
                        table.c.event_name == "product_view"
                    )
                )
            ).one()
            assert nullable_row.properties is None and nullable_row.created_at is None
    finally:
        await engine.dispose()


def _event(session_id: str, now: datetime, **properties):
    return {
        "id": uuid4(),
        "event_type": "storefront",
        "event_name": "page_view",
        "source": BRIDGE_SOURCE,
        "session_id": session_id,
        "numeric_value": None,
        "event_timestamp": now,
        "properties": {
            "site_id": "offline-fixture",
            "environment": "test",
            "synthetic": False,
            "payload_hash": session_id,
            **properties,
        },
    }


async def test_late_arrival_cannot_split_summary_counts_across_snapshots(tmp_path):
    """A second connection commits after the first summary result is buffered."""
    db_url = f"sqlite+aiosqlite:///{tmp_path / 'race.db'}"
    engine = create_async_engine(
        db_url, execution_options={"schema_translate_map": {"public": None}}
    )
    writer_engine = create_async_engine(
        db_url, execution_options={"schema_translate_map": {"public": None}}
    )
    now = datetime.now(UTC)
    statements = []

    class LateWriterSession(AsyncSession):
        async def execute(self, statement, *args, **kwargs):
            result = await super().execute(statement, *args, **kwargs)
            statements.append(statement)
            if len(statements) == 1:
                async with async_sessionmaker(writer_engine)() as writer:
                    await persist_events(writer, [_event("late-session", now)])
            return result

    try:
        async with engine.begin() as connection:
            await connection.run_sync(StorefrontAnalyticsEvent.__table__.create)
        async with async_sessionmaker(engine)() as writer:
            await persist_events(writer, [_event("first-session", now)])
        async with async_sessionmaker(engine, class_=LateWriterSession)() as reader:
            result = await read_summary(
                reader, "offline-fixture", "test", now - timedelta(days=1), now, 1
            )
        assert result["metrics"]["event_count"] == 1
        assert result["metrics"]["sessions"] == 1
        assert result["event_counts"] == {"page_view": 1}
        assert len(statements) == 1
        # This also checks that the expression can target PostgreSQL; it does
        # not imply authenticated execution against PostgreSQL or Neon.
        compiled = str(statements[0].compile(dialect=postgresql.dialect()))
        assert "count(distinct(" in compiled.lower()
        assert "analytics_events" in compiled and "WITH " in compiled
        async with async_sessionmaker(engine)() as reader:
            next_result = await read_summary(
                reader, "offline-fixture", "test", now - timedelta(days=1), now, 1
            )
        assert next_result["metrics"]["event_count"] == 2
        assert next_result["metrics"]["sessions"] == 2
    finally:
        await writer_engine.dispose()
        await engine.dispose()


async def test_session_count_uses_same_scope_and_provenance_as_event_count(tmp_path):
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{tmp_path / 'scope.db'}",
        execution_options={"schema_translate_map": {"public": None}},
    )
    now = datetime.now(UTC)
    events = [
        _event("shared-session", now),
        _event("shared-session", now),
        _event("other-session", now),
        _event("synthetic-session", now, synthetic=True),
        _event("missing-flag-session", now, synthetic=None),
        _event("other-site-session", now, site_id="other-site"),
        _event("other-environment-session", now, environment="production"),
        _event("older-session", now - timedelta(days=2)),
    ]
    commerce = _event("commerce-session", now, currency="USD")
    commerce.update(source=COMMERCE_SOURCE, event_name="purchase", numeric_value=10)
    events.append(commerce)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(StorefrontAnalyticsEvent.__table__.create)
        async with async_sessionmaker(engine)() as db:
            await persist_events(db, events)
            result = await read_summary(
                db, "offline-fixture", "test", now - timedelta(days=1), now, 1
            )
        assert result["metrics"]["event_count"] == 3
        assert result["metrics"]["sessions"] == 2
        assert result["metrics"]["verified_purchases"] == 1
        assert result["metrics"]["verified_revenue"] == 10
        assert result["coverage"]["synthetic_events_excluded"] == 1
    finally:
        await engine.dispose()
