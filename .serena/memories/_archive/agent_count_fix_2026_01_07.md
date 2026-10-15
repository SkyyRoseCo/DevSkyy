# Dynamic Agent Count Fix - 2026-01-07

## Problem
Health endpoint returned hardcoded "54" agents that didn't reflect reality, causing confusion in monitoring.

## Root Cause
The "54" was from the old architecture where DevSkyy had 54+ specialized agents before consolidating to 6 SuperAgents. The health endpoint was never updated after this architectural change.

## Solution
Replaced hardcoded value with dynamic agent counting using the new `orchestration/agent_counter.py` module.

## Files Modified

### 1. Created: `orchestration/agent_counter.py`
**Purpose**: Dynamic agent/tool discovery with Ralph-Wiggums error handling

**Key Functions**:
- `count_active_agents()` - Async function that counts:
  - MCP tools by parsing `@mcp.tool` decorators in devskyy_mcp.py
  - SuperAgents by scanning agent_sdk/super_agents/*.py files
  - Legacy agents by scanning agents/*.py files (optional)
- `count_active_agents_sync()` - Synchronous version for non-async contexts
- Ralph-Wiggums integration: 2 retries, 0.5-2s backoff, fallback to safe defaults

**Fallback Defaults** (if counting fails):
```python
{"mcp_tools": 21, "super_agents": 6, "legacy_agents": 15, "total": 27, "active": 27}
```

### 2. Modified: `main_enterprise.py`
**Line 57**: Added import
```python
from orchestration.agent_counter import count_active_agents
```

**Lines 613-657**: Updated health_check() function
- Removed: Hardcoded `"total": 54, "active": 54`
- Added: `agent_counts = await count_active_agents()`
- Added: `**agent_counts` spread operator to merge dynamic counts

**New Response Structure**:
```json
{
  "agents": {
    "mcp_tools": 21,
    "super_agents": 6,
    "legacy_agents": 14,
    "total": 27,
    "active": 27,
    "categories": [...]
  }
}
```

### 3. Modified: `tests/test_new_api_endpoints.py`
**Lines 300-321**: Updated test_health() function

**Changed From**:
```python
assert data["agents"]["total"] == 54  # Hardcoded assertion
```

**Changed To**:
```python
# Flexible assertions that verify structure and reasonable values
assert "mcp_tools" in agents
assert "super_agents" in agents
assert agents["total"] >= 20
assert agents["mcp_tools"] >= 15
assert agents["super_agents"] >= 6
```

## Actual Counts (as of 2026-01-07)

**MCP Tools**: 21
- devskyy_scan_code
- devskyy_fix_code
- devskyy_self_healing
- devskyy_generate_wordpress_theme
- devskyy_ml_prediction
- devskyy_manage_products
- devskyy_dynamic_pricing
- devskyy_generate_3d_from_description
- devskyy_generate_3d_from_image
- devskyy_virtual_tryon
- devskyy_batch_virtual_tryon
- devskyy_generate_ai_model
- devskyy_virtual_tryon_status
- devskyy_marketing_campaign
- devskyy_multi_agent_workflow
- devskyy_system_monitoring
- devskyy_train_lora_from_products
- devskyy_lora_dataset_preview
- devskyy_lora_version_info
- devskyy_lora_product_history
- devskyy_list_agents

**SuperAgents**: 6
- analytics_agent.py
- commerce_agent.py
- creative_agent.py
- marketing_agent.py
- operations_agent.py
- support_agent.py

**Legacy Agents**: 14 (in agents/ directory, not counted in total)

**Total**: 27 (21 + 6)

## Benefits

1. **Accurate Monitoring**: Health endpoint now reflects actual system capacity
2. **Self-Documenting**: New fields (mcp_tools, super_agents) show system architecture
3. **Resilient**: Ralph-Wiggums error handling prevents counting failures
4. **Future-Proof**: Adding new agents automatically updates count
5. **No Manual Updates**: Developers don't need to remember to update hardcoded values

## Testing

```bash
# Test health endpoint
curl http://localhost:8000/health | python3 -m json.tool

# Expected output:
# {
#   "agents": {
#     "mcp_tools": 21,
#     "super_agents": 6,
#     "legacy_agents": 14,
#     "total": 27,
#     "active": 27
#   }
# }

# Run test suite
pytest tests/test_new_api_endpoints.py::test_health -v
```

## Historical Context

**Old Architecture**: 54+ specialized agents
**New Architecture**: 6 SuperAgents + 21 MCP tools
**Consolidation**: According to `adk/super_agents.py`, the system consolidated 54+ specialized agents into 6 SuperAgents for reduced complexity

**Why "54" Existed**:
- Original comment in code: "Architecture: 6 Super Agents replacing 54+ specialized agents"
- Health endpoint was never updated after consolidation
- Tests were written against the hardcoded value

## Related Changes

The following documentation also needed updating (future work):
- `devskyy_mcp.py:3` - Header says "54 specialized AI agents"
- Various README files may reference "54 agents"

---
*Fix Date: 2026-01-07*
*Old Value: 54 (hardcoded)*
*New Value: 27 (21 + 6, dynamically counted)*
*Resilience: Ralph-Wiggums error handling with fallback*
