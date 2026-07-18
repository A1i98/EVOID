---
title: 'Your First Intent'
description: 'Build a sandwich order system in 5 minutes. One file, one Intent, one processor.'
---

# Your First Intent

Build a sandwich order system in 5 minutes. One file, one Intent, one processor.

Sandy runs a small sandwich shop. Paper orders get lost. Let's fix that with a simple EVOID program.

## The Smallest Possible EVOID Program

```python
import asyncio
from evoid import Intent, Level, execute, register_processor
from evoid.core import Context

# 1. Define what you want
ORDER_SANDWICH = Intent(
    name="order_sandwich",
    level=Level.STANDARD,
    metadata={"shop": "Sandy's Sandwiches"},
)

# 2. Define how to do it
async def handle_order(intent: Intent) -> dict:
    sandwich = intent.metadata.get("sandwich", "unknown")
    qty = intent.metadata.get("qty", 1)
    return {
        "status": "confirmed",
        "order": sandwich,
        "quantity": qty,
        "total": qty * 8.99,
    }

# 3. Wire it together
register_processor("order_sandwich", handle_order)

# 4. Execute
async def main():
    result = await execute(ORDER_SANDWICH)
    print(result.value)

asyncio.run(main())
```

```bash
python main.py
# {'status': 'confirmed', 'order': 'BLT', 'quantity': 2, 'total': 17.98}
```

That's IOP. Three lines of setup, one line of execution.

## What Just Happened?

```
ORDER_SANDWICH (Intent — what you want)
       ↓
execute() (Runtime — builds pipeline, runs processors)
       ↓
handle_order (Processor — how to do it)
       ↓
Result (Data — what you got)
```

**Intent** = data that declares purpose. It carries a name, a level, and metadata.
**Processor** = a function that does the work. Takes an Intent, returns a result.
**Pipeline** = the chain of processors. Here it's just one step: `handle_order`.
**Result** = the output. Success or failure, with timing.

## Adding a Level

Sandy's BLT is popular but takes longer. Mark it as `critical` so the system allocates more time:

```python
ORDER_SANDWICH = Intent(
    name="order_sandwich",
    level=Level.CRITICAL,  # More time, full audit
    metadata={"shop": "Sandy's Sandwiches"},
)
```

Three levels, three behaviors:

| Level | Pipeline | Timeout | Use Case |
|-------|----------|---------|----------|
| `ephemeral` | `validate` | 5s | Cache, temp data |
| `standard` | `validate`, `authorize` | 10s | Normal orders |
| `critical` | `validate`, `authorize`, `audit`, `protect` | 30s | Payments, important data |

You choose the level. The runtime handles the infrastructure.

## Adding More Intents

Sandy needs to manage the menu too:

```python
from evoid import Intent, Level, register, register_processor

# Define intents
ORDER_SANDWICH = Intent(
    name="order_sandwich",
    level=Level.STANDARD,
    metadata={"shop": "Sandy's Sandwiches"},
)

VIEW_MENU = Intent(
    name="view_menu",
    level=Level.EPHEMERAL,  # Fast, no persistence needed
    metadata={"shop": "Sandy's Sandwiches"},
)

# Define processors
async def handle_order(intent: Intent) -> dict:
    sandwich = intent.metadata.get("sandwich", "BLT")
    qty = intent.metadata.get("qty", 1)
    return {"status": "confirmed", "order": sandwich, "quantity": qty}

async def handle_menu(intent: Intent) -> dict:
    return {
        "menu": [
            {"name": "BLT", "price": 8.99},
            {"name": "Club", "price": 9.99},
            {"name": "Veggie", "price": 7.99},
        ]
    }

# Register everything
register(ORDER_SANDWICH)
register(VIEW_MENU)
register_processor("order_sandwich", handle_order)
register_processor("view_menu", handle_menu)
```

```python
# Execute any intent by name
result = await execute(ORDER_SANDWICH, sandwich="Club", qty=3)
# {'status': 'confirmed', 'order': 'Club', 'quantity': 3}
```

## Using Context

Processors share data through a `Context` object. One processor writes, the next reads:

```python
from evoid import Intent, Level, execute, register, register_processor
from evoid.core import Context

CHECK_INVENTORY = Intent(name="check_inventory", level=Level.STANDARD)
PREPARE_ORDER = Intent(name="prepare_order", level=Level.STANDARD)

async def check_inventory(intent: Intent, ctx: Context) -> dict:
    """Processor 1: Check if we have ingredients."""
    sandwich = intent.metadata.get("sandwich", "BLT")
    ctx.state["sandwich"] = sandwich
    ctx.state["in_stock"] = True  # Simplified check
    return {"checked": True}

async def prepare_order(intent: Intent, ctx: Context) -> dict:
    """Processor 2: Prepare the sandwich."""
    sandwich = ctx.state.get("sandwich")
    in_stock = ctx.state.get("in_stock", False)
    if not in_stock:
        return {"error": "Out of stock"}
    return {"status": "preparing", "sandwich": sandwich}

register(CHECK_INVENTORY)
register(PREPARE_ORDER)
register_processor("check_inventory", check_inventory)
register_processor("prepare_order", prepare_order)
```

`ctx.state` is shared between processors. `ctx.intent` is the current Intent. `ctx.deps` is for injected dependencies (covered later).

## What You Learned

| Concept | What It Is |
|---------|-----------|
| `Intent` | Data that declares purpose — name, level, metadata |
| `Level` | Infrastructure behavior — ephemeral/standard/critical |
| `Processor` | Pure function that does the work |
| `Pipeline` | Chain of processors executed in order |
| `Context` | Shared state between processors |
| `Result` | Output — success/failure with timing |

## Next: The Menu

Now that Sandy can take orders, let's build a proper menu system with [The Menu](the-menu.md).
