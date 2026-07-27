---
title: 'Configuration Reference'
description: 'Every config option, its env var, type, default, and purpose.'
---

# Configuration Reference

EVOID reads config from `evoid.toml`, `pyproject.toml [tool.evoid]`, or `evoid_config.py`.

## Config Loading Order

1. `evoid.toml` (service-level, highest priority)
2. `pyproject.toml` `[tool.evoid]` (project-level)
3. `evoid_config.py` (Python-native)
4. Defaults (if nothing found)

## Service

| Setting | Env Var | Type | Default | Description |
|---------|---------|------|---------|-------------|
| `service.name` | — | `str` | `"evoid-service"` | Service name |
| `service.version` | — | `str` | `"0.1.0"` | Service version |

## Runtime

| Setting | Env Var | Type | Default | Description |
|---------|---------|------|---------|-------------|
| `runtime.adapter` | `EVOID_ADAPTER` | `str` | `"asgi"` | Transport: `asgi`, `cli`, `telegram`, `robyn`, `websocket` |
| `runtime.host` | `EVOID_HOST` | `str` | `"0.0.0.0"` | Bind host |
| `runtime.port` | `EVOID_PORT` | `int` | `8000` | Bind port (1-65535) |

## Engines

| Setting | Env Var | Type | Default | Description |
|---------|---------|------|---------|-------------|
| `engines.schema` | `EVOID_SCHEMA` | `str` | `"native"` | Schema engine: `native`, `pydantic`, `msgspec`, `attrs` |
| `engines.storage` | `EVOID_STORAGE` | `str` | `"memory"` | Storage: `memory`, `sqlite`, `sqlalchemy`, `redis`, `postgres`, `scylla`, `smart_storage` |
| `engines.cache` | `EVOID_CACHE` | `str` | `"memory"` | Cache: `memory`, `redis` |
| `engines.serializer` | `EVOID_SERIALIZER` | `str` | `"json"` | Serializer: `json`, `msgspec`, `orjson` |
| `engines.di` | `EVOID_DI` | `str` | `"native"` | DI engine: `native` |
| `engines.logger` | `EVOID_LOGGER` | `str` | `"structlog"` | Logger: `structlog`, `loguru` |
| `engines.metrics` | `EVOID_METRICS` | `str` | `"simple"` | Metrics: `simple`, `prometheus` |
| `engines.auth` | `EVOID_AUTH` | `str` | `"simple"` | Auth: `simple`, `jwt` |

### Engine Options

Per-engine connection params via `[engines.options.<name>]`:

```toml
[engines.options.postgresql]
url = "postgres://localhost:5432/mydb"

[engines.options.redis]
url = "redis://localhost:6379"

[engines.options.sqlite]
db_path = "evoid.db"
```

## Pipeline

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `pipeline.processors` | `list[str]` | `["validate", "authorize"]` | Default processor chain |

## Python Config

```python
from evoid.config import config

app = config(
    service={"name": "my-api", "version": "1.0.0"},
    runtime={"adapter": "asgi", "port": 8000},
    engines={"storage": "sqlite", "cache": "redis"},
    pipeline={"processors": ["validate", "authorize"]},
)
```

## TOML Config

```toml
[service]
name = "my-api"
version = "1.0.0"

[runtime]
adapter = "asgi"
host = "0.0.0.0"
port = 8000

[engines]
schema = "native"
storage = "sqlite"
cache = "redis"
serializer = "json"

[pipeline]
processors = ["validate", "authorize"]
```

## pyproject.toml

```toml
[tool.evoid]
adapter = "asgi"
port = 8000

[tool.evoid.engines]
storage = "sqlite"
cache = "memory"
```

## Related

- [Configuration](../learn/configuration.md): conceptual overview
- [Python Config](../learn/configuration.md#python-config-recommended): Python config guide
