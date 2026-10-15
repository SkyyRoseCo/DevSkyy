"""
Commerce SuperAgent

Handles e-commerce operations: products, orders, inventory, pricing.
"""

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions


class CommerceAgent:
    """
    SuperAgent specialized in e-commerce operations.

    Capabilities:
    - Product management (CRUD)
    - Order processing
    - Inventory tracking
    - Dynamic pricing
    - WooCommerce integration
    """

    @staticmethod
    def get_agent_definition() -> AgentDefinition:
        """Return the agent definition for use as a subagent."""
        return AgentDefinition(
            description=(
                "E-commerce specialist for managing products, orders, inventory, "
                "and pricing. Use when the task involves WooCommerce operations, "
                "product catalog management, or e-commerce analytics."
            ),
            prompt="""You are the Commerce SuperAgent for SkyyRose, an AI-powered e-commerce platform.

Your expertise includes:
- Product catalog management (create, update, delete products)
- Order processing and fulfillment
- Inventory tracking and alerts
- Dynamic pricing strategies
- WooCommerce API integration
- Product recommendations

Brand Context (SkyyRose):
- Premium romantic jewelry and gifts
- Colors: Rose Gold (#B76E79), Sophisticated Black (#1A1A1A)
- Tone: Elegant, sophisticated, bold
- No tagline is authorised

When handling product operations:
1. Always consider brand guidelines
2. Validate product data before submission
3. Use dynamic pricing when appropriate
4. Ensure inventory accuracy
5. Provide detailed operation summaries

Use the available MCP tools for WooCommerce operations.""",
            tools=[
                "Read",
                "Write",
                "Bash",
                "mcp__devskyy__manage_product",
                "mcp__devskyy__analyze_data",
            ],
            model="sonnet",
        )

    @staticmethod
    def get_standalone_options() -> ClaudeAgentOptions:
        """Get options for using this agent standalone (not as subagent)."""
        return ClaudeAgentOptions(
            system_prompt=CommerceAgent.get_agent_definition().prompt,
            allowed_tools=CommerceAgent.get_agent_definition().tools,
            model="sonnet",
            permission_mode="acceptEdits",
        )
