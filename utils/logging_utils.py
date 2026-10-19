"""
Compatibility shim — import from :mod:`utils.log` in new code.

Kept so existing ``from utils.logging_utils import ...`` call sites (MCP server,
``utils/rate_limiting.py``, tests) keep working. All names are the objects
defined in :mod:`utils.log`; the context variables are shared, not copied.
"""

from __future__ import annotations

from typing import TextIO

from utils.log import (
    LogContext,
    clear_request_context,
)
from utils.log import configure_logging as _configure_logging
from utils.log import (
    correlation_id_var,
    generate_correlation_id,
    get_correlation_id,
    get_logger,
    log_api_request,
    log_api_response,
    log_error,
    request_id_var,
    set_correlation_id,
    set_request_context,
    user_id_var,
)


def configure_logging(json_output: bool = True, stream: TextIO | None = None) -> None:
    """Configure structlog for the MCP server (legacy signature, JSON by default).

    Pass ``stream=sys.stderr`` from stdio entrypoints: stdout is the JSON-RPC channel.
    """
    _configure_logging(json_output=json_output, stream=stream)


__all__ = [
    "LogContext",
    "clear_request_context",
    "configure_logging",
    "correlation_id_var",
    "generate_correlation_id",
    "get_correlation_id",
    "get_logger",
    "log_api_request",
    "log_api_response",
    "log_error",
    "request_id_var",
    "set_correlation_id",
    "set_request_context",
    "user_id_var",
]
