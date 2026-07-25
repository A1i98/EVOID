---
title: 'Error Handling'
description: 'How EVOID handles exceptions, Result objects, and error recovery in pipelines.'
---

# Error Handling

EVOID captures exceptions in `Result.error` and stops the pipeline. The adapter converts the error to an HTTP response.

## The Result Object

Every pipeline execution returns a Result:

```python
from evoid import execute, Intent

result = await execute(intent)
if result.success:
    print(result.value)
else:
    print(f"Error: {result.error}")
    print(f"Ran {len(result.processors)} processors")
```

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Pipeline completed without exception |
| `value` | `Any` | Return value from last processor |
| `error` | `Exception \| None` | Exception if pipeline failed |
| `processors` | `tuple[str, ...]` | Processors that ran before failure |
| `duration` | `float` | Total execution time in seconds |

## How Exceptions Flow

When a processor raises an exception:

1. Pipeline stops immediately
2. Exception stored in `Result.error`
3. Remaining processors do not run
4. Adapter converts error to response (HTTP 500 by default)

```python
async def handler(ctx):
    raise ValueError("Item not found")
# Pipeline: validate → handler (raises) → STOPS
# Result: success=False, error=ValueError("Item not found")
```

## Structured Error Dicts

For controlled errors, return a dict instead of raising:

```python
async def handler(ctx):
    item = find_item(ctx.metadata["item_id"])
    if not item:
        return {"error": "Not found", "status": 404}
    return item
```

## Non-Critical Errors

Use `ctx.errors` to collect warnings without stopping the pipeline:

```python
async def validate_optional(ctx):
    try:
        validate(ctx.metadata["body"])
    except ValidationError as e:
        ctx.errors.append(e)
    return {"validated": True, "warnings": len(ctx.errors)}
```

## Custom Error Classes

Use frozen dataclasses for typed errors:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class AppError:
    message: str
    status: int = 400

async def handler(ctx):
    raise AppError("Not found", status=404)
```

## Related

- [Pipeline](pipeline.md): how processors compose
- [Intent](intent.md): level determines which processors run
