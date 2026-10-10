"""
DevSkyy Support SuperAgent
==========================

Handles all customer support operations for SkyyRose.

Consolidates:
- Customer inquiries
- Ticket management
- FAQ responses
- Returns/refunds
- Live chat
- Escalation handling

ML Capabilities:
- Intent classification
- FAQ matching
- Escalation prediction
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

logger = logging.getLogger(__name__)


class SupportAgent(EnhancedSuperAgent):
    """
    Support Super Agent - Handles all customer support operations.

    Features:
    - 17 prompt engineering techniques
    - ML-based intent classification
    - FAQ matching with confidence scores
    - Escalation prediction
    - Multi-channel support

    Example:
        agent = SupportAgent()
        await agent.initialize()
        result = await agent.handle_inquiry("Where is my order #12345?")
    """

    agent_type = SuperAgentType.SUPPORT
    sub_capabilities = [
        "customer_inquiries",
        "ticket_management",
        "faq_responses",
        "returns_refunds",
        "live_chat",
        "escalation_handling",
    ]

    # Support-specific technique preferences
    TECHNIQUE_PREFERENCES = {
        "inquiry": PromptTechnique.RAG,
        "ticket": PromptTechnique.STRUCTURED_OUTPUT,
        "faq": PromptTechnique.FEW_SHOT,
        "return": PromptTechnique.CHAIN_OF_THOUGHT,
        "chat": PromptTechnique.ROLE_BASED,
        "escalation": PromptTechnique.CONSTITUTIONAL,
    }

    # FAQ Knowledge Base
    FAQ_KNOWLEDGE = {
        "shipping": {
            "question": "How long does shipping take?",
            "answer": "Standard shipping takes 5-7 business days within the US. Express shipping (2-3 days) is available at checkout. International shipping typically takes 7-14 business days.",
        },
        "returns": {
            "question": "What is your return policy?",
            "answer": "We accept returns within 30 days of purchase. Items must be unworn with original tags attached. Returns are free for exchanges; refunds are processed minus a $9.95 shipping fee.",
        },
        "sizing": {
            "question": "How do I find my size?",
            "answer": "Check our size guide on each product page. We offer XS-3XL in most styles. Our pieces have a relaxed, streetwear fit - if between sizes, we recommend sizing down for a more fitted look.",
        },
        "payment": {
            "question": "What payment methods do you accept?",
            "answer": "We accept all major credit cards, PayPal, Apple Pay, Google Pay, and Shop Pay. Installment payments available through Klarna and Afterpay.",
        },
        "tracking": {
            "question": "How do I track my order?",
            "answer": "Once shipped, you'll receive an email with tracking information. You can also track your order in your account dashboard or by entering your order number on our tracking page.",
        },
    }

    def __init__(self, config: AgentConfig | None = None, rag_service: Any | None = None):
        if config is None:
            config = AgentConfig(
                name="support_agent",
                provider=ADKProvider.PYDANTIC,
                model=OPENAI_MINI_MODEL,
                system_prompt=self._build_system_prompt(),
                capabilities=[
                    AgentCapability.CUSTOMER_SUPPORT,
                    AgentCapability.TEXT_GENERATION,
                    AgentCapability.REASONING,
                ],
                tools=self._build_tools(),
                temperature=0.3,  # Lower for consistency
            )
        super().__init__(config)

        # RAGAnything — live policy/FAQ knowledge base
        self._rag_service = rag_service
        self._rag_collection = "skyyrose-support"

    def _build_system_prompt(self) -> str:
        """Build the support agent system prompt"""
        return """You are the Support SuperAgent for SkyyRose luxury streetwear.

## IDENTITY
You are a warm, professional customer support specialist with expertise in:
- E-commerce customer service
- Order management
- Problem resolution
- Brand representation
- Conflict de-escalation

## BRAND CONTEXT
- Brand: SkyyRose
- Positioning: Premium luxury streetwear
- Values: Quality, authenticity, customer care
- Location: Oakland, California

## SUPPORT PHILOSOPHY
- First-contact resolution whenever possible
- Empathy before solutions
- Proactive communication
- Exceed expectations

## POLICIES
**Returns:**
- 30-day return window
- Items must be unworn with tags
- Free returns for exchanges
- Refunds minus $9.95 shipping fee

**Exchanges:**
- Free for same-value items
- Size exchanges prioritized
- 48-hour processing

**Shipping:**
- Free shipping over $150
- Standard: $9.95 (5-7 business days)
- Express: $19.95 (2-3 business days)
- International: Varies by location

**Refunds:**
- 5-7 business days after item received
- Original payment method

## ESCALATION CRITERIA
Escalate to human support when:
- Order value exceeds $500
- Legal or safety issues mentioned
- VIP/influencer customers
- Repeated failed resolution attempts
- Customer requests human agent
- Fraud suspected
- Shipping lost > 14 days

## COMMUNICATION GUIDELINES
- Greet warmly, use customer's name
- Acknowledge the issue first
- Provide clear, actionable solutions
- Confirm understanding
- End with gratitude and invitation to return
- Keep responses concise but complete
- Never argue or become defensive"""

    def _build_tools(self) -> list[ToolDefinition]:
        """Build support-specific tools"""
        return [
            # Inquiry Tools
            ToolDefinition(
                name="search_faq",
                description="Search FAQ knowledge base",
                parameters={
                    "query": {"type": "string", "description": "Customer question"},
                    "category": {"type": "string", "description": "FAQ category"},
                    "threshold": {"type": "number", "description": "Confidence threshold"},
                },
            ),
            ToolDefinition(
                name="classify_intent",
                description="Classify customer intent using ML",
                parameters={
                    "message": {"type": "string", "description": "Customer message"},
                    "context": {"type": "object", "description": "Conversation context"},
                },
            ),
            # Order Tools
            ToolDefinition(
                name="lookup_order",
                description="Look up order details",
                parameters={
                    "order_id": {"type": "string", "description": "Order ID"},
                    "email": {"type": "string", "description": "Customer email"},
                },
            ),
            ToolDefinition(
                name="track_shipment",
                description="Get shipment tracking status",
                parameters={
                    "order_id": {"type": "string", "description": "Order ID"},
                    "tracking_number": {"type": "string", "description": "Tracking number"},
                },
            ),
            ToolDefinition(
                name="update_order",
                description="Update order (cancel, modify address)",
                parameters={
                    "order_id": {"type": "string", "description": "Order ID"},
                    "action": {"type": "string", "description": "Update action"},
                    "details": {"type": "object", "description": "Update details"},
                },
            ),
            # Return/Refund Tools
            ToolDefinition(
                name="initiate_return",
                description="Start return process",
                parameters={
                    "order_id": {"type": "string", "description": "Order ID"},
                    "items": {"type": "array", "description": "Items to return"},
                    "reason": {"type": "string", "description": "Return reason"},
                    "preference": {"type": "string", "description": "Refund or exchange"},
                },
            ),
            ToolDefinition(
                name="process_refund",
                description="Process refund for order",
                parameters={
                    "order_id": {"type": "string", "description": "Order ID"},
                    "amount": {"type": "number", "description": "Refund amount"},
                    "reason": {"type": "string", "description": "Refund reason"},
                },
            ),
            ToolDefinition(
                name="check_return_status",
                description="Check status of return",
                parameters={
                    "return_id": {"type": "string", "description": "Return ID"},
                    "order_id": {"type": "string", "description": "Original order ID"},
                },
            ),
            # Ticket Tools
            ToolDefinition(
                name="create_ticket",
                description="Create support ticket",
                parameters={
                    "customer_email": {"type": "string", "description": "Customer email"},
                    "subject": {"type": "string", "description": "Ticket subject"},
                    "description": {"type": "string", "description": "Issue description"},
                    "priority": {"type": "string", "description": "Priority level"},
                    "category": {"type": "string", "description": "Issue category"},
                },
            ),
            ToolDefinition(
                name="update_ticket",
                description="Update ticket status or notes",
                parameters={
                    "ticket_id": {"type": "string", "description": "Ticket ID"},
                    "status": {"type": "string", "description": "New status"},
                    "notes": {"type": "string", "description": "Internal notes"},
                    "response": {"type": "string", "description": "Customer response"},
                },
            ),
            ToolDefinition(
                name="escalate_ticket",
                description="Escalate ticket to human agent",
                parameters={
                    "ticket_id": {"type": "string", "description": "Ticket ID"},
                    "reason": {"type": "string", "description": "Escalation reason"},
                    "priority": {"type": "string", "description": "Escalation priority"},
                    "summary": {"type": "string", "description": "Issue summary"},
                },
            ),
            # Customer Tools
            ToolDefinition(
                name="get_customer_history",
                description="Get customer order and support history",
                parameters={
                    "customer_id": {"type": "string", "description": "Customer ID"},
                    "email": {"type": "string", "description": "Customer email"},
                },
            ),
            ToolDefinition(
                name="add_customer_note",
                description="Add note to customer profile",
                parameters={
                    "customer_id": {"type": "string", "description": "Customer ID"},
                    "note": {"type": "string", "description": "Note content"},
                    "category": {"type": "string", "description": "Note category"},
                },
            ),
        ]

    def _register_tools(self) -> None:
        """Register support tools with the global ToolRegistry for MCP integration."""
        registry = ToolRegistry.get_instance()

        support_tools = [
            ToolSpec(
                name="support_search_faq",
                description="Search FAQ knowledge base for answers",
                category=ToolCategory.AI,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="query",
                        type=ParameterType.STRING,
                        description="Customer question to search",
                        required=True,
                    ),
                    ToolParameter(
                        name="category",
                        type=ParameterType.STRING,
                        description="FAQ category filter",
                        required=False,
                    ),
                    ToolParameter(
                        name="threshold",
                        type=ParameterType.NUMBER,
                        description="Confidence threshold (0-1)",
                        required=False,
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"support", "faq", "search"},
            ),
            ToolSpec(
                name="support_classify_intent",
                description="Classify customer intent using ML",
                category=ToolCategory.AI,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="message",
                        type=ParameterType.STRING,
                        description="Customer message to classify",
                        required=True,
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"support", "intent", "ml"},
            ),
            ToolSpec(
                name="support_lookup_order",
                description="Look up order details by ID or email",
                category=ToolCategory.COMMERCE,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="order_id",
                        type=ParameterType.STRING,
                        description="Order ID",
                        required=False,
                    ),
                    ToolParameter(
                        name="email",
                        type=ParameterType.STRING,
                        description="Customer email",
                        required=False,
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"support", "order", "lookup"},
            ),
            ToolSpec(
                name="support_track_shipment",
                description="Get shipment tracking status",
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
                        name="tracking_number",
                        type=ParameterType.STRING,
                        description="Tracking number",
                        required=False,
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"support", "tracking", "shipping"},
            ),
            ToolSpec(
                name="support_initiate_return",
                description="Start return process for order",
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
                        name="items",
                        type=ParameterType.ARRAY,
                        description="Items to return",
                        required=True,
                    ),
                    ToolParameter(
                        name="reason",
                        type=ParameterType.STRING,
                        description="Return reason",
                        required=True,
                    ),
                    ToolParameter(
                        name="preference",
                        type=ParameterType.STRING,
                        description="Refund or exchange preference",
                        required=False,
                    ),
                ],
                idempotent=False,
                cacheable=False,
                tags={"support", "return", "commerce"},
            ),
            ToolSpec(
                name="support_process_refund",
                description="Process refund for order",
                category=ToolCategory.COMMERCE,
                severity=ToolSeverity.HIGH,
                parameters=[
                    ToolParameter(
                        name="order_id",
                        type=ParameterType.STRING,
                        description="Order ID",
                        required=True,
                    ),
                    ToolParameter(
                        name="amount",
                        type=ParameterType.NUMBER,
                        description="Refund amount",
                        required=True,
                    ),
                    ToolParameter(
                        name="reason",
                        type=ParameterType.STRING,
                        description="Refund reason",
                        required=True,
                    ),
                ],
                idempotent=False,
                cacheable=False,
                tags={"support", "refund", "finance"},
            ),
            ToolSpec(
                name="support_create_ticket",
                description="Create support ticket",
                category=ToolCategory.SYSTEM,
                severity=ToolSeverity.LOW,
                parameters=[
                    ToolParameter(
                        name="customer_email",
                        type=ParameterType.STRING,
                        description="Customer email",
                        required=True,
                    ),
                    ToolParameter(
                        name="subject",
                        type=ParameterType.STRING,
                        description="Ticket subject",
                        required=True,
                    ),
                    ToolParameter(
                        name="description",
                        type=ParameterType.STRING,
                        description="Issue description",
                        required=True,
                    ),
                    ToolParameter(
                        name="priority",
                        type=ParameterType.STRING,
                        description="Priority level (low, medium, high, urgent)",
                        required=False,
                    ),
                ],
                idempotent=False,
                cacheable=False,
                tags={"support", "ticket", "create"},
            ),
            ToolSpec(
                name="support_escalate_ticket",
                description="Escalate ticket to human agent",
                category=ToolCategory.SYSTEM,
                severity=ToolSeverity.MEDIUM,
                parameters=[
                    ToolParameter(
                        name="ticket_id",
                        type=ParameterType.STRING,
                        description="Ticket ID",
                        required=True,
                    ),
                    ToolParameter(
                        name="reason",
                        type=ParameterType.STRING,
                        description="Escalation reason",
                        required=True,
                    ),
                    ToolParameter(
                        name="priority",
                        type=ParameterType.STRING,
                        description="Escalation priority",
                        required=False,
                    ),
                    ToolParameter(
                        name="summary",
                        type=ParameterType.STRING,
                        description="Issue summary for human agent",
                        required=False,
                    ),
                ],
                idempotent=False,
                cacheable=False,
                tags={"support", "escalation", "ticket"},
            ),
            ToolSpec(
                name="support_get_customer_history",
                description="Get customer order and support history",
                category=ToolCategory.COMMERCE,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="customer_id",
                        type=ParameterType.STRING,
                        description="Customer ID",
                        required=False,
                    ),
                    ToolParameter(
                        name="email",
                        type=ParameterType.STRING,
                        description="Customer email",
                        required=False,
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"support", "customer", "history"},
            ),
        ]

        for spec in support_tools:
            registry.register(spec)

    async def execute(self, prompt: str, **kwargs) -> AgentResult:
        """Execute support operation"""
        start_time = datetime.now(UTC)

        try:
            task_type = self._classify_support_task(prompt)
            technique = self.TECHNIQUE_PREFERENCES.get(
                task_type, self.select_technique(TaskCategory.QA)
            )

            # Check for escalation needs
            if self._should_escalate(prompt, kwargs):
                return await self._handle_escalation(prompt, start_time)

            # Apply RAG technique for FAQ-based queries
            if task_type == "faq":
                faq_context: list[dict[str, str]] | None = None
                if self._rag_service is not None:
                    try:
                        rag_result = await self._rag_service.query(
                            collection=self._rag_collection,
                            question=prompt,
                            mode="local",  # entity-centric — best for policy lookups
                            top_k=5,
                        )
                        answer = rag_result.get("answer", "")
                        # RAGPrompting.create_prompt expects list[dict[str, str]]
                        # with "text"/"source" keys, not list[str].
                        faq_context = [{"text": answer, "source": "rag"}] if answer else None
                    except Exception as rag_exc:
                        logger.warning(
                            f"RAG FAQ fetch failed, falling back to static FAQs: {rag_exc}"
                        )
                if faq_context is None:
                    faq_context = self._get_relevant_faqs(prompt)
                enhanced = self.apply_technique(PromptTechnique.RAG, prompt, context=faq_context)
            else:
                enhanced = self.apply_technique(
                    technique, prompt, role="customer support specialist for SkyyRose", **kwargs
                )

            if hasattr(self, "_backend_agent"):
                result = await self._backend_agent.run(enhanced.enhanced_prompt)
                content = str(result.output) if hasattr(result, "output") else str(result)
            else:
                content = await self._fallback_process(prompt, task_type)

            return AgentResult(
                agent_name=self.name,
                agent_provider=self._active_provider,
                content=content,
                status=AgentStatus.COMPLETED,
                started_at=start_time,
                metadata={"task_type": task_type, "technique": technique.value, "escalated": False},
            )

        except Exception as e:
            logger.error(f"Support agent error: {e}")
            return AgentResult(
                agent_name=self.name,
                agent_provider=self._active_provider,
                content="",
                status=AgentStatus.FAILED,
                error=str(e),
                started_at=start_time,
            )

    def _classify_support_task(self, prompt: str) -> str:
        """Classify the support task type"""
        prompt_lower = prompt.lower()

        task_keywords = {
            "inquiry": ["question", "wondering", "curious", "ask"],
            "ticket": ["ticket", "case", "issue number", "reference"],
            "faq": ["how do", "what is", "when", "where", "policy"],
            "return": ["return", "exchange", "refund", "send back"],
            "chat": ["help", "assist", "need support"],
            "escalation": ["manager", "supervisor", "human", "speak to"],
        }

        for task_type, keywords in task_keywords.items():
            if any(kw in prompt_lower for kw in keywords):
                return task_type

        return "inquiry"

    def _should_escalate(self, prompt: str, context: dict) -> bool:
        """Determine if ticket should be escalated"""
        prompt_lower = prompt.lower()

        # Explicit escalation requests
        if any(kw in prompt_lower for kw in ["manager", "supervisor", "human", "real person"]):
            return True

        # Legal/safety keywords
        if any(kw in prompt_lower for kw in ["lawyer", "legal", "sue", "unsafe", "dangerous"]):
            return True

        # Check order value if provided
        order_value = context.get("order_value", 0)
        return order_value > 500

    async def _handle_escalation(self, prompt: str, start_time: datetime) -> AgentResult:
        """Handle escalation to human agent"""
        response = """I understand you'd like to speak with a human team member. I'm connecting you with our customer care team now.

While you wait:
- A team member will be with you within 2 hours during business hours (9AM-6PM PST)
- For urgent matters, call us at 1-888-SKYYROSE
- Your conversation history has been saved for seamless handoff

Is there anything else I can help clarify before the handoff?"""

        return AgentResult(
            agent_name=self.name,
            agent_provider=self._active_provider,
            content=response,
            status=AgentStatus.COMPLETED,
            started_at=start_time,
            metadata={
                "task_type": "escalation",
                "escalated": True,
                "escalation_reason": "customer_request",
            },
        )

    def _get_relevant_faqs(self, query: str) -> list[dict[str, str]]:
        """Get relevant FAQs for query"""
        query_lower = query.lower()
        relevant = []

        keyword_mappings = {
            "shipping": ["ship", "delivery", "arrive", "long"],
            "returns": ["return", "exchange", "send back", "refund"],
            "sizing": ["size", "fit", "measurements"],
            "payment": ["pay", "payment", "credit card", "klarna"],
            "tracking": ["track", "where is", "status", "order"],
        }

        for faq_key, keywords in keyword_mappings.items():
            if any(kw in query_lower for kw in keywords):
                faq = self.FAQ_KNOWLEDGE.get(faq_key)
                if faq:
                    relevant.append(
                        {
                            "text": f"Q: {faq['question']}\nA: {faq['answer']}",
                            "source": f"faq_{faq_key}",
                        }
                    )

        return relevant

    async def _fallback_process(self, prompt: str, task_type: str) -> str:
        """Fallback processing"""
        return f"""Support Agent Response

Thank you for reaching out to SkyyRose support!

Query: {prompt[:200]}...
Category: {task_type}

Our team is reviewing your request. For immediate assistance:
- Email: support@skyyrose.com
- Phone: 1-888-SKYYROSE
- Hours: 9AM-6PM PST, Monday-Friday

We'll respond within 24 hours."""

    # =========================================================================
    # Support-Specific Methods
    # =========================================================================

    async def handle_inquiry(
        self, message: str, customer_context: dict | None = None
    ) -> AgentResult:
        """Handle customer inquiry with full context"""
        context = customer_context or {}

        prompt = f"""Customer Inquiry for SkyyRose Support:

Message: {message}
Customer Context: {context}

Please:
1. Identify the customer's primary need
2. Check relevant FAQs and policies
3. Provide a warm, helpful response
4. Include any relevant next steps
5. Offer additional assistance"""

        return await self.execute_with_learning(
            prompt,
            task_type="inquiry",
            technique=PromptTechnique.RAG,
            context=self._get_relevant_faqs(message),
        )

    async def classify_intent(self, message: str) -> dict[str, Any]:
        """Classify customer intent using ML"""
        if self.ml_module:
            prediction = await self.ml_module.predict("intent_classifier", message)
            return {
                "message": message[:100],
                "intent": prediction.prediction,
                "confidence": prediction.confidence,
            }

        # Fallback classification
        task_type = self._classify_support_task(message)
        return {"message": message[:100], "intent": task_type, "confidence": 0.7}

    async def process_return(
        self, order_id: str, items: list[str], reason: str, preference: str = "refund"
    ) -> AgentResult:
        """Process return request"""
        prompt = f"""Process return request:

Order ID: {order_id}
Items: {items}
Reason: {reason}
Preference: {preference}

Please:
1. Verify return eligibility (30-day policy)
2. Calculate refund amount (minus $9.95 if not exchange)
3. Generate return label instructions
4. Provide timeline expectations
5. Offer exchange alternatives if applicable"""

        return await self.execute_with_learning(
            prompt, task_type="return", technique=PromptTechnique.CHAIN_OF_THOUGHT
        )

    async def predict_escalation(self, conversation_history: list[str]) -> dict[str, Any]:
        """Predict if conversation needs escalation"""
        if self.ml_module:
            conversation_text = "\n".join(conversation_history)
            prediction = await self.ml_module.predict("escalation_predictor", conversation_text)
            return {
                "should_escalate": prediction.prediction.get("escalate", False),
                "confidence": prediction.confidence,
                "reason": prediction.prediction.get("reason", "unknown"),
            }

        # Fallback based on keywords
        combined = " ".join(conversation_history).lower()
        should_escalate = self._should_escalate(combined, {})
        return {
            "should_escalate": should_escalate,
            "confidence": 0.7,
            "reason": "keyword_match" if should_escalate else "none",
        }


# =============================================================================
# Export
# =============================================================================

__all__ = ["SupportAgent"]
