---
title: 'Installation'
description: '- Python 3.13+ - uv (recommended) or pip'
---

# Installation

## Requirements

- Python 3.13+
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

## Optional Dependencies

EVOID ships with a minimal core. Install extras for specific features:

```bash
# ASGI server (uvicorn + starlette)
uv add "evoid[asgi]"

# Pydantic schema engine
uv add "evoid[pydantic]"

# Redis caching
uv add "evoid[redis]"

# SQLAlchemy storage
uv add "evoid[sqlalchemy]"

# Loguru logging
uv add "evoid[loguru]"

# Everything
uv add "evoid[full]"
```

| Extra | Packages | Use When |
|-------|----------|----------|
| `asgi` | starlette, uvicorn | Running HTTP APIs |
| `pydantic` | pydantic | Schema validation with Pydantic models |
| `redis` | redis | Distributed caching |
| `sqlalchemy` | sqlalchemy, aiosqlite | SQL database storage |
| `loguru` | loguru | Beautiful structured logging |
| `full` | All above | Everything enabled |

!!! note "Python version"
    EVOID requires Python 3.13 or higher. Check your version with `python --version`. If you need multiple Python versions, use `uv python install 3.13`.

## Verify Installation

```bash
evo version
```

Expected output:

```
evo 2.0.0-alpha
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
