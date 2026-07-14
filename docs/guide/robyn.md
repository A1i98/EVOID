# Robyn Adapter

EVOID integrates with [Robyn](https://github.com/sparckles/Robyn), a high-performance Python web framework.

## Installation

```bash
uv add evoid robyn
```

## Basic Usage

```python
from evoid.web.route import Service, get, post
from evoid.adapters.robyn import RobynAdapter

app = Service("my-api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": f"User {user_id}"}

@post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created"}

# Run with Robyn adapter
adapter = RobynAdapter(app)
adapter.run(host="0.0.0.0", port=8000)
```

## Features

- 🚀 **High Performance** - Built on Rust-based Robyn
- ⚡ **Async Native** - Full async/await support
- 🔌 **EVOID Integration** - Seamless IOP support
- 📡 **WebSocket Support** - Real-time communication

## Configuration

```python
from evoid.adapters.robyn import RobynAdapter

adapter = RobynAdapter(
    app,
    host="0.0.0.0",
    port=8000,
    workers=4
)
adapter.run()
```

## Comparison

| Feature | Robyn | ASGI (Uvicorn) |
|---------|-------|----------------|
| Performance | ⚡⚡⚡ | ⚡⚡ |
| WebSocket | ✅ | ✅ |
| HTTP/2 | ✅ | ✅ |
| Ease of Setup | Easy | Easy |
