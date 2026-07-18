---
title: 'FAQ'
description: 'Frequently asked questions about EVOID.'
---

# FAQ

Frequently asked questions about EVOID.

## General

### What is IOP?

Intent-Oriented Programming is a paradigm where data declares what it needs. The runtime handles how. Instead of writing "how to save a user," you declare "this is critical data" and the runtime adds encryption, audit logging, and replication automatically.

### When should I use EVOID?

Use EVOID when:

- Multiple services need to communicate
- Infrastructure varies by data criticality
- You want pipeline-based extensibility
- You need typed, validated processing chains

### When should I NOT use EVOID?

EVOID is overkill for:

- Simple single-file scripts
- Tiny APIs with < 5 endpoints
- Projects where you don't need pipeline extensibility

### Is EVOID production-ready?

EVOID is in beta (v0.4.x). The core is stable, zero dependencies, all tests passing. APIs may change before v1.0. Pin your version in production.

## Technical

### How does EVOID differ from middleware?

Traditional middleware wraps the entire request/response. EVOID processors run as part of a pipeline, with access to shared state (`ctx.state`). Processors are composable, replaceable, and can be injected at any point.

### Can I use EVOID with FastAPI?

Yes. EVOID complements FastAPI. Use FastAPI for HTTP endpoints and EVOID for internal service communication, validation pipelines, and inter-service messaging.

### What's the performance overhead?

EVOID pipeline execution has near-zero overhead. The fast path (no inspection, no timeout) runs at ~10K ops/s on a 5-processor pipeline. Inspection and timeout add minimal cost.

### How do I switch from SQLite to PostgreSQL?

Change `evoid.toml` and run `evo sync`:

```toml
[engines]
storage = "sqlalchemy"
```

```bash
evo sync
```

Zero code changes to your business logic.

### How do I add authentication?

Use the `auth_checker` processor in your pipeline:

```python
from evoid.processors import auth_checker
from evoid.core.extend import before

before("GET:/users/{id}", "auth_checker")
```

Or create a custom processor:

```python
from evoid.core import Context, register_processor

async def check_auth(ctx: Context) -> dict:
    token = ctx.intent.metadata.get("headers", {}).get("authorization")
    if not token:
        raise ValueError("Unauthorized")
    ctx.state["user"] = verify_token(token)
    return {"authenticated": True}

register_processor("check_auth", check_auth)
```

### How do I handle errors?

Raise exceptions in processors. The pipeline stops and returns a failed `Result`:

```python
result = await execute(intent)

if not result.success:
    print(f"Error: {result.error}")
    print(f"Failed after: {result.processors}")
```

For non-critical errors, append to `ctx.errors`:

```python
ctx.errors.append(ValidationError("optional check failed"))
# Pipeline continues
```

### How do I test my processors?

```python
import asyncio
from evoid.core import Context, Intent, Level

async def test_validate():
    intent = Intent(name="test", level=Level.STANDARD)
    ctx = Context(intent=intent, state={"data": "hello"})

    result = await validate(ctx)

    assert result["valid"] is True
    assert ctx.state["validated"] is True

asyncio.run(test_validate())
```

## CLI

### How do I create a project?

```bash
evo init my-api
cd my-api
```

### How do I add a service?

```bash
evo service new api
```

### How do I run my service?

```bash
evo service run api
```

### How do I sync dependencies?

```bash
evo sync
```

This reads `evoid.toml` and installs required packages.

## Related

- [Quick Start](quickstart.md) — Get started in 5 minutes
- [What is IOP?](what-is-iop.md) — Understanding the paradigm
- [Troubleshooting](troubleshooting.md) — Common errors and fixes
- [Configuration](../learn/configuration.md) — TOML config reference
