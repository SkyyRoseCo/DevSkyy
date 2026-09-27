"""
Agent Orchestrator

Coordinates multiple SuperAgents to handle complex multi-agent workflows.
"""

from typing import Any

from agent_sdk.custom_tools import create_devskyy_tools
from agent_sdk.super_agents import (
    AnalyticsAgent,
    CommerceAgent,
    CreativeAgent,
    MarketingAgent,
    OperationsAgent,
    SupportAgent,
)
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
)


class AgentOrchestrator:
    """
    Orchestrates multiple SuperAgents for complex workflows.

    This class coordinates the 6 SuperAgents (Commerce, Creative, Marketing,
    Support, Operations, Analytics) to handle enterprise-level tasks that
    require collaboration across multiple domains.
    """

    def __init__(
        self,
        enable_all_agents: bool = True,
        custom_agents: dict[str, Any] | None = None,
    ):
        """
        Initialize the orchestrator.

        Args:
            enable_all_agents: If True, registers all 6 SuperAgents
            custom_agents: Additional custom agent definitions
        """
        self.agents = {}

        if enable_all_agents:
            self.agents = {
                "commerce": CommerceAgent.get_agent_definition(),
                "creative": CreativeAgent.get_agent_definition(),
                "marketing": MarketingAgent.get_agent_definition(),
                "support": SupportAgent.get_agent_definition(),
                "operations": OperationsAgent.get_agent_definition(),
                "analytics": AnalyticsAgent.get_agent_definition(),
            }

        if custom_agents:
            self.agents.update(custom_agents)

        # Create DevSkyy MCP tools
        self.mcp_server = create_devskyy_tools()

    def get_orchestrator_options(
        self,
        permission_mode: str = "default",
        model: str = "sonnet",
    ) -> ClaudeAgentOptions:
        """
        Get configured options for the orchestrator.

        Args:
            permission_mode: Permission mode for tool execution
            model: Claude model to use

        Returns:
            ClaudeAgentOptions configured for multi-agent orchestration
        """
        return ClaudeAgentOptions(
            system_prompt="""You are the DevSkyy Enterprise Orchestrator, coordinating multiple specialized SuperAgents.

Available SuperAgents:
- commerce: E-commerce operations (products, orders, inventory)
- creative: Visual content generation (3D models, images)
- marketing: Content creation, SEO, social media
- support: Customer service and tickets
- operations: DevOps, deployments, WordPress
- analytics: Data analysis and reporting

Orchestration Strategy:
1. Analyze the task to identify required capabilities
2. Determine which SuperAgents are needed
3. Delegate subtasks to appropriate agents using the Task tool
4. Coordinate agent outputs
5. Synthesize final result

When to use each agent:
- commerce: Product management, orders, pricing
- creative: 3D models, images, visual assets
- marketing: Blog posts, social media, campaigns
- support: Customer inquiries, tickets
- operations: Deployments, infrastructure
- analytics: Reports, forecasts, insights

For complex tasks:
- Break down into agent-specific subtasks
- Execute agents in parallel when possible
- Use sequential execution when outputs depend on each other
- Aggregate results into coherent final output

Brand Context (SkyyRose):
- Luxury fashion brand
- Colors: Rose Gold (#B76E79), Dark (#0a0a0a), Gold (#D4AF37)
- Tone: Elegant, sophisticated, bold
- No brand slogan is authorized.

Always maintain brand consistency across all agent interactions.""",
            agents=self.agents,
            mcp_servers={"devskyy": self.mcp_server},
            allowed_tools=[
                "Task",  # CRITICAL: Required for invoking subagents
                "Read",
                "Write",
                "Bash",
                "WebSearch",
                "WebFetch",
                # MCP tools
                "mcp__devskyy__generate_3d_model",
                "mcp__devskyy__manage_product",
                "mcp__devskyy__analyze_data",
                "mcp__devskyy__create_marketing_content",
                "mcp__devskyy__handle_support_ticket",
                "mcp__devskyy__execute_deployment",
            ],
            permission_mode=permission_mode,
            model=model,
        )

    async def execute_workflow(
        self,
        task: str,
        permission_mode: str = "default",
    ) -> dict[str, Any]:
        """
        Execute a multi-agent workflow.

        Args:
            task: The task description for the orchestrator
            permission_mode: Permission mode for execution

        Returns:
            Dict containing result, usage, and metadata
        """
        options = self.get_orchestrator_options(permission_mode=permission_mode)

        result_data = {
            "result": "",
            "usage": None,
            "total_cost_usd": None,
            "duration_ms": None,
            "session_id": None,
        }

        async with ClaudeSDKClient(options=options) as client:
            await client.query(task)

            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            result_data["result"] += block.text

                elif isinstance(message, ResultMessage):
                    result_data["usage"] = message.usage
                    result_data["total_cost_usd"] = message.total_cost_usd
                    result_data["duration_ms"] = message.duration_ms
                    result_data["session_id"] = message.session_id
                    if message.result:
                        result_data["result"] = message.result

        return result_data

    async def query_single_agent(
        self,
        agent_name: str,
        task: str,
        permission_mode: str = "acceptEdits",
    ) -> dict[str, Any]:
        """
        Query a single SuperAgent directly.

        Args:
            agent_name: Name of the agent (commerce, creative, marketing, etc.)
            task: Task for the agent
            permission_mode: Permission mode

        Returns:
            Dict containing result and metadata
        """
        # Map agent names to their classes
        agent_map = {
            "commerce": CommerceAgent,
            "creative": CreativeAgent,
            "marketing": MarketingAgent,
            "support": SupportAgent,
            "operations": OperationsAgent,
            "analytics": AnalyticsAgent,
        }

        if agent_name not in agent_map:
            raise ValueError(f"Unknown agent: {agent_name}")

        agent_class = agent_map[agent_name]
        options = agent_class.get_standalone_options()
        options.permission_mode = permission_mode
        options.mcp_servers = {"devskyy": self.mcp_server}

        result_data = {
            "agent": agent_name,
            "result": "",
            "usage": None,
            "total_cost_usd": None,
        }

        async with ClaudeSDKClient(options=options) as client:
            await client.query(task)

            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            result_data["result"] += block.text

                elif isinstance(message, ResultMessage):
                    result_data["usage"] = message.usage
                    result_data["total_cost_usd"] = message.total_cost_usd
                    if message.result:
                        result_data["result"] = message.result

        return result_data
