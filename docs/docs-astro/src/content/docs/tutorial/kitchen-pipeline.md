---
title: 'Kitchen Pipeline'
description: 'The full order workflow — receive, prepare, package, serve. Pipeline extensions in action.'
---

# Kitchen Pipeline

The full order workflow — receive, prepare, package, serve. Pipeline extensions in action.

Sandy's kitchen has a workflow: receive order → check ingredients → prepare → package → serve. Let's model this as a pipeline.

!!! info "Pipeline = recipe"
    A pipeline is like a recipe card. Each step is a processor — one job, one responsibility. The pipeline runs them in order. You can insert steps, remove steps, or swap the entire recipe without touching the kitchen code.

## The Kitchen Flow

```python
from evoid import Intent, Level, register, register_processor
from evoid.core import Context
from evoid.core.extend import add_intent_with_pipeline

ORDER = Intent(name="order", level=Level.STANDARD)

# Each step is a processor — one responsibility, pure function
async def receive(intent: Intent, ctx: Context) -> dict:
    """Step 1: Receive and validate the order."""
    sandwich = intent.metadata.get("sandwich")
    qty = intent.metadata.get("qty", 1)
    if not sandwich:
        return {"error": "No sandwich specified"}
    ctx.state["sandwich"] = sandwich
    ctx.state["qty"] = qty
    ctx.state["step"] = "received"
    return {"received": True}

async def check_ingredients(intent: Intent, ctx: Context) -> dict:
    """Step 2: Verify we have ingredients."""
    sandwich = ctx.state["sandwich"]
    # Simplified inventory check
    inventory = {"BLT": 10, "Club": 5, "Veggie": 8}
    available = inventory.get(sandwich, 0)
    if available <= 0:
        return {"error": f"No {sandwich} ingredients left"}
    ctx.state["step"] = "ingredients_checked"
    return {"ingredients_available": True}

async def prepare(intent: Intent, ctx: Context) -> dict:
    """Step 3: Prepare the sandwich."""
    sandwich = ctx.state["sandwich"]
    ctx.state["step"] = "preparing"
    # In real app: track preparation time, assign chef
    return {"preparing": sandwich}

async def package(intent: Intent, ctx: Context) -> dict:
    """Step 4: Package for serving."""
    sandwich = ctx.state["sandwich"]
    qty = ctx.state["qty"]
    ctx.state["step"] = "packaged"
    return {"packaged": True, "items": qty}

async def serve(intent: Intent, ctx: Context) -> dict:
    """Step 5: Mark as ready for pickup."""
    sandwich = ctx.state["sandwich"]
    qty = ctx.state["qty"]
    return {
        "status": "ready",
        "sandwich": sandwich,
        "quantity": qty,
        "steps_completed": ctx.state.get("step", "unknown"),
    }

# Wire the full pipeline
register(ORDER)
register_processor("receive", receive)
register_processor("check_ingredients", check_ingredients)
register_processor("prepare", prepare)
register_processor("package", package)
register_processor("serve", serve)

add_intent_with_pipeline(
    ORDER,
    processors=["receive", "check_ingredients", "prepare", "package", "serve"],
    handler=serve,
)
```

## Running the Pipeline

```python
import asyncio
from evoid import execute

async def main():
    result = await execute(ORDER, sandwich="BLT", qty=2)

    if result.success:
        print(f"Order ready: {result.value}")
        print(f"Took {result.duration:.3f}s")
        print(f"Steps: {len(result.processors)}")
    else:
        print(f"Failed: {result.error}")
        print(f"Stopped at step {len(result.processors)}")

asyncio.run(main())
```

```
Order ready: {'status': 'ready', 'sandwich': 'BLT', 'quantity': 2}
Took 0.002s
Steps: 5
```

## Pipeline Extensions

Sandy wants logging and timing without changing the kitchen code:

```python
from evoid import register_processor
from evoid.core.extend import before, after

# Add timing
async def timing(intent: Intent, ctx: Context) -> dict:
    import time
    ctx.state["start_time"] = time.monotonic()
    return {"timed": True}

async def report_timing(intent: Intent, ctx: Context) -> dict:
    import time
    start = ctx.state.get("start_time", 0)
    elapsed = time.monotonic() - start
    print(f"[TIMER] Order took {elapsed:.3f}s")
    return {"elapsed": elapsed}

register_processor("timing", timing)
register_processor("report_timing", report_timing)

# Inject at the start and end
before("order", "timing")
after("order", "report_timing")
```

Now the pipeline is: `timing` → `receive` → `check_ingredients` → `prepare` → `package` → `serve` → `report_timing`

## Modifying the Pipeline

### Insert Before a Specific Step

```python
from evoid.core.extend import before_processor

async def allergy_check(intent: Intent, ctx: Context) -> dict:
    """Check for allergies before preparation."""
    sandwich = ctx.state["sandwich"]
    # In real app: check customer allergy profile
    ctx.state["allergy_safe"] = True
    return {"allergy_checked": True}

register_processor("allergy_check", allergy_check)

# Insert right before "prepare"
before_processor("order", "prepare", "allergy_check")
```

Pipeline: `timing` → `receive` → `check_ingredients` → `allergy_check` → `prepare` → `package` → `serve` → `report_timing`

### Replace the Entire Pipeline

```python
from evoid.core.extend import replace_pipeline

# For express orders — skip some steps
replace_pipeline("order", ["receive", "package", "serve"])
```

### Remove a Step

```python
from evoid.core.extend import remove_processor

# Remove timing in production
remove_processor("order", "timing")
remove_processor("order", "report_timing")
```

## Inspecting the Pipeline

See what processors will run for any Intent:

```python
from evoid.core.extend import get_pipeline_config, list_overrides

config = get_pipeline_config(ORDER)
print(config.processors)
# ('receive', 'check_ingredients', 'allergy_check', 'prepare', 'package', 'serve')

overrides = list_overrides()
print(overrides)
# {'order': ['timing', 'receive', 'check_ingredients', ...]}
```

## Where Plugins Fit

Sandy's pipeline is pure IOP — no plugins yet. But the moment she installs one, the pipeline expands:

```python
# Before: Sandy's manual pipeline
# receive → check_ingredients → prepare → package → serve

# After installing evoid-auth:
# validate → authorize → receive → check_ingredients → prepare → package → serve
# The auth plugin added two steps automatically based on the Intent level.

# After installing evoid-sqlite:
# validate → authorize → receive → check_ingredients → store_order → prepare → package → serve
# Sandy added store_order as a processor, and the storage plugin handles persistence.
```

!!! example "Pipeline with plugins"
    ```python
    from evoid import Intent, Level
    
    # This Intent is STANDARD — auth plugin activates
    ORDER = Intent(name="order", level=Level.STANDARD)
    # Pipeline: validate → authorize → receive → check_ingredients → ...
    
    # This Intent is CRITICAL — full plugin activation
    PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)
    # Pipeline: validate → authorize → audit → protect → handler
    
    # Sandy didn't write auth code. She didn't write audit code.
    # She just chose the level. The plugins did the rest.
    ```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Pipeline composition | Chain processors for multi-step workflows |
| `before()` / `after()` | Inject at start/end without changing code |
| `before_processor()` / `after_processor()` | Insert relative to specific steps |
| `replace_pipeline()` | Swap the entire chain |
| `remove_processor()` | Drop a step |
| `get_pipeline_config()` | Inspect final pipeline |
| `list_overrides()` | See all modifications |

## Next: Growing Pains

Sandy's shop is booming. The CLI isn't enough — she needs a website. Let's see what breaks and how to fix it — [Growing Pains](growing-pains.md).
