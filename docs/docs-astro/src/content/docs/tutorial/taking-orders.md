---
title: 'Taking Orders'
description: 'CLI interface for Sandy — orders from the command line.'
---

# Taking Orders

CLI interface for Sandy — orders from the command line.

Sandy needs to take orders without writing Python code. Let's build a CLI.

## The `evo` CLI

EVOID ships with a CLI called `evo`. Use it to run services and manage your project:

```bash
# Create a new project
evo init sandy-shop
cd sandy-shop

# Create a service
evo service new orders

# Run the service
evo service run orders
```

## Building the Orders Service

Edit `services/orders/main.py`:

```python
from evoid import Intent, Level, register, register_processor
from evoid.core import Context, execute

# Menu data
MENU = [
    {"id": 1, "name": "BLT", "price": 8.99},
    {"id": 2, "name": "Club", "price": 9.99},
    {"id": 3, "name": "Veggie", "price": 7.99},
]

# Intents
ORDER_SANDWICH = Intent(
    name="order_sandwich",
    level=Level.STANDARD,
    metadata={"shop": "Sandy's Sandwiches"},
)

VIEW_MENU = Intent(
    name="view_menu",
    level=Level.EPHEMERAL,
)

# Processors
async def handle_order(intent: Intent, ctx: Context) -> dict:
    sandwich = intent.metadata.get("sandwich", "BLT")
    qty = intent.metadata.get("qty", 1)

    # Find in menu
    item = next((m for m in MENU if m["name"] == sandwich), None)
    if not item:
        return {"error": f"'{sandwich}' not on menu"}

    total = item["price"] * qty
    ctx.state["order_total"] = total

    return {
        "status": "confirmed",
        "sandwich": sandwich,
        "quantity": qty,
        "price_each": item["price"],
        "total": total,
    }

async def handle_menu(intent: Intent) -> dict:
    return {"menu": MENU}

# Register
register(ORDER_SANDWICH)
register(VIEW_MENU)
register_processor("order_sandwich", handle_order)
register_processor("view_menu", handle_menu)
```

## Running as a Service

```bash
evo service run orders
```

The service starts and listens for Intents. Other services or adapters can send Intents to it.

## Direct Execution

For testing, execute Intents directly in Python:

```python
import asyncio
from evoid import execute

async def test():
    # View menu
    result = await execute(VIEW_MENU)
    print(result.value)
    # {'menu': [{'id': 1, 'name': 'BLT', 'price': 8.99}, ...]}

    # Place an order
    result = await execute(ORDER_SANDWICH, sandwich="BLT", qty=2)
    print(result.value)
    # {'status': 'confirmed', 'sandwich': 'BLT', 'quantity': 2, 'price_each': 8.99, 'total': 17.98}

    # Check timing
    print(f"Completed in {result.duration:.4f}s")
    print(f"Processors: {result.processors}")

asyncio.run(test())
```

## Pipeline with Timeout

Add a timeout to prevent slow orders:

```python
ORDER_SANDWICH = Intent(
    name="order_sandwich",
    level=Level.STANDARD,
    timeout=5.0,  # 5 second max
)
```

If the processor takes longer, the pipeline returns a failed Result with `TimeoutError`.

## Adding a Processor Chain

Sandy wants inventory checking before order confirmation:

```python
from evoid import register_processor

async def check_inventory(intent: Intent, ctx: Context) -> dict:
    """Verify sandwich is available."""
    sandwich = intent.metadata.get("sandwich", "BLT")
    # Simplified — in real app, check database
    available = sandwich in ["BLT", "Club", "Veggie"]
    ctx.state["available"] = available
    if not available:
        return {"error": f"'{sandwich}' unavailable"}
    return {"checked": True}

async def handle_order(intent: Intent, ctx: Context) -> dict:
    if not ctx.state.get("available", False):
        return {"error": "Item unavailable"}
    # ... process order
    return {"status": "confirmed"}

register_processor("check_inventory", check_inventory)
register_processor("order_sandwich", handle_order)
```

Wire them into a pipeline:

```python
from evoid.core.extend import add_intent_with_pipeline

add_intent_with_pipeline(
    ORDER_SANDWICH,
    processors=["check_inventory", "order_sandwich"],
    handler=handle_order,
)
```

Now the pipeline runs: `check_inventory` → `order_sandwich`.

## What You Learned

| Concept | What It Is |
|---------|-----------|
| `evo` CLI | Project management, service creation, running |
| Service model | Group related Intents into a runnable service |
| `execute()` | Run Intents directly with keyword arguments |
| Timeout | Limit pipeline execution time |
| `add_intent_with_pipeline` | Custom processor chain for an Intent |

## Next: Kitchen Pipeline

Let's build the full kitchen workflow — [Kitchen Pipeline](kitchen-pipeline.md).
