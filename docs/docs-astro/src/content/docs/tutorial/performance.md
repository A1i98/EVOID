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
from evoid.core.extend import before_all
from evoid import Level
before_all("rate_limiter", level=Level.STANDARD)
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
