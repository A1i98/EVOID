---
title: 'AI Agent Integration'
description: 'Build AI agents that discover and invoke EVOID Intents.'
---

# AI Agent Integration

Build AI agents that discover, understand, and invoke EVOID Intents.

## The Idea

EVOID Intents are structured data. AI agents can:

1. **Discover** — List all available Intents via `export_schemas()`
2. **Understand** — Read descriptions, parameters, and return types
3. **Invoke** — Execute Intents with metadata

## MCP Server

Create an MCP server that exposes Intents as tools:

```python
from evoid import Intent, Level, register
from evoid.adapters.mcp import create_mcp_server, list_tools, handle_tool_call

# Register Intents
register(Intent(
    name="get_user",
    level=Level.STANDARD,
    metadata={
        "user_id": 0,
        "description": "Get a user by their unique ID",
        "mcp_visible": True,
    },
))

register(Intent(
    name="create_order",
    level=Level.CRITICAL,
    metadata={
        "product_id": 0,
        "quantity": 1,
        "description": "Create a new order",
        "mcp_visible": True,
    },
))

# Create MCP server
server = create_mcp_server(name="my-api")

# List available tools
tools = list_tools(server)
# [{"name": "get_user", "description": "Get a user by ID", "inputSchema": {...}}, ...]

# Handle a tool call from AI agent
result = await handle_tool_call(server, "get_user", {"user_id": 42})
# {"id": 42, "name": "Alice"}
```

## Visibility Control

Only Intents with `mcp_visible=True` are exposed:

```python
# Visible to AI
Intent(name="get_user", metadata={"mcp_visible": True})

# Hidden (default)
Intent(name="internal_hook", metadata={})
```

## Schema Export

Export schemas for custom AI integrations:

```python
from evoid import export_schemas, export_json_schemas

# Python objects
schemas = export_schemas()
# {"get_user": IntentSchema(name="get_user", level="standard", ...)}

# JSON Schema (for OpenAPI, MCP, etc.)
json_schemas = export_json_schemas()
# {"get_user": {"type": "object", "title": "get_user", ...}}
```

## Native IOP Style

```python
from evoid.native import create_service, on
from evoid import Intent, Level
from evoid.adapters.mcp import create_mcp_server, handle_tool_call

app = create_service("ai-api")

GET_USER = Intent(
    name="get_user",
    level=Level.STANDARD,
    metadata={
        "user_id": 0,
        "description": "Get a user by ID",
        "mcp_visible": True,
    },
)

async def handle_get_user(intent: Intent) -> dict:
    user_id = intent.metadata.get("user_id")
    return {"id": user_id, "name": "Alice"}

on(app, GET_USER, handle_get_user)

# Create MCP server
server = create_mcp_server("ai-api")

# AI agent calls: handle_tool_call(server, "get_user", {"user_id": 42})
```

## How It Works

```
AI Agent
   |
   | 1. list_tools(server) → discovers Intents
   | 2. Reads schema → understands parameters
   | 3. handle_tool_call(server, name, args) → invokes Intent
   |
   v
MCP Server
   |
   | 1. Looks up Intent by name
   | 2. Builds Intent with metadata from arguments
   | 3. Calls runtime.execute(intent)
   |
   v
EVOID Runtime
   |
   | 1. Resolves pipeline
   | 2. Executes processors
   | 3. Returns Result
   |
   v
Result → AI Agent
```

## Use Cases

| Scenario | How |
|----------|-----|
| Chatbot with database access | Expose `get_user`, `search_products` as MCP tools |
| AI-powered API | Export schemas, let AI generate requests |
| Automated testing | AI agent invokes Intents and verifies results |
| Self-documenting API | Schema export generates OpenAPI docs |

## Related

- [Schema Export](../learn/schema-export.md) — Export Intent schemas
- [Plugin Hooks](../learn/plugin-hooks.md) — Lifecycle events
- [Configuration](../learn/configuration.md) — Configure your service
