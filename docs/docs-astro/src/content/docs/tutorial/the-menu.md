---
title: 'The Menu'
description: 'Multiple Intents, pipeline composition, and levels — Sandy builds a proper menu system.'
---

# The Menu

Multiple Intents, pipeline composition, and levels — Sandy builds a proper menu system.

Sandy's shop is growing. She needs a menu system that handles browsing, adding items, and searching.

## Defining the Menu

```python
from evoid import Intent, Level, register, register_processor
from evoid.core import Context

# Menu data — just a dict, no classes needed
MENU = [
    {"id": 1, "name": "BLT", "price": 8.99, "category": "classic"},
    {"id": 2, "name": "Club", "price": 9.99, "category": "classic"},
    {"id": 3, "name": "Veggie", "price": 7.99, "category": "healthy"},
    {"id": 4, "name": "Reuben", "price": 10.99, "category": "premium"},
    {"id": 5, "name": "Philly", "price": 11.99, "category": "premium"},
]

# Intents
VIEW_MENU = Intent(
    name="view_menu",
    level=Level.EPHEMERAL,  # Fast, cacheable
)

SEARCH_MENU = Intent(
    name="search_menu",
    level=Level.EPHEMERAL,
)

ADD_ITEM = Intent(
    name="add_item",
    level=Level.STANDARD,  # Needs persistence
)

# Processors
async def handle_view_menu(intent: Intent) -> dict:
    return {"menu": MENU}

async def handle_search(intent: Intent) -> dict:
    query = intent.metadata.get("query", "").lower()
    results = [item for item in MENU if query in item["name"].lower()]
    return {"results": results, "count": len(results)}

async def handle_add_item(intent: Intent) -> dict:
    name = intent.metadata.get("name")
    price = intent.metadata.get("price", 0.0)
    category = intent.metadata.get("category", "custom")
    new_item = {"id": len(MENU) + 1, "name": name, "price": price, "category": category}
    MENU.append(new_item)
    return {"status": "added", "item": new_item}

# Register
register(VIEW_MENU)
register(SEARCH_MENU)
register(ADD_ITEM)

register_processor("view_menu", handle_view_menu)
register_processor("search_menu", handle_search)
register_processor("add_item", handle_add_item)
```

## Pipeline Composition

Each Intent gets a pipeline. The default pipeline depends on the level:

```python
from evoid.core.resolve import resolve_pipeline

# See what pipeline each intent gets
config = resolve_pipeline(VIEW_MENU)
print(config.processors)  # ("validate",) — ephemeral gets fast path

config = resolve_pipeline(ADD_ITEM)
print(config.processors)  # ("validate", "authorize") — standard gets auth
```

## Adding Custom Processors

Sandy wants logging on every menu action:

```python
async def log_action(intent: Intent, ctx: Context) -> dict:
    """Log every intent execution."""
    action = intent.name
    print(f"[LOG] Action: {action}")
    ctx.state["logged"] = True
    return {"logged": True}

register_processor("log_action", log_action)
```

Wire it to specific intents using the extend system:

```python
from evoid.core.extend import before, after

# Add logging BEFORE every menu action
before("view_menu", "log_action")
before("search_menu", "log_action")
before("add_item", "log_action")
```

Now every menu action runs: `log_action` → `validate` → `handler`.

## Levels in Action

Watch how the same action behaves differently with different levels:

```python
# EPHEMERAL — fast, no auth, 5s timeout
SEARCH = Intent(name="search_menu", level=Level.EPHEMERAL)

# STANDARD — balanced, auth check, 10s timeout
ADD = Intent(name="add_item", level=Level.STANDARD)

# CRITICAL — full protection, audit, 30s timeout
DELETE = Intent(name="delete_item", level=Level.CRITICAL)
```

The level determines:
- Which processors run by default
- How long the pipeline can take
- Whether auditing and protection are enabled

## Error Handling

When a processor fails, the pipeline stops:

```python
async def handle_add_item(intent: Intent) -> dict:
    name = intent.metadata.get("name")
    if not name:
        raise ValueError("Item name is required")
    price = intent.metadata.get("price", 0)
    if price <= 0:
        raise ValueError("Price must be positive")
    # ... add item
    return {"status": "added"}
```

```python
result = await execute(ADD_ITEM, name="", price=5)
# result.success = False
# result.error = ValueError("Item name is required")
# result.processors = ("validate",) — only ran until failure
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Multiple Intents | Each Intent is independent, gets its own pipeline |
| Pipeline composition | Processors chain together, share Context |
| Levels | Determine default pipeline, timeout, infrastructure |
| Extend system | `before()` / `after()` inject processors without changing code |
| Error handling | Pipeline stops on exception, Result captures failure |

## Next: Taking Orders

Let's build a CLI so Sandy can take orders from the command line — [Taking Orders](taking-orders.md).
