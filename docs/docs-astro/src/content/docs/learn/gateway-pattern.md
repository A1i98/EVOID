---
title: 'Gateway Pattern'
description: 'The gateway is your app entry point. All external requests flow through it to services via the message bus.'
---

# Gateway Pattern

When you run `evo init`, a **gateway** service is created automatically. It's the entry point for all external requests. Every other service lives behind it.

## What Is the Gateway

The gateway is a regular EVOID service. Nothing special about its code. What makes it a "gateway" is its role: it receives HTTP requests and routes them to the right service via the message bus.

```
HTTP Request → Gateway → Message Bus → Service
                     ← Response ←
```

## Why a Gateway

Without a gateway, each service exposes its own HTTP endpoint:

```
Client → Order Service (port 8001)
Client → Payment Service (port 8002)
Client → Inventory Service (port 8003)
```

The client must know every service's URL. Adding a service means updating the client.

With a gateway:

```
Client → Gateway (port 8000) → Message Bus → any service
```

The client only knows one URL. The gateway handles routing.

## Gateway Structure

`evo init` creates this:

```
my-project/
├── services/
│   └── gateway/
│       ├── evoid.toml      # port 8000
│       └── main.py         # @get("/health"), routes to other services
├── shared/
└── pyproject.toml
```

The gateway starts on port 8000. New services get 8001, 8002, etc.

## How Routing Works

The gateway uses the message bus to route Intents:

```python
from evoid import Intent, Level, publish

# Gateway receives HTTP request
# Creates Intent from the request
# Publishes to message bus
# The right service handles it

intent = Intent(
    name="process_payment",
    level=Level.CRITICAL,
    metadata={"amount": 99.99},
)
result = await publish(intent)
```

Services subscribe to specific Intent names. The bus delivers to whoever is listening.

## Gateway vs Direct Calls

| Pattern | Coupling | Scaling | Discovery |
|---------|----------|---------|-----------|
| Direct HTTP | Each service knows others | Hard to add/remove | Manual URLs |
| Gateway + Bus | Services only know bus | Add/remove freely | Intent names |

## Adding Services

```bash
evo service new api        # port 8001
evo service new payments   # port 8002
evo service new inventory  # port 8003
```

The gateway doesn't need to know about these services. When a service registers an Intent handler, the bus makes it available. The gateway routes by Intent name, not by service URL.

## Gateway in Production

In production, the gateway is the only externally exposed service. Internal services communicate via the message bus. The gateway handles:

- HTTP → Intent conversion
- Authentication (via pipeline)
- Rate limiting (via pipeline)
- Load balancing (via `evoid-cluster`)

## Related

- [Message Bus](message-bus.md): how Intents flow between services
- [Inter-Service](../tutorial/inter-service.md): tutorial walkthrough
- [Cluster](cluster.md): connecting gateways across machines
