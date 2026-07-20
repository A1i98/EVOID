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

Install extras for specific features. Core EVOID has zero required dependencies.

### Built-in Extras

```bash
# ASGI server (starlette + uvicorn)
uv add "evoid[asgi]"

# Pydantic schema engine
uv add "evoid[pydantic]"

# SQLite storage
uv add "evoid[sqlite]"

# Loguru logging
uv add "evoid[loguru]"

# TOML config support
uv add "evoid[toml]"

# Testing WebUI
uv add "evoid[testing]"

# Everything
uv add "evoid[full]"
```

| Extra | Packages | Use When |
|-------|----------|----------|
| `asgi` | starlette, uvicorn | Running HTTP APIs |
| `pydantic` | pydantic | Schema validation with Pydantic models |
| `sqlite` | aiosqlite | SQLite database storage |
| `loguru` | loguru | Beautiful structured logging |
| `toml` | tomli, tomli_w | TOML config support |
| `testing` | starlette | Test dashboard WebUI |
| `full` | All above | Everything enabled |

### Using evo install

```bash
evo install sqlite        # Install SQLite storage
evo install full          # Install all optional deps
```

### Plugins (Advanced)

Need Redis, PostgreSQL, or advanced features? Install plugins from PyPI:

```bash
# Via evo CLI
evo plug install evoid-redis           # Redis cache
evo plug install evoid-postgresql      # PostgreSQL storage
evo plug install evoid-di              # Advanced DI
evo plug install evoid-auth            # Custom auth providers

# Or via pip/uv
uv add evoid-redis
uv add evoid-postgresql

# Search for plugins
evo plug search cache

# List installed
evo plug list
```

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
