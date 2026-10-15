# DevSkyy repo overview (pointer file — read the docs, not this)

Verified 2026-10-14 on `main`. Everything here is a locator; the authoritative text is
in the files named.

## Read first
- `CLAUDE.md` (root) — operating rules, STOP-AND-SHOW gate, verification matrix, brand
  tokens, deploy table, CI facts. Scoped `CLAUDE.md` files load under `agents/`, `api/`,
  `database/`, `llm/`, `frontend/`, `docs/`, `skyyrose/elite_studio/`, and the theme.
- `AGENTS.md` — the same contract for non-Claude agents.
- `SOT.md` — registry of canonical product / imagery / brand / memory sources.
- `.wolf/memory.md` — cross-agent handoff log (append one row per session);
  `.wolf/anatomy.md` — file index; `.wolf/cerebrum.md` — learnings.

## Where things are (top-level)
- `skyyrose/core/` — product SOT readers; `get_product` lives in `skyyrose/core/product.py`.
- `skyyrose/elite_studio/`, `skyyrose/multi_agent/` — render/studio and agent code.
- `scripts/` — tooling; `scripts/sync_product_registry.py` syncs registry projections.
- `wordpress-theme/skyyrose-flagship/` (V1; `SKYYROSE_VERSION` 2.2.4 in `functions.php`),
  `wordpress-theme/skyyrose-flagship-2/` (V2), `wordpress-theme/skyyrose-flagship-sot/`.
- `frontend/` — dashboard (own `package.json`; do not mix its `node_modules` with root).
- `api/`, `llm/`, `database/`, `security/`, `orchestration/`, `agents/`, `mcp_tools/`.
- `tests/` — pytest; run with `rtk proxy pytest ...`.

## Stale-memory warning
`.serena/memories/_archive/` holds Dec 2025–Jan 2026 notes (e.g. "6 SuperAgents + 21 MCP
tools", `api.skyyrose.com`, theme v3.2.0). They are hidden from `list_memories` on
purpose and are NOT current. When anything here conflicts with `CLAUDE.md`, the code, or
`get_product`, the latter wins.
