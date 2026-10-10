# WordPress Bridge Agent — Design Document

**Date:** 2026-02-26
**Status:** Approved
**Author:** Claude Opus 4.6

---

## Summary

A Claude Agent SDK-powered orchestrator that connects all 9 DevSkyy dashboard pipelines to the WordPress site (skyyrose.co). The agent runs on-demand from the dashboard, uses adaptive thinking to reason about operations, and streams progress back via SSE.

---

## Architecture

```
Dashboard (Next.js)  — ALL admin pages
  Round Table | 3D Pipeline | Imagery | Social | Products | Monitoring
                        |
                        | POST /api/v1/agent/execute
                        | { "intent": "...", "context": {...} }
                        v
FastAPI — Agent Endpoint (SSE streaming)
  +--------------------------------------------------+
  | Claude Agent SDK (Opus 4.6, adaptive thinking)   |
  | System Prompt: SkyyRose brand + all tools        |
  | MCP Server: 15 tools wrapping existing code      |
  +------------------+-------------------------------+
                     | calls tools
  +------------------v-------------------------------+
  | Existing Code (untouched)                        |
  | - WordPressClient (669 lines)                    |
  | - WordPressComClient (387 lines)                 |
  | - WordPressProductSync (212 lines)               |
  | - Pipeline API calls                             |
  +------------------+-------------------------------+
                     |
                     v
               skyyrose.co
               WooCommerce
```

### Key Decisions

- **Runtime:** Claude Agent SDK `query()` with custom MCP server
- **Trigger:** On-demand from dashboard (POST endpoint)
- **Streaming:** SSE for live progress updates to dashboard
- **Webhooks:** Incoming WooCommerce webhooks dispatched as agent prompts
- **Model:** `claude-opus-4-6` with `thinking: {type: "adaptive"}`
- **Existing code:** All WordPress client code reused as-is, wrapped in MCP tools

---

## MCP Tools (15)

### WordPress Core (8)

| Tool | Wraps | Purpose |
|------|-------|---------|
| `wp_sync_product` | `WordPressProductSync.sync_product()` | Sync single product to WooCommerce |
| `wp_sync_collection` | `WordPressProductSync.sync_collection()` | Batch sync all products in a collection |
| `wp_create_page` | `WordPressClient.create_page()` | Create or update a WordPress page |
| `wp_upload_media` | `WordPressClient.upload_media()` | Upload image/file to media library |
| `wp_get_orders` | `WordPressClient.list_orders()` | List recent WooCommerce orders |
| `wp_update_order` | `WordPressClient.update_order_status()` | Change order status |
| `wp_health_check` | `WordPressClient.health_check()` | Check WP/WC connectivity |
| `wp_get_products` | `WordPressClient.list_products()` | List WooCommerce products |

### Pipeline Bridge (7)

| Tool | Purpose |
|------|---------|
| `wp_publish_round_table` | Format LLM Round Table result as WordPress draft post (winner highlight, all entries ranked, custom meta) |
| `wp_attach_3d_model` | Upload GLB file URL to product custom field `_product_3d_model_url` |
| `wp_upload_product_image` | Upload generated image to media library, attach to product gallery |
| `wp_publish_social_campaign` | Format social media campaign content as WordPress blog post |
| `wp_update_conversion_data` | Push conversion metrics (heat scores, funnel data) to product meta |
| `get_pipeline_status` | Aggregate all 9 pipeline statuses from `/api/pipeline-status` |
| `get_product_catalog` | Read local product catalog (21 products, 3 collections) |

---

## Pipeline Integration Map

| Dashboard Pipeline | Direction | WordPress Target | Data Flow |
|-------------------|-----------|-----------------|-----------|
| LLM Round Table | Dashboard -> WP | `/wp/v2/posts` | Competition results as blog posts |
| 3D Pipeline | Dashboard -> WP | Product meta `_product_3d_model_url` | GLB URLs for 3D viewer |
| Imagery | Dashboard -> WP | `/wp/v2/media` + product gallery | Generated product photos |
| Products | Bidirectional | `/wc/v3/products` | Catalog sync (price, stock, description) |
| Social Media | Dashboard -> WP | `/wp/v2/posts` | Campaign content repurposed as blog |
| Conversion | Dashboard -> WP | Product meta `_trending_score` | Heat scores for smart recommendations |
| Orders | WP -> Dashboard | Webhook `order-created` | New order processing |
| Health | Bidirectional | WP REST API | Connectivity + theme integrity |
| Pipeline Status | Read-only | Internal | Aggregate all pipeline health |

---

## Files to Create

| File | Action | Purpose |
|------|--------|---------|
| `agents/wordpress_bridge/__init__.py` | Create | Package init, exports |
| `agents/wordpress_bridge/mcp_server.py` | Create | 15 MCP tools wrapping existing WordPress clients |
| `agents/wordpress_bridge/agent.py` | Create | Agent SDK entry point with `run_agent()` function |
| `agents/wordpress_bridge/prompts.py` | Create | System prompt + prompt templates for each pipeline |
| `api/v1/wordpress_agent.py` | Create | FastAPI SSE endpoint + webhook dispatcher |
| `frontend/lib/wordpress/agent-client.ts` | Create | SSE client hook `useWordPressAgent()` |
| `frontend/app/admin/wordpress/page.tsx` | Modify | Wire existing buttons to agent endpoint |
| `tests/agents/test_wordpress_bridge.py` | Create | Unit tests for MCP tools + agent |

### Files NOT Modified (reused as-is)

- `integrations/wordpress_client.py` (669 lines)
- `integrations/wordpress_com_client.py` (387 lines)
- `integrations/wordpress_product_sync.py` (212 lines)
- `frontend/lib/wordpress/operations-manager.ts` (635 lines)
- `frontend/lib/wordpress/sync-service.ts` (260 lines)

---

## Agent System Prompt

The agent receives:

1. **Brand context:** SkyyRose, "", 3 collections (Black Rose, Love Hurts, Signature), rose gold #B76E79
2. **Product catalog:** 21 products with SKUs, collections, pricing
3. **Tool descriptions:** When to use each of the 15 tools
4. **Rules:**
   - Never modify prices without explicit user confirmation
   - Always verify WordPress connectivity before batch operations
   - Retry failed operations once with adjusted parameters
   - Report errors clearly with actionable next steps
   - Use draft status for content posts (user reviews before publishing)

---

## FastAPI Endpoint

```
POST /api/v1/agent/execute
Content-Type: application/json
Accept: text/event-stream

Request:
{
  "intent": "sync_collection",
  "prompt": "Sync all Black Rose products to WooCommerce",
  "context": {
    "collection": "black-rose",
    "source": "admin/wordpress"
  }
}

Response (SSE):
data: {"type": "thinking", "content": "Checking WordPress connectivity..."}
data: {"type": "tool_use", "tool": "wp_health_check", "status": "running"}
data: {"type": "tool_result", "tool": "wp_health_check", "result": {"connected": true}}
data: {"type": "tool_use", "tool": "wp_sync_collection", "status": "running"}
data: {"type": "progress", "content": "Syncing product 3/8: BLACK Rose Sherpa..."}
data: {"type": "result", "content": "Synced 8 products. 6 updated, 2 created."}
```

---

## Webhook Processing

When WooCommerce fires a webhook:

1. `POST /api/v1/wordpress/webhooks/dispatch` receives payload
2. Validates HMAC signature (existing `verify_webhook_signature()`)
3. Formats as structured prompt: "New order #1234: 2x Black Rose Sherpa ($89 each)"
4. Spawns agent with order-processing context
5. Agent decides: update inventory count, notify dashboard, log event

---

## Frontend Integration

```typescript
// frontend/lib/wordpress/agent-client.ts
export function useWordPressAgent() {
  const [status, setStatus] = useState<'idle' | 'running' | 'done' | 'error'>('idle');
  const [messages, setMessages] = useState<AgentMessage[]>([]);

  async function execute(intent: string, prompt: string, context?: Record<string, any>) {
    setStatus('running');
    const response = await fetch('/api/v1/agent/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ intent, prompt, context }),
    });

    const reader = response.body.getReader();
    // Read SSE stream, update messages array
    // Set status to 'done' or 'error' on completion
  }

  return { status, messages, execute };
}
```

Dashboard buttons (e.g., "Sync Products", "Publish Results") call `execute()` and display streaming messages in a panel.

---

## Error Handling

| Scenario | Agent Behavior |
|----------|---------------|
| WordPress API down | Reports "WordPress unreachable at skyyrose.co" with last-known status |
| WooCommerce auth failed | Reports "WooCommerce authentication failed — check consumer key/secret" |
| Product sync conflict | Reports SKU conflict details, asks user for resolution |
| Tool execution fails | Retries once with adjusted parameters, then reports failure |
| Token budget exceeded | Summarizes progress so far, returns partial result |
| Invalid webhook signature | Rejects silently (existing behavior preserved) |

---

## Testing Strategy

1. **Unit tests:** Each MCP tool tested in isolation with mocked WordPress clients
2. **Integration test:** Agent runs with mock MCP server, verifies tool call sequences
3. **SSE test:** Verify streaming endpoint produces valid event stream
4. **Webhook test:** Verify dispatch formats prompts correctly from WC payloads

---

## Dependencies

- `claude-agent-sdk` (new) — Agent SDK for Python
- `anthropic` (existing) — Claude API client
- All other dependencies already in project

---

## Cost Estimate

Per agent invocation (Opus 4.6):
- Simple operation (health check): ~$0.01-0.03
- Medium operation (sync 8 products): ~$0.05-0.15
- Complex operation (full collection sync + media): ~$0.15-0.50

On-demand model keeps costs proportional to actual usage.
