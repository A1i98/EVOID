---
title: 'Error Reference'
description: 'Every exception EVOID can raise, when it happens, and how to handle it.'
---

# Error Reference

EVOID captures exceptions in `Result.error` and stops the pipeline. The adapter converts the error to an HTTP response.

## Exceptions

### `ValueError` — Intent Not Registered / Validation Failed

Raised when executing an Intent that hasn't been registered, or when a processor returns `{"validated": False}`.

```python
# Intent not found
result = await execute(Intent(name="nonexistent", level=Level.STANDARD))
# Result: success=False, error=ValueError("Intent 'nonexistent' not registered")

# Validation rejection
async def validate(ctx):
    return {"validated": False, "error": "name is required"}
# Pipeline stops. Result: success=False, error=ValueError("Validation failed in validate: name is required")
```

**Fix**: register the Intent, or check validation return value.

### `PermissionError` — Rejected by Processor

Raised when a processor returns `{"authorized": False}` or `{"validated": False}`. The `_check_rejection()` function in the pipeline detects rejection signals.

```python
async def authorize(ctx):
    if not user_has_role(ctx, "admin"):
        return {"authorized": False, "reason": "admin only"}
    return {"authorized": True}
# Pipeline stops. Result: success=False, error=PermissionError("Rejected by authorize: admin only")
```

**Fix**: check `result.error` and return 403.

### `TimeoutError` — Processor Timeout

Raised when a processor exceeds the Intent's timeout. Default timeouts: EPHEMERAL=5s, STANDARD=10s, CRITICAL=30s.

```python
PAYMENT = Intent(name="pay", level=Level.CRITICAL, timeout=5.0)
# If handler takes >5s: Result.error = TimeoutError("Processor 'pay' timed out after 5.0s")
```

**Fix**: increase timeout or optimize the processor.

### `LookupError` — Processor Not Found

Raised in strict mode when a processor name in the pipeline doesn't match any registered processor.

```python
from evoid.core.runtime import Config

config = Config(strict=True)
result = await execute(intent, config=config)
# If pipeline references "unknown_processor": LookupError
```

**Fix**: check processor names against `evo list-processors`.

### User-Raised Exceptions

Any exception raised by a handler is caught by the pipeline and stored in `Result.error`. The pipeline stops. The adapter returns HTTP 500.

```python
async def handler(ctx):
    raise ValueError("Item not found")
# Result: success=False, error=ValueError("Item not found")
# HTTP 500: {"detail": "Item not found"}
```

## Result Object

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | `True` if pipeline completed without exception |
| `value` | `Any` | Return value from last processor |
| `error` | `Exception \| None` | Exception if pipeline failed |
| `processors` | `tuple[str, ...]` | Processors that ran |
| `duration` | `float` | Total execution time |

## Handling Errors

### Check result.success

```python
result = await execute(intent)
if result.success:
    return result.value
else:
    return {"error": str(result.error)}
```

### Catch specific errors

```python
try:
    result = await execute(intent)
except TimeoutError:
    return {"error": "timeout"}
except PermissionError:
    return {"error": "forbidden", "status": 403}
```

### Collect non-critical errors

```python
async def handler(ctx):
    try:
        validate(ctx.metadata["body"])
    except ValidationError as e:
        ctx.errors.append(e)  # Pipeline continues
    return {"validated": True, "warnings": len(ctx.errors)}
```

## Related

- [Error Handling](../tutorial/error-handling.md): tutorial walkthrough
- [Pipeline](../learn/pipeline.md): how exceptions propagate
