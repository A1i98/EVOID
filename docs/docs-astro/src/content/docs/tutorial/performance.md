---
title: 'Performance'
description: 'Pipeline inspection, timeouts, circuit breakers, rate limiting at scale.'
---

# Performance

Pipeline inspection, timeouts, circuit breakers, rate limiting at scale.

## Pipeline Inspection

See exactly what runs and how long it takes:

```python
from evoid import execute, Intent, Level
from evoid.core.runtime import Config

config = Config(inspect=True)
result = await execute(ORDER, config=config, sandwich="BLT", qty=1)

for step in result.steps:
    status = "OK" if step.success else "FAIL"
    print(f"  {step.name}: {step.duration:.4f}s [{status}]")
```

## Timeouts

Prevent slow processors from blocking:

```python
ORDER = Intent(
    name="process_order",
    level=Level.STANDARD,
    timeout=5.0,  # 5 second max
)
```

If a processor exceeds the timeout, the pipeline returns `TimeoutError`.

## Circuit Breaker

Protect against failing services:

```python
from evoid.processors import circuit_breaker

# Register the circuit breaker
from evoid import register_processor
register_processor("circuit_breaker", circuit_breaker)

# Add to critical endpoints
from evoid.core.extend import before
before("process_order", "circuit_breaker")
```

The circuit breaker trips after 3 failures, then resets after 30 seconds.

## Rate Limiting

Protect against abuse:

```python
from evoid.processors import rate_limiter

register_processor("rate_limiter", rate_limiter)

# Apply to all standard endpoints
from evoid.core.extend import before

# Apply to specific intents
before("GET:/menu", "rate_limiter")
before("POST:/orders", "rate_limiter")
```

## Bounded State

Prevent memory leaks in long-running services:

```python
from evoid.processors import rate_limiter, circuit_breaker

# Rate limiter capped at 10,000 entries
# Circuit breaker capped at 1,000 entries
# Auto-eviction on overflow
```

## Performance Tips

| Tip | Why |
|-----|-----|
| Use `ephemeral` for reads | Fastest pipeline, no auth |
| Use `timeout` for external calls | Prevent blocking |
| Use `concurrency` for batch ops | Parallel processing |
| Use `Config(inspect=True)` in dev | Debug pipeline performance |

## Production Monitoring

Track pipeline performance in production:

```python
import time
from evoid import Intent, Level, register_processor
from evoid.core import Context

async def monitor_pipeline(intent: Intent, ctx: Context) -> dict:
    """Track execution metrics."""
    start = time.monotonic()
    ctx.state["monitor_start"] = start
    return {"monitoring": True}

async def report_metrics(intent: Intent, ctx: Context) -> dict:
    """Report execution metrics after pipeline completes."""
    start = ctx.state.get("monitor_start", 0)
    duration = time.monotonic() - start

    # Send to your metrics system (Prometheus, Datadog, etc.)
    print(f"[METRICS] {intent.name}: {duration:.4f}s")

    # Track by level
    level = intent.level.value
    print(f"[METRICS] level={level} duration={duration:.4f}")

    return {"duration": duration}

register_processor("monitor_pipeline", monitor_pipeline)
register_processor("report_metrics", report_metrics)
```

Apply globally:

```python
from evoid.core.extend import before

# Apply to specific intents
before("GET:/menu", "monitor_pipeline")
before("POST:/orders", "monitor_pipeline")
before("POST:/payment", "monitor_pipeline")
```

## Profiling Slow Processors

Find which processor is the bottleneck:

```python
from evoid import execute, Intent, Level
from evoid.core.runtime import Config

async def profile_order():
    config = Config(inspect=True)
    result = await execute(ORDER, config=config, sandwich="BLT", qty=1)

    # Sort by duration
    steps = sorted(result.steps, key=lambda s: s.duration, reverse=True)

    print("Slowest processors:")
    for step in steps[:5]:
        print(f"  {step.name}: {step.duration:.4f}s")
```

## When to Optimize

| Symptom | Fix |
|---------|-----|
| Single request slow | Check pipeline inspection for slow processor |
| High latency under load | Add `concurrency` limit to parallel execution |
| Memory growing | Check rate_limiter/circuit_breaker bounds |
| Timeouts too frequent | Increase `timeout` or optimize processor |

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Pipeline inspection | Per-processor timing and state |
| Timeouts | Limit processor execution time |
| Circuit breaker | Protect against failing services |
| Rate limiting | Prevent abuse |
| Bounded state | Prevent memory leaks |

## Next: Production

Let's deploy Sandy to production — [Production](production.md).
