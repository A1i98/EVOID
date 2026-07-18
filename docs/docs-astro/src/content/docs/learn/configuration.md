---
title: 'Configuration'
description: 'Configure EVOID with TOML or Python. Every field explained.'
---

# Configuration

EVOID supports two config formats:

1. **TOML** (`evoid.toml`) — traditional, human-readable
2. **Python** (`evoid_config.py`) — native, type-safe, IOP-native

Both produce the same config. Change infrastructure by changing config — business logic stays untouched.

!!! tip "Config over code"
    Switch from SQLite to PostgreSQL? Change one line in config, run `evo install sqlite`. Zero code changes.

## Python Config (Recommended)

```python
# evoid_config.py
from evoid.config import config

app = config(
    service={"name": "my-api", "version": "1.0.0"},
    runtime={"adapter": "asgi", "port": 8000},
    engines={"storage": "redis", "cache": "memory"},
)
```

## TOML Config

```toml
# evoid.toml
[service]
name = "my-api"
version = "1.0.0"

[runtime]
adapter = "asgi"
port = 8000

[engines]
storage = "redis"
cache = "memory"
```

## Auto-Detection

EVOID auto-detects the config format:

```python
from evoid.config import load_config

config = load_config()  # Tries evoid.toml, then evoid_config.py
```

## Project Structure

```
my-api/
  evoid.toml              # Project config (root)
  shared/                 # Shared code between services
  services/
    api/
      evoid.toml          # Service config (optional override)
      main.py
    workers/
      evoid.toml          # Service config for worker
      main.py
```

**Two levels of config:**
- **Project** (`root/evoid.toml`) — defaults for all services
- **Service** (`services/*/evoid.toml`) — overrides for one service

Service config **merges into** project config. Only specify what you want to override.

## Complete Reference

### [service] — Service Identity

```toml
[service]
name = "my-api"
version = "1.0.0"
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | `"evoid-service"` | Service name. Used in logs, metrics, and inter-service communication. |
| `version` | `str` | `"0.1.0"` | Semantic version. Included in health check responses. |

### [runtime] — Server Configuration

```toml
[runtime]
adapter = "asgi"
host = "0.0.0.0"
port = 8000
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `adapter` | `str` | `"asgi"` | How Intents are triggered. See [Adapter Reference](#adapter-reference). |
| `host` | `str` | `"0.0.0.0"` | Bind address. Use `127.0.0.1` for local-only. |
| `port` | `int` | `8000` | Bind port. |

### [engines] — Infrastructure Selection

```toml
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

Each engine is pluggable. Change the value to swap the implementation.

| Field | Options | Default | Purpose |
|-------|---------|---------|---------|
| `schema` | `native`, `pydantic`, `msgspec`, `attrs` | `native` | Data validation |
| `storage` | `memory`, `sqlite`, `sqlalchemy`, `redis`, `postgres`, `mongo` | `memory` | Data persistence |
| `cache` | `memory`, `redis` | `memory` | Caching layer |
| `serializer` | `json`, `msgspec`, `orjson` | `json` | Serialization |
| `di` | `native` | `native` | Dependency injection |
| `logger` | `structlog`, `loguru` | `loguru` | Structured logging |
| `metrics` | `simple`, `prometheus` | `simple` | Metrics collection |
| `auth` | `simple`, `jwt` | `simple` | Authentication |

### [pipeline] — Default Processors

```toml
[pipeline]
processors = ["validate", "authorize"]
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `processors` | `list[str]` | `["validate", "authorize"]` | Default processor chain for all Intents. Override per-Intent in code. |

## Real-World Examples

### Minimal API (Development)

```toml
[service]
name = "dev-api"
version = "0.1.0"

[runtime]
adapter = "asgi"
port = 8000

[engines]
schema = "native"
storage = "memory"
cache = "memory"
serializer = "json"
logger = "loguru"
```

### Production API with PostgreSQL

```toml
[service]
name = "production-api"
version = "2.1.0"

[runtime]
adapter = "asgi"
host = "0.0.0.0"
port = 8000

[engines]
schema = "pydantic"
storage = "sqlalchemy"
cache = "redis"
serializer = "orjson"
logger = "structlog"
metrics = "prometheus"
auth = "jwt"

[pipeline]
processors = ["validate", "authorize", "audit"]
```

```bash
evo sync
# Installs: pydantic, sqlalchemy, aiosqlite, redis, orjson, structlog, prometheus-client, pyjwt
```

### Telegram Bot

```toml
[service]
name = "my-bot"
version = "1.0.0"

[runtime]
adapter = "telegram"

[engines]
schema = "native"
storage = "sqlite"
cache = "memory"
serializer = "json"
logger = "loguru"
```

### Microservices (Multiple Services)

**Project root** (`evoid.toml`):
```toml
[service]
name = "my-platform"
version = "1.0.0"

[engines]
schema = "pydantic"
storage = "sqlalchemy"
cache = "redis"
serializer = "json"
logger = "structlog"
```

**API service** (`services/api/evoid.toml`):
```toml
[service]
name = "api"

[runtime]
adapter = "asgi"
port = 8000
```

**Worker service** (`services/workers/evoid.toml`):
```toml
[service]
name = "workers"

[runtime]
adapter = "cli"

[engines]
storage = "postgres"
```

The worker inherits `schema`, `cache`, `serializer`, `logger` from project config but overrides `storage` and `adapter`.

## Config Precedence

```
Service config  →  merges into  →  Project config  →  defaults
```

1. Start with project config defaults
2. Service config overrides specific fields
3. Environment variables override both (if supported)

Example:

```toml
# Project: services/ with PostgreSQL
[engines]
storage = "sqlalchemy"

# Service: services/cache-only/evoid.toml
# This service only needs memory — override storage
[engines]
storage = "memory"
```

## Adapter Reference

| Adapter | Use Case | Package Required | Trigger Source |
|---------|----------|------------------|----------------|
| `asgi` | HTTP APIs | `evoid[asgi]` | HTTP requests |
| `cli` | Command-line tools | core only | Terminal commands |
| `telegram` | Telegram bots | `evoid[telegram]` | Telegram messages |
| `robyn` | Robyn framework | `evoid[robyn]` | HTTP requests |
| `websocket` | WebSocket apps | `evoid[asgi]` | WebSocket messages |

## Syncing Dependencies

`evo sync` reads `evoid.toml`, maps engine names to packages, and installs them:

```bash
evo sync
# Reads: evoid.toml
# Maps: storage="sqlalchemy" → sqlalchemy[asyncio], aiosqlite
# Installs via: uv add
```

### Engine → Package Map

| Engine | Value | Packages Installed |
|--------|-------|-------------------|
| `schema` | `pydantic` | `pydantic>=2.0.0` |
| `schema` | `msgspec` | `msgspec>=0.18.0` |
| `storage` | `sqlite` | `aiosqlite>=0.20.0` |
| `storage` | `sqlalchemy` | `sqlalchemy[asyncio]>=2.0.0`, `aiosqlite` |
| `storage` | `redis` | `redis>=4.0.0` |
| `storage` | `postgres` | `asyncpg>=0.28.0` |
| `cache` | `redis` | `redis>=4.0.0` |
| `serializer` | `msgspec` | `msgspec>=0.18.0` |
| `serializer` | `orjson` | `orjson>=3.9.0` |
| `logger` | `structlog` | `structlog>=24.0.0` |
| `logger` | `loguru` | `loguru>=0.7.0` |
| `metrics` | `prometheus` | `prometheus-client>=0.15.0` |
| `auth` | `jwt` | `pyjwt>=2.10.0` |
| `adapter` | `asgi` | `starlette>=0.27.0`, `uvicorn[standard]>=0.24.0` |
| `adapter` | `robyn` | `robyn>=0.30.0` |
| `adapter` | `telegram` | `aiogram>=3.0.0` |

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

## Environment Variables

Override config values at runtime:

```bash
EVOID_HOST=127.0.0.1
EVOID_PORT=3000
EVOID_ADAPTER=cli
```

## Related

- [Installation](../getting-started/installation.md) — Install EVOID
- [Plugins](plugins.md) — Custom engines
- [Architecture](../getting-started/architecture.md) — How config affects execution
