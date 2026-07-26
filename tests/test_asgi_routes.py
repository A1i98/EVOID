import asyncio

from evoid.adapters.asgi import create_app, get
from evoid.core import clear_registry, register_processor


async def _raw_asgi_request(app, method: str, path: str) -> tuple[int, dict]:
    """Simple raw ASGI caller — no httpx required."""
    response_body = []
    status_code = 200

    scope = {
        "type": "http",
        "method": method.upper(),
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [],
    }

    async def receive():
        return {"type": "http.request", "body": b""}

    async def send(message):
        nonlocal status_code
        if message["type"] == "http.response.start":
            status_code = message["status"]
        elif message["type"] == "http.response.body":
            response_body.append(message.get("body", b""))

    await app(scope, receive, send)
    import json
    body_bytes = b"".join(response_body)
    data = json.loads(body_bytes.decode()) if body_bytes else {}
    return status_code, data


def test_asgi_decorator_routes():
    clear_registry()

    @get("/docs")
    async def docs():
        return {"status": "ok"}

    @get("/users/{user_id}")
    async def get_user(user_id: str):
        return {"user_id": user_id}

    async def docs_proc(ctx):
        return {"status": "ok"}

    async def user_proc(ctx):
        return {"user_id": ctx.metadata["params"]["user_id"]}

    register_processor("GET:/docs", docs_proc)
    register_processor("GET:/users/{user_id}", user_proc)

    app = create_app(name="test")

    # Health check
    code, data = asyncio.run(_raw_asgi_request(app, "GET", "/health"))
    assert code == 200

    # Decorator route /docs
    code, data = asyncio.run(_raw_asgi_request(app, "GET", "/docs"))
    assert code == 200
    assert data["result"] == {"status": "ok"}

    # Parameterized route /users/123
    code, data = asyncio.run(_raw_asgi_request(app, "GET", "/users/123"))
    assert code == 200
    assert data["result"] == {"user_id": "123"}

    # Nonexistent route
    code, data = asyncio.run(_raw_asgi_request(app, "GET", "/unknown"))
    assert code == 404
