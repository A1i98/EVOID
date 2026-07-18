---
title: 'AI Analytics'
description: 'AI agents discover and invoke your Intents. MCP integration for intelligent operations.'
---

# AI Analytics

AI agents discover and invoke your Intents. MCP integration for intelligent operations.

## The Vision

Sandy wants AI to help manage inventory: "What's running low? What should we reorder?"

## Schema Export

EVOID exports Intent schemas — AI agents can read and understand them:

```python
from evoid import export_json_schemas

schemas = export_json_schemas()
# AI agent sees:
# {
#   "get_inventory": {"type": "object", "description": "Check inventory levels"},
#   "place_order": {"type": "object", "description": "Order supplies"},
#   "analyze_sales": {"type": "object", "description": "Analyze sales patterns"}
# }
```

## MCP Server

Create an MCP server that exposes Intents as tools:

```python
from evoid.adapters.mcp import create_mcp_server, list_tools, handle_tool_call
from evoid import Intent, Level, register

# Register Intents with descriptions
register(Intent(
    name="get_inventory",
    level=Level.STANDARD,
    metadata={
        "description": "Check inventory levels across all locations",
        "location": "",
        "mcp_visible": True,
    },
))

register(Intent(
    name="reorder_supply",
    level=Level.CRITICAL,
    metadata={
        "description": "Place a supply order for a specific item",
        "item": "",
        "quantity": 0,
        "mcp_visible": True,
    },
))

# Create MCP server
server = create_mcp_server("sandy-analytics")

# AI agent discovers tools
tools = list_tools(server)
# [{"name": "get_inventory", "description": "Check inventory levels..."}, ...]

# AI agent invokes a tool
result = await handle_tool_call(server, "get_inventory", {"location": "downtown"})
```

## Visibility Control

Only Intents with `mcp_visible=True` are exposed:

```python
# Visible to AI
Intent(name="get_inventory", metadata={"mcp_visible": True})

# Hidden (default)
Intent(name="internal_hook", metadata={})
```

## AI Agent Flow

```
AI Agent
   ↓
1. list_tools(server) → discovers Intents
2. Reads schema → understands parameters
3. handle_tool_call(server, name, args) → invokes Intent
   ↓
MCP Server
   ↓
1. Looks up Intent by name
2. Builds Intent with metadata
3. Calls runtime.execute(intent)
   ↓
EVOID Runtime
   ↓
1. Resolves pipeline
2. Executes processors
3. Returns Result
   ↓
Result → AI Agent
```

## Use Cases

| Scenario | How |
|----------|-----|
| Smart inventory | AI checks stock, suggests reorders |
| Sales analysis | AI queries orders, finds patterns |
| Customer service | AI answers "where's my order?" |
| Predictive maintenance | AI monitors equipment health |

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Schema export | JSON Schema from Intents |
| MCP server | Expose Intents as AI tools |
| Visibility control | `mcp_visible` flag |
| AI agent flow | Discover → Understand → Invoke |

## Next: Parallel Orders

Let's process orders in parallel — [Parallel Orders](parallel-orders.md).
