"""
Pytest Configuration
====================

Shared fixtures and configuration.
"""

import base64
import ipaddress
import os
import sys

import pytest

# Deterministic TEST secrets, set before any security module reads the env.
# These are NOT production secrets — they only make the suite hermetic so it
# doesn't fall back to ephemeral keys (which log noisy per-run warnings).
# `setdefault` means a real env value wins, and a test that needs the key
# ABSENT can still `monkeypatch.delenv` it. Production supplies these via the
# real environment and fails closed without them (security/*.py).
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-not-for-production")
os.environ.setdefault("JWT_REFRESH_SECRET_KEY", "test-jwt-refresh-secret-not-for-production")
os.environ.setdefault(
    "ENCRYPTION_MASTER_KEY",
    base64.b64encode(b"devskyy-test-encryption-key-0032").decode(),  # exactly 32 bytes
)

# =============================================================================
# Async HTTP Client Fixtures (for GDPR and API tests)
# =============================================================================


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Reset rate limiter state before every test to prevent 429 bleed."""
    from security.rate_limiting import rate_limiter

    rate_limiter.sliding_windows.clear()
    rate_limiter.token_buckets.clear()


@pytest.fixture(autouse=True)
def _offline_ssrf_dns():
    """Keep the SSRF validator's DNS lookup off the network.

    SSRFProtection._resolve_hostname calls a real socket.getaddrinfo, so any test
    that pushes a URL through validate_url passed or failed with the machine's
    resolver: a transient outage blocked the Stop gate (bug-352) and a whole-tree
    outage census found 18 such tests in four files. Only resolution is stubbed,
    hostnames get a public address and IP literals resolve to themselves, so the
    scheme / blocked-domain / private-range / metadata checks still run. Set DEVSKYY_TESTS_ALLOW_DNS=1 to opt a run back in.
    """
    if os.environ.get("DEVSKYY_TESTS_ALLOW_DNS") == "1":
        yield
        return
    # Same two constraints as _no_live_sdk_escalation below: patch only when a test
    # module has already loaded the class (importing `security` here would drag its
    # package into jobs that never touch it), and do not request ``monkeypatch``.
    module = sys.modules.get("security.ssrf_protection")
    cls = getattr(module, "SSRFProtection", None) if module else None
    if cls is None:
        yield
        return

    def _resolve_offline(self, hostname: str) -> list[str]:
        # An IP literal must resolve to ITSELF: the validator blocks private ranges
        # by checking the resolved address, so answering "public" for 10.0.0.1 would
        # switch that protection off inside the tests written to prove it.
        try:
            return [str(ipaddress.ip_address(hostname.strip("[]")))]
        except ValueError:
            return ["93.184.216.34"]

    original = cls.__dict__["_resolve_hostname"]
    cls._resolve_hostname = _resolve_offline
    try:
        yield
    finally:
        cls._resolve_hostname = original


@pytest.fixture(autouse=True)
def _no_live_sdk_escalation():
    """Fail closed: never spawn a live Claude Agent SDK agent from pytest.

    Orchestrator._sdk_escalation runs a real, paid, full-tool-profile SDK
    session when every core agent fails. Tests that exercise the escalation
    path (e.g. test_route_escalation_on_failure) would otherwise make a live
    API call, which costs money and hangs under account rate limits.
    Set DEVSKYY_TESTS_ALLOW_SDK=1 to opt a run back in deliberately.
    """
    if os.environ.get("DEVSKYY_TESTS_ALLOW_SDK") == "1":
        yield
        return
    # Do not import the orchestrator here: that drags in the whole agents
    # package (and core/errors/production_errors.py, which needs Python 3.12
    # syntax) into jobs that never touch it. Only patch when a test module
    # has already loaded it.
    # Deliberately not using the ``monkeypatch`` fixture: requesting it here
    # changes fixture setup order for every test, which broke module-level
    # autouse fixtures that tear down after a test's own monkeypatch is undone.
    module = sys.modules.get("agents.core.orchestrator")
    orchestrator_cls = getattr(module, "Orchestrator", None) if module else None
    if orchestrator_cls is None:
        yield
        return

    async def _unavailable(self, task, **kwargs):
        return None

    original = orchestrator_cls.__dict__.get("_sdk_escalation")
    orchestrator_cls._sdk_escalation = _unavailable
    try:
        yield
    finally:
        if original is None:
            delattr(orchestrator_cls, "_sdk_escalation")
        else:
            orchestrator_cls._sdk_escalation = original


@pytest.fixture
async def client():
    """
    Async HTTP client for testing FastAPI endpoints.

    Uses httpx.AsyncClient with ASGITransport for the main FastAPI app.
    """
    import httpx

    from main_enterprise import app

    # Use ASGITransport for httpx >= 0.27
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers(jwt_manager):
    """
    Authorization headers with a valid JWT token for a regular user.

    Returns headers dict with Bearer token for user "test-user-123".
    """
    tokens = jwt_manager.create_token_pair(
        user_id="test-user-123",
        roles=["api_user"],
    )
    return {"Authorization": f"Bearer {tokens.access_token}"}


@pytest.fixture
def admin_headers(jwt_manager):
    """
    Authorization headers with a valid JWT token for an admin user.

    Returns headers dict with Bearer token for user "admin-user-456"
    with admin privileges.
    """
    tokens = jwt_manager.create_token_pair(
        user_id="admin-user-456",
        roles=["admin", "api_user"],
    )
    return {"Authorization": f"Bearer {tokens.access_token}"}


@pytest.fixture
def tool_registry():
    """Fresh tool registry for each test."""
    from core.runtime.tool_registry import ToolRegistry

    return ToolRegistry()


@pytest.fixture
def tool_context():
    """Default tool call context."""
    from core.runtime.tool_registry import ToolCallContext

    return ToolCallContext(
        request_id="test-request",
        user_id="test-user",
    )


@pytest.fixture
def encryption():
    """AES-256-GCM encryption instance."""
    from security.aes256_gcm_encryption import AESGCMEncryption

    return AESGCMEncryption()


@pytest.fixture
def jwt_manager():
    """JWT manager instance - uses the same instance as the app."""
    from security.jwt_oauth2_auth import jwt_manager as _jwt_manager

    return _jwt_manager


@pytest.fixture
def brand_kit():
    """Default SkyyRose brand kit."""
    from wordpress.elementor import SKYYROSE_BRAND_KIT

    return SKYYROSE_BRAND_KIT


@pytest.fixture
def elementor_builder():
    """Elementor builder instance."""
    from wordpress.elementor import ElementorBuilder

    return ElementorBuilder()


# =============================================================================
# Enterprise Intelligence Fixtures
# =============================================================================


import asyncio  # noqa: E402
import os  # noqa: E402
from unittest.mock import AsyncMock, MagicMock, Mock  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["TESTING_MODE"] = "true"
    os.environ["CACHE_TTL_SECONDS"] = "1"  # Fast cache expiry


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_cohere_embed_response():
    """Mock Cohere embed API response."""
    return {
        "embeddings": [[0.1] * 1024, [0.2] * 1024, [0.3] * 1024],
        "meta": {"api_version": {"version": "1"}},
    }


@pytest.fixture
def mock_cohere_rerank_response():
    """Mock Cohere rerank API response."""
    return {
        "results": [
            {"index": 2, "relevance_score": 0.95},
            {"index": 0, "relevance_score": 0.85},
            {"index": 1, "relevance_score": 0.75},
        ],
    }


@pytest.fixture
def mock_deepseek_response():
    """Mock DeepSeek API response."""
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "deepseek-chat",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n - 1)",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 20, "completion_tokens": 50, "total_tokens": 70},
    }


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response."""
    return {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": "This code looks correct."}],
        "model": "claude-3-5-sonnet-20241022",
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 50, "output_tokens": 10},
    }


@pytest.fixture
def mock_groq_response():
    """Mock Groq API response."""
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "llama-3.1-8b-instant",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "INTENT: product_search\nCONFIDENCE: 0.95",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 15, "completion_tokens": 10, "total_tokens": 25},
    }


@pytest.fixture
def mock_github_search_response():
    """Mock GitHub Code Search API response."""
    return {
        "total_count": 2,
        "items": [
            {
                "name": "auth.py",
                "path": "src/middleware/auth.py",
                "repository": {
                    "full_name": "org/repo1",
                    "html_url": "https://github.com/org/repo1",
                },
                "html_url": "https://github.com/org/repo1/blob/main/src/middleware/auth.py",
                "score": 0.95,
            }
        ],
    }


@pytest.fixture
def mock_cohere_client(mock_cohere_embed_response, mock_cohere_rerank_response):
    """Mock Cohere client."""
    client = AsyncMock()
    embed_response = AsyncMock()
    embed_response.embeddings = mock_cohere_embed_response["embeddings"]
    client.embed.return_value = embed_response

    rerank_result = MagicMock()
    rerank_result.results = [
        MagicMock(index=r["index"], relevance_score=r["relevance_score"])
        for r in mock_cohere_rerank_response["results"]
    ]
    client.rerank.return_value = rerank_result
    return client


@pytest.fixture
def mock_deepseek_client(mock_deepseek_response):
    """Mock DeepSeek HTTP client."""

    async def mock_post(*args, **kwargs):
        response = AsyncMock()
        response.status_code = 200
        response.json.return_value = mock_deepseek_response
        response.raise_for_status = Mock()
        return response

    client = AsyncMock()
    client.post = mock_post
    return client


@pytest.fixture
def mock_anthropic_client(mock_anthropic_response):
    """Mock Anthropic client."""

    class MockMessage:
        def __init__(self, response):
            self.id = response["id"]
            self.content = response["content"]
            self.model = response["model"]
            self.stop_reason = response["stop_reason"]
            self.usage = response["usage"]

    client = AsyncMock()
    client.messages.create.return_value = MockMessage(mock_anthropic_response)
    return client


@pytest.fixture
def mock_api_keys(monkeypatch):
    """Mock all API keys for testing."""
    monkeypatch.setenv("COHERE_API_KEY", "test_cohere_key")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test_deepseek_key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key")
    monkeypatch.setenv("GITHUB_ENTERPRISE_TOKEN", "test_github_token")


@pytest.fixture
def temp_vector_db(tmp_path):
    """Temporary vector database directory."""
    db_path = tmp_path / "vectordb"
    db_path.mkdir()
    return str(db_path)


@pytest.fixture
def temp_catalog_dir(tmp_path):
    """Temporary catalog output directory."""
    catalog_dir = tmp_path / "catalogs"
    catalog_dir.mkdir()
    return str(catalog_dir)


@pytest.fixture
def performance_timer():
    """Simple performance timer for benchmark tests."""
    import time

    class Timer:
        def __init__(self):
            self._start = None
            self._end = None

        def start(self):
            self._start = time.perf_counter()

        def stop(self):
            self._end = time.perf_counter()

        def elapsed_ms(self) -> float:
            if self._start is None or self._end is None:
                return 0.0
            return (self._end - self._start) * 1000

    return Timer()


# Markers
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may require external services)"
    )
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "performance: marks tests as performance benchmarks")
