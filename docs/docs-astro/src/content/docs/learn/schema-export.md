---
title: 'Intent Schema Export'
description: 'Export Intent definitions as machine-readable schemas for AI agents and plugins.'
---

# Intent Schema Export

Export Intent definitions as machine-readable schemas. AI agents can discover, understand, and invoke Intents programmatically.

## Basic Usage

```python
from evoid import export_schemas, export_json_schema

# Export all schemas
schemas = export_schemas()

# Export single schema
schema = export_json_schema("get_user")
```

## What Gets Exported

Each Intent produces an `IntentSchema`:

```python
@dataclass(frozen=True)
class IntentSchema:
    name: str                    # "get_user"
    level: str                   # "standard"
    description: str             # "Get a user by ID"
    metadata_fields: tuple       # FieldSchema objects
    return_schema: dict          # JSON Schema for return type
    pipeline: tuple[str, ...]    # ["validate", "authorize"]
    timeout: float | None        # 10.0
    priority: int                # 0
```

## Adding Descriptions

Add `description` to Intent metadata:

```python
from evoid import Intent, Level, register

GET_USER = Intent(
    name="get_user",
    level=Level.STANDARD,
    metadata={
        "user_id": 0,
        "description": "Get a user by their unique ID",
        "mcp_visible": True,
    },
)

register(GET_USER)
```

## JSON Schema Format

The exported JSON Schema is compatible with OpenAPI and MCP:

```json
{
  "type": "object",
  "title": "get_user",
  "description": "Get a user by their unique ID",
  "properties": {
    "name": {"type": "string", "const": "get_user"},
    "level": {"type": "string", "enum": ["ephemeral", "standard", "critical"]},
    "metadata": {
      "type": "object",
      "properties": {
        "user_id": {"type": "integer", "default": 0}
      },
      "required": ["user_id"]
    }
  },
  "_evoid": {
    "pipeline": ["validate", "authorize"],
    "timeout": 10.0,
    "priority": 0
  }
}
```

## Native IOP Style

In native IOP, schema export is explicit:

```python
from evoid.native import create_service, on
from evoid import Intent, Level, export_schemas

app = create_service("api")

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

# Export schemas for AI agents
schemas = export_schemas()
# {"get_user": IntentSchema(...)}
```

## Visibility Control

Only Intents with `mcp_visible=True` are exposed to AI agents:

```python
# Visible to AI agents
Intent(name="get_user", metadata={"mcp_visible": True})

# Hidden from AI agents (default)
Intent(name="internal_hook", metadata={})
```

## Use Cases

| Use Case | How |
|----------|-----|
| AI agent discovers available Intents | `export_schemas()` |
| AI agent understands what each Intent does | Read `description` and `metadata_fields` |
| AI agent invokes an Intent | Call `execute(intent)` with metadata |
| Plugin generates API docs | Convert `export_json_schemas()` to OpenAPI |
| Plugin validates AI agent requests | Check against `metadata_fields` schema |

## Related

- [MCP Adapter](../tutorial/ai-agent.md) — AI agent interface
- [Plugin Hooks](plugin-hooks.md) — Lifecycle events
- [Intent](intent.md) — Intent structure
