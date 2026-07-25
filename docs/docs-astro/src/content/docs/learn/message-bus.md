---
title: 'Message Bus'
description: 'Publish/subscribe for decoupled service communication.'
---

# Message Bus

Services communicate through Intents, not direct function calls. The message bus routes Intents between handlers.

## Publish and Subscribe

```python
from evoid import Intent, Level, publish, subscribe

# Subscribe to an Intent
subscribe("order_placed", handle_order)

# Publish an Intent
await publish(Intent(name="order_placed", level=Level.STANDARD))
```

The publisher doesn't know who handles the Intent. The subscriber doesn't know who published it. Both are decoupled.

## How It Works

1. `publish(intent)` adds the Intent to the message bus
2. Bus looks up subscribers for `intent.name`
3. Each subscriber's handler runs with the Intent
4. Results are collected (or discarded for fire-and-forget)

## Use Cases

**Cross-service events**: Service A publishes `order_placed`, Service B (inventory) and Service C (notifications) both subscribe.

**Async workflows**: Publish an Intent, let the pipeline handle it in the background.

**Plugin hooks**: Plugins subscribe to lifecycle events without modifying your code.

## Related

- [Pipeline](pipeline.md): how Intents execute
- [Adapters](adapters.md): how external events become Intents
