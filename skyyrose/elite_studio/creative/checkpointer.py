"""PostgreSQL checkpointer for the Creative Operations Hub LangGraph.

Owns the lifecycle of an `AsyncPostgresSaver` so the graph can resume
mid-pipeline after a Tripo3D failure (or any other transient error)
instead of silently losing state.

Design notes:
    - Singleton `AsyncConnectionPool` per process (production pattern).
    - `AsyncPostgresSaver.setup()` is idempotent — it manages its own
      schema (`checkpoints`, `checkpoint_blobs`, `checkpoint_writes`,
      `checkpoint_migrations`). We deliberately do NOT track these
      tables in alembic — the library owns that schema and bumps it on
      version upgrades.
    - If `DATABASE_URL` is not set or is sqlite, returns `None` and the
      caller falls back to no checkpointing (in-memory state only).

""
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

logger = logging.getLogger(__name__)

_pool = None
_checkpointer: AsyncPostgresSaver | None = None
# Lock guards init so concurrent first-time callers don't double-create
# the pool or hand out a not-yet-setup() saver.
_init_lock = asyncio.Lock()


def _normalize_pg_url(url: str) -> str | None:
    """Normalize a SQLAlchemy URL to a plain psycopg URL.

    `AsyncPostgresSaver` uses psycopg3 directly. SQLAlchemy URLs like
    `postgresql+asyncpg://...` or `postgresql+psycopg://...` need the
    driver suffix stripped.

    Returns:
        Plain `postgresql://` URL, or None if the URL is not Postgres.
    """
    if not url:
        return None
    if url.startswith("sqlite"):
        return None
    if url.startswith("postgresql+"):
        # Strip the +driver suffix
        scheme, rest = url.split("://", 1)
        return f"postgresql://{rest}"
    if url.startswith("postgres://"):
        # Heroku-style — psycopg accepts both
        return url
    if url.startswith("postgresql://"):
        return url
    return None


async def get_checkpointer() -> AsyncPostgresSaver | None:
    """Return the singleton `AsyncPostgresSaver`, creating it on first call.

    Returns `None` when no Postgres URL is configured, signalling to the
    caller that the graph should be compiled without a checkpointer.
    """
    global _pool, _checkpointer

    # Fast path — no lock needed once the saver is fully set up.
    if _checkpointer is not None:
        return _checkpointer

    async with _init_lock:
        # Re-check under the lock: another caller may have completed init
        # while we were waiting.
        if _checkpointer is not None:
            return _checkpointer

        raw_url = os.getenv("DATABASE_URL", "")
        pg_url = _normalize_pg_url(raw_url)
        if pg_url is None:
            logger.info(
                "creative_checkpointer_disabled",
                extra={
                    "reason": "no_postgres_url",
                    "raw_url_scheme": (
                        raw_url.split("://", 1)[0] if "://" in raw_url else "(unset)"
                    ),
                },
            )
            return None

        try:
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
            from psycopg_pool import AsyncConnectionPool
        except ImportError as exc:
            logger.warning(
                "creative_checkpointer_import_failed",
                extra={
                    "error": str(exc),
                    "hint": "pip install langgraph-checkpoint-postgres 'psycopg[binary,pool]'",
                },
            )
            return None

        # Pool size defaults to 20 but can be tuned for small Postgres
        # instances (e.g. Heroku hobby max_connections=25, where 20 here
        # plus the SQLAlchemy pool will exhaust the server).
        pool_size = int(os.getenv("CHECKPOINTER_POOL_SIZE", "20"))
        pool = AsyncConnectionPool(
            conninfo=pg_url,
            max_size=pool_size,
            kwargs={"autocommit": True, "prepare_threshold": 0},
            open=False,
        )
        await pool.open()
        saver = AsyncPostgresSaver(pool)
        # Run setup() BEFORE publishing the saver so concurrent fast-path
        # readers never see a half-initialised checkpointer.
        await saver.setup()
        _pool = pool
        _checkpointer = saver
        logger.info("creative_checkpointer_ready", extra={"pool_size": pool_size})

    return _checkpointer


async def close_checkpointer() -> None:
    """Close the connection pool. Call from the FastAPI shutdown hook."""
    global _pool, _checkpointer
    async with _init_lock:
        if _pool is not None:
            await _pool.close()
        _pool = None
        _checkpointer = None


__all__ = ["get_checkpointer", "close_checkpointer"]
