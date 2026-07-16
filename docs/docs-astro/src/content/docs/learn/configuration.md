---
title: 'Configuration'
description: 'EVOID uses TOML configuration. Change infrastructure by changing config — business logic stays untouched.'
---

# Configuration

EVOID uses TOML configuration. Change infrastructure by changing config — business logic stays untouched.

!!! tip "Config over code"
    Need to switch from SQLite to PostgreSQL? Change `evoid.toml`, run `evo sync`. Zero code changes.

## Project Structure

When you run `evo init my-api`:

```
my-api/
  evoid.toml          # Project config
  shared/             # Shared code between services
  services/
    api/
      evoid.toml      # Service config (optional)
      main.py         # Service entry point
```

## Project Config

The root `evoid.toml`:

```toml
[project]
name = "my-api"
version = "1.0.0"

[runtime]
adapter = "asgi"
host = "0.0.0.0"
port = 8000

[engines]
schema = "native"
storage = "memory"
cache = "memory"
serializer = "json"
di = "native"
logger = "loguru"
metrics = "simple"
auth = "simple"
```

## Service Config

Each service can override project config:

```toml
[service]
name = "api"
port = 8000

[engines]
storage = "sqlite"
cache = "memory"
```

Service config takes precedence over project config for that service.

## Engine Reference

| Engine | Options | Default | Purpose |
|--------|---------|---------|---------|
| `schema` | `native`, `pydantic` | `native` | Data validation |
| `storage` | `memory`, `sqlite`, `postgres` | `memory` | Data persistence |
| `cache` | `memory` | `memory` | Caching layer |
| `serializer` | `json` | `json` | Serialization |
| `di` | `native` | `native` | Dependency injection |
| `logger` | `structlog`, `loguru` | `loguru` | Logging |
| `metrics` | `simple` | `simple` | Metrics collection |
| `auth` | `simple` | `simple` | Authentication |

## Swapping Infrastructure

Switch from SQLite to PostgreSQL without touching code:

```toml
# Before
[engines]
storage = "sqlite"

# After
[engines]
storage = "postgres"
```

Then sync dependencies:

```bash
evo sync
```

## Syncing Dependencies

`evo sync` reads `evoid.toml`, maps engine names to packages, and installs them via `uv`:

| Engine | Package |
|--------|---------|
| `sqlite` | `aiosqlite` |
| `redis` | `redis.asyncio` |
| `structlog` | `structlog` |
| `loguru` | `loguru` |
| `pydantic` | `pydantic` |
| `sqlalchemy` | `sqlalchemy[asyncio]` |

## Runtime Adapter

The adapter determines how Intents are triggered:

| Adapter | Use Case | Package |
|---------|----------|---------|
| `asgi` | HTTP APIs | `evoid[asgi]` |
| `cli` | Command-line tools | core only |
| `telegram` | Telegram bots | `evoid[telegram]` |
| `robyn` | Robyn framework | `evoid[robyn]` |
| `websocket` | WebSocket connections | `evoid[asgi]` |

## Environment Variables

Override config with environment variables:

```bash
EVOID_HOST=127.0.0.1
EVOID_PORT=3000
EVOID_ADAPTER=cli
```

## Optional Dependencies

Install only what you need:

```bash
uv add "evoid[asgi]"           # HTTP APIs
uv add "evoid[pydantic]"       # Pydantic schemas
uv add "evoid[redis]"          # Redis cache
uv add "evoid[sqlalchemy]"     # SQL storage
uv add "evoid[loguru]"         # Loguru logging
uv add "evoid[full]"           # Everything
```

See [Installation](../getting-started/installation.md) for the full extras list.
