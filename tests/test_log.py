"""Contract tests for the unified logging module ``utils.log``.

The three legacy entry points (``utils.logging_utils``, ``core.structured_logging``,
``utils.logger``) must stay import-compatible *and* share one set of context
variables, so a correlation ID bound by an agent is visible to MCP log lines.
"""

from __future__ import annotations

import io
import json
import logging

import pytest
import structlog


@pytest.fixture(autouse=True)
def _reset_state():
    """configure_logging() is process-global; restore it after every test."""
    from utils import log

    log.clear_contextvars()
    yield
    log.clear_contextvars()
    structlog.reset_defaults()


@pytest.mark.unit
def test_legacy_modules_share_one_set_of_contextvars():
    from core import structured_logging
    from utils import log, logging_utils

    assert logging_utils.correlation_id_var is log.correlation_id_var
    assert logging_utils.request_id_var is log.request_id_var
    assert logging_utils.user_id_var is log.user_id_var
    assert structured_logging.correlation_id_var is log.correlation_id_var
    assert structured_logging.user_id_var is log.user_id_var
    assert structured_logging.agent_id_var is log.agent_id_var


@pytest.mark.unit
def test_agent_bound_correlation_id_is_visible_to_mcp_helpers():
    """The regression this module exists for: two ContextVar sets never met."""
    from utils.logging_utils import get_correlation_id

    from core.structured_logging import bind_contextvars

    bind_contextvars(correlation_id="corr-from-agent", agent_id="a-1")
    assert get_correlation_id() == "corr-from-agent"


@pytest.mark.unit
def test_unbind_all_and_selective():
    from utils import log

    log.bind_contextvars(correlation_id="c", user_id="u", agent_id="a")
    log.unbind_contextvars("user_id")
    assert log.user_id_var.get() == ""
    assert log.correlation_id_var.get() == "c"
    log.unbind_contextvars()
    assert log.correlation_id_var.get() == ""
    assert log.agent_id_var.get() == ""


@pytest.mark.unit
def test_json_output_injects_context_and_goes_to_stream():
    from utils import log

    buf = io.StringIO()
    log.configure_logging(json_output=True, stream=buf)
    log.bind_contextvars(correlation_id="corr-1", user_id="u-9", agent_id="agent-7")
    log.get_logger("t").info("hello", sku="br-001")

    line = json.loads(buf.getvalue().strip().splitlines()[-1])
    assert line["event"] == "hello"
    assert line["sku"] == "br-001"
    assert line["correlation_id"] == "corr-1"
    assert line["user_id"] == "u-9"
    assert line["agent_id"] == "agent-7"
    assert line["level"] == "info"
    assert "timestamp" in line


@pytest.mark.unit
def test_log_level_filters_below_threshold():
    from utils import log

    buf = io.StringIO()
    log.configure_logging(json_output=True, stream=buf, log_level="WARNING")
    logger = log.get_logger("t")
    logger.info("dropped")
    logger.warning("kept")
    events = [json.loads(ln)["event"] for ln in buf.getvalue().strip().splitlines()]
    assert events == ["kept"]


@pytest.mark.unit
def test_invalid_log_level_raises():
    from utils import log

    with pytest.raises(ValueError):
        log.configure_logging(log_level="LOUD")


@pytest.mark.unit
def test_exception_is_rendered_into_json():
    from utils import log

    buf = io.StringIO()
    log.configure_logging(json_output=True, stream=buf)
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        log.get_logger("t").error("failed", exc_info=True)
    line = json.loads(buf.getvalue().strip().splitlines()[-1])
    assert "RuntimeError: boom" in line["exception"]


@pytest.mark.unit
def test_stdlib_backend_routes_through_stdlib_logging(caplog):
    from utils import log

    log.configure_logging(json_output=True, stdlib=True, stream=io.StringIO())
    with caplog.at_level(logging.INFO):
        log.get_logger("devskyy.test").info("via_stdlib", k="v")
    assert any("via_stdlib" in r.getMessage() for r in caplog.records)


@pytest.mark.unit
def test_legacy_configure_signatures_still_work():
    from utils.logging_utils import configure_logging as util_configure

    from core.structured_logging import configure_logging as core_configure

    util_configure(json_output=True, stream=io.StringIO())
    core_configure(json_output=False, log_level="DEBUG", include_timestamp=False)


@pytest.mark.unit
def test_stdlib_script_logger_is_reexported():
    from utils import log, logger

    assert log.setup_logger is logger.setup_logger
    assert log.JsonFormatter is logger.JsonFormatter
    assert log.temporary_level is logger.temporary_level


@pytest.mark.unit
def test_correlation_id_shapes():
    from utils import log

    assert log.generate_correlation_id().startswith("corr-")
    log.correlation_id_var.set("")
    generated = log.get_correlation_id()
    assert generated.startswith("corr-")
