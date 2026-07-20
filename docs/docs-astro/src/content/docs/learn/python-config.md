---
title: 'Python-Native Config'
description: 'Configure EVOID with Python dataclasses — type-safe, composable, IOP-native.'
---

# Python-Native Config

Configure EVOID with Python. Two formats supported: TOML and Python.

## Python Config (evoid_config.py)

```python
from evoid.config import config

app = config(
    service={"name": "my-api", "version": "1.0.0"},
    runtime={"adapter": "asgi", "port": 8000},
    engines={"storage": "memory", "cache": "memory", "logger": "loguru"},
)
```

### What You Get

- **Type safety** — Dataclasses validate at load time
- **IDE autocomplete** — Full completion for all fields
- **Composable** — Import and extend configs
- **IOP-native** — Works with EVOID's plugin system

## TOML Config (evoid.toml)

```toml
[service]
name = "my-api"
version = "1.0.0"

[runtime]
adapter = "asgi"
port = 8000

[engines]
storage = "memory"
cache = "memory"
logger = "loguru"
```

## Auto-Detection

EVOID auto-detects the config format:

```python
from evoid.config import load_config

# Tries evoid.toml first, then evoid_config.py
config = load_config()

# Or specify explicitly
config = load_config("evoid.toml")
config = load_config("evoid_config.py")
```

## Validation

```python
from evoid.config import config, validate_config

app = config(runtime={"port": 99999})
errors = validate_config(app)
# ['runtime.port must be 1-65535 (got 99999)']
```

## Config Fields

### [service]

```python
config(
    service={
        "name": "my-api",       # Service name
        "version": "1.0.0",     # Semantic version
    }
)
```

### [runtime]

```python
config(
    runtime={
        "adapter": "asgi",      # asgi, cli, telegram, robyn, websocket
        "host": "0.0.0.0",      # Bind address
        "port": 8000,           # Bind port
    }
)
```

### [engines]

```python
config(
    engines={
        "schema": "native",     # native (built-in), pydantic, msgspec
        "storage": "memory",    # memory, sqlite (built-in), sqlalchemy
        "cache": "memory",      # memory (built-in)
        "serializer": "json",   # json (built-in), msgspec, orjson
        "di": "native",         # native (built-in)
        "logger": "loguru",     # loguru, structlog
        "metrics": "simple",    # simple (built-in), prometheus
        "auth": "simple",       # simple (built-in)
    }
)
```

!!! note "Plugin engines"
    Need Redis, PostgreSQL, or advanced DI? Install the corresponding plugin:
    ```bash
    uv add evoid-redis        # Redis cache
    uv add evoid-postgresql   # PostgreSQL storage
    uv add evoid-di           # Advanced DI (scoped, context-aware)
    ```

### [pipeline]

```python
config(
    pipeline={
        "processors": ["validate", "authorize"],
    }
)
```

## Composing Configs

```python
from evoid.config import config

# Base config
base = config(
    engines={"storage": "memory", "cache": "memory"},
)

# Production override
prod = config(
    service={"name": "prod-api"},
    engines={"storage": "sqlite", "cache": "memory"},
)
```

## Native IOP Style

In native IOP, config is just data:

```python
from evoid.config import config
from evoid.native import create_service, on
from evoid import Intent, Level

# Load config
app = config(
    service={"name": "user-service"},
    engines={"storage": "memory"},
)

# Create service
service = create_service(app.service.name)

# Register intents
GET_USER = Intent(name="get_user", level=Level.STANDARD)
on(service, GET_USER, handle_get_user)
```

## Related

- [Configuration](configuration.md) — TOML config reference
- [Plugin Standard](plugin-standard.md) — Plugin packaging
- [Installation](../getting-started/installation.md) — Install EVOID
