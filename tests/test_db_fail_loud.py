"""TDD guard: production must fail loud when DATABASE_URL is unset.

database/db.py:58 defaults DATABASE_URL to a local SQLite file so dev/test
workflows never need a real database. DatabaseManager.initialize() now refuses
that fallback when ENVIRONMENT=production and DATABASE_URL is missing, raising
RuntimeError naming the env var (never a value) before any engine is created.
"""

from __future__ import annotations

import pytest

from database.db import DatabaseConfig, DatabaseManager


@pytest.fixture(autouse=True)
async def _clean_db_singleton():
    """DatabaseManager is a process-wide singleton (database/db.py:698) — force
    clean state before and after every test so one test's engine can't leak
    into the next via the early `if self._engine is not None: return`.
    """
    await DatabaseManager().close()
    yield
    await DatabaseManager().close()


class TestProductionFailLoud:
    """ENVIRONMENT=production requires DATABASE_URL to be set explicitly."""

    async def test_production_without_database_url_raises(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.delenv("DATABASE_URL", raising=False)

        with pytest.raises(RuntimeError, match="DATABASE_URL"):
            await DatabaseManager().initialize()

        assert DatabaseManager()._engine is None

    async def test_production_with_database_url_passes_through(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        # Real deployments pass a Postgres DSN; an in-memory SQLite URL keeps
        # this test hermetic while still proving the guard doesn't fire once
        # DATABASE_URL is present.
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

        db = DatabaseManager()
        await db.initialize(DatabaseConfig(url="sqlite+aiosqlite:///:memory:"))

        assert db._engine is not None
        health = await db.health_check()
        assert health["status"] == "healthy"

    async def test_dev_without_database_url_does_not_raise(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.delenv("DATABASE_URL", raising=False)

        # DatabaseConfig.url's own default is a pydantic class attribute bound
        # to os.getenv(...) at module-import time, not per-instantiation, so
        # monkeypatch can't retarget it here (see database/db.py:58). What's
        # under test is narrower and correct for this change: the new guard
        # in initialize() must not raise when ENVIRONMENT != production,
        # regardless of DATABASE_URL — pass an explicit in-memory config so
        # the test stays hermetic (no ./devskyy.db file artifact).
        db = DatabaseManager()
        await db.initialize(DatabaseConfig(url="sqlite+aiosqlite:///:memory:"))

        assert db._engine is not None


class TestAsyncDatabaseUrlNormalization:
    """Keep channel binding on psycopg and normalize sslmode for asyncpg."""

    def test_channel_binding_url_uses_psycopg_and_preserves_security_options(self):
        from database.db import _normalize_async_url

        url = _normalize_async_url(
            "postgresql://u:p@ep-x-123.us-west-2.aws.neon.tech/neondb"
            "?sslmode=require&channel_binding=require"
        )
        assert url.startswith("postgresql+psycopg://")
        assert "sslmode=require" in url
        assert "channel_binding=require" in url

        routed = _normalize_async_url(
            "postgresql+asyncpg://u:p@h/db?ssl=require&channel_binding=require"
        )
        assert routed.startswith("postgresql+psycopg://")
        assert "sslmode=require" in routed and "channel_binding=require" in routed
        assert "?ssl=" not in routed and "&ssl=" not in routed
        for options in (
            "ssl=require&sslmode=disable&channel_binding=require",
            "ssl=true&channel_binding=require",
            "command_timeout=5&channel_binding=require",
            "sslmode=require&channel_binding=require&channel_binding=disable",
        ):
            with pytest.raises(ValueError):
                _normalize_async_url("postgresql+asyncpg://u:p@h/db?" + options)

    def test_plain_postgres_url_untouched_params_absent(self):
        from database.db import _normalize_async_url

        assert (
            _normalize_async_url("postgres://u:p@h:5432/db") == "postgresql+asyncpg://u:p@h:5432/db"
        )

    def test_already_async_url_with_sslmode_still_translated(self):
        from database.db import _normalize_async_url

        url = _normalize_async_url("postgresql+asyncpg://u:p@h/db?sslmode=verify-full")
        assert "sslmode=" not in url
        assert "ssl=verify-full" in url

    def test_sqlite_url_untouched(self):
        from database.db import _normalize_async_url

        assert (
            _normalize_async_url("sqlite+aiosqlite:///./devskyy.db")
            == "sqlite+aiosqlite:///./devskyy.db"
        )
