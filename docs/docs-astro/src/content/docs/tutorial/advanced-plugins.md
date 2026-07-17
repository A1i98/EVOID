---
title: 'Advanced Plugins'
description: 'Write plugins that tap into runtime behavior with lifecycle hooks.'
---

# Advanced Plugins

Write plugins that observe and extend runtime behavior using lifecycle hooks.

## Plugin Architecture

```
Plugin
   |
   | on_event(Event.PRE_EXECUTE, handler)
   | on_event(Event.POST_EXECUTE, handler)
   | on_event(Event.INTENT_REGISTERED, handler)
   |
   v
Event Emitter
   |
   | Emits events during pipeline execution
   |
   v
Pipeline Executor
```

## Writing a Plugin

### Metrics Plugin

Track execution metrics for all Intents:

```python
from evoid import on_event, Event, EventContext

_metrics: dict[str, dict] = {}

def on_execute(ctx: EventContext):
    name = ctx.intent_name
    if name not in _metrics:
        _metrics[name] = {"count": 0, "total_time": 0.0}
    _metrics[name]["count"] += 1

def on_complete(ctx: EventContext):
    name = ctx.intent_name
    if name in _metrics:
        _metrics[name]["total_time"] += ctx.metadata.get("duration", 0)

# Register hooks
on_event(Event.PRE_EXECUTE, on_execute)
on_event(Event.POST_EXECUTE, on_complete)

def get_metrics():
    return _metrics.copy()
```

### Audit Plugin

Log all Intent executions:

```python
import time
from evoid import on_event, Event, EventContext

_audit_log: list[dict] = []

def audit(ctx: EventContext):
    _audit_log.append({
        "intent": ctx.intent_name,
        "level": ctx.intent_level,
        "timestamp": time.time(),
        "pipeline": list(ctx.pipeline),
    })

on_event(Event.POST_EXECUTE, audit)

def get_audit_log():
    return _audit_log.copy()
```

### Rate Limit Plugin

Track request counts per Intent:

```python
from collections import defaultdict
from time import time
from evoid import on_event, Event, EventContext

_counts: dict[str, list[float]] = defaultdict(list)
LIMITS = {"ephemeral": 100, "standard": 50, "critical": 20}
WINDOW = 60

def check_rate(ctx: EventContext):
    name = ctx.intent_name
    now = time()
    _counts[name] = [t for t in _counts[name] if now - t < WINDOW]

    limit = LIMITS.get(ctx.intent_level, 50)
    if len(_counts[name]) >= limit:
        raise Exception(f"Rate limit exceeded for {name}")

    _counts[name].append(now)

on_event(Event.PRE_EXECUTE, check_rate)
```

## Hook Lifecycle

```
Intent Registration
   → INTENT_REGISTERED event

Pipeline Execution
   → PRE_EXECUTE event
   → For each processor:
       → PRE_PROCESS event
       → processor runs
       → POST_PROCESS event
   → POST_EXECUTE event
```

## Security Model

| Property | Description |
|----------|-------------|
| Read-only context | `EventContext` is frozen, cannot be mutated |
| No pipeline control | Hooks observe, they don't modify |
| Timeout | 5s per hook, pipeline continues |
| Max hooks | 16 per event |
| Error isolation | Hook errors don't affect execution |

## Performance

Hooks have near-zero overhead when not registered:

```python
# This is the hot path check — O(1)
if _has_hooks("pre_execute"):
    await emit("pre_execute", context)
```

- No hooks: one dict length check
- One hook: direct function call
- Multiple hooks: sequential with timeout

## Combining with Schema Export

Plugins can use schema export to generate documentation:

```python
from evoid import export_schemas, on_event, Event

def auto_document():
    schemas = export_schemas()
    for name, schema in schemas.items():
        print(f"{name}: {schema.description}")
        print(f"  Pipeline: {schema.pipeline}")
        print(f"  Fields: {len(schema.metadata_fields)}")
```

## Native IOP Style

```python
from evoid.native import create_service, on
from evoid import Intent, Level, on_event, Event

app = create_service("api")

# Plugin: log all registrations
def on_register(ctx):
    print(f"Intent registered: {ctx.intent_name}")

on_event(Event.INTENT_REGISTERED, on_register)

# Register intents — hook fires for each
GET_USER = Intent(name="get_user", level=Level.STANDARD)
on(app, GET_USER, handle_get_user)
# Prints: "Intent registered: get_user"
```

## Related

- [Plugin Hooks](../learn/plugin-hooks.md) — Hook reference
- [Schema Export](../learn/schema-export.md) — Export Intent schemas
- [Plugins](../learn/plugins.md) — Plugin system overview
