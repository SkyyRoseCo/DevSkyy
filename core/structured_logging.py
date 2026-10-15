"""
Compatibility shim — import from :mod:`utils.log` in new code.

Kept so ``from core.structured_logging import ...`` (``main_enterprise.py``,
``agents/base_super_agent``) keeps working. The context variables are the same
objects as in :mod:`utils.log`, so an ID bound here is visible to every other
logging entry point.
"""

from __future__ import annotations

from utils.log import (
    add_context_vars,
    agent_id_var,
    bind_contextvars,
    clear_contextvars,
)
from utils.log import configure_logging as _configure_logging
from utils.log import correlation_id_var, get_logger, unbind_contextvars, user_id_var


def configure_logging(
    *,
    json_output: bool | None = None,
    log_level: str = "INFO",
    include_timestamp: bool = True,
) -> None:
    """Configure structured logging for the FastAPI app (legacy signature).

    JSON unless stdout is a TTY; routes through stdlib ``logging`` so third-party
    libraries share the handler.
    """
    _configure_logging(
        json_output=json_output,
        log_level=log_level,
        include_timestamp=include_timestamp,
        callsite=False,
        stdlib=True,
    )


__all__ = [
    "add_context_vars",
    "agent_id_var",
    "bind_contextvars",
    "clear_contextvars",
    "configure_logging",
    "correlation_id_var",
    "get_logger",
    "unbind_contextvars",
    "user_id_var",
]
