---
title: 'Production'
description: "Deploy, monitor, and scale Sandy's franchise."
---

# Production

Deploy, monitor, and scale Sandy's franchise.

## Production Config

```toml
# evoid.toml
[project]
name = "sandy-franchise"
version = "1.0.0"

[runtime]
adapter = "asgi"
host = "0.0.0.0"
port = 8000

[engines]
schema = "native"
storage = "sqlite"
cache = "redis"
logger = "loguru"

[pipeline]
timeout = 10.0
```

## Running in Production

```bash
# With uvicorn
uvicorn my_app:app --host 0.0.0.0 --port 8000 --workers 4

# Or with evo CLI
evo service run sandy-franchise --host 0.0.0.0 --port 8000
```

## Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install evoid
EXPOSE 8000
CMD ["evo", "service", "run", "sandy-franchise"]
```

## Monitoring

```python
from evoid.core.pipeline import Result

async def monitor(intent: Intent) -> dict:
    """Track pipeline performance."""
    result = await execute(intent)

    # Log metrics
    print(f"Intent: {intent.name}")
    print(f"Duration: {result.duration:.3f}s")
    print(f"Processors: {len(result.processors)}")
    print(f"Success: {result.success}")

    return result.value
```

## Scaling

| Strategy | When |
|----------|------|
| Multiple workers | CPU-bound, single location |
| Multiple services | Different domains (orders, inventory) |
| Message Bus | Cross-service communication |
| Parallel execution | Batch processing |

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Production config | Settings for real deployment |
| uvicorn / Docker | Running in production |
| Monitoring | Track performance and errors |
| Scaling strategies | Workers, services, parallelism |

## Next: What's Next

Let's recap Sandy's journey — [What's Next](whats-next.md).
