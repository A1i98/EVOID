---
title: 'Installation'
description: 'Install EVOID with zero core dependencies. Add only what you need.'
---

# Installation

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

!!! tip "Why uv?"
    `uv` is 10-100x faster than pip and handles virtual environments automatically. Install it from [astral.sh/uv](https://docs.astral.sh/uv/).

## Install EVOID

=== "uv (Recommended)"

    ```bash
    uv add evoid
    ```

=== "pip"

    ```bash
    pip install evoid
    ```

!!! info "Zero core dependencies"
    EVOID has NO required dependencies. Install only what you need.

## Optional Dependencies

Install extras for specific features:

```bash
# ASGI server (starlette + uvicorn)
uv add "evoid[asgi]"

# Pydantic schema engine
uv add "evoid[pydantic]"

# SQLite storage
uv add "evoid[sqlite]"

# Redis caching
uv add "evoid[redis]"

# SQLAlchemy storage (plugin)
uv add "evoid[sqlalchemy]"

# Loguru logging
uv add "evoid[loguru]"

# TOML config support
uv add "evoid[toml]"

# Testing WebUI
uv add "evoid[testing]"

# Everything
uv add "evoid[full]"
```

### Using evo install

```bash
evo install sqlite        # Install SQLite storage
evo install redis         # Install Redis cache
evo install full          # Install all optional deps
```

| Extra | Packages | Use When |
|-------|----------|----------|
| `asgi` | starlette, uvicorn | Running HTTP APIs |
| `pydantic` | pydantic | Schema validation with Pydantic models |
| `sqlite` | aiosqlite | SQLite database storage |
| `redis` | redis | Distributed caching |
| `sqlalchemy` | sqlalchemy, aiosqlite | SQL database storage |
| `loguru` | loguru | Beautiful structured logging |
| `toml` | tomli, tomli_w | TOML config support |
| `testing` | starlette | Test dashboard WebUI |
| `full` | All above | Everything enabled |

## Verify Installation

```bash
evo version
```

Expected output:

```
evo 0.4.1
```

## Create Your First Project

```bash
evo init my-api
cd my-api
evo service new api
evo service run api
```

Server starts at `http://0.0.0.0:8000`. Test it:

```bash
curl http://localhost:8000/
```
