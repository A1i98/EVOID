---
title: 'Parallel Execution'
description: 'Run multiple Intents concurrently for faster responses.'
---

# Parallel Execution

Run multiple Intents concurrently for faster responses.

## Basic Parallel Execution

```python
from evoid import Intent, Level, gather
from evoid.web.route import Service, get

app = Service("api")

USER_API = Intent(name="fetch_users", level=Level.STANDARD)
ORDER_API = Intent(name="fetch_orders", level=Level.STANDARD)

async def fetch_users(intent: Intent) -> list:
    return [{"id": 1}, {"id": 2}]

async def fetch_orders(intent: Intent) -> list:
    return [{"order_id": 101}, {"order_id": 102}]

from evoid import add_intent
add_intent(USER_API, fetch_users)
add_intent(ORDER_API, fetch_orders)

@get("/dashboard")
async def dashboard() -> dict:
    results = await gather(USER_API, ORDER_API)
    return {
        "users": results[0].value,
        "orders": results[1].value,
    }
```

!!! tip "Performance gain"
    Both fetches run at the same time. Total time is the slowest one, not the sum.

## Concurrency Limits

Control how many intents run simultaneously:

```python
# Default: 10 concurrent
results = await gather(intent1, intent2, intent3)

# Custom limit
results = await gather(intent1, intent2, intent3, concurrency=5)
```

## Priority Execution

Execute intents in priority order:

```python
from evoid import Intent, Level
from evoid.core.parallel import gather_with_priority

urgent = Intent(name="urgent_task", level=Level.CRITICAL, priority=10)
normal = Intent(name="normal_task", level=Level.STANDARD, priority=5)
background = Intent(name="bg_task", level=Level.EPHEMERAL, priority=1)

results = await gather_with_priority(urgent, normal, background)
# Urgent runs first, then normal, then background
```

## IntentQueue

Queue-based processing for ordered execution:

```python
from evoid import Intent, Level
from evoid.core.parallel import IntentQueue

queue = IntentQueue(max_concurrent=5)

queue.enqueue(Intent(name="task1", level=Level.CRITICAL), priority=10)
queue.enqueue(Intent(name="task2", level=Level.STANDARD), priority=5)
queue.enqueue(Intent(name="task3", level=Level.EPHEMERAL), priority=1)

results = await queue.process()
```

## CPU-bound Work

!!! warning "Blocking the event loop"
    CPU-intensive tasks block the async event loop. Use `run_in_thread_async` to offload them:

```python

```python
from evoid.core.parallel import run_in_thread_async

def cpu_intensive(data):
    # This would block the event loop
    return sum(x * x for x in range(data))

result = await run_in_thread_async(cpu_intensive, 1000000)
```
