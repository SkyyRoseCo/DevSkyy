"""SkyyRose commerce agent — entry point.

Run a one-shot question against the agent:

    python main.py "What's the Black Rose collection about?"
    python main.py "Is br-001 in stock and what does it cost?"

With no argument it runs three independent demo queries so you can see the agent and its
custom catalog tools working end-to-end. (Each query() call is stateless — they do not
share conversation history; for a multi-turn session use ClaudeSDKClient instead.)

Requires ANTHROPIC_API_KEY in the environment (or a .env file — see .env.example).
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    query,
)
from dotenv import load_dotenv

from tools import catalog_server

# Load .env from this file's directory so the bundled CLI subprocess inherits the key.
PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")


# The system prompt is the agent's IDENTITY — stable every turn. Per-collection canon
# (ethos, accent) lives behind the catalog tools so it's fetched exact, never paraphrased.
SYSTEM_PROMPT = """\
You are the SkyyRose Concierge — the voice of SkyyRose, a luxury streetwear house whose \
ethos is "" You help shoppers find pieces and understand the \
collections. You speak with the quiet confidence of someone who knows the product cold.

# VOICE
- Grounded, confident, unhurried. Bay Area soul, not boutique fluff. Short sentences earn their place.
- The GARMENT is the protagonist. Lead with the piece — its make, its weight, what it's for — not with a sales pitch.
- Quote exact SKUs and prices. Specificity is the luxury.

# DO
- Answer product questions ONLY from the catalog tools (see TOOLS).
- Name the collection's character when it's relevant, using its real canon from `collection_canon`.
- When something is sold out, say so plainly and let the piece stand — no apology theater.

# DON'T (these are house rules — breaking them breaks the brand)
- NO urgency or scarcity tactics: no countdowns, no "selling fast," no "only N left," no manufactured FOMO.
- NO "customers also bought" cross-sell spam. Recommend only when asked, and only what fits.
- NEVER compare SkyyRose to European luxury houses (Gucci, Dior, LV, etc.). The lineage is streetwear — Oakland and the Bay, not Milan or Paris.
- NEVER invent products, SKUs, prices, stock, sizes, or collection lore. If a tool returns nothing, say so.
- NEVER cross-wire collection canon (see CANON). Each collection's line belongs to it alone.

# BRAND CANON
- No brand slogan is authorized.
- Four collections, each its own world:
  - Signature (gold) — the flagship; foundational pieces built to outlast trends.
  - Black Rose (silver) — ARMOR. Beauty with a hard edge.
  - Love Hurts (crimson) — "the bloodline that raised me." (This line is Love Hurts ONLY.)
  - Kids Capsule (rose gold) — the same concrete-born luxury, sized for the next generation.
- Pull the exact wording from `collection_canon` before you describe a collection — don't trust your memory of it.

# TOOLS
- `lookup_product` — a specific item, by SKU or name keyword. Use for "is X in stock," "what's the price of Y."
- `list_collection` — everything in a collection (products + its canon). Use for "show me Love Hurts."
- `collection_canon` — a collection's story/ethos WITHOUT products. Use for "what's Black Rose about."
You have no filesystem or shell access; do not attempt to read or write files.

# EXAMPLES (style, grounding, and house rules in action)

User: Is br-001 in stock and how much?
[calls lookup_product("br-001")]
Assistant: The Black Rose Bomber (br-001) is $320 — satin-lined, matte black, a silver-thread \
rose across the back panel. It's sold out right now. When Black Rose restocks, this is the piece to watch.

User: What's the Black Rose collection about?
[calls collection_canon("Black Rose")]
Assistant: Black Rose is armor — beauty with a hard edge, cut for the days that demand it. \
Matte black, silver hardware, tailoring built to protect. It's the collection you reach for when \
you need the world to take you seriously.

User: Do you carry a denim jacket?
[calls lookup_product("denim jacket") -> no match]
Assistant: Nothing in the catalog matches a denim jacket right now — I won't point you to \
something that isn't real. If you want a layer with weight to it, the Love Hurts Varsity Jacket \
(lh-005, $395) is the closest in spirit. Want a look?"""


def build_options() -> ClaudeAgentOptions:
    """Construct the agent configuration.

    - `mcp_servers` mounts our in-process catalog server under the name "catalog".
    - `allowed_tools` pre-approves ONLY the three catalog tools, so they run without a prompt.
    - `permission_mode="dontAsk"` denies any tool not pre-approved (e.g. built-in Bash/Read).
      That keeps a non-interactive run from hanging on a permission prompt while still letting
      the agent loop continue — denials come back to Claude as data, not as a crash.
    - `setting_sources=[]` means the agent ignores any user/project/local Claude settings on
      disk, so it stays self-contained and won't inherit the surrounding repo's configuration.
    - `model` is pinned for reproducible behavior. Without it the model floats with whatever
      the bundled CLI defaults to, which can change across CLI updates. Override as needed.
    """
    return ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        model="claude-sonnet-4-6",  # pinned for reproducibility; swap to taste
        # tools=[] removes ALL built-in tools (Bash/Read/Edit/…) from context. A commerce
        # concierge needs none of them, and shrinking the tool surface to just our 3 MCP
        # tools keeps the CLI below its tool-search threshold — so tools load eagerly
        # instead of the model running a ToolSearch round-trip before every catalog call.
        tools=[],
        mcp_servers={"catalog": catalog_server},
        allowed_tools=[
            "mcp__catalog__lookup_product",
            "mcp__catalog__list_collection",
            "mcp__catalog__collection_canon",
        ],
        permission_mode="dontAsk",
        max_turns=6,
        setting_sources=[],
        cwd=str(PROJECT_DIR),
    )


async def ask(prompt: str, options: ClaudeAgentOptions) -> None:
    """Send one prompt and stream the response, surfacing tool calls and the final cost."""
    print(f"\n\033[1m▶ {prompt}\033[0m")

    # The SDK raises on an error result (e.g. credit balance too low, rate limit) AFTER
    # yielding it, so wrap the stream and report cleanly instead of crashing the script.
    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock):
                        # Show when Claude reaches for a catalog tool, and with what arguments.
                        print(f"  \033[2m[tool] {block.name} {block.input}\033[0m")
                    elif isinstance(block, TextBlock):
                        print(f"  {block.text}")
            elif isinstance(message, ResultMessage):
                if message.is_error:
                    print(f"  \033[31m[error] {message.subtype}\033[0m")
                cost = message.total_cost_usd
                if cost is not None:
                    print(f"  \033[2m(session {message.session_id[:8]} · ${cost:.4f})\033[0m")
    except Exception as exc:  # noqa: BLE001 - surface any SDK/transport error as one clean line
        print(f"  \033[31m[api error] {exc}\033[0m")


async def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ANTHROPIC_API_KEY is not set.\n"
            "Copy .env.example to .env and add your key, or export it:\n"
            "  export ANTHROPIC_API_KEY=sk-ant-...\n"
            "Get a key at https://console.anthropic.com/",
            file=sys.stderr,
        )
        raise SystemExit(1)

    options = build_options()

    # A CLI argument becomes the single prompt; otherwise run three independent demo queries
    # that exercise each tool: canon, browse, and a specific stock/price lookup.
    cli_prompt = " ".join(sys.argv[1:]).strip()
    prompts = (
        [cli_prompt]
        if cli_prompt
        else [
            "What's the Black Rose collection all about?",
            "Show me everything in the Love Hurts collection.",
            "Is br-001 in stock, and what does it cost?",
        ]
    )

    for prompt in prompts:
        await ask(prompt, options)


if __name__ == "__main__":
    asyncio.run(main())
