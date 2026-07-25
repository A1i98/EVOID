---
title: 'Cluster'
description: 'Multi-node clustering: connect EVOID nodes into a unified distributed system.'
---

# Cluster

The `evoid-cluster` plugin connects multiple EVOID nodes via WebSocket. Nodes share Intents, not data.

## How It Works

Each node announces its services. ClusterBridge hooks into the local message bus and forwards Intents to remote nodes. No direct data access between nodes. Only Intent and Result flow.

```
Node A (payments) ←→ ClusterBridge ←→ Node B (chat)
```

## Install

```bash
evo plug install evoid-cluster
```

## Configuration

Create `cluster.toml`:

```toml
[node]
id = "node-1"
host = "0.0.0.0"
port = 9000
roles = ["api", "worker"]

[[peers]]
host = "10.0.0.2"
port = 9000

[[services]]
pattern = "chat:*"
```

| Field | Purpose |
|-------|---------|
| `node.id` | Unique node identifier |
| `node.roles` | What this node handles (api, worker, etc.) |
| `peers` | Other nodes to connect to |
| `services.pattern` | Intent patterns this node handles |

## Routing

The IntentRouter decides where each Intent goes:

- Local handler exists: run locally
- No local handler: forward to peer with matching service pattern
- No peer available: return error

Your code doesn't know if the handler is local or remote. The Intent declares what. The cluster decides where.

## Health Checking

Each node monitors peers. If a node goes down, the router skips it and tries the next available peer.

## TLS

Production clusters should enable TLS:

```toml
[node.tls]
cert = "/path/to/cert.pem"
key = "/path/to/key.pem"
```

## Related

- [Plugin Collection](plugin-collection.md): all official plugins
- [Message Bus](message-bus.md): how Intents flow locally
