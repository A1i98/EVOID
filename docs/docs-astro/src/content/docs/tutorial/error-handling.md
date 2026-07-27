---
title: 'Error Handling'
description: 'Structured errors, Result objects, and proper HTTP responses. See [Error Handling Reference](../learn/error-handling.md) for full details.'
---

# Error Handling

Structured errors, Result objects, and proper HTTP responses.

> **Full reference:** [Error Handling Reference](../learn/error-handling.md) — Result object, exception flow, structured error dicts, non-critical errors, custom error classes.

## Quick Patterns

| Scenario | Code |
|----------|------|
| Fatal error (stops pipeline) | `raise ValueError("Item not found")` |
| Structured error (continues) | `return {"error": "Not found", "status": 404}` |
| Non-critical warning | `ctx.errors.append(e)` — pipeline continues |
| Check result | `result.success`, `result.error` |

## What You Learned

| Scenario | Approach |
|----------|----------|
| Fatal error | `raise Exception("msg")` — pipeline stops |
| Structured error | Return `{"error": "msg"}` |
| Non-critical warning | `ctx.errors.append(e)` — pipeline continues |
| Check result | `result.success`, `result.error` |

## Next: Dependency Injection

Manage dependencies properly next: [Dependency Injection](dependency-injection.md).