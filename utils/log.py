"""
DevSkyy Unified Logging
=======================

Single import surface for logging across the repo. Replaces three overlapping
modules, which are now thin re-export shims over this one:

- ``utils.logging_utils``       (MCP server, structlog, stdout-safe)
- ``core.structured_logging``   (FastAPI app, structlog over stdlib logging)
- ``utils.logger``              (stdlib-only; re-exported below, still importable)

One set of context variables
----------------------------
``correlation_id``, ``request_id``, ``user_id`` and ``agent_id`` live here and
nowhere else. Previously the app and the MCP server each owned a private
``correlation_id`` ContextVar, so an ID bound by an agent never reached MCP log
lines. Every legacy module now aliases these objects.

Usage::

    from utils.log import configure_logging, get_logger, bind_contextvars

    configure_logging(json_output=True, stream=sys.stderr)   # MCP stdio server
    configure_logging()                                      # app: JSON unless TTY

    log = get_logger(__name__)
    bind_contextvars(correlation_id="abc", agent_id="seo-1")
    log.info("render_started", sku="br-001")

For dependency-free scripts, use ``setup_logger`` (stdlib only, no structlog
configuration, rotating file handler).

Note: this file is ``log.py``, not ``logging.py``. A module named ``logging.py``
shadows the standard library for any script run from its directory.
"""

from __future__ import annotations

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any, TextIO

import structlog
from structlog.types import EventDict, WrappedLogger
from utils.logger import (
    JsonFormatter,
    LoggerConfig,
)
from utils.logger import get_logger as get_stdlib_logger
from utils.logger import log_with_context, setup_logger, temporary_level

# ---------------------------------------------------------------------------
# Context variables — the only definitions in the repo
# ---------------------------------------------------------------------------

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")
agent_id_var: ContextVar[str] = ContextVar("agent_id", default="")

_CONTEXT_VARS: dict[str, ContextVar[str]] = {
    "correlation_id": correlation_id_var,
    "request_id": request_id_var,
    "user_id": user_id_var,
    "agent_id": agent_id_var,
}


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return f"corr-{uuid.uuid4().hex[:16]}"


def get_correlation_id() -> str:
    """Current correlation ID, or a freshly generated one if none is bound."""
    return correlation_id_var.get() or generate_correlation_id()


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for the current async context."""
    correlation_id_var.set(correlation_id)


def set_request_context(request_id: str | None = None, user_id: str | None = None) -> None:
    """Bind request/user IDs and make sure a correlation ID exists."""
    if request_id:
        request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    if not correlation_id_var.get():
        set_correlation_id(generate_correlation_id())


def clear_request_context() -> None:
    """Reset every bound context variable."""
    unbind_contextvars()


def bind_contextvars(**kwargs: str) -> None:
    """Bind any of ``correlation_id``, ``request_id``, ``user_id``, ``agent_id``.

    Unknown keys are ignored (use ``LogContext`` for arbitrary structlog fields).
    """
    for key, value in kwargs.items():
        var = _CONTEXT_VARS.get(key)
        if var is not None:
            var.set(value)


def unbind_contextvars(*keys: str) -> None:
    """Unbind the named context variables; with no arguments, unbind all."""
    for key, var in _CONTEXT_VARS.items():
        if not keys or key in keys:
            var.set("")


def clear_contextvars() -> None:
    """Alias for ``unbind_contextvars()``."""
    unbind_contextvars()


def add_context_vars(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """structlog processor: stamp bound context IDs onto every event.

    Explicit event keys win over ambient context.
    """
    for key, var in _CONTEXT_VARS.items():
        value = var.get()
        if value and key not in event_dict:
            event_dict[key] = value
    return event_dict


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def _resolve_level(log_level: str | int) -> int:
    if isinstance(log_level, int):
        return log_level
    level = logging.getLevelName(log_level.upper())
    if not isinstance(level, int):
        raise ValueError(f"invalid log level: {log_level!r}")
    return level


def configure_logging(
    json_output: bool | None = None,
    *,
    log_level: str | int = "INFO",
    stream: TextIO | None = None,
    include_timestamp: bool = True,
    callsite: bool = True,
    stdlib: bool = False,
) -> None:
    """Configure structlog once at process startup.

    Args:
        json_output: ``True`` JSON, ``False`` console. ``None`` auto-detects:
            JSON unless the target stream is a TTY.
        log_level: Minimum level, name or number. Invalid names raise ``ValueError``.
        stream: Output stream. ``None`` -> ``sys.stdout``. **The MCP stdio server
            must pass ``sys.stderr``** — stdout is its JSON-RPC channel.
        include_timestamp: Add an ISO-8601 UTC ``timestamp``.
        callsite: Add ``filename`` / ``lineno`` / ``func_name``.
        stdlib: Route through stdlib ``logging`` (``structlog.stdlib``) and call
            ``logging.basicConfig``, so third-party libraries share the same
            handler. This is the FastAPI app's mode; leave ``False`` for the MCP
            server.
    """
    level = _resolve_level(log_level)
    target = stream if stream is not None else sys.stdout
    if json_output is None:
        json_output = not getattr(target, "isatty", lambda: False)()

    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
    ]
    if stdlib:
        processors.append(structlog.stdlib.add_logger_name)
    processors.append(add_context_vars)
    if include_timestamp:
        processors.append(structlog.processors.TimeStamper(fmt="iso", utc=True))
    if callsite:
        processors.append(
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                ]
            )
        )
    processors.append(structlog.processors.StackInfoRenderer())

    if json_output:
        processors.append(structlog.processors.format_exc_info)
        processors.append(structlog.processors.JSONRenderer(sort_keys=True))
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=getattr(target, "isatty", lambda: False)(),
                exception_formatter=structlog.dev.plain_traceback,
            )
        )

    if stdlib:
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        logging.basicConfig(format="%(message)s", stream=target, level=level)
    else:
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(file=target),
            cache_logger_on_first_use=True,
        )


def get_logger(name: str | None = None) -> Any:
    """Return a structlog logger (``name`` is typically ``__name__``)."""
    return structlog.get_logger(name)


class LogContext:
    """Context manager that binds structlog fields for the duration of a block."""

    def __init__(self, **kwargs: Any) -> None:
        self.context = kwargs

    def __enter__(self) -> LogContext:
        structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        structlog.contextvars.unbind_contextvars(*self.context)


# ---------------------------------------------------------------------------
# API-boundary helpers (used by the MCP server)
# ---------------------------------------------------------------------------


async def log_api_request(
    endpoint: str,
    method: str,
    params: dict | None = None,
    correlation_id: str | None = None,
) -> None:
    """Log an outbound API request with correlation tracking."""
    if correlation_id:
        set_correlation_id(correlation_id)
    with LogContext(endpoint=endpoint, method=method, correlation_id=get_correlation_id()):
        await get_logger(__name__).ainfo("api_request", params=params or {})


async def log_api_response(
    endpoint: str,
    status_code: int,
    duration_ms: float,
    error: str | None = None,
) -> None:
    """Log an API response with performance metrics."""
    with LogContext(
        endpoint=endpoint,
        status_code=status_code,
        duration_ms=duration_ms,
        correlation_id=get_correlation_id(),
    ):
        logger = get_logger(__name__)
        if error:
            await logger.aerror("api_response_error", error=error)
        else:
            await logger.ainfo("api_response_success")


async def log_error(
    error: Exception,
    context: dict | None = None,
    stack_trace: str | None = None,
) -> None:
    """Log an exception with full context."""
    error_context: dict[str, Any] = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "correlation_id": get_correlation_id(),
    }
    if context:
        error_context.update(context)
    if stack_trace:
        error_context["stack_trace"] = stack_trace
    with LogContext(**error_context):
        await get_logger(__name__).aerror("exception_occurred")


__all__ = [
    "JsonFormatter",
    "LogContext",
    "LoggerConfig",
    "add_context_vars",
    "agent_id_var",
    "bind_contextvars",
    "clear_contextvars",
    "clear_request_context",
    "configure_logging",
    "correlation_id_var",
    "generate_correlation_id",
    "get_correlation_id",
    "get_logger",
    "get_stdlib_logger",
    "log_api_request",
    "log_api_response",
    "log_error",
    "log_with_context",
    "request_id_var",
    "set_correlation_id",
    "set_request_context",
    "setup_logger",
    "temporary_level",
    "unbind_contextvars",
    "user_id_var",
]
