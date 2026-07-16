---
title: 'First Steps'
description: 'Install EVOID, create a project, and run your first endpoint in under 5 minutes.'
---

# First Steps

Install EVOID, create a project, and run your first endpoint in under 5 minutes.

## Install EVOID

=== "uv (Recommended)"

    ```bash
    uv add evoid
    ```

=== "pip"

    ```bash
    pip install evoid
    ```

## Create a Project

```bash
evo init my-api
cd my-api
```

This creates:

```
my-api/
  evoid.toml
  shared/
  services/
```

## Add a Service

```bash
evo service new api
```

This creates `services/api/main.py` with a basic structure.

## Write Your First Endpoint

Edit `services/api/main.py`:

```python
from evoid.web.route import Service, get

app = Service("my-api")

@get("/")
async def home() -> dict:
    return {"message": "Hello from EVOID!"}

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": f"User {user_id}"}
```

## Run the Server

```bash
evo service run api
```

You should see:

```
Starting my-api on http://0.0.0.0:8000
```

## Test It

```bash
curl http://localhost:8000/
# {"message": "Hello from EVOID!"}

curl http://localhost:8000/users/42
# {"id": 42, "name": "User 42"}
```

!!! info "What just happened?"
    Three things occurred behind the scenes:

1. `@get("/")` created an Intent named `GET:/` with level `standard`
2. Your function was registered as a processor for that Intent
3. An ASGI server was started to route HTTP requests to Intents

That's IOP. You declared what you wanted (`GET:/`). EVOID handled how (ASGI, routing, pipeline).

!!! tip "Try it yourself"
    Change the return value and restart the server — the response updates immediately.
