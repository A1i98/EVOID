---
title: 'Context'
description: 'The data bag processors share. Read it, write it, pass it along.'
---

# Context

Every processor receives one argument: a `Context`. It's a mutable data bag — no methods, no logic, just fields.

```python
from evoid.core import Context

async def my_processor(ctx: Context) -> dict:
    # Read intent metadata
    name = ctx.intent.metadata.get("name")

    # Read/write shared state
    ctx.state["step"] = "done"

    # Access injected deps
    db = ctx.deps.get("db")

    return {"ok": True}
```

## Fields

| Field | Type | What it is |
|-------|------|------------|
| `ctx.intent` | `Intent` | The intent that triggered this pipeline. Immutable. |
| `ctx.state` | `dict` | Shared state between processors. Read/write. |
| `ctx.deps` | `dict` | Injected dependencies (db, cache, etc). Set by adapters/plugins. |
| `ctx.metadata` | `dict` | Copy of intent metadata. Writable without touching the intent. |
| `ctx.errors` | `list` | Accumulated errors. Processors can append, never clear. |
| `ctx.id` | `str` | Auto-generated unique ID for this execution. |

## Data Flow

Processors communicate through `ctx.state`. One writes, the next reads:

```python
async def check_inventory(ctx: Context) -> dict:
    sandwich = ctx.intent.metadata.get("sandwich")
    ctx.state["in_stock"] = sandwich in ["BLT", "Club", "Veggie"]
    return {"checked": True}

async def create_order(ctx: Context) -> dict:
    if not ctx.state.get("in_stock"):
        return {"error": "Out of stock"}
    return {"status": "created"}
```

Think of it as a conveyor belt. Each station reads what the previous one wrote.

## `ctx.deps` vs `ctx.state`

- **`state`**: Your working memory. Changes every request. Processor-to-processor.
- **`deps`**: Your tools. Set once by the adapter or plugin. Database connections, caches, config. Processors read but don't rewrite.

```python
# Adapter sets deps (once, at startup)
ctx.deps["db"] = sqlite3.connect("shop.db")
ctx.deps["cache"] = redis_client

# Processors use deps (every request)
async def get_menu(ctx: Context) -> dict:
    cache = ctx.deps.get("cache")
    cached = cache.get("menu") if cache else None
    if cached:
        return json.loads(cached)
    # ... fetch from db
```

## `fork()`

Create a child context for parallel execution. Same intent, copy of state and deps:

```python
from evoid.core import fork

async def parallel_work(ctx: Context) -> dict:
    child = fork(ctx)
    child.state["branch"] = "left"
    # ctx.state is unchanged — child has its own copy
```

## Why Not Just Use kwargs?

Because processors are pure functions. They take one thing in, one thing out. Context is that one thing. No magic signatures, no argument ordering guessing — just `ctx`.
