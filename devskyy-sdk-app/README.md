# devskyy-sdk-app

A **SkyyRose commerce agent** built on the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/python) for Python. It answers product questions by calling **custom in-process MCP tools** that search the SkyyRose product registry — the one product source of truth — so every SKU, name, price, size, and availability it quotes is a real registry fact.

Built with `claude-agent-sdk` (≥ 0.2.110) and managed with [`uv`](https://docs.astral.sh/uv/).

## What's here

| File | Purpose |
|------|---------|
| `main.py` | Entry point. Builds `ClaudeAgentOptions`, runs `query()`, streams the response. |
| `tools.py` | Three custom tools (`lookup_product`, `list_collection`, `collection_canon`) wrapped in an in-process MCP server via `@tool` + `create_sdk_mcp_server`. |
| `catalog.py` | Product data read from the product registry (`wordpress-theme/skyyrose-flagship/data/logo-registry.json` — the ONE SkyyRose product source of truth, the same record `python -m skyyrose.core.product <sku>` prints), per-collection canon (ethos/accent/lineage), and search functions. Fails closed if the registry is missing; nothing is demo data. |
| `test_tools.py` | Offline checks for the tools and wiring. **No API calls, no cost.** |
| `.env.example` | Template for your `ANTHROPIC_API_KEY`. |

## Setup

```bash
cd devskyy-sdk-app

# 1. Create the virtual environment and install dependencies
uv sync

# 2. Add your API key
cp .env.example .env
#   then edit .env and paste your key from https://console.anthropic.com/
```

`uv sync` reads `pyproject.toml`, creates `.venv/`, and installs `claude-agent-sdk` + `python-dotenv`. The SDK **bundles the Claude Code CLI**, so there is nothing else to install.

## Run

```bash
# One-shot question
uv run python main.py "Is br-001 available, and what does it cost?"

# No argument -> three independent demo queries (each query() call is stateless)
uv run python main.py
```

Verify the tools without spending anything:

```bash
uv run python test_tools.py     # -> "All offline tool checks passed."
```

## How it works

```
main.py  ──query(prompt, options)──▶  bundled Claude Code CLI (subprocess)
   │                                          │
   │  ClaudeAgentOptions:                      │  Claude decides to call a tool
   │   • system_prompt (SkyyRose concierge)    ▼
   │   • mcp_servers={"catalog": ...}    mcp__catalog__lookup_product
   │   • allowed_tools=[...]                    │  (runs IN this Python process)
   │   • permission_mode="dontAsk"              ▼
   │   • setting_sources=[]              tools.py handler -> catalog.py
   ▼
 streamed AssistantMessage / ToolUseBlock / ResultMessage
```

Key design choices, and why:

- **In-process MCP tools.** `create_sdk_mcp_server` keeps the tool functions inside this process (no subprocess), so they can share your app's state and run with low latency. The mount key (`"catalog"`) becomes the middle segment of the tool name: `mcp__catalog__lookup_product`.
- **`permission_mode="dontAsk"`.** Only the two catalog tools are in `allowed_tools`. Any built-in tool the model reaches for (Bash, Read, …) is auto-denied and returned to Claude as data — so a non-interactive run never hangs on a permission prompt, and the agent loop keeps going.
- **`setting_sources=[]`.** The agent ignores user/project/local Claude settings on disk, staying fully self-contained.
- **`is_error` (not `isError`).** Tool handlers return a `{"content": [...], "is_error": bool}` dict. A clean "no results" is *data* (no `is_error`); a bad/empty argument sets `is_error: True` so Claude can recover.

## Make it yours

- **Catalog source:** `catalog.py` reads the product registry JSON directly because this app cannot import the `skyyrose` package. It maps only real registry fields (`catalog.name/price/description`, `garment.available_sizes`, `collections[slug].name`) and derives availability from `catalog.is_preorder` / `catalog.published` — the registry has no stock counts, so the agent never claims any. Product facts are edited in the registry (via `skyyrose.core.product_registry`), never here.
- **New tools:** write another `@tool`-decorated async function, add it to the `tools=[...]` list in `create_sdk_mcp_server`, and add its `mcp__catalog__<name>` to `allowed_tools`.
- **Change the model:** the agent pins `model="claude-sonnet-4-6"` in `build_options()` for reproducibility. Swap it for another current model, or drop the line to float with the bundled CLI default.
- **Tighten the persona:** edit `SYSTEM_PROMPT` in `main.py`.

## Docs

- [Python SDK reference](https://code.claude.com/docs/en/agent-sdk/python)
- [Custom tools guide](https://code.claude.com/docs/en/agent-sdk/custom-tools)
- [Permissions guide](https://code.claude.com/docs/en/agent-sdk/permissions)
- [SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
