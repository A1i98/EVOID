---
title: 'Pipeline Inspection & Variable Routing'
description: 'See what happens inside the pipeline and route variables through specific processors.'
---

# Pipeline Inspection & Variable Routing

See inside the pipeline and control how variables flow through it.

## Pipeline Reporting

Enable inspection to capture per-processor details:

```python
from evoid.core.runtime import execute, Config

result = await execute(intent, config=Config(inspect=True))

# See which processors ran and how long each took
for step in result.steps:
    print(f"{step.name}: {step.duration:.3f}s {'OK' if step.success else 'FAIL'}")
```

### Per-processor state snapshots

When `inspect=True`, each step captures input and output state:

```python
for step in result.steps:
    # What state looked like BEFORE this processor
    print(f"  input:  {step.input_state}")
    # What state looked like AFTER this processor
    print(f"  output: {step.output_state}")
```

### Track a specific variable

Follow a variable through the pipeline:

```python
result = await execute(intent, config=Config(inspect=True))

for step in result.steps:
    if "user_id" in step.output_state:
        before = step.input_state.get("user_id", "N/A")
        after = step.output_state["user_id"]
        print(f"{step.name}: user_id {before} → {after}")
```

## Variable Routing

Route specific variables through specific processors at specific points.

### Basic routing

```python
from evoid.core.extend import route_variable

# For intent "GET:/users/{id}", route "user_id" through "enrich_user" before "authorize"
route_variable(
    intent_name="GET:/users/{id}",
    variable="user_id",
    through="enrich_user",
    before="authorize",
)
```

### How it works

1. You define a routing rule
2. Before execution, the rule modifies the pipeline
3. The specified processor runs at the specified point
4. The processor receives the variable via `ctx.metadata`

### Example: enrich user data

```python
from evoid.core.extend import route_variable
from evoid import Context

# Define the enricher processor
async def enrich_user(ctx: Context) -> dict:
    user_id = ctx.metadata.get("user_id")
    # Fetch full user data from database
    user = await db.get_user(user_id)
    ctx.state["enriched_user"] = user
    return {"enriched": True}

# Route user_id through enrich_user before authorize
route_variable("GET:/users/{id}", "user_id", "enrich_user", before="authorize")

# Now the pipeline becomes:
# [validate, enrich_user, authorize, handler]
# enrich_user receives user_id from ctx.metadata
# authorize can use ctx.state["enriched_user"]
```

### Multiple routing rules

```python
route_variable("GET:/users/{id}", "user_id", "enrich_user", before="authorize")
route_variable("GET:/users/{id}", "user_id", "check_permissions", before="handler")

# Pipeline becomes:
# [validate, enrich_user, check_permissions, authorize, handler]
```

## Native IOP Style

```python
from evoid.native import create_service, on
from evoid import Intent, Level, Context
from evoid.core.extend import route_variable

app = create_service("api")

# Define processors
async def enrich_user(ctx: Context) -> dict:
    user_id = ctx.metadata.get("user_id")
    ctx.state["user"] = await db.get_user(user_id)
    return {"enriched": True}

async def check_permissions(ctx: Context) -> dict:
    user = ctx.state.get("user")
    if not user or not user.has_permission("read"):
        raise PermissionError("No access")
    return {"authorized": True}

# Register processors
register_processor("enrich_user", enrich_user)
register_processor("check_permissions", check_permissions)

# Route variables
route_variable("GET:/users/{id}", "user_id", "enrich_user", before="check_permissions")

# Intent with custom pipeline
GET_USER = Intent(
    name="GET:/users/{id}",
    level=Level.STANDARD,
    metadata={
        "method": "GET",
        "path": "/users/{id}",
        "processors": ("validate", "authorize", "handler"),
    },
)

# Handler — receives enriched data
async def handle_get_user(intent: Intent) -> dict:
    user = intent.state.get("user")
    return {"id": user.id, "name": user.name}

on(app, GET_USER, handle_get_user)
```

## Summary

| Feature | What it does |
|---------|-------------|
| `Config(inspect=True)` | Capture per-processor state snapshots |
| `result.steps` | See each processor's input/output/duration |
| `route_variable()` | Route a variable through a processor at a specific point |
| `before=` | Insert processor before target |
| `after=` | Insert processor after target (default) |

!!! tip "IOP principle"
    Pipeline inspection and variable routing are just data manipulation. No new concepts — just more visibility into what the pipeline already does.
