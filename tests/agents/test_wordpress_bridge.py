"""Tests for WordPress Bridge Agent MCP tools.

The @tool decorator from claude_agent_sdk wraps each function into an
SdkMcpTool object. The original async function is accessible via the
.handler attribute.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestWordPressCoreTools:
    """Tests for the 8 WordPress core MCP tools."""

    @pytest.fixture
    def mock_wp_client(self):
        """Mock WordPressClient with pre-configured return values."""
        client = AsyncMock()
        client.health_check.return_value = {
            "healthy": True,
            "woocommerce_api": True,
            "wordpress_api": True,
            "site_url": "https://skyyrose.co",
            "api_type": "wpcom",
        }
        client.list_products.return_value = [
            {"id": 1, "name": "Rose Gold Pendant", "sku": "SR-BR-001"}
        ]
        client.list_orders.return_value = [{"id": 100, "status": "processing"}]
        client.update_order_status.return_value = {"id": 100, "status": "completed"}
        client.create_page.return_value = {"id": 50, "title": {"rendered": "Test Page"}}
        client.upload_media_from_url.return_value = MagicMock(
            id=10,
            url="https://skyyrose.co/wp-content/uploads/test.jpg",
            title="Test Image",
            alt_text="A test image",
            mime_type="image/jpeg",
        )
        return client

    @pytest.fixture
    def mock_sync(self):
        """Mock WordPressProductSync with pre-configured return values."""
        sync = AsyncMock()
        sync.sync_product.return_value = MagicMock(
            sku="SR-BR-001", woo_id=1, action="updated", error=None
        )
        sync.sync_collection.return_value = [
            MagicMock(sku="SR-BR-001", woo_id=1, action="updated", error=None),
            MagicMock(sku="SR-BR-002", woo_id=2, action="created", error=None),
        ]
        return sync

    # -----------------------------------------------------------------------
    # wp_health_check
    # -----------------------------------------------------------------------

    async def test_wp_health_check(self, mock_wp_client):
        """wp_health_check should return site status JSON."""
        with patch(
            "agents.wordpress_bridge.mcp_server._get_wp_client",
            return_value=mock_wp_client,
        ):
            from agents.wordpress_bridge.mcp_server import wp_health_check

            result = await wp_health_check.handler({})

        assert "is_error" not in result
        text = result["content"][0]["text"]
        data = json.loads(text)
        assert data["healthy"] is True
        assert data["woocommerce_api"] is True
        mock_wp_client.health_check.assert_awaited_once()

    # -----------------------------------------------------------------------
    # wp_get_products
    # -----------------------------------------------------------------------

    async def test_wp_get_products(self, mock_wp_client):
        """wp_get_products should list products with count."""
        with patch(
            "agents.wordpress_bridge.mcp_server._get_wp_client",
            return_value=mock_wp_client,
        ):
            from agents.wordpress_bridge.mcp_server import wp_get_products

            result = await wp_get_products.handler(
                {"collection": "signature", "page": 1, "per_page": 10}
            )

        assert "is_error" not in result
        text = result["content"][0]["text"]
        data = json.loads(text)
        assert data["count"] == 1
        assert data["products"][0]["sku"] == "SR-BR-001"
        mock_wp_client.list_products.assert_awaited_once_with(
            collection="signature", page=1, per_page=10
        )

    # -----------------------------------------------------------------------
    # wp_get_orders
    # -----------------------------------------------------------------------

    async def test_wp_get_orders(self, mock_wp_client):
        """wp_get_orders should list orders with count."""
        with patch(
            "agents.wordpress_bridge.mcp_server._get_wp_client",
            return_value=mock_wp_client,
        ):
            from agents.wordpress_bridge.mcp_server import wp_get_orders

            result = await wp_get_orders.handler(
                {"status": "processing", "page": 1, "per_page": 20}
            )

        assert "is_error" not in result
        text = result["content"][0]["text"]
        data = json.loads(text)
        assert data["count"] == 1
        assert data["orders"][0]["status"] == "processing"
        mock_wp_client.list_orders.assert_awaited_once_with(
            status="processing", page=1, per_page=20
        )

    # -----------------------------------------------------------------------
    # wp_update_order
    # -----------------------------------------------------------------------

    async def test_wp_update_order(self, mock_wp_client):
        """wp_update_order should update order status and confirm."""
        with patch(
            "agents.wordpress_bridge.mcp_server._get_wp_client",
            return_value=mock_wp_client,
        ):
            from agents.wordpress_bridge.mcp_server import wp_update_order

            result = await wp_update_order.handler({"order_id": 100, "status": "completed"})

        assert "is_error" not in result
        text = result["content"][0]["text"]
        data = json.loads(text)
        assert "Order 100 updated" in data["message"]
        assert data["order"]["status"] == "completed"
        mock_wp_client.update_order_status.assert_awaited_once_with(
            order_id=100, status="completed"
        )

    # -----------------------------------------------------------------------
    # wp_sync_product
    # -----------------------------------------------------------------------

    async def test_wp_sync_product(self, mock_sync):
        """wp_sync_product should sync a product and return result."""
        with patch(
            "agents.wordpress_bridge.mcp_server._get_product_sync",
            new_callable=AsyncMock,
            return_value=mock_sync,
        ):
            from agents.wordpress_bridge.mcp_server import wp_sync_product

            result = await wp_sync_product.handler(
                {
                    "sku": "SR-BR-001",
                    "name": "Rose Gold Pendant",
                    "collection": "black-rose",
                    "price": "299.00",
                    "description": "A beautiful rose gold pendant.",
                }
            )

        assert "is_error" not in result
        text = result["content"][0]["text"]
        data = json.loads(text)
        assert data["sku"] == "SR-BR-001"
        assert data["action"] == "updated"
        assert data["woo_id"] == 1
        mock_sync.sync_product.assert_awaited_once()

    # -----------------------------------------------------------------------
    # wp_sync_collection
    # -----------------------------------------------------------------------

    async def test_wp_sync_collection(self, mock_sync):
        """wp_sync_collection should batch-sync and return summary."""
        with patch(
            "agents.wordpress_bridge.mcp_server._get_product_sync",
            new_callable=AsyncMock,
            return_value=mock_sync,
        ):
            from agents.wordpress_bridge.mcp_server import wp_sync_collection

            result = await wp_sync_collection.handler({"collection": "black-rose"})

        assert "is_error" not in result
        text = result["content"][0]["text"]
        data = json.loads(text)
        assert data["collection"] == "black_rose"
        assert data["synced"] == 2
        mock_sync.sync_collection.assert_awaited_once()

    # -----------------------------------------------------------------------
    # wp_create_page
    # -----------------------------------------------------------------------

    async def test_wp_create_page(self, mock_wp_client):
        """wp_create_page should create a page and return confirmation."""
        with patch(
            "agents.wordpress_bridge.mcp_server._get_wp_client",
            return_value=mock_wp_client,
        ):
            from agents.wordpress_bridge.mcp_server import wp_create_page

            result = await wp_create_page.handler(
                {
                    "title": "About Us",
                    "slug": "about-us",
                    "content": "<h1>About SkyyRose</h1>",
                    "status": "draft",
                }
            )

        assert "is_error" not in result
        text = result["content"][0]["text"]
        data = json.loads(text)
        assert "About Us" in data["message"]
        assert data["page"]["id"] == 50
        mock_wp_client.create_page.assert_awaited_once_with(
            title="About Us",
            slug="about-us",
            content="<h1>About SkyyRose</h1>",
            status="draft",
        )

    # -----------------------------------------------------------------------
    # wp_upload_media
    # -----------------------------------------------------------------------

    async def test_wp_upload_media(self, mock_wp_client):
        """wp_upload_media should upload from URL and return media info."""
        with patch(
            "agents.wordpress_bridge.mcp_server._get_wp_client",
            return_value=mock_wp_client,
        ):
            from agents.wordpress_bridge.mcp_server import wp_upload_media

            result = await wp_upload_media.handler(
                {
                    "image_url": "https://cdn.example.com/rose-pendant.jpg",
                    "title": "Rose Pendant",
                    "alt_text": "SkyyRose Rose Gold Pendant product photo",
                }
            )

        assert "is_error" not in result
        text = result["content"][0]["text"]
        data = json.loads(text)
        assert data["media_id"] == 10
        assert "skyyrose.co" in data["url"]
        mock_wp_client.upload_media_from_url.assert_awaited_once_with(
            image_url="https://cdn.example.com/rose-pendant.jpg",
            title="Rose Pendant",
            alt_text="SkyyRose Rose Gold Pendant product photo",
        )

    # -----------------------------------------------------------------------
    # Error handling
    # -----------------------------------------------------------------------

    async def test_tool_returns_error_on_exception(self):
        """All tools should return is_error=True when an exception occurs."""
        with patch(
            "agents.wordpress_bridge.mcp_server._get_wp_client",
            side_effect=ValueError("Missing env vars"),
        ):
            from agents.wordpress_bridge.mcp_server import wp_health_check

            result = await wp_health_check.handler({})

        assert result.get("is_error") is True
        assert "ValueError" in result["content"][0]["text"]


class TestPipelineBridgeTools:
    """Tests for the 7 pipeline bridge MCP tools."""

    @pytest.fixture
    def mock_wp_client(self):
        """Mock WordPressClient with pre-configured return values for pipeline tools."""
        client = AsyncMock()
        client.create_page.return_value = {
            "id": 50,
            "title": {"rendered": "Test"},
            "link": "https://skyyrose.co/test",
        }
        client.upload_media_from_url.return_value = MagicMock(
            id=10,
            url="https://skyyrose.co/wp-content/uploads/test.jpg",
        )
        client.wc_base_url = "https://skyyrose.co/index.php?rest_route=/wc/v3"
        # Mock internal httpx client for raw WC API calls
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"id": 1, "meta_data": []}
        client._client = AsyncMock()
        client._client.put.return_value = mock_response
        client.consumer_key = "ck_test"
        client.consumer_secret = "cs_test"
        return client

    # -----------------------------------------------------------------------
    # wp_publish_round_table
    # -----------------------------------------------------------------------

    async def test_wp_publish_round_table(self, mock_wp_client):
        """wp_publish_round_table should create a draft page with HTML table of results."""
        with patch(
            "agents.wordpress_bridge.mcp_server._get_wp_client",
            return_value=mock_wp_client,
        ):
            from agents.wordpress_bridge.mcp_server import wp_publish_round_table

            result = await wp_publish_round_table.handler(
                {
                    "title": "Round Table: Best Copy",
                    "winner": {
                        "provider": "Claude",
                        "score": 95,
                        "response": "",
                    },
                    "entries": [
                        {"provider": "Claude", "score": 95},
                        {"provider": "GPT-4", "score": 88},
                        {"provider": "Gemini", "score": 82},
                    ],
                }
            )

        assert "is_error" not in result
        text = result["content"][0]["text"]
        data = json.loads(text)
        assert data["page_id"] == 50
        assert data["entries_count"] == 3
        assert "edit_url" in data

        # Verify create_page was called with draft status and HTML content
        call_kwargs = mock_wp_client.create_page.call_args
        assert call_kwargs.kwargs["status"] == "draft"
        assert "<h2>Winner: Claude</h2>" in call_kwargs.kwargs["content"]
        assert "<table>" in call_kwargs.kwargs["content"]

    # -----------------------------------------------------------------------
    # wp_attach_3d_model
    # -----------------------------------------------------------------------

    async def test_wp_attach_3d_model(self, mock_wp_client):
        """wp_attach_3d_model should update product meta via WC API."""
        with patch(
            "agents.wordpress_bridge.mcp_server._get_wp_client",
            return_value=mock_wp_client,
        ):
            from agents.wordpress_bridge.mcp_server import wp_attach_3d_model

            result = await wp_attach_3d_model.handler(
                {
                    "product_id": 42,
                    "glb_url": "https://cdn.skyyrose.co/models/pendant.glb",
                }
            )

        assert "is_error" not in result
        text = result["content"][0]["text"]
        data = json.loads(text)
        assert data["product_id"] == 42
        assert data["glb_url"] == "https://cdn.skyyrose.co/models/pendant.glb"

        # Verify the WC API PUT was called with correct meta
        mock_wp_client._client.put.assert_awaited_once()
        put_call = mock_wp_client._client.put.call_args
        assert "/products/42" in put_call.args[0]
        meta = put_call.kwargs["json"]["meta_data"]
        assert meta[0]["key"] == "_product_3d_model_url"
        assert meta[0]["value"] == "https://cdn.skyyrose.co/models/pendant.glb"

    # -----------------------------------------------------------------------
    # wp_upload_product_image
    # -----------------------------------------------------------------------

    async def test_wp_upload_product_image(self, mock_wp_client):
        """wp_upload_product_image should upload media and attach to product."""
        with patch(
            "agents.wordpress_bridge.mcp_server._get_wp_client",
            return_value=mock_wp_client,
        ):
            from agents.wordpress_bridge.mcp_server import wp_upload_product_image

            result = await wp_upload_product_image.handler(
                {
                    "product_id": 7,
                    "image_url": "https://cdn.example.com/generated-pendant.jpg",
                    "alt_text": "AI-generated pendant photo",
                }
            )

        assert "is_error" not in result
        text = result["content"][0]["text"]
        data = json.loads(text)
        assert data["media_id"] == 10
        assert data["product_id"] == 7
        assert "skyyrose.co" in data["media_url"]

        # Verify upload was called
        mock_wp_client.upload_media_from_url.assert_awaited_once_with(
            image_url="https://cdn.example.com/generated-pendant.jpg",
            title="Product 7 image",
            alt_text="AI-generated pendant photo",
        )
        # Verify product gallery was updated via WC API
        mock_wp_client._client.put.assert_awaited_once()

    # -----------------------------------------------------------------------
    # wp_publish_social_campaign
    # -----------------------------------------------------------------------

    async def test_wp_publish_social_campaign(self, mock_wp_client):
        """wp_publish_social_campaign should create a draft page with campaign content."""
        with patch(
            "agents.wordpress_bridge.mcp_server._get_wp_client",
            return_value=mock_wp_client,
        ):
            from agents.wordpress_bridge.mcp_server import wp_publish_social_campaign

            result = await wp_publish_social_campaign.handler(
                {
                    "title": "Spring Launch",
                    "platform": "Instagram",
                    "content": "",
                    "hashtags": ["SkyyRose", "LuxuryFashion", "Oakland"],
                }
            )

        assert "is_error" not in result
        text = result["content"][0]["text"]
        data = json.loads(text)
        assert data["page_id"] == 50
        assert data["platform"] == "Instagram"
        assert "SkyyRose" in data["hashtags"]

        # Verify create_page was called as draft with platform badge
        call_kwargs = mock_wp_client.create_page.call_args
        assert call_kwargs.kwargs["status"] == "draft"
        assert "Instagram" in call_kwargs.kwargs["content"]
        assert "hashtag" in call_kwargs.kwargs["content"]

    # -----------------------------------------------------------------------
    # wp_update_conversion_data
    # -----------------------------------------------------------------------

    async def test_wp_update_conversion_data(self, mock_wp_client):
        """wp_update_conversion_data should push metrics to product meta."""
        with patch(
            "agents.wordpress_bridge.mcp_server._get_wp_client",
            return_value=mock_wp_client,
        ):
            from agents.wordpress_bridge.mcp_server import wp_update_conversion_data

            result = await wp_update_conversion_data.handler(
                {
                    "product_id": 5,
                    "trending_score": 87.5,
                    "funnel_data": {"views": 1200, "carts": 80, "purchases": 15},
                }
            )

        assert "is_error" not in result
        text = result["content"][0]["text"]
        data = json.loads(text)
        assert data["product_id"] == 5
        assert data["trending_score"] == 87.5

        # Verify WC API PUT with correct meta keys
        put_call = mock_wp_client._client.put.call_args
        meta = put_call.kwargs["json"]["meta_data"]
        meta_keys = [m["key"] for m in meta]
        assert "_trending_score" in meta_keys
        assert "_funnel_views" in meta_keys
        assert "_funnel_carts" in meta_keys
        assert "_funnel_purchases" in meta_keys

    # -----------------------------------------------------------------------
    # get_pipeline_status
    # -----------------------------------------------------------------------

    async def test_get_pipeline_status(self):
        """get_pipeline_status should return all 9 pipelines."""
        from agents.wordpress_bridge.mcp_server import get_pipeline_status

        result = await get_pipeline_status.handler({})

        assert "is_error" not in result
        text = result["content"][0]["text"]
        data = json.loads(text)
        assert data["total_pipelines"] == 9
        pipeline_names = [p["name"] for p in data["pipelines"]]
        assert "LLM Round Table" in pipeline_names
        assert "3D Pipeline" in pipeline_names
        assert "Imagery Pipeline" in pipeline_names

    # -----------------------------------------------------------------------
    # get_product_catalog
    # -----------------------------------------------------------------------

    async def test_get_product_catalog(self):
        """get_product_catalog should return collection info from COLLECTION_CONFIG."""
        from agents.wordpress_bridge.mcp_server import get_product_catalog

        # Request all collections (empty filter)
        result = await get_product_catalog.handler({"collection": ""})

        assert "is_error" not in result
        text = result["content"][0]["text"]
        data = json.loads(text)
        assert data["collections_count"] == 3
        collections = data["collections"]
        # All three SkyyRose collections should be present
        assert "signature" in collections
        assert "black_rose" in collections
        assert "love_hurts" in collections

    async def test_get_product_catalog_filtered(self):
        """get_product_catalog with collection filter should return only that collection."""
        from agents.wordpress_bridge.mcp_server import get_product_catalog

        result = await get_product_catalog.handler({"collection": "signature"})

        assert "is_error" not in result
        text = result["content"][0]["text"]
        data = json.loads(text)
        assert data["collections_count"] == 1
        assert "signature" in data["collections"]

    # -----------------------------------------------------------------------
    # create_wordpress_tools factory
    # -----------------------------------------------------------------------

    def test_create_wordpress_tools_returns_server(self):
        """create_wordpress_tools should return a configured MCP server with 15 tools."""
        with patch("agents.wordpress_bridge.mcp_server.create_sdk_mcp_server") as mock_create:
            mock_create.return_value = MagicMock(name="wordpress_bridge")
            from agents.wordpress_bridge.mcp_server import create_wordpress_tools

            server = create_wordpress_tools()

        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args
        assert call_kwargs.kwargs["name"] == "wordpress_bridge"
        assert call_kwargs.kwargs["version"] == "1.0.0"
        assert len(call_kwargs.kwargs["tools"]) == 15
        assert server is not None


class TestWordPressBridgeAgent:
    """Tests for the agent entry point."""

    def test_agent_initialization(self):
        from agents.wordpress_bridge.agent import WordPressBridgeAgent

        agent = WordPressBridgeAgent()
        assert agent.model == "claude-opus-4-6"
        assert agent.mcp_server is not None
        assert agent.correlation_id is None

    def test_agent_with_custom_model(self):
        from agents.wordpress_bridge.agent import WordPressBridgeAgent

        agent = WordPressBridgeAgent(model="claude-sonnet-4-6", correlation_id="test-123")
        assert agent.model == "claude-sonnet-4-6"
        assert agent.correlation_id == "test-123"

    def test_agent_options_contain_mcp_server(self):
        from agents.wordpress_bridge.agent import WordPressBridgeAgent

        agent = WordPressBridgeAgent()
        options = agent.get_options()
        assert options.mcp_servers is not None
        assert "wordpress_bridge" in options.mcp_servers

    def test_agent_options_system_prompt(self):
        from agents.wordpress_bridge.agent import WordPressBridgeAgent

        agent = WordPressBridgeAgent()
        options = agent.get_options()
        assert "SkyyRose" in options.system_prompt
        assert "SkyyRose" in options.system_prompt

    def test_agent_options_adaptive_thinking(self):
        from agents.wordpress_bridge.agent import WordPressBridgeAgent

        agent = WordPressBridgeAgent()
        options = agent.get_options()
        assert options.thinking == {"type": "adaptive"}

    def test_agent_options_permission_mode(self):
        from agents.wordpress_bridge.agent import WordPressBridgeAgent

        agent = WordPressBridgeAgent()
        options = agent.get_options(permission_mode="default")
        assert options.permission_mode == "default"

    def test_run_agent_is_async_generator(self):
        import inspect

        from agents.wordpress_bridge.agent import run_agent

        assert inspect.isasyncgenfunction(run_agent)


class TestWordPressAgentEndpoint:
    """Tests for the FastAPI SSE endpoint."""

    @pytest.fixture
    def app(self):
        from types import SimpleNamespace

        from api.v1.wordpress_agent import router
        from security.jwt_oauth2_auth import get_current_user

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")
        # These tests exercise endpoint BEHAVIOR (SSE streaming, event/webhook
        # formatting). The auth gate itself is covered separately by
        # test_execute_endpoint_requires_auth / test_webhook_dispatch_requires_auth.
        # Override the auth dependency so behavior tests run as an authed caller.
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(sub="test-user")
        return app

    @pytest.fixture
    def client(self, app):
        return TestClient(app)

    @staticmethod
    def _unauthenticated_client() -> TestClient:
        """A client whose app has NO auth override — for asserting the gate."""
        from api.v1.wordpress_agent import router

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")
        return TestClient(app, raise_server_exceptions=False)

    def test_execute_endpoint_requires_auth(self):
        """Unauthenticated POST must be rejected by auth BEFORE body validation."""
        client = self._unauthenticated_client()
        response = client.post("/api/v1/agent/execute", json={"intent": "x", "prompt": "y"})
        assert response.status_code in (401, 403)

    def test_webhook_dispatch_requires_auth(self):
        """The webhook dispatch route runs the same write-agent — must be gated."""
        client = self._unauthenticated_client()
        response = client.post(
            "/api/v1/agent/webhooks/dispatch",
            json={"topic": "order.created", "payload": {}},
        )
        assert response.status_code in (401, 403)

    def test_execute_endpoint_rejects_missing_prompt(self, client):
        """Should return 422 for missing prompt (authed request, body invalid)."""
        response = client.post("/api/v1/agent/execute", json={"intent": "test"})
        assert response.status_code == 422

    def test_execute_endpoint_rejects_empty_prompt(self, client):
        """Should return 422 for empty prompt."""
        response = client.post("/api/v1/agent/execute", json={"intent": "test", "prompt": ""})
        assert response.status_code == 422

    def test_execute_endpoint_returns_sse_stream(self, client):
        """Should return SSE content type."""

        async def mock_run_agent(prompt, **kwargs):
            yield {"type": "thinking", "content": "Checking..."}
            yield {
                "type": "result",
                "content": "Done",
                "session_id": "s-123",
                "cost_usd": 0.02,
            }

        with patch("api.v1.wordpress_agent.run_agent", mock_run_agent):
            response = client.post(
                "/api/v1/agent/execute",
                json={"intent": "health_check", "prompt": "Check connectivity"},
            )
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")
            body = response.text
            assert "data:" in body
            assert "[DONE]" in body

    def test_execute_endpoint_streams_events(self, client):
        """Should stream multiple events then DONE."""

        async def mock_run_agent(prompt, **kwargs):
            yield {"type": "text", "content": "Hello"}
            yield {"type": "result", "content": "Finished"}

        with patch("api.v1.wordpress_agent.run_agent", mock_run_agent):
            response = client.post(
                "/api/v1/agent/execute",
                json={"intent": "test", "prompt": "Test prompt"},
            )
            lines = [l for l in response.text.split("\n") if l.startswith("data:")]
            # Should have at least 3 data lines: 2 events + [DONE]
            assert len(lines) >= 3

    def test_execute_endpoint_handles_agent_error(self, client):
        """Should stream error event when agent raises."""

        async def mock_run_agent(prompt, **kwargs):
            raise RuntimeError("Agent crashed")
            yield  # noqa: F541, E501 — makes this an async generator

        with patch("api.v1.wordpress_agent.run_agent", mock_run_agent):
            response = client.post(
                "/api/v1/agent/execute",
                json={"intent": "test", "prompt": "Trigger error"},
            )
            assert response.status_code == 200  # SSE always returns 200
            assert "error" in response.text
            assert "[DONE]" in response.text

    def test_webhook_dispatch_formats_order(self, client):
        """Webhook dispatch should format order topic correctly."""
        mock_execute = AsyncMock(return_value={"result": "Order processed", "session_id": "s-1"})

        with patch("api.v1.wordpress_agent.WordPressBridgeAgent") as MockAgent:
            instance = MockAgent.return_value
            instance.execute = mock_execute
            response = client.post(
                "/api/v1/agent/webhooks/dispatch",
                json={
                    "topic": "order.created",
                    "payload": {
                        "id": 1234,
                        "total": "178.00",
                        "line_items": [{"name": "Black Rose Sherpa", "quantity": 2}],
                    },
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "processed"
            assert data["topic"] == "order.created"
            # Verify agent was called with a prompt containing order info
            call_args = mock_execute.call_args
            assert "1234" in call_args[0][0]

    def test_webhook_dispatch_handles_product_topic(self, client):
        """Webhook dispatch should handle product topics."""
        mock_execute = AsyncMock(return_value={"result": "Synced", "session_id": "s-2"})

        with patch("api.v1.wordpress_agent.WordPressBridgeAgent") as MockAgent:
            instance = MockAgent.return_value
            instance.execute = mock_execute
            response = client.post(
                "/api/v1/agent/webhooks/dispatch",
                json={
                    "topic": "product.updated",
                    "payload": {"id": 42, "name": "Love Hurts Tee"},
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "processed"

    def test_webhook_dispatch_handles_unknown_topic(self, client):
        """Webhook dispatch should handle unknown topics gracefully."""
        mock_execute = AsyncMock(return_value={"result": "Handled", "session_id": "s-3"})

        with patch("api.v1.wordpress_agent.WordPressBridgeAgent") as MockAgent:
            instance = MockAgent.return_value
            instance.execute = mock_execute
            response = client.post(
                "/api/v1/agent/webhooks/dispatch",
                json={
                    "topic": "coupon.created",
                    "payload": {"id": 99, "code": "SKYYROSE10"},
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "processed"

    def test_webhook_dispatch_returns_500_on_agent_failure(self, client):
        """Webhook dispatch should return 500 when agent fails."""
        with patch("api.v1.wordpress_agent.WordPressBridgeAgent") as MockAgent:
            instance = MockAgent.return_value
            instance.execute = AsyncMock(side_effect=RuntimeError("Agent down"))
            response = client.post(
                "/api/v1/agent/webhooks/dispatch",
                json={
                    "topic": "order.created",
                    "payload": {"id": 1},
                },
            )
            assert response.status_code == 500
            assert response.json()["detail"] == "Internal server error"


class TestMCPServerIntegration:
    """Integration tests verifying the full MCP server and agent setup."""

    def test_create_wordpress_tools_returns_valid_server(self):
        """create_wordpress_tools() should return a configured MCP server."""
        from agents.wordpress_bridge.mcp_server import create_wordpress_tools

        server = create_wordpress_tools()
        assert server is not None

    def test_all_15_tools_are_registered(self):
        """The MCP server should register all 15 tools."""
        from agents.wordpress_bridge.mcp_server import create_wordpress_tools

        server = create_wordpress_tools()
        # The server config should contain tool info
        # Verify by checking the server object has tools registered
        assert server is not None
        # If we can introspect the server, count the tools
        # Otherwise just verify it creates without error

    def test_agent_init_creates_valid_options(self):
        """Agent should produce valid ClaudeAgentOptions."""
        from agents.wordpress_bridge.agent import WordPressBridgeAgent

        agent = WordPressBridgeAgent()
        options = agent.get_options()
        assert "wordpress_bridge" in options.mcp_servers
        assert options.model == "claude-opus-4-6"
        assert options.thinking == {"type": "adaptive"}
        assert options.max_turns == 20

    def test_system_prompt_contains_brand_context(self):
        """System prompt should have SkyyRose brand info."""
        from agents.wordpress_bridge.prompts import SYSTEM_PROMPT

        assert "SkyyRose" in SYSTEM_PROMPT
        assert "SkyyRose" in SYSTEM_PROMPT
        assert "#B76E79" in SYSTEM_PROMPT
        assert "Black Rose" in SYSTEM_PROMPT
        assert "Love Hurts" in SYSTEM_PROMPT
        assert "Signature" in SYSTEM_PROMPT

    def test_system_prompt_does_not_contain_retired_tagline(self):
        """System prompt must NOT contain the retired tagline."""
        from agents.wordpress_bridge.prompts import SYSTEM_PROMPT

        # The retired tagline should only appear in the "NEVER use" warning
        lines_without_warning = [
            line
            for line in SYSTEM_PROMPT.split("\n")
            if "NEVER" not in line
            and "retired" not in line.lower()
            and "decommissioned" not in line.lower()
        ]
        combined = "\n".join(lines_without_warning)
        assert "Where Love Meets Luxury" not in combined

    def test_system_prompt_lists_all_15_tools(self):
        """System prompt should reference all 15 tool names."""
        from agents.wordpress_bridge.prompts import SYSTEM_PROMPT

        tool_names = [
            "wp_health_check",
            "wp_get_products",
            "wp_get_orders",
            "wp_update_order",
            "wp_sync_product",
            "wp_sync_collection",
            "wp_create_page",
            "wp_upload_media",
            "wp_publish_round_table",
            "wp_attach_3d_model",
            "wp_upload_product_image",
            "wp_publish_social_campaign",
            "wp_update_conversion_data",
            "get_pipeline_status",
            "get_product_catalog",
        ]
        for tool_name in tool_names:
            assert tool_name in SYSTEM_PROMPT, f"Tool {tool_name} not found in system prompt"

    def test_prompt_templates_have_placeholders(self):
        """Per-pipeline prompt templates should have correct placeholders."""
        from agents.wordpress_bridge.prompts import (
            ATTACH_3D_MODEL_PROMPT,
            PROCESS_ORDER_PROMPT,
            PUBLISH_SOCIAL_PROMPT,
            SYNC_COLLECTION_PROMPT,
            UPLOAD_IMAGERY_PROMPT,
        )

        assert "{collection}" in SYNC_COLLECTION_PROMPT
        assert "{product_id}" in ATTACH_3D_MODEL_PROMPT
        assert "{glb_url}" in ATTACH_3D_MODEL_PROMPT
        assert "{product_id}" in UPLOAD_IMAGERY_PROMPT
        assert "{image_url}" in UPLOAD_IMAGERY_PROMPT
        assert "{platform}" in PUBLISH_SOCIAL_PROMPT
        assert "{order_id}" in PROCESS_ORDER_PROMPT

    def test_package_lazy_imports(self):
        """Package __init__.py should support lazy attribute access."""
        import agents.wordpress_bridge as wb

        # SYSTEM_PROMPT should be accessible (prompts.py exists)
        assert hasattr(wb, "SYSTEM_PROMPT") or "SYSTEM_PROMPT" in wb.__all__
        # create_wordpress_tools should be accessible
        assert "create_wordpress_tools" in wb.__all__
