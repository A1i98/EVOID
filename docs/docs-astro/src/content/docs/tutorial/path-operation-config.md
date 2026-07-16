---
title: 'Path Operation Configuration'
description: 'Configure Intent behavior, pipelines, and metadata per route.'
---

# Path Operation Configuration

Configure Intent behavior, pipelines, and metadata per route.

## Intent Levels

Every route creates an Intent with a level. The level determines the default pipeline:

```python
from evoid.web.route import Service, get, post

app = Service("api")

@app.get("/cache-data", level="ephemeral")
async def cache_data() -> dict:
    return {"cached": True}

@app.get("/users/{user_id}", level="standard")
async def get_user(user_id: int) -> dict:
    return {"id": user_id}

@app.post("/payments", level="critical")
async def process_payment(amount: float) -> dict:
    return {"status": "paid", "amount": amount}
```

| Level | Default Pipeline | Timeout |
|-------|-----------------|---------|
| `ephemeral` | `validate` | 5s |
| `standard` | `validate`, `authorize` | 10s |
| `critical` | `validate`, `authorize`, `audit`, `protect` | 30s |

## Custom Pipeline Per Route

Override the default pipeline with `pipeline`:

```python
from evoid.web.route import Service, post

app = Service("api")

@app.post("/payments", pipeline=["validate", "check_fraud", "charge", "audit"])
async def process_payment(amount: float) -> dict:
    return {"status": "paid", "amount": amount}
```

The pipeline runs processors in order — `validate` first, then `check_fraud`, etc.

## @controller Style

Set level at the controller or method level:

```python
from evoid.web.controller import Service, Controller, GET, POST

app = Service("api")

@Controller("/admin", level="critical")
class AdminController:
    @GET("/dashboard")
    async def dashboard(self) -> dict:
        return {"stats": {}}

    @GET("/logs", level="standard")
    async def logs(self) -> dict:
        return {"logs": []}
```

Methods inherit the controller's level unless overridden.

## Native Style

Set level and metadata directly on the Intent:

```python
from evoid import Intent, Level, add_intent

PAYMENT = Intent(
    name="process_payment",
    level=Level.CRITICAL,
    metadata={
        "method": "POST",
        "path": "/payments",
        "timeout": 15.0,
        "priority": 10,
    },
)

async def handle_payment(intent: Intent) -> dict:
    return {"status": "paid"}

add_intent(PAYMENT, handle_payment)
```

## Before/After Processors

Inject processors before or after specific routes:

```python
from evoid.web.route import Service, get, before, after

app = Service("api")

@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id}

# Run rate_limit BEFORE the handler
before("GET:/users/{user_id}", "rate_limit")

# Run audit_log AFTER the handler
after("GET:/users/{user_id}", "audit_log")
```

Pipeline order: `rate_limit` → `validate` → `authorize` → `get_user` → `audit_log`

## Replace Entire Pipeline

Replace all processors for a route:

```python
from evoid.web.route import Service, get, replace_pipeline

app = Service("api")

@app.get("/cached/{key}")
async def get_cached(key: str) -> dict:
    return {"key": key, "value": "cached data"}

replace_pipeline("GET:/cached/{key}", ["cache", "serialize"])
```

## Inspect Pipeline Config

Check what processors will run for any intent:

```python
from evoid.core.extend import get_pipeline_config, list_overrides

# Get pipeline for a specific intent
config = get_pipeline_config(intent)
print(config.processors)  # ("validate", "authorize", ...)

# List all overrides
overrides = list_overrides()
# {"GET:/users/{id}": ["rate_limit", "validate", "authorize", "audit_log"]}
```

## Priority and Timeout

Set priority and timeout in metadata:

```python
@app.post("/payments", level="critical")
async def process_payment(amount: float) -> dict:
    return {"status": "paid"}
```

Or in native style:

```python
PAYMENT = Intent(
    name="process_payment",
    level=Level.CRITICAL,
    timeout=15.0,
    priority=10,
)
```

| Field | Description |
|-------|-------------|
| `timeout` | Max seconds for pipeline execution |
| `priority` | Execution priority (higher = first) |
| `level` | Determines default pipeline and processing |
