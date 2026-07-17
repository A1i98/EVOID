---
title: 'Plugin Lifecycle Hooks'
description: 'Tap into runtime events with secure, high-performance hooks.'
---

# Plugin Lifecycle Hooks

Tap into runtime events. Plugins can observe pipeline execution, processor execution, and Intent registration.

## Basic Usage

```python
from evoid import on_event, Event, EventContext

def my_hook(ctx: EventContext):
    print(f"Intent executed: {ctx.intent_name}")

on_event(Event.POST_EXECUTE, my_hook)
```

## Available Events

| Event | When | Data |
|-------|------|------|
| `PRE_EXECUTE` | Before pipeline runs | intent_name, pipeline |
| `POST_EXECUTE` | After pipeline runs | intent_name, success, duration |
| `PRE_PROCESS` | Before each processor | processor name |
| `POST_PROCESS` | After each processor | processor name, duration |
| `INTENT_REGISTERED` | When Intent is registered | name, level |
| `INTENT_RESOLVED` | When Intent is resolved | name |

## EventContext

Hooks receive a read-only snapshot:

```python
@dataclass(frozen=True)
class EventContext:
    intent_name: str       # "get_user"
    intent_level: str      # "standard"
    pipeline: tuple        # ("validate", "authorize")
    timestamp: float       # monotonic time
    metadata: dict         # extra data from emit
```

!!! security "Security model"
    Hooks receive `EventContext` (frozen, read-only), NOT the mutable `Context`. Hooks cannot modify pipeline execution.

## Practical Examples

### Request Logger

```python
import time
from evoid import on_event, Event, EventContext

def log_request(ctx: EventContext):
    print(f"[{ctx.intent_name}] started at {ctx.timestamp}")

on_event(Event.PRE_EXECUTE, log_request)
```

### Performance Monitor

```python
from evoid import on_event, Event, EventContext

_metrics = {}

def track_performance(ctx: EventContext):
    name = ctx.intent_name
    _metrics[name] = _metrics.get(name, 0) + 1

on_event(Event.POST_EXECUTE, track_performance)
```

### Audit Trail

```python
from evoid import on_event, Event, EventContext

_audit_log = []

def audit(ctx: EventContext):
    _audit_log.append({
        "intent": ctx.intent_name,
        "level": ctx.level,
        "time": ctx.timestamp,
    })

on_event(Event.POST_EXECUTE, audit)
```

## Managing Hooks

```python
from evoid import on_event, off_event, hook_count, Event

# Register
on_event(Event.POST_EXECUTE, my_hook)

# Count
print(hook_count())                    # Total hooks
print(hook_count(Event.POST_EXECUTE))  # Hooks for specific event

# Unregister
off_event(Event.POST_EXECUTE, my_hook)

# Clear all
from evoid.core.events import clear_hooks
clear_hooks()
```

## Performance

When no hooks are registered, event emission is near-zero cost:

```python
# This check is O(1) — single dict lookup
if _has_hooks("pre_execute"):
    await emit("pre_execute", context)
```

- No hooks → one dict length check, no allocation
- One hook → direct function call
- Multiple hooks → sequential calls with timeout per hook

## Security

| Property | Guarantee |
|----------|-----------|
| Read-only context | `EventContext` is frozen dataclass |
| No mutation | Hooks cannot modify `Context` or `Result` |
| Timeout | Each hook has 5s timeout |
| Max hooks | 16 per event (configurable) |
| Error isolation | Hook errors don't affect pipeline |

## Native IOP Style

```python
from evoid.native import create_service, on
from evoid import Intent, Level, on_event, Event

app = create_service("api")

# Hook runs for ALL intents
def log_all(ctx):
    print(f"Executed: {ctx.intent_name}")

on_event(Event.POST_EXECUTE, log_all)

# Register intent
GET_USER = Intent(name="get_user", level=Level.STANDARD)

async def handle(intent: Intent) -> dict:
    return {"id": 1}

on(app, GET_USER, handle)
```

## Related

- [Schema Export](schema-export.md) — Export Intent schemas
- [Pipeline](pipeline.md) — How execution works
- [Processors](processors.md) — Processor functions
