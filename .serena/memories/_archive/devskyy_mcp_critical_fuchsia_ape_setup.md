# DevSkyy MCP - Critical Fuchsia Ape Setup

## Status: ✅ CONFIGURED CORRECTLY

The devskyy_mcp.py server connects to critical-fuchsia-ape FastMCP endpoint.

**Endpoint**: `https://critical-fuchsia-ape.fastmcp.app`
**Authentication**: Bearer token via `CRITICAL_FUCHSIA_APE_KEY`
**Backend Selection**: `MCP_BACKEND=critical-fuchsia-ape`

## Configuration Pattern

### .mcp.json Server Entry

```json
"devskyy-critical-fuchsia-ape": {
  "command": "python",
  "args": ["devskyy_mcp.py"],
  "env": {
    "MCP_BACKEND": "critical-fuchsia-ape",
    "CRITICAL_FUCHSIA_APE_URL": "https://critical-fuchsia-ape.fastmcp.app",
    "CRITICAL_FUCHSIA_APE_KEY": "${CRITICAL_FUCHSIA_APE_KEY}"
  }
}
```

### devskyy_mcp.py Backend Selection

```python
MCP_BACKEND = os.getenv("MCP_BACKEND", "devskyy")

if MCP_BACKEND == "critical-fuchsia-ape":
    # FastMCP hosted endpoint
    API_BASE_URL = os.getenv("CRITICAL_FUCHSIA_APE_URL", "https://critical-fuchsia-ape.fastmcp.app")
    API_KEY = os.getenv("CRITICAL_FUCHSIA_APE_KEY", "")
else:
    # Local DevSkyy backend
    API_BASE_URL = os.getenv("DEVSKYY_API_URL", "http://localhost:8000")
    API_KEY = os.getenv("DEVSKYY_API_KEY", "")
```

## Required Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MCP_BACKEND` | Set to `critical-fuchsia-ape` to use FastMCP | Yes |
| `CRITICAL_FUCHSIA_APE_URL` | FastMCP endpoint URL | Yes |
| `CRITICAL_FUCHSIA_APE_KEY` | API key for authentication | Yes |

## How to Use

### Option 1: Environment Variables

```bash
export MCP_BACKEND=critical-fuchsia-ape
export CRITICAL_FUCHSIA_APE_URL="https://critical-fuchsia-ape.fastmcp.app"
export CRITICAL_FUCHSIA_APE_KEY="your-api-key"
python devskyy_mcp.py
```

### Option 2: Claude Desktop Config

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "devskyy": {
      "command": "python",
      "args": ["/path/to/devskyy_mcp.py"],
      "env": {
        "MCP_BACKEND": "critical-fuchsia-ape",
        "CRITICAL_FUCHSIA_APE_URL": "https://critical-fuchsia-ape.fastmcp.app",
        "CRITICAL_FUCHSIA_APE_KEY": "your-api-key"
      }
    }
  }
}
```

## Available Tools (13)

- `devskyy_scan_code` - Scan code for issues
- `devskyy_fix_code` - Auto-fix code problems
- `devskyy_self_healing` - Self-healing pipeline
- `devskyy_generate_wordpress_theme` - Generate WP themes
- `devskyy_ml_prediction` - ML predictions
- `devskyy_manage_products` - Product management
- `devskyy_dynamic_pricing` - Dynamic pricing
- `devskyy_generate_3d_from_description` - Text-to-3D
- `devskyy_generate_3d_from_image` - Image-to-3D
- `devskyy_marketing_campaign` - Campaign generation
- `devskyy_multi_agent_workflow` - Multi-agent tasks
- `devskyy_system_monitoring` - System monitoring
- `devskyy_list_agents` - List available agents

## Files

- `devskyy_mcp.py` - MCP server with backend selection
- `.mcp.json` - Server configuration with critical-fuchsia-ape entry
- `scripts/setup_critical_fuchsia_ape.sh` - Setup script
