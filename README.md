<p align="center">
  <img src="https://img.shields.io/badge/python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/version-0.4.1-orange?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/license-Apache%202.0-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/core%20deps-zero-brightgreen?style=for-the-badge" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/status-Beta-purple?style=for-the-badge" alt="Status">
</p>

<h1 align="center">EVOID</h1>

<p align="center">
  <strong>Reference Runtime for Intent-Oriented Programming</strong>
</p>

<p align="center">
  <em>Data declares what, runtime decides how.</em>
</p>

<p align="center">
  <a href="#what-is-iop">What is IOP?</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#features">Features</a> •
  <a href="#documentation">Docs</a> •
  <a href="https://pypi.org/project/evoid/">PyPI</a>
</p>

---

## What is IOP?

**Intent-Oriented Programming** — your data declares what it needs, the runtime handles how.

```python
from evoid.web.route import Service, get, post

app = Service("my-api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": "Alice"}

@post("/payments", level="critical")
async def process_payment(amount: float) -> dict:
    return {"status": "paid", "amount": amount}
```

Three intent levels control infrastructure:

| Level | Pipeline | Use Case |
|:------|:---------|:---------|
| `ephemeral` | `validate` | Cache, sessions, temp data |
| `standard` | `validate`, `authorize` | User profiles, posts |
| `critical` | `validate`, `authorize`, `audit`, `protect` | Payments, medical, legal |

---

## Install

```bash
uv add evoid
```

**Zero core dependencies** — add only what you need:

```bash
evo install sqlite      # SQLite storage
evo install redis       # Redis cache
evo install pydantic    # Pydantic schema
evo install full        # Everything
```

---

## Quick Start

```bash
evo init my-api
cd my-api
evo service new api
evo service run api
# Server starts at http://0.0.0.0:8000
```

---

## Three Syntax Styles

All IOP underneath. Pick your style:

### @route

```python
from evoid.web.route import Service, get

app = Service("my-api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": "Alice"}
```

### @controller

```python
from evoid.web.controller import Service, Controller, GET, POST

app = Service("my-api")

@Controller("/users")
class UserController:
    @GET("/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id}
```

### Native

```python
from evoid import Intent, Level, add_intent

GET_USER = Intent(name="get_user", level=Level.STANDARD)

async def handler(intent: Intent) -> dict:
    return {"id": 1, "name": "Alice"}

add_intent(GET_USER, handler)
```

---

## Features

<table>
<tr>
<td>

**Zero Dependencies**
Core has no required packages

</td>
<td>

**AI Agent Integration**
Schema export + MCP server

</td>
<td>

**Plugin System**
PyPI + git install

</td>
</tr>
<tr>
<td>

**Python-Native Config**
Type-safe, composable

</td>
<td>

**Pipeline Hooks**
6 lifecycle events

</td>
<td>

**Testing System**
pytest + WebUI dashboard

</td>
</tr>
<tr>
<td>

**Async-Native**
Full async/await support

</td>
<td>

**Parallel Execution**
Concurrent intents

</td>
<td>

**Multi-Adapter**
ASGI, CLI, Telegram, WebSocket

</td>
</tr>
</table>

---

## AI Agent Integration

```python
from evoid import export_schemas
from evoid.adapters.mcp import create_mcp_server

# Export schemas for AI discovery
schemas = export_schemas()

# Create MCP server
server = create_mcp_server("my-api")
```

---

## Plugin System

```bash
evo plug install evoid-redis           # From PyPI
evo plug install git+https://...       # From git
evo plug search cache                  # Search PyPI
evo plug list                          # List installed
```

---

## Configuration

### Python (Recommended)

```python
from evoid.config import config

app = config(
    service={"name": "my-api"},
    runtime={"adapter": "asgi", "port": 8000},
    engines={"storage": "redis"},
)
```

### TOML

```toml
[service]
name = "my-api"

[engines]
storage = "redis"
```

---

## Testing

```python
from evoid.testing import tc
from myapp import GET_USER

def test_get_user():
    return tc(GET_USER, expect={"id": 1})
```

```bash
pytest tests/ -v
pytest tests/ --evoid-webui    # With dashboard
```

---

## CLI Reference

| Command | Alias | Description |
|:--------|:------|:------------|
| `evo init <name>` | `i` | Create project |
| `evo service new <name>` | `s new` | Add service |
| `evo service run <name>` | `s run` | Run service |
| `evo run` | `r` | Run all |
| `evo serve` | `sv` | Quick serve |
| `evo exec <intent>` | `e` | Execute intent |
| `evo install <pkg>` | `ins` | Install dep |
| `evo plug install <name>` | `pl i` | Install plugin |
| `evo plug search <query>` | `pl s` | Search plugins |
| `evo version` | `v` | Version |

---

## Project Structure

```
my-api/
  evoid_config.py       # Python config
  shared/               # Shared code
  services/
    api/
      main.py           # Service code
```

---

## Documentation

**User docs:** [https://evolvebeyond.github.io/EVOID/](https://evolvebeyond.github.io/EVOID/)

**Wiki:** [https://github.com/EvolveBeyond/EVOID/wiki](https://github.com/EvolveBeyond/EVOID/wiki)

**Architecture:** [https://deepwiki.com/EvolveBeyond/EVOID](https://deepwiki.com/EvolveBeyond/EVOID)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

1. Fork → Branch → Commit → PR
2. Tests: `pytest tests/ -v`
3. Lint: `ruff check evoid/`

---

## License

[Apache 2.0](LICENSE)

---

<p align="center">
  <img src="https://raw.githubusercontent.com/EvolveBeyond/EVOID/main/assets/evoid-footer.png" alt="EVOID" width="200">
  <br>
  <sub>Built with IOP principles. Intent is the platform.</sub>
</p>
