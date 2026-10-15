"""
DevSkyy Commerce SuperAgent
===========================

Handles all e-commerce operations for SkyyRose.

Consolidates:
- Product management
- Order processing
- Inventory control
- Dynamic pricing
- Payment handling
- Shipping/fulfillment

ML Capabilities:
- Demand forecasting (Prophet)
- Dynamic pricing optimization
- Inventory prediction
"""

import logging
from datetime import UTC, datetime
from typing import Any

from adk.base import (
    ADKProvider,
    AgentCapability,
    AgentConfig,
    AgentResult,
    AgentStatus,
    ToolDefinition,
)
from core.runtime.tool_registry import (
    ParameterType,
    ToolCategory,
    ToolParameter,
    ToolRegistry,
    ToolSeverity,
    ToolSpec,
)
from llm.model_ids import OPENAI_MINI_MODEL
from orchestration.prompt_engineering import PromptTechnique

from .base_super_agent import EnhancedSuperAgent, SuperAgentType, TaskCategory

# WordPress/WooCommerce integration
try:
    from integrations.wordpress_client import WordPressWooCommerceClient

    WORDPRESS_AVAILABLE = True
except ImportError:
    WORDPRESS_AVAILABLE = False
    WordPressWooCommerceClient = None

logger = logging.getLogger(__name__)


class CommerceAgent(EnhancedSuperAgent):
    """
    Commerce Super Agent - Handles all e-commerce operations.

    Features:
    - 17 prompt engineering techniques
    - ML-based demand forecasting
    - Dynamic pricing optimization
    - Real-time inventory management
    - WooCommerce API integration

    Example:
        agent = CommerceAgent()
        await agent.initialize()
        result = await agent.process_order("Process order #12345")
    """

    agent_type = SuperAgentType.COMMERCE
    sub_capabilities = [
        "product_management",
        "order_processing",
        "inventory_control",
        "dynamic_pricing",
        "payment_handling",
        "shipping_fulfillment",
    ]

    # Commerce-specific technique preferences
    TECHNIQUE_PREFERENCES = {
        "pricing": PromptTechnique.CHAIN_OF_THOUGHT,
        "inventory": PromptTechnique.STRUCTURED_OUTPUT,
        "order": PromptTechnique.REACT,
        "product": PromptTechnique.FEW_SHOT,
        "shipping": PromptTechnique.STRUCTURED_OUTPUT,
        "forecast": PromptTechnique.CHAIN_OF_THOUGHT,
    }

    def __init__(
        self,
        config: AgentConfig | None = None,
        wordpress_client: Any = None,
        rag_service: Any | None = None,
    ):
        if config is None:
            config = AgentConfig(
                name="commerce_agent",
                provider=ADKProvider.PYDANTIC,
                model=OPENAI_MINI_MODEL,
                system_prompt=self._build_system_prompt(),
                capabilities=[
                    AgentCapability.ECOMMERCE,
                    AgentCapability.TOOL_CALLING,
                    AgentCapability.REASONING,
                ],
                tools=self._build_tools(),
                temperature=0.3,  # Lower for accuracy
            )
        super().__init__(config)

        # WordPress/WooCommerce client
        self._wordpress_client = wordpress_client
        self._wordpress_connected = False

        # RAGAnything — multimodal knowledge-base context
        self._rag_service = rag_service
        self._rag_collection = "skyyrose-catalog"

    def _build_system_prompt(self) -> str:
        """Build the commerce agent system prompt"""
        return """You are the Commerce SuperAgent for SkyyRose luxury streetwear.

## IDENTITY
You are an expert e-commerce operations manager with deep knowledge of:
- Product lifecycle management
- Order fulfillment optimization
- Dynamic pricing strategies
- Inventory forecasting
- Payment processing
- Shipping logistics

## BRAND CONTEXT
- Brand: SkyyRose
- Location: Oakland, California
- Collections: BLACK ROSE (limited edition), LOVE HURTS (emotional expression), SIGNATURE (foundation)
- Platform: WooCommerce on WordPress
- Price Range: Premium ($50-$500+)

## RESPONSIBILITIES
1. **Product Management**
   - Create, update, and manage product catalog
   - Optimize product descriptions for SEO
   - Manage variants (sizes, colors)
   - Handle product images and 3D models

2. **Order Processing**
   - Track orders from placement to delivery
   - Handle modifications and cancellations
   - Process returns and exchanges
   - Manage customer communications

3. **Inventory Control**
   - Real-time stock tracking
   - Demand forecasting
   - Reorder point optimization
   - Low stock alerts

4. **Dynamic Pricing**
   - Competitor price monitoring
   - Demand-based price adjustments
   - Promotional pricing
   - Bundle pricing strategies

5. **Payment Handling**
   - Process payments securely
   - Handle refunds and disputes
   - Manage payment methods
   - Fraud detection

6. **Shipping/Fulfillment**
   - Carrier rate comparison
   - Shipment tracking
   - Delivery optimization
   - International shipping

## GUIDELINES
- Maintain premium brand pricing integrity
- Prioritize customer satisfaction
- Optimize for profitability while staying competitive
- Flag any inventory issues immediately
- Use data-driven decision making
- Always provide structured, actionable responses

## OUTPUT FORMAT
When analyzing or recommending, use this structure:
1. Current State Assessment
2. Key Findings/Issues
3. Recommendations
4. Action Items
5. Metrics to Track"""

    def _build_tools(self) -> list[ToolDefinition]:
        """Build commerce-specific tools"""
        return [
            # Product Tools
            ToolDefinition(
                name="get_product",
                description="Get product details by SKU or ID",
                parameters={
                    "sku": {"type": "string", "description": "Product SKU"},
                    "include_stock": {"type": "boolean", "description": "Include stock info"},
                    "include_analytics": {
                        "type": "boolean",
                        "description": "Include sales analytics",
                    },
                },
            ),
            ToolDefinition(
                name="update_product",
                description="Update product information",
                parameters={
                    "sku": {"type": "string", "description": "Product SKU"},
                    "updates": {"type": "object", "description": "Fields to update"},
                },
            ),
            ToolDefinition(
                name="create_product",
                description="Create a new product",
                parameters={
                    "name": {"type": "string", "description": "Product name"},
                    "collection": {"type": "string", "description": "Collection name"},
                    "price": {"type": "number", "description": "Base price"},
                    "description": {"type": "string", "description": "Product description"},
                    "variants": {"type": "array", "description": "Size/color variants"},
                },
            ),
            # Inventory Tools
            ToolDefinition(
                name="get_inventory",
                description="Get inventory levels for product(s)",
                parameters={
                    "sku": {
                        "type": "string",
                        "description": "Product SKU (optional, all if omitted)",
                    },
                    "warehouse": {"type": "string", "description": "Warehouse location"},
                },
            ),
            ToolDefinition(
                name="update_inventory",
                description="Update product inventory levels",
                parameters={
                    "sku": {"type": "string", "description": "Product SKU"},
                    "quantity": {"type": "integer", "description": "New quantity"},
                    "action": {"type": "string", "description": "set, add, or subtract"},
                },
            ),
            ToolDefinition(
                name="forecast_demand",
                description="Forecast product demand using ML",
                parameters={
                    "sku": {"type": "string", "description": "Product SKU"},
                    "days_ahead": {"type": "integer", "description": "Forecast horizon"},
                },
            ),
            # Order Tools
            ToolDefinition(
                name="get_order",
                description="Get order details",
                parameters={
                    "order_id": {"type": "string", "description": "Order ID"},
                    "include_history": {"type": "boolean", "description": "Include order history"},
                },
            ),
            ToolDefinition(
                name="update_order_status",
                description="Update order status",
                parameters={
                    "order_id": {"type": "string", "description": "Order ID"},
                    "status": {"type": "string", "description": "New status"},
                    "notify_customer": {"type": "boolean", "description": "Send notification"},
                },
            ),
            ToolDefinition(
                name="process_return",
                description="Process a return request",
                parameters={
                    "order_id": {"type": "string", "description": "Order ID"},
                    "items": {"type": "array", "description": "Items to return"},
                    "reason": {"type": "string", "description": "Return reason"},
                },
            ),
            # Pricing Tools
            ToolDefinition(
                name="calculate_price",
                description="Calculate dynamic pricing for product",
                parameters={
                    "sku": {"type": "string", "description": "Product SKU"},
                    "factors": {
                        "type": "object",
                        "description": "Pricing factors (demand, competition, etc.)",
                    },
                },
            ),
            ToolDefinition(
                name="create_promotion",
                description="Create a promotional discount",
                parameters={
                    "name": {"type": "string", "description": "Promotion name"},
                    "discount_type": {"type": "string", "description": "percentage or fixed"},
                    "discount_value": {"type": "number", "description": "Discount amount"},
                    "products": {"type": "array", "description": "Applicable product SKUs"},
                    "start_date": {"type": "string", "description": "Start date"},
                    "end_date": {"type": "string", "description": "End date"},
                },
            ),
            # Shipping Tools
            ToolDefinition(
                name="get_shipping_rates",
                description="Get shipping options and rates",
                parameters={
                    "destination": {"type": "object", "description": "Destination address"},
                    "items": {"type": "array", "description": "Items to ship"},
                    "carriers": {"type": "array", "description": "Preferred carriers"},
                },
            ),
            ToolDefinition(
                name="create_shipment",
                description="Create a shipment for an order",
                parameters={
                    "order_id": {"type": "string", "description": "Order ID"},
                    "carrier": {"type": "string", "description": "Shipping carrier"},
                    "service": {"type": "string", "description": "Service level"},
                },
            ),
            ToolDefinition(
                name="track_shipment",
                description="Get shipment tracking info",
                parameters={
                    "tracking_number": {"type": "string", "description": "Tracking number"},
                    "carrier": {"type": "string", "description": "Carrier name"},
                },
            ),
            # RAGAnything — product knowledge search
            ToolDefinition(
                name="rag_knowledge_search",
                description=(
                    "Search the SkyyRose product knowledge graph for detailed catalog, "
                    "care instructions, sizing, fabric specs, or supplier information."
                ),
                parameters={
                    "question": {"type": "string", "description": "Search question"},
                    "mode": {
                        "type": "string",
                        "description": "Retrieval mode: local, global, hybrid, naive, mix",
                        "default": "mix",
                    },
                },
            ),
        ]

    def _register_tools(self) -> None:
        """Register commerce tools with the global ToolRegistry for MCP integration."""
        registry = ToolRegistry.get_instance()

        # Define commerce tool specifications
        commerce_tools = [
            ToolSpec(
                name="commerce_get_product",
                description="Get product details by SKU or ID",
                category=ToolCategory.COMMERCE,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="sku",
                        type=ParameterType.STRING,
                        description="Product SKU",
                        required=True,
                    ),
                    ToolParameter(
                        name="include_stock",
                        type=ParameterType.BOOLEAN,
                        description="Include stock info",
                    ),
                    ToolParameter(
                        name="include_analytics",
                        type=ParameterType.BOOLEAN,
                        description="Include sales analytics",
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"commerce", "product", "read"},
            ),
            ToolSpec(
                name="commerce_update_product",
                description="Update product information",
                category=ToolCategory.COMMERCE,
                severity=ToolSeverity.MEDIUM,
                parameters=[
                    ToolParameter(
                        name="sku",
                        type=ParameterType.STRING,
                        description="Product SKU",
                        required=True,
                    ),
                    ToolParameter(
                        name="updates",
                        type=ParameterType.OBJECT,
                        description="Fields to update",
                        required=True,
                    ),
                ],
                requires_auth=True,
                tags={"commerce", "product", "write"},
            ),
            ToolSpec(
                name="commerce_create_product",
                description="Create a new product",
                category=ToolCategory.COMMERCE,
                severity=ToolSeverity.MEDIUM,
                parameters=[
                    ToolParameter(
                        name="name",
                        type=ParameterType.STRING,
                        description="Product name",
                        required=True,
                    ),
                    ToolParameter(
                        name="collection",
                        type=ParameterType.STRING,
                        description="Collection name",
                        required=True,
                    ),
                    ToolParameter(
                        name="price",
                        type=ParameterType.NUMBER,
                        description="Base price",
                        required=True,
                    ),
                    ToolParameter(
                        name="description",
                        type=ParameterType.STRING,
                        description="Product description",
                    ),
                    ToolParameter(
                        name="variants", type=ParameterType.ARRAY, description="Size/color variants"
                    ),
                ],
                requires_auth=True,
                tags={"commerce", "product", "write"},
            ),
            ToolSpec(
                name="commerce_get_inventory",
                description="Get inventory levels for product(s)",
                category=ToolCategory.COMMERCE,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="sku",
                        type=ParameterType.STRING,
                        description="Product SKU (optional, all if omitted)",
                    ),
                    ToolParameter(
                        name="warehouse",
                        type=ParameterType.STRING,
                        description="Warehouse location",
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"commerce", "inventory", "read"},
            ),
            ToolSpec(
                name="commerce_update_inventory",
                description="Update product inventory levels",
                category=ToolCategory.COMMERCE,
                severity=ToolSeverity.MEDIUM,
                parameters=[
                    ToolParameter(
                        name="sku",
                        type=ParameterType.STRING,
                        description="Product SKU",
                        required=True,
                    ),
                    ToolParameter(
                        name="quantity",
                        type=ParameterType.INTEGER,
                        description="New quantity",
                        required=True,
                    ),
                    ToolParameter(
                        name="action",
                        type=ParameterType.STRING,
                        description="set, add, or subtract",
                        required=True,
                    ),
                ],
                requires_auth=True,
                tags={"commerce", "inventory", "write"},
            ),
            ToolSpec(
                name="commerce_forecast_demand",
                description="Forecast product demand using ML",
                category=ToolCategory.COMMERCE,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="sku",
                        type=ParameterType.STRING,
                        description="Product SKU",
                        required=True,
                    ),
                    ToolParameter(
                        name="days_ahead",
                        type=ParameterType.INTEGER,
                        description="Forecast horizon",
                        required=True,
                    ),
                ],
                idempotent=True,
                cacheable=True,
                cache_ttl_seconds=3600,
                tags={"commerce", "ml", "forecast"},
            ),
            ToolSpec(
                name="commerce_get_order",
                description="Get order details",
                category=ToolCategory.COMMERCE,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="order_id",
                        type=ParameterType.STRING,
                        description="Order ID",
                        required=True,
                    ),
                    ToolParameter(
                        name="include_history",
                        type=ParameterType.BOOLEAN,
                        description="Include order history",
                    ),
                ],
                idempotent=True,
                requires_auth=True,
                tags={"commerce", "order", "read"},
            ),
            ToolSpec(
                name="commerce_update_order_status",
                description="Update order status",
                category=ToolCategory.COMMERCE,
                severity=ToolSeverity.MEDIUM,
                parameters=[
                    ToolParameter(
                        name="order_id",
                        type=ParameterType.STRING,
                        description="Order ID",
                        required=True,
                    ),
                    ToolParameter(
                        name="status",
                        type=ParameterType.STRING,
                        description="New status",
                        required=True,
                    ),
                    ToolParameter(
                        name="notify_customer",
                        type=ParameterType.BOOLEAN,
                        description="Send notification",
                    ),
                ],
                requires_auth=True,
                tags={"commerce", "order", "write"},
            ),
            ToolSpec(
                name="commerce_calculate_price",
                description="Calculate dynamic pricing for product",
                category=ToolCategory.COMMERCE,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="sku",
                        type=ParameterType.STRING,
                        description="Product SKU",
                        required=True,
                    ),
                    ToolParameter(
                        name="factors", type=ParameterType.OBJECT, description="Pricing factors"
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"commerce", "pricing", "ml"},
            ),
        ]

        for spec in commerce_tools:
            registry.register(spec)
            logger.debug(f"Registered commerce tool: {spec.name}")

    async def execute(self, prompt: str, **kwargs) -> AgentResult:
        """Execute commerce operation"""
        start_time = datetime.now(UTC)

        try:
            # Determine task type for technique selection
            task_type = self._classify_commerce_task(prompt)

            # Select appropriate technique
            technique = self.TECHNIQUE_PREFERENCES.get(
                task_type, self.select_technique(TaskCategory.REASONING)
            )

            # RAGAnything context enrichment — pre-fetch product knowledge
            rag_context = None
            if self._rag_service is not None:
                try:
                    rag_result = await self._rag_service.query(
                        collection=self._rag_collection,
                        question=prompt,
                        mode="mix",
                        top_k=5,
                    )
                    rag_context = rag_result.get("answer", "") or None
                except Exception as rag_exc:
                    logger.warning(f"RAG context fetch failed, continuing without: {rag_exc}")

            # Apply technique to enhance prompt (inject RAG context when available)
            enhanced = self.apply_technique(
                technique,
                prompt,
                context=rag_context,
                **{k: v for k, v in kwargs.items() if k != "context"},
            )

            # Execute with backend
            if hasattr(self, "_backend_agent"):
                result = await self._backend_agent.run(enhanced.enhanced_prompt)
                content = str(result.output) if hasattr(result, "output") else str(result)
            else:
                # Fallback processing
                content = await self._fallback_process(prompt, task_type)

            return AgentResult(
                agent_name=self.name,
                agent_provider=self._active_provider,
                content=content,
                status=AgentStatus.COMPLETED,
                started_at=start_time,
                metadata={
                    "task_type": task_type,
                    "technique": technique.value,
                },
            )

        except Exception as e:
            logger.error(f"Commerce agent error: {e}")
            return AgentResult(
                agent_name=self.name,
                agent_provider=self._active_provider,
                content="",
                status=AgentStatus.FAILED,
                error=str(e),
                started_at=start_time,
            )

    def _classify_commerce_task(self, prompt: str) -> str:
        """Classify the commerce task type"""
        prompt_lower = prompt.lower()

        task_keywords = {
            "pricing": ["price", "pricing", "cost", "discount", "promotion", "markup"],
            "inventory": ["inventory", "stock", "quantity", "reorder", "warehouse"],
            "order": ["order", "purchase", "checkout", "cart", "transaction"],
            "product": ["product", "item", "sku", "catalog", "variant"],
            "shipping": ["ship", "delivery", "carrier", "tracking", "fulfillment"],
            "forecast": ["forecast", "predict", "demand", "trend", "projection"],
        }

        for task_type, keywords in task_keywords.items():
            if any(kw in prompt_lower for kw in keywords):
                return task_type

        return "general"

    async def _fallback_process(self, prompt: str, task_type: str) -> str:
        """Fallback processing when backend unavailable"""
        return f"""Commerce Agent Analysis

Task Type: {task_type}
Query: {prompt[:200]}...

Processing with commerce expertise. For full functionality, ensure backend LLM is configured.

Recommended Actions:
1. Review the specific {task_type} request
2. Check relevant data sources
3. Apply business rules
4. Generate structured response"""

    # =========================================================================
    # WordPress/WooCommerce Integration
    # =========================================================================

    async def _ensure_wordpress_client(self) -> None:
        """Ensure the WooCommerce client is initialized from environment creds.

        WordPressClient connects in __post_init__ (there is no separate
        connect()); a client injected via the constructor is honored as-is.
        Missing creds are non-fatal — the agent stays disconnected and the WC
        methods return an error dict the caller maps to a per-item failure.
        """
        if self._wordpress_connected:
            return
        if self._wordpress_client is None:
            if not WORDPRESS_AVAILABLE:
                return
            try:
                self._wordpress_client = WordPressWooCommerceClient.from_env()
            except Exception as exc:
                logger.warning("WooCommerce client not configured: %s", exc)
                return
        self._wordpress_connected = True
        logger.info("WooCommerce client ready")

    async def close_wordpress_client(self) -> None:
        """Close WordPress client connection."""
        if self._wordpress_client and self._wordpress_connected:
            await self._wordpress_client.close()
            self._wordpress_connected = False
            logger.info("WordPress/WooCommerce client closed")

    async def sync_product_to_woocommerce(
        self,
        name: str,
        price: float,
        description: str = "",
        short_description: str = "",
        sku: str | None = None,
        stock_quantity: int | None = None,
        status: str = "draft",
        categories: list[str] | None = None,
        tags: list[str] | None = None,
        images: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Sync a product to WooCommerce.

        Args:
            name: Product name
            price: Regular price
            description: Full description
            short_description: Short description
            sku: Stock keeping unit
            stock_quantity: Available stock
            status: Product status (draft, publish)
            categories: Category names
            tags: Tag names
            images: Image URLs

        Returns:
            Created product data with WooCommerce ID
        """
        await self._ensure_wordpress_client()

        if not self._wordpress_connected:
            return {"error": "WordPress client not connected"}

        try:
            from integrations.wordpress_client import ProductStatus, WooCommerceProduct

            # Prepare product data
            product = WooCommerceProduct(
                name=name,
                regular_price=str(price),
                description=description,
                short_description=short_description,
                sku=sku,
                stock_quantity=stock_quantity,
                status=ProductStatus(status) if status else ProductStatus.DRAFT,
                categories=[{"name": cat} for cat in (categories or [])],
                tags=[{"name": tag} for tag in (tags or [])],
                images=[{"src": img} for img in (images or [])],
            )

            # Create in WooCommerce
            result = await self._wordpress_client.create_product(product)

            logger.info(f"Product synced to WooCommerce: {result.id} - {result.name}")

            return {
                "success": True,
                "woocommerce_id": result.id,
                "name": result.name,
                "sku": result.sku,
                "permalink": result.permalink,
                "status": result.status,
            }

        except Exception as e:
            logger.error(f"Failed to sync product to WooCommerce: {e}")
            return {"error": str(e)}

    async def get_woocommerce_product(self, product_id: int) -> dict[str, Any]:
        """
        Get product from WooCommerce.

        Args:
            product_id: WooCommerce product ID

        Returns:
            Product data
        """
        await self._ensure_wordpress_client()

        if not self._wordpress_connected:
            return {"error": "WordPress client not connected"}

        try:
            product = await self._wordpress_client.get_product(product_id)
            return product.model_dump()
        except Exception as e:
            logger.error(f"Failed to get WooCommerce product {product_id}: {e}")
            return {"error": str(e)}

    async def update_woocommerce_product(
        self,
        product_id: int,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Update product in WooCommerce.

        Args:
            product_id: WooCommerce product ID
            updates: Fields to update

        Returns:
            Updated product data
        """
        await self._ensure_wordpress_client()

        if not self._wordpress_connected:
            return {"error": "WordPress client not connected"}

        try:
            product = await self._wordpress_client.update_product(product_id, updates)
            logger.info(f"Product updated in WooCommerce: {product_id}")
            return product.model_dump()
        except Exception as e:
            logger.error(f"Failed to update WooCommerce product {product_id}: {e}")
            return {"error": str(e)}

    async def sync_orders_from_woocommerce(
        self,
        status: str | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """
        Sync orders from WooCommerce.

        Args:
            status: Filter by order status
            limit: Maximum orders to fetch

        Returns:
            List of orders
        """
        await self._ensure_wordpress_client()

        if not self._wordpress_connected:
            return {"error": "WordPress client not connected"}

        try:
            from integrations.wordpress_client import OrderStatus

            order_status = OrderStatus(status) if status else None
            orders = await self._wordpress_client.list_orders(
                per_page=limit,
                status=order_status,
            )

            logger.info(f"Synced {len(orders)} orders from WooCommerce")

            return {
                "success": True,
                "count": len(orders),
                "orders": [order.model_dump() for order in orders],
            }

        except Exception as e:
            logger.error(f"Failed to sync orders from WooCommerce: {e}")
            return {"error": str(e)}

    async def update_order_status_in_woocommerce(
        self,
        order_id: int,
        status: str,
    ) -> dict[str, Any]:
        """
        Update order status in WooCommerce.

        Args:
            order_id: WooCommerce order ID
            status: New order status

        Returns:
            Updated order data
        """
        await self._ensure_wordpress_client()

        if not self._wordpress_connected:
            return {"error": "WordPress client not connected"}

        try:
            from integrations.wordpress_client import OrderStatus

            order = await self._wordpress_client.update_order_status(
                order_id,
                OrderStatus(status),
            )

            logger.info(f"Order {order_id} status updated to {status}")

            return {
                "success": True,
                "order_id": order.id,
                "status": order.status,
            }

        except Exception as e:
            logger.error(f"Failed to update order {order_id} status: {e}")
            return {"error": str(e)}

    # =========================================================================
    # Commerce-Specific Methods
    # =========================================================================

    async def forecast_demand(self, sku: str, days_ahead: int = 30) -> dict[str, Any]:
        """
        Forecast product demand using ML.

        Uses the ML module's demand_forecaster model.
        """
        if self.ml_module:
            prediction = await self.ml_module.predict(
                "demand_forecaster", {"sku": sku, "days": days_ahead}
            )
            return {
                "sku": sku,
                "forecast_days": days_ahead,
                "prediction": prediction.prediction,
                "confidence": prediction.confidence,
            }

        return {"sku": sku, "error": "ML module not available"}

    async def optimize_price(
        self, sku: str, factors: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Calculate optimal price using ML.

        Factors: demand, competition, inventory, seasonality
        """
        if self.ml_module:
            input_data = {"sku": sku, "factors": factors or {}}
            prediction = await self.ml_module.predict("price_optimizer", input_data)
            return {
                "sku": sku,
                "recommended_price": prediction.prediction,
                "confidence": prediction.confidence,
                "factors_considered": factors,
            }

        return {"sku": sku, "error": "ML module not available"}

    async def process_order(self, order_id: str, action: str = "status") -> AgentResult:
        """Process an order with full workflow"""
        prompt = f"""Process order {order_id}

Action requested: {action}

Please:
1. Retrieve the order details
2. Verify inventory availability
3. Process the requested action
4. Update order status
5. Notify customer if appropriate
6. Return summary of actions taken"""

        return await self.execute_with_learning(
            prompt, task_type="order", technique=PromptTechnique.REACT
        )

    async def manage_inventory(self, sku: str | None = None, action: str = "status") -> AgentResult:
        """Manage inventory with forecasting"""
        prompt = f"""Inventory management task

SKU: {sku or "All products"}
Action: {action}

Please:
1. Check current inventory levels
2. Analyze recent sales velocity
3. Forecast future demand
4. Identify reorder needs
5. Generate recommendations
6. Provide structured inventory report"""

        return await self.execute_with_learning(
            prompt,
            task_type="inventory",
            technique=PromptTechnique.STRUCTURED_OUTPUT,
            schema={
                "current_stock": "number",
                "sales_velocity": "number",
                "days_of_supply": "number",
                "reorder_recommendation": "boolean",
                "reorder_quantity": "number",
                "insights": "array",
            },
        )

    async def analyze_pricing(
        self, sku: str, competitor_prices: list[float] | None = None
    ) -> AgentResult:
        """Analyze and recommend pricing"""
        prompt = f"""Pricing analysis for SKU: {sku}

Competitor prices: {competitor_prices or "Not provided"}

Please analyze:
1. Current product pricing position
2. Competitor price comparison
3. Demand elasticity estimation
4. Margin analysis
5. Promotional opportunity assessment
6. Recommended price adjustments

Use Chain-of-Thought reasoning to explain your pricing strategy."""

        return await self.execute_with_learning(
            prompt, task_type="pricing", technique=PromptTechnique.CHAIN_OF_THOUGHT
        )


# =============================================================================
# Export
# =============================================================================

__all__ = ["CommerceAgent"]
