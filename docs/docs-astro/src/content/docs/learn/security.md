---
title: 'Security'
description: 'Secrets management, pipeline security, and AI data control in EVOID.'
---

# Security

Security in EVOID operates at three layers: **secrets management**, **pipeline enforcement**, and **AI data control**. Each layer is independent — you can use one without the others.

## 1. Secrets Management

EVOID has zero core dependencies and no built-in `.env` loader. This is deliberate — secrets management is infrastructure, not runtime. Here's how to handle it.

### The Problem with `.env` Files

Every framework handles secrets differently. Some load `.env` automatically. Some require `python-dotenv`. Some expose secrets in config files. The result: secrets leak into git, get hardcoded, or get scattered across config files.

### The EVOID Pattern: Environment Variables

The simplest approach — use `os.environ` directly:

```python
import os
from evoid.config import config

DB_URL = os.environ["DATABASE_URL"]  # crashes if missing — intentional
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost")  # optional

app = config(
    service={"name": "my-api"},
    engines={"storage": "sqlite"},
)
```

!!! info "Why no built-in .env loader"
    `.env` files are a development convenience, not a security feature. In production, secrets come from environment variables, secret managers, or mounted volumes. EVOID stays out of the way — you decide how to inject secrets.

### Recommended Patterns

#### Development: `.env` + `python-dotenv`

```bash
pip install python-dotenv
```

```python
# main.py — load .env before anything else
from dotenv import load_dotenv
load_dotenv()

import os
from evoid.config import config

DB_URL = os.environ["DATABASE_URL"]
```

```
# .env (never commit this)
DATABASE_URL=sqlite:///dev.db
REDIS_URL=redis://localhost
SECRET_KEY=dev-secret-key
```

```
# .gitignore
.env
.env.*
!.env.example
```

#### Production: Environment Variables

```bash
# Docker
docker run -e DATABASE_URL="postgres://..." my-app

# Systemd
Environment=DATABASE_URL=postgres://...

# Kubernetes
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: my-secrets
        key: database-url
```

#### Production: Secret Managers

```python
import os

# AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager
# Fetch secrets at startup, inject as env vars

DB_URL = os.environ["DATABASE_URL"]  # injected by orchestrator
```

### Config Files: Never Hardcode Secrets

```toml
# evoid.toml — safe (no secrets)
[service]
name = "my-api"

[engines]
storage = "sqlite"

# WRONG — never put secrets in config files
# [engines.redis]
# url = "redis://:password@localhost"  # ❌
```

```python
# RIGHT — secrets from env, config from file
import os
from evoid.config import config

app = config(
    service={"name": "my-api"},
    engines={"storage": "sqlite"},
)

# Redis URL from environment
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost")
```

!!! warning "Golden rule"
    > Secrets go in environment variables. Configuration goes in files. Never mix them.

### `.env.example` Template

Provide a template for developers:

```
# .env.example (commit this)
DATABASE_URL=sqlite:///dev.db
REDIS_URL=redis://localhost
SECRET_KEY=change-me-in-production
```

```bash
# Developer setup
cp .env.example .env
# Edit .env with local values
```

---

## 2. Pipeline Security

EVOID's pipeline enforces security through **Intent levels**. The level you choose determines which security processors run.

### Security by Level

| Level | Security Processors | What Runs |
|-------|-------------------|-----------|
| `ephemeral` | `validate` | Data shape check only |
| `standard` | `validate` → `authorize` | Shape check + permission check |
| `critical` | `validate` → `authorize` → `audit` → `protect` | Full security stack |

### The `protect` Processor

The built-in `protect` processor provides:

- **Rate limiting** — per-key request throttling
- **Circuit breaker** — stops processing after repeated failures

```python
from evoid import Intent, Level

# This Intent gets full protection
PAYMENT = Intent(
    name="process_payment",
    level=Level.CRITICAL,
    # Pipeline: validate → authorize → audit → protect → handler
    # Rate limit: 20 requests/minute
    # Circuit breaker: opens after 3 failures, half-open after 30s
)
```

### The `authorize` Processor

With `evoid-auth` installed, the `authorize` processor checks roles:

```python
from evoid_auth import register_provider

async def my_auth(token: str) -> dict:
    user = await db.find_by_token(token)
    return {"user": user.name, "role": user.role}

register_provider("my_auth", my_auth)
```

Role hierarchy: `admin(4) > editor(3) > viewer(2) > guest(1)`

```python
# This Intent requires editor role or higher
CREATE_POST = Intent(
    name="create_post",
    level=Level.STANDARD,
    metadata={"required_role": "editor"},
)
```

### Plugin Security

Plugins follow EVOID's security model:

- **Event hooks are read-only** — hooks receive `EventContext` (frozen), never the mutable `Context`
- **Max 16 hooks per event** — prevents hook flooding
- **5s timeout per hook** — prevents slow hooks from blocking the pipeline
- **Zero cost when no hooks** — single dict length check

```python
from evoid import on_event, Event

# This hook can READ the context, but NOT modify it
def log_execution(ctx):
    print(f"Executed: {ctx.intent_name}")  # read-only

on_event(Event.POST_EXECUTE, log_execution)
# ctx is EventContext — frozen, read-only
# You cannot write to ctx.state or ctx.deps
```

---

## 3. AI Data Control

When you expose Intents to AI agents via MCP, you control exactly what the AI can see and do.

### The Problem

AI agents need to understand your system to interact with it. But you don't want them seeing:
- Internal implementation details
- Sensitive business logic
- Admin-only operations
- Debug endpoints

### The Solution: Visibility Control

EVOID uses `mcp_visible` in Intent metadata to control what AI agents see:

```python
from evoid import Intent, Level

# Visible to AI agents — AI can discover and invoke this
GET_USER = Intent(
    name="get_user",
    level=Level.STANDARD,
    metadata={
        "description": "Get a user by their unique ID",
        "mcp_visible": True,  # ← AI agents can see this
    },
)

# Hidden from AI agents (default) — AI cannot see this
DELETE_USER = Intent(
    name="delete_user",
    level=Level.CRITICAL,
    metadata={
        "description": "Permanently delete a user",
        # mcp_visible defaults to False — AI cannot see this
    },
)

# Internal hook — completely invisible
DEBUG_INTENT = Intent(
    name="internal_debug",
    level=Level.EPHEMERAL,
    # No description, no mcp_visible — invisible to everything
)
```

### How It Works

```python
from evoid.adapters.mcp import create_mcp_server

# Create MCP server — only visible Intents are exposed
server = create_mcp_server("my-api", visible_only=True)

# AI agent sees:
#   - get_user (mcp_visible=True)
#   - create_post (mcp_visible=True)
#
# AI agent does NOT see:
#   - delete_user (mcp_visible=False, default)
#   - internal_debug (no metadata)
```

### Granular Control

Control visibility at multiple levels:

#### Per-Intent: `mcp_visible`

```python
# Show to AI
Intent(name="get_user", metadata={"mcp_visible": True})

# Hide from AI (default)
Intent(name="admin_panel", metadata={})
```

#### Per-Field: Metadata Schema

Control which fields AI agents can see:

```python
GET_USER = Intent(
    name="get_user",
    level=Level.STANDARD,
    metadata={
        "description": "Get a user by ID",
        "mcp_visible": True,
        # Only these fields are exported to AI:
        "user_id": 0,  # AI can see: "user_id is an integer"
        # Internal fields are hidden:
        "internal_flag": True,  # Not in schema export
    },
)
```

#### Per-Level: Pipeline Enforcement

Even if AI invokes an Intent, the pipeline still runs:

```python
# AI agent calls get_user
# Pipeline: validate → authorize → handler
# The authorize step checks the AI agent's permissions
# If the AI agent doesn't have the right role → denied

# AI agent tries to call delete_user
# Can't even see it (mcp_visible=False)
# Even if it somehow called it → CRITICAL pipeline → full audit trail
```

### What AI Agents See vs. Don't See

| Data | Visible? | How to Control |
|------|----------|----------------|
| Intent name | Yes (if mcp_visible) | `mcp_visible` flag |
| Intent description | Yes | `metadata["description"]` |
| Metadata fields | Only documented ones | Include in metadata dict |
| Pipeline config | Yes | Always exported (for AI understanding) |
| Handler code | **Never** | AI only sees the Intent, not the implementation |
| ctx.state | **Never** | Context is server-side only |
| ctx.deps | **Never** | Dependencies are server-side only |
| Other Intents | Only if visible | Each Intent has its own `mcp_visible` |

### AI Agent Security Checklist

- [ ] Mark only necessary Intents with `mcp_visible=True`
- [ ] Use `Level.STANDARD` or `Level.CRITICAL` for AI-exposed Intents
- [ ] Add descriptions so AI understands what each Intent does
- [ ] Never expose admin/debug Intents to AI
- [ ] Review `export_schemas()` output before deploying
- [ ] Monitor AI agent invocations via audit logs (Level.CRITICAL)

```python
# Audit what AI agents can see
from evoid import export_schemas

schemas = export_schemas()
for name, schema in schemas.items():
    print(f"{name}: {schema.description}")
    print(f"  Level: {schema.level}")
    print(f"  Pipeline: {schema.pipeline}")
    # Review before deploying to production
```

---

## Summary

| Layer | What It Protects | How |
|-------|-----------------|-----|
| **Secrets** | Credentials, API keys | Environment variables, never in config |
| **Pipeline** | Request processing | Intent levels → security processors |
| **AI Control** | Data exposed to AI | `mcp_visible` flag, schema export |

!!! tip "Defense in depth"
    Use all three layers. Secrets management keeps credentials safe. Pipeline security enforces permissions. AI control limits what agents can see. No single layer is enough alone.

## Related

- [Intent](intent.md) — Intent levels and security processors
- [Schema Export](schema-export.md) — AI visibility control
- [Plugin Hooks](plugin-hooks.md) — Security model for lifecycle hooks
- [Plugin Collection](plugin-collection.md) — evoid-auth for authorization
