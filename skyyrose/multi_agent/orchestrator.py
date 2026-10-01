"""
Multi-Agent Orchestrator — The Brain

Two modes:
  1. run_orchestrator() — Full orchestrator with subagents, hooks, custom tools
  2. run_single_agent() — Run a single named subagent directly

Both use Claude Agent SDK for autonomous operation.
"""

from __future__ import annotations

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
)

from .agents import AGENT_DEFINITIONS
from .config import (
    MAX_BUDGET_USD,
    MAX_TURNS_ORCHESTRATOR,
    MAX_TURNS_SUBAGENT,
    ORCHESTRATOR_MODEL,
    REPO_DIR,
    SUBAGENT_MODEL,
)
from .hooks import HOOKS
from .tools import skyyrose_mcp_server

# ---------------------------------------------------------------------------
# System Prompt — The Orchestrator's Identity
# ---------------------------------------------------------------------------

ORCHESTRATOR_SYSTEM_PROMPT = """You are the SkyyRose Multi-Agent Orchestrator — the central intelligence
coordinating a team of specialized AI agents for the SkyyRose luxury fashion platform.

PLATFORM OVERVIEW:
- SkyyRose: luxury streetwear brand, 3 collections (Black Rose, Love Hurts, Signature)
- WordPress theme: skyyrose-flagship (assets, templates, WooCommerce)
- Next.js frontend: devskyy.app (Vercel deployment)
- 28 products, 6 on pre-order
- AI pipeline: Elite Studio (Vision→Generation→QC→Compositing)

YOUR SUBAGENT TEAM:
1. brand-writer — Generates marketing copy, product descriptions, social captions
2. theme-auditor — Audits WordPress theme CSS, fonts, a11y, performance
3. product-analyst — Analyzes product catalog, images, pricing, completeness
4. deploy-manager — Checks deployments, runs builds, monitors git status
5. qa-inspector — End-to-end quality checks, regression testing

HOW TO WORK:
- Analyze the user's request and decide which agent(s) to delegate to
- For complex requests, spawn multiple subagents in parallel using the Agent tool
- Use custom SkyyRose tools (mcp__skyyrose-tools__*) for direct data access
- Synthesize subagent results into clear, actionable summaries
- Always report what was found, what's good, and what needs attention

CUSTOM TOOLS AVAILABLE:
- get_product_catalog — Full product listing with prices
- get_product_overrides — Generation specs for a SKU
- list_product_images — Find images for any product
- list_theme_templates — All PHP templates in the theme
- get_theme_css_stats — CSS file sizes and line counts
- check_font_loading — GDPR compliance for fonts
- get_brand_guidelines — Brand identity and voice rules
- generate_product_copy — Product copy generation support
- elite_studio_status — AI pipeline production status
- elite_studio_produce — Run Elite Studio for a product
- check_vercel_status — Frontend deployment status
- git_status_summary — Git branch and changes

RULES:
- No active brand tagline. Do not invent a replacement or reuse retired slogans.
- Brand colors: Rose Gold #B76E79, Dark #0A0A0A, Gold #D4AF37
- Be concise, professional, and actionable in your summaries"""


# ---------------------------------------------------------------------------
# Full Orchestrator Mode
# ---------------------------------------------------------------------------


async def run_orchestrator(
    prompt: str,
    interactive: bool = False,
    max_budget: float = MAX_BUDGET_USD,
) -> str:
    """Run the full multi-agent orchestrator.

    Args:
        prompt: User's request
        interactive: If True, use ClaudeSDKClient for multi-turn conversation
        max_budget: Maximum USD budget for the session

    Returns:
        Final result text from the orchestrator.
    """
    options = ClaudeAgentOptions(
        cwd=str(REPO_DIR),
        model=ORCHESTRATOR_MODEL,
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        allowed_tools=[
            "Read",
            "Glob",
            "Grep",
            "Bash",
            "Agent",
            # Custom MCP tools (auto-prefixed with mcp__skyyrose-tools__)
            "mcp__skyyrose-tools__get_product_catalog",
            "mcp__skyyrose-tools__get_product_overrides",
            "mcp__skyyrose-tools__list_product_images",
            "mcp__skyyrose-tools__list_theme_templates",
            "mcp__skyyrose-tools__get_theme_css_stats",
            "mcp__skyyrose-tools__check_font_loading",
            "mcp__skyyrose-tools__get_brand_guidelines",
            "mcp__skyyrose-tools__generate_product_copy",
            "mcp__skyyrose-tools__elite_studio_status",
            "mcp__skyyrose-tools__elite_studio_produce",
            "mcp__skyyrose-tools__check_vercel_status",
            "mcp__skyyrose-tools__git_status_summary",
        ],
        mcp_servers={"skyyrose-tools": skyyrose_mcp_server},
        agents=AGENT_DEFINITIONS,
        hooks=HOOKS,
        max_turns=MAX_TURNS_ORCHESTRATOR,
        max_budget_usd=max_budget,
        thinking={"type": "adaptive"},
        permission_mode="default",
    )

    if interactive:
        return await _run_interactive(prompt, options)
    return await _run_oneshot(prompt, options)


async def _run_oneshot(prompt: str, options: ClaudeAgentOptions) -> str:
    """One-shot query — send prompt, collect result.

    Uses ClaudeSDKClient (NOT query()) because claude-agent-sdk 0.1.41's
    query() calls transport.end_input() after string prompts, which closes
    stdin and breaks the bidirectional control protocol required by SDK
    MCP servers. Symptom: CLIConnectionError("ProcessTransport is not
    ready for writing"). ClaudeSDKClient keeps stdin open for control
    responses.
    """
    result_text = ""

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text, end="", flush=True)

            elif isinstance(message, ResultMessage):
                result_text = message.result or ""
                print("\n\n--- Session complete ---")
                print(f"Cost: ${message.total_cost_usd:.4f}")
                print(f"Duration: {message.duration_ms / 1000:.1f}s")

    return result_text


async def _run_interactive(prompt: str, options: ClaudeAgentOptions) -> str:
    """Interactive multi-turn conversation with the orchestrator."""
    result_text = ""

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text, end="", flush=True)

            elif isinstance(message, ResultMessage):
                result_text = message.result or ""
                print(f"\n\n--- Turn complete (${message.total_cost_usd:.4f}) ---")

        # Interactive loop
        while True:
            try:
                user_input = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nSession ended.")
                break

            if user_input.lower() in ("exit", "quit", "q"):
                break

            if not user_input:
                continue

            await client.query(user_input)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(block.text, end="", flush=True)

                elif isinstance(message, ResultMessage):
                    result_text = message.result or ""
                    print(f"\n\n--- Turn complete (${message.total_cost_usd:.4f}) ---")

    return result_text


# ---------------------------------------------------------------------------
# Single Agent Mode
# ---------------------------------------------------------------------------


async def run_single_agent(
    agent_name: str,
    prompt: str,
    max_budget: float = MAX_BUDGET_USD,
) -> str:
    """Run a single named subagent directly.

    Args:
        agent_name: One of the registered agent names
        prompt: Task for the agent

    Returns:
        Agent's result text.
    """
    if agent_name not in AGENT_DEFINITIONS:
        available = ", ".join(AGENT_DEFINITIONS.keys())
        raise ValueError(f"Unknown agent '{agent_name}'. Available: {available}")

    agent_def = AGENT_DEFINITIONS[agent_name]

    options = ClaudeAgentOptions(
        cwd=str(REPO_DIR),
        model=SUBAGENT_MODEL,
        system_prompt=agent_def.prompt,
        allowed_tools=[
            *(agent_def.tools or ["Read", "Glob", "Grep"]),
            # All custom MCP tools
            "mcp__skyyrose-tools__get_product_catalog",
            "mcp__skyyrose-tools__get_product_overrides",
            "mcp__skyyrose-tools__list_product_images",
            "mcp__skyyrose-tools__list_theme_templates",
            "mcp__skyyrose-tools__get_theme_css_stats",
            "mcp__skyyrose-tools__check_font_loading",
            "mcp__skyyrose-tools__get_brand_guidelines",
            "mcp__skyyrose-tools__generate_product_copy",
            "mcp__skyyrose-tools__elite_studio_status",
            "mcp__skyyrose-tools__elite_studio_produce",
            "mcp__skyyrose-tools__check_vercel_status",
            "mcp__skyyrose-tools__git_status_summary",
        ],
        mcp_servers={"skyyrose-tools": skyyrose_mcp_server},
        hooks=HOOKS,
        max_turns=MAX_TURNS_SUBAGENT,
        max_budget_usd=max_budget,
        thinking={"type": "adaptive"},
        permission_mode="default",
    )

    result_text = ""

    # ClaudeSDKClient (not query()) — see _run_oneshot docstring for SDK MCP rationale.
    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text, end="", flush=True)

            elif isinstance(message, ResultMessage):
                result_text = message.result or ""
                cost = message.total_cost_usd
                duration = message.duration_ms / 1000
                print(f"\n\n--- {agent_name} complete (${cost:.4f}, {duration:.1f}s) ---")

    return result_text
