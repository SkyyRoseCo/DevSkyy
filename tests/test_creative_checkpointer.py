"""Tests for the LangGraph Postgres checkpointer.

Verifies:
    - URL normalization handles SQLAlchemy and Heroku-style URLs
    - `get_checkpointer()` returns None gracefully when no PG URL is set
    - sqlite URLs short-circuit to None (no checkpointing)
    - async runner returns a structured error envelope without raising
      when DATABASE_URL is unset (falls back to non-checkpointed graph)
"""

from __future__ import annotations

import asyncio

import pytest

from skyyrose.elite_studio.creative import checkpointer as checkpointer_mod


class TestNormalizePgUrl:
    def test_returns_none_for_empty(self):
        assert checkpointer_mod._normalize_pg_url("") is None

    def test_returns_none_for_sqlite(self):
        assert checkpointer_mod._normalize_pg_url("sqlite:///./db.sqlite") is None
        assert checkpointer_mod._normalize_pg_url("sqlite+aiosqlite:///./db.sqlite") is None

    def test_strips_sqlalchemy_driver_suffix(self):
        url = "postgresql+asyncpg://user:pw@host:5432/db"
        assert checkpointer_mod._normalize_pg_url(url) == "postgresql://user:pw@host:5432/db"

        url = "postgresql+psycopg://u:p@h:5432/d"
        assert checkpointer_mod._normalize_pg_url(url) == "postgresql://u:p@h:5432/d"

    def test_passes_through_plain_postgresql_url(self):
        url = "postgresql://u:p@h:5432/d"
        assert checkpointer_mod._normalize_pg_url(url) == url

    def test_passes_through_heroku_postgres_url(self):
        # Heroku still uses the legacy "postgres://" scheme; psycopg accepts it.
        url = "postgres://u:p@h:5432/d"
        assert checkpointer_mod._normalize_pg_url(url) == url

    def test_returns_none_for_unknown_scheme(self):
        assert checkpointer_mod._normalize_pg_url("mysql://x") is None


@pytest.mark.asyncio
async def test_get_checkpointer_returns_none_without_db_url(monkeypatch):
    """Without DATABASE_URL, the checkpointer factory returns None silently."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    # Reset module-level singletons so the test is order-independent.
    checkpointer_mod._pool = None
    checkpointer_mod._checkpointer = None

    result = await checkpointer_mod.get_checkpointer()
    assert result is None


@pytest.mark.asyncio
async def test_get_checkpointer_returns_none_for_sqlite(monkeypatch):
    """sqlite URLs short-circuit to None (LangGraph PG saver only supports PG)."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    checkpointer_mod._pool = None
    checkpointer_mod._checkpointer = None

    result = await checkpointer_mod.get_checkpointer()
    assert result is None


@pytest.mark.asyncio
async def test_arun_creative_falls_back_when_no_pg(monkeypatch):
    """arun_creative should still work (no checkpointing) when DATABASE_URL is unset."""
    from skyyrose.elite_studio.creative import router as router_mod
    from skyyrose.elite_studio.creative import runner as runner_mod

    monkeypatch.delenv("DATABASE_URL", raising=False)
    # Reset singletons
    checkpointer_mod._pool = None
    checkpointer_mod._checkpointer = None
    router_mod._CREATIVE_GRAPH_CHECKPOINTED = None

    # We don't care about the actual operation succeeding — we care that
    # the call doesn't blow up trying to import psycopg / connect to PG.
    result = await runner_mod.arun_creative(
        intent="design-ideation",
        params={"theme": "minimalist"},
    )
    assert isinstance(result, dict)
    assert "operation_id" in result
    assert "status" in result


@pytest.fixture
def checkpoint_runtime(monkeypatch):
    """Isolate lifecycle tests; no database/authentication is involved."""
    import asyncio
    import sys
    from types import ModuleType
    from unittest.mock import AsyncMock

    pool_module = ModuleType("psycopg_pool")
    saver_module = ModuleType("langgraph.checkpoint.postgres.aio")
    pools = []
    savers = []

    class Pool:
        def __init__(self, **kwargs):
            self.open = AsyncMock()
            self.close = AsyncMock()
            pools.append(self)

    class Saver:
        def __init__(self, pool):
            self.pool = pool
            self.setup = AsyncMock()
            savers.append(self)

    pool_module.AsyncConnectionPool = Pool
    saver_module.AsyncPostgresSaver = Saver
    monkeypatch.setitem(sys.modules, "psycopg_pool", pool_module)
    monkeypatch.setitem(sys.modules, "langgraph.checkpoint.postgres.aio", saver_module)
    monkeypatch.setenv("DATABASE_URL", "postgresql://synthetic:synthetic@localhost/test")
    monkeypatch.setattr(checkpointer_mod, "_pool", None)
    monkeypatch.setattr(checkpointer_mod, "_checkpointer", None)
    monkeypatch.setattr(checkpointer_mod, "_init_lock", asyncio.Lock())
    return pools, savers, Saver


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failure", [RuntimeError("synthetic setup failure"), asyncio.CancelledError()]
)
async def test_failed_or_cancelled_setup_closes_pool_and_can_retry(
    checkpoint_runtime, monkeypatch, failure
):
    pools, savers, Saver = checkpoint_runtime
    original = Saver.__init__

    def failing_setup(self, pool):
        original(self, pool)
        self.setup.side_effect = failure

    monkeypatch.setattr(Saver, "__init__", failing_setup)
    with pytest.raises(type(failure)):
        await checkpointer_mod.get_checkpointer()
    pools[0].close.assert_awaited_once()
    assert checkpointer_mod._pool is None
    assert checkpointer_mod._checkpointer is None
    monkeypatch.setattr(Saver, "__init__", original)
    result = await checkpointer_mod.get_checkpointer()
    assert result is savers[1]
    await checkpointer_mod.close_checkpointer()
    pools[1].close.assert_awaited_once()


@pytest.mark.asyncio
async def test_concurrent_first_calls_publish_one_ready_saver(checkpoint_runtime):
    import asyncio

    pools, savers, _ = checkpoint_runtime
    results = await asyncio.gather(*(checkpointer_mod.get_checkpointer() for _ in range(12)))
    assert len(pools) == len(savers) == 1
    assert all(result is savers[0] for result in results)
    savers[0].setup.assert_awaited_once()
    await checkpointer_mod.close_checkpointer()
    assert checkpointer_mod._checkpointer is checkpointer_mod._pool is None
    pools[0].close.assert_awaited_once()


@pytest.mark.asyncio
async def test_real_task_cancellation_closes_unpublished_pool(checkpoint_runtime, monkeypatch):
    pools, savers, Saver = checkpoint_runtime
    setup_started = asyncio.Event()
    setup_blocked = asyncio.Event()
    original = Saver.__init__

    async def pending_setup():
        setup_started.set()
        await setup_blocked.wait()

    def paused_saver(self, pool):
        original(self, pool)
        self.setup.side_effect = pending_setup

    monkeypatch.setattr(Saver, "__init__", paused_saver)
    task = asyncio.create_task(checkpointer_mod.get_checkpointer())
    await setup_started.wait()
    assert checkpointer_mod._pool is checkpointer_mod._checkpointer is None
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    pools[0].close.assert_awaited_once()
    assert checkpointer_mod._pool is checkpointer_mod._checkpointer is None


@pytest.mark.asyncio
async def test_pending_setup_is_not_published_to_concurrent_callers(
    checkpoint_runtime, monkeypatch
):
    pools, savers, Saver = checkpoint_runtime
    setup_started = asyncio.Event()
    setup_released = asyncio.Event()
    original = Saver.__init__

    async def pending_setup():
        setup_started.set()
        await setup_released.wait()

    def paused_saver(self, pool):
        original(self, pool)
        self.setup.side_effect = pending_setup

    monkeypatch.setattr(Saver, "__init__", paused_saver)
    first = asyncio.create_task(checkpointer_mod.get_checkpointer())
    await setup_started.wait()
    others = [asyncio.create_task(checkpointer_mod.get_checkpointer()) for _ in range(10)]
    await asyncio.sleep(0)
    assert not any(task.done() for task in others)
    assert checkpointer_mod._pool is checkpointer_mod._checkpointer is None
    assert len(pools) == 1
    setup_released.set()
    results = await asyncio.gather(first, *others)
    assert all(result is savers[0] for result in results)
    await checkpointer_mod.close_checkpointer()


@pytest.mark.asyncio
async def test_pool_open_failure_and_cleanup_failure_preserve_original_error(
    checkpoint_runtime, monkeypatch, caplog
):
    pools, _, _ = checkpoint_runtime
    import psycopg_pool

    original = psycopg_pool.AsyncConnectionPool.__init__

    def failing_pool(self, **kwargs):
        original(self, **kwargs)
        self.open.side_effect = RuntimeError("synthetic open failure")
        self.close.side_effect = RuntimeError("sensitive cleanup detail")

    monkeypatch.setattr(psycopg_pool.AsyncConnectionPool, "__init__", failing_pool)
    with pytest.raises(RuntimeError, match="synthetic open failure"):
        await checkpointer_mod.get_checkpointer()
    pools[0].close.assert_awaited_once()
    assert checkpointer_mod._pool is checkpointer_mod._checkpointer is None
    assert "sensitive cleanup detail" not in caplog.text
    assert "creative_checkpointer_cleanup_failed" in caplog.text


@pytest.mark.asyncio
async def test_repeated_cancellation_drains_close_before_propagating(
    checkpoint_runtime, monkeypatch
):
    pools, _, Saver = checkpoint_runtime
    setup_started, close_started, close_release = asyncio.Event(), asyncio.Event(), asyncio.Event()
    original = Saver.__init__

    async def pending_setup():
        setup_started.set()
        await asyncio.Event().wait()

    async def pending_close():
        close_started.set()
        await close_release.wait()

    def paused_saver(self, pool):
        original(self, pool)
        self.setup.side_effect = pending_setup
        pool.close.side_effect = pending_close

    monkeypatch.setattr(Saver, "__init__", paused_saver)
    task = asyncio.create_task(checkpointer_mod.get_checkpointer())
    await setup_started.wait()
    task.cancel()
    await close_started.wait()
    task.cancel()
    await asyncio.sleep(0)
    assert not task.done()
    close_release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    pools[0].close.assert_awaited_once()
    assert not checkpointer_mod._cleanup_tasks


@pytest.mark.asyncio
async def test_unresponsive_close_is_bounded_and_records_incomplete_cleanup(
    checkpoint_runtime, monkeypatch, caplog
):
    _, _, Saver = checkpoint_runtime
    original = Saver.__init__

    async def unresponsive_close():
        await asyncio.Event().wait()

    def stalled_saver(self, pool):
        original(self, pool)
        self.setup.side_effect = RuntimeError("synthetic setup failure")
        pool.close.side_effect = unresponsive_close

    monkeypatch.setattr(Saver, "__init__", stalled_saver)
    monkeypatch.setattr(checkpointer_mod, "_POOL_CLEANUP_TIMEOUT_SECONDS", 0.01)
    with pytest.raises(RuntimeError, match="synthetic setup failure"):
        await asyncio.wait_for(checkpointer_mod.get_checkpointer(), 1)
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    assert "creative_checkpointer_cleanup_timeout" in caplog.text
    assert checkpointer_mod._pool is checkpointer_mod._checkpointer is None
    assert not checkpointer_mod._cleanup_tasks
