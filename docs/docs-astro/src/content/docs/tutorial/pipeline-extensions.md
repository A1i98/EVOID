---
title: 'Pipeline Extensions'
description: 'Add cross-cutting concerns (logging, rate limiting, caching) without modifying handlers.'
---

# Pipeline Extensions

Add cross-cutting concerns (logging, rate limiting, caching) without modifying handlers.

## The Problem

!!! danger "DRY violation"
    You have 20 endpoints. Every one needs rate limiting and logging. Copy-pasting the same code into each handler is error-prone and violates DRY.

## The Solution

Inject processors before or after specific routes:

```python
from evoid.web.route import Service, get, before, after

app = Service("api")

@get("/users/{id}")
async def get_user(id: int) -> dict:
    return {"id": id}

# Add rate limiting BEFORE all processors
before("GET:/users/{id}", "rate_limit")

# Add logging AFTER all processors
after("GET:/users/{id}", "log_response")
```

Now every `GET:/users/{id}` request runs: `rate_limit` → `validate` → `authorize` → `get_user` → `log_response`.

## Extension Functions

### before(intent_name, processor)

Add a processor at the start of the pipeline:

```python
before("GET:/users/{id}", "rate_limit")
# Pipeline: [rate_limit, validate, authorize, ...]
```

### after(intent_name, processor)

Add a processor at the end of the pipeline:

```python
after("GET:/users/{id}", "audit_log")
# Pipeline: [..., validate, authorize, audit_log]
```

### before_processor(intent_name, target, new)

Insert before a specific processor:

```python
before_processor("GET:/users/{id}", "authorize", "check_permission")
# Pipeline: [validate, check_permission, authorize, ...]
```

### after_processor(intent_name, target, new)

Insert after a specific processor:

```python
after_processor("GET:/users/{id}", "validate", "enrich_data")
# Pipeline: [validate, enrich_data, authorize, ...]
```

### replace_pipeline(intent_name, processors)

Replace the entire pipeline:

```python
replace_pipeline("GET:/users/{id}", ["cache", "fetch", "serialize"])
```

### remove_processor(intent_name, processor)

Remove a processor from the pipeline:

```python
remove_processor("GET:/users/{id}", "audit")
```

## Practical Example: Logging Middleware

```python
from evoid.web.route import Service, get, before, after

app = Service("api")

@get("/users/{id}")
async def get_user(id: int) -> dict:
    return {"id": id}

@post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created"}

# Apply to all GET routes
before("GET:/users/{id}", "timing")
after("GET:/users/{id}", "log_request")

# Apply to all POST routes
before("POST:/users", "rate_limit")
after("POST:/users", "audit_log")
```

## Inspecting Overrides

!!! tip "Debugging pipelines"
    Use `list_overrides()` to see exactly what processors run for each intent:

```python
from evoid.core.extend import list_overrides

overrides = list_overrides()
# {"GET:/users/{id}": ["rate_limit", "validate", "authorize", "log_request"], ...}
```

## Clearing Overrides

```python
from evoid.core.extend import clear_overrides

clear_overrides()
```
