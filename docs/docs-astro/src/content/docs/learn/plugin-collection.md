---
title: 'Plugin Collection'
description: 'Official EVOID plugins on PyPI — storage, cache, DI, auth, tasks, cluster, game, transport, scheduler, dashboard.'
---

# Plugin Collection

!!! tip "New here?"
    EVOID ships with built-in engines for storage, cache, DI, and more. You don't need any plugins to get started. See [Plugins and Engines](plugins.md) for what's included, or [Plugin Ecosystem](plugin-ecosystem.md) to build your own.

Official EVOID plugins on PyPI. Each is an independent package — install only what you need.

!!! info "IOP in every plugin"
    Every plugin follows IOP principles: data declares what it needs, the runtime handles how. A storage plugin doesn't know about your business logic. An auth plugin doesn't know about your database. They're Lego blocks — snap them together, and the pipeline composes them.

## Quick Install

```bash
# Via evo CLI (short names)
evo install di
evo install redis
evo install smart-storage

# Via uv
uv add evoid-di
uv add evoid-redis
uv add evoid-smart-storage
```

## Available Plugins

### evoid-base — Shared Contracts

The foundation. Defines `StorageEngine`, `CacheEngine`, and `LoggerEngine` protocols that all other plugins implement.

```python
from evoid_base import StorageEngine, CacheEngine

# Every storage plugin implements this interface
class MyStorage(StorageEngine):
    async def read(self, key: str) -> dict | None: ...
    async def write(self, key: str, data: dict) -> None: ...
    async def delete(self, key: str) -> None: ...
    async def health(self) -> bool: ...
```

**Why it matters:** You can swap `evoid-sqlite` for `evoid-postgresql` without changing a single line of business code. The contract stays the same. That's IOP — the Intent says "store this," and the pipeline routes to whichever engine you installed.

---

### Storage Plugins

| Package | Install | Best For |
|---------|---------|----------|
| `evoid-sqlite` | `evo install sqlite` | Prototyping, single-user apps, embedded |
| `evoid-postgresql` | `evo install postgresql` | Production, multi-tenant, complex queries |
| `evoid-scylla` | `evo install scylla` | High-throughput, distributed, Cassandra-compatible |

```python
from evoid_sqlite import create_storage

storage = create_storage("my_app.db")
await storage.write("user:1", {"name": "Alice"})
user = await storage.read("user:1")
```

!!! example "IOP in action"
    ```python
    # The Intent doesn't care which database you use
    SAVE_USER = Intent(name="save_user", level=Level.STANDARD)
    
    # Pipeline: validate → authorize → your handler
    # Storage plugin: chosen at config time, not code time
    
    # Switch from SQLite to PostgreSQL? Change one config line:
    # storage = "postgresql"  (was "sqlite")
    # Your handler code stays identical.
    ```

---

### evoid-redis — Redis Cache

Async Redis cache with TTL. The standard choice for ephemeral data.

```bash
evo install redis
```

```python
from evoid_redis import create_cache

cache = create_cache("redis://localhost")
await cache.set("session:abc123", {"user": "Alice"}, ttl=3600)
session = await cache.get("session:abc123")
```

!!! example "IOP: ephemeral level"
    ```python
    # Ephemeral Intent — cache lookup, no auth, no audit
    GET_SESSION = Intent(name="get_session", level=Level.EPHEMERAL)
    
    async def handle_session(ctx: Context) -> dict:
        session_id = ctx.metadata["session_id"]
        # The cache plugin handles TTL, serialization, connection pooling
        # Your code just reads and writes
        return await ctx.deps["cache"].get(f"session:{session_id}")
    
    # Pipeline: validate (5s timeout) — that's it.
    # No authorize. No audit. Fast path.
    ```

---

### evoid-smart-storage — Multi-DB Routing

Routes data to different backends automatically. The traffic controller for your storage layer.

```bash
evo install smart-storage
```

```toml
# evoid.toml
[engines]
storage = "smart_storage"

[engines.smart_storage.mapping]
credentials = "postgresql"    # Sensitive data → PostgreSQL
session = "redis"             # Temporary data → Redis
logs = "memory"               # Debug data → Memory

[engines.smart_storage.level_routing]
critical = "postgresql"       # Payments → PostgreSQL (ACID)
standard = "sqlite"           # Profiles → SQLite (simple)
```

!!! example "IOP: level-aware routing"
    ```python
    # This Intent is CRITICAL — smart-storage routes to PostgreSQL
    PROCESS_PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)
    
    # This Intent is EPHEMERAL — smart-storage routes to Redis
    CACHE_HIT = Intent(name="cache_check", level=Level.EPHEMERAL)
    
    # Same business code, different backends — the level decides.
    # No if/else in your handler. No database imports.
    ```

---

### evoid-di — Dependency Injection

Three levels of complexity in one package. From "give me the thing" to "give me the right thing based on who's asking."

```bash
evo install di
```

```python
from evoid_di import DIEngine

# Level 1: Simple — name in, instance out
di = DIEngine()
di.register("db", create_db)
db = di.resolve("db")

# Level 2: Scoped — singleton, transient, or per-user
di.register("db", create_db, scope="singleton")
di.register("session", create_session, scope="per_user")

# Level 3: Context-aware — different impl based on Intent level
di = DIEngine(rules_config=rules, implementations=impls)
instance = await di.resolve("notifier", ctx)
# CRITICAL intent → EmailNotifier
# STANDARD intent → SlackNotifier
# EPHEMERAL intent → LogNotifier
```

!!! example "IOP: context-aware DI"
    ```python
    # Same interface, different implementations per level
    rules = [
        Rule(condition="level == CRITICAL", target="email_notifier"),
        Rule(condition="level == STANDARD", target="slack_notifier"),
    ]
    
    # The Intent declares its level. DI decides which notifier to inject.
    # Your processor just calls ctx.deps["notifier"].send(...)
    # No switch/case. No config reading. The pipeline does it.
    ```

---

### evoid-auth — Authentication & Authorization

Bring your own provider — no forced JWT, no forced OAuth. Just a function that takes a token and returns a role.

```bash
evo install auth
```

```python
from evoid_auth import register_provider

async def my_auth(token: str) -> dict:
    user = await db.find_by_token(token)
    return {"user": user.name, "role": user.role}

register_provider("my_auth", my_auth)

# Wire to pipeline
from evoid.core.extend import before
before("GET:/users", "authenticate")
```

!!! example "IOP: standard + critical levels"
    ```python
    # STANDARD: validate + authorize (your auth provider runs here)
    GET_PROFILE = Intent(name="get_profile", level=Level.STANDARD)
    # Pipeline: validate → authorize → handler
    # authorize calls your provider, checks role ≥ viewer
    
    # CRITICAL: validate + authorize + audit + protect
    TRANSFER_MONEY = Intent(name="transfer_money", level=Level.CRITICAL)
    # Pipeline: validate → authorize → audit → protect → handler
    # Same auth check, plus audit log, plus protection layer
    
    # EPHEMERAL: validate only (no auth needed)
    HEALTH_CHECK = Intent(name="health_check", level=Level.EPHEMERAL)
    # Pipeline: validate — that's it. Fast, no overhead.
    ```

---

### evoid-tasks — Background Tasks

Godot-inspired task lifecycle with EVOID pipeline integration. Fire-and-forget, scheduled, or event-driven.

```bash
evo install tasks
uv add "evoid-tasks[loguru]"  # with structured logging
```

```python
from evoid_tasks import scheduler, TaskContext

# Fire-and-forget
scheduler.run(send_email, to="alice@example.com")

# Scheduled with lifecycle
@scheduler.task(interval=60)
async def monitor(ctx: TaskContext):
    if ctx.tick:
        await check_levels()

# Event-driven
@scheduler.on("order_placed")
async def update_stats(ctx: TaskContext):
    await recalc(ctx.event_data)
```

!!! example "IOP: tasks as processors"
    ```python
    from evoid_tasks import as_intent
    
    # A background task becomes an IOP Intent
    SYNC_INVENTORY = as_intent(
        name="sync_inventory",
        level=Level.STANDARD,
        pipeline=("validate", "authorize"),
    )
    
    # The task runs through the same pipeline as any other Intent
    # Same auth, same validation, same audit — because it's IOP
    # No special "background task" logic. Just a processor.
    ```

---

### evoid-scheduler — Priority-Aware Scheduling

Replaces EVOID's built-in parallel execution with a system-aware priority scheduler. Auto-defers low-priority tasks when the system is overloaded.

```bash
evo plug install evoid-scheduler
```

```python
from evoid_scheduler import SchedulerEngine, Priority

scheduler = SchedulerEngine()

# High-priority intent goes first
scheduler.submit(process_payment, priority=Priority.CRITICAL)

# Low-priority gets deferred if CPU is busy
scheduler.submit(sync_analytics, priority=Priority.LOW)
```

!!! example "IOP: priority in metadata"
    ```python
    # Priority declared in Intent metadata
    PAYMENT = Intent(
        name="process_payment",
        level=Level.CRITICAL,
        metadata={"priority": Priority.CRITICAL},  # 100
    )
    
    ANALYTICS = Intent(
        name="sync_analytics",
        level=Level.STANDARD,
        metadata={"priority": Priority.LOW},  # 25
    )
    
    # Scheduler reads system load. If CPU > 80%:
    #   - CRITICAL intents run immediately
    #   - LOW intents get deferred to a queue
    # Your code doesn't know this happens. The pipeline handles it.
    ```

---

### evoid-cluster — Multi-Node Clustering

Connects multiple EVOID nodes into a unified distributed system via WebSocket. Nodes share Intents, not data.

```bash
evo plug install evoid-cluster
```

```toml
# cluster.toml
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

!!! example "IOP: distributed intents"
    ```python
    # Node 1 handles payments
    PROCESS_PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)
    
    # Node 2 handles chat
    SEND_MESSAGE = Intent(name="send_message", level=Level.STANDARD)
    
    # ClusterBridge routes automatically:
    # - "process_payment" stays on Node 1 (local handler)
    # - "chat:send" forwards to Node 2 (remote handler)
    # - Result comes back via WebSocket
    
    # Your code doesn't know if the handler is local or remote.
    # The Intent declares what. The cluster decides where.
    ```

---

### evoid-godot — Game Integration

Server-side adapter for connecting Godot games to EVOID. Works with the GDScript client plugin.

```bash
evo plug install evoid-godot
```

```python
from evoid_godot import setup_game_subscriptions, game_intent_handler

# Setup default handlers for game events
setup_game_subscriptions("my-game")
```

!!! example "IOP: game intents"
    ```python
    # From Godot client: EvoidApp.send_intent("player_move", {"x": 10, "y": 20})
    # Server receives it as an Intent:
    
    PLAYER_MOVE = Intent(
        name="game:my-game:player_move",
        level=Level.EPHEMERAL,  # Game state is temporary
        metadata={"player_id": "abc", "x": 10, "y": 20},
    )
    
    # Pipeline: validate — that's it. Fast, no auth for movement.
    # But a "purchase_item" intent? That's CRITICAL:
    
    PURCHASE_ITEM = Intent(
        name="game:my-game:purchase_item",
        level=Level.CRITICAL,  # Real money involved
        metadata={"player_id": "abc", "item": "sword", "price": 9.99},
    )
    # Pipeline: validate → authorize → audit → protect → handler
    ```

---

### evoid-transport — Low-Latency UDP

Binary UDP protocol for game state synchronization. ~0.5ms overhead vs ~2-5ms for WebSocket.

```bash
evo plug install evoid-transport
```

```python
from evoid_transport import EvoidUDPPort

transport = EvoidUDPPort()
await transport.start("my-game")

# Broadcast state to all players every tick
await transport.broadcast_state_sync(game_state, tick=60)

# Measure latency per client
latency = await transport.measure_latency("player-123")
```

!!! example "IOP: channels map to levels"
    ```python
    # Channel 0 (RELIABLE) — card plays, purchases
    # Channel 1 (UNRELIABLE) — position updates, animations
    # Channel 2 (CHAT) — chat messages
    
    # This maps directly to IOP levels:
    # RELIABLE + CRITICAL = payments, legal moves
    # RELIABLE + STANDARD = card plays, chat
    # UNRELIABLE + EPHEMERAL = position, animation frames
    
    # The transport doesn't know your game logic.
    # Your Intent's level determines the channel.
    ```

---

### evoid-dashboard — Monitoring Dashboard

ASGI-based web dashboard. Service map, intent registry, message bus history, DB viewer.

```bash
evo install dashboard
uv add "evoid-dashboard[full]"  # with jinja2 + uvicorn
```

```python
from evoid_dashboard import create_dashboard

# Run on port 8001
create_dashboard(port=8001)
```

Open `http://localhost:8001` to see:
- Service map with connections
- All registered Intents
- Message bus history
- Database connections
- System info

!!! example "IOP: see your pipeline in action"
    ```python
    # The dashboard shows every Intent with its level and pipeline:
    #
    # Intent              Level      Pipeline                          Status
    # get_user            STANDARD   validate → authorize → handler    ✅ 2ms
    # process_payment     CRITICAL   validate → authorize → audit →    ✅ 15ms
    #                                 protect → handler
    # cache_check         EPHEMERAL  validate → handler                ✅ 0.3ms
    #
    # You see exactly what IOP gives you: levels determine pipelines,
    # pipelines determine infrastructure, and the dashboard shows it all.
    ```

---

## Combining Plugins

Plugins are Lego blocks. Snap together what you need:

```toml
# evoid.toml — full stack
[engines]
storage = "smart_storage"
cache = "redis"
di = "di"

[adapter]
type = "asgi"
port = 8000
```

```python
from evoid_di import DIEngine
from evoid_auth import register_provider
from evoid_tasks import scheduler

# Smart Storage routes by Intent level
di = DIEngine(rules_config=rules, implementations={
    "sqlite": lambda: create_sqlite("app.db"),
    "redis": lambda: create_redis("redis://localhost"),
    "postgresql": lambda: create_postgres("postgres://..."),
})

# Auth with custom provider
register_provider("jwt", jwt_auth)

# Background task through the same pipeline
@scheduler.task(interval=300)
async def sync_inventory(ctx):
    await sync_all_locations()
```

!!! example "Full IOP stack in action"
    ```python
    # A payment comes in:
    PROCESS_PAYMENT = Intent(
        name="process_payment",
        level=Level.CRITICAL,
        metadata={"amount": 99.99, "currency": "USD"},
    )
    
    # Pipeline executes:
    # 1. validate      → schema check (built-in)
    # 2. authorize     → evoid-auth checks role (plugin)
    # 3. audit         → logs to PostgreSQL via smart-storage (plugin)
    # 4. protect       → rate limit + circuit breaker (built-in)
    # 5. handler       → your payment code
    #
    # Infrastructure chosen by:
    #   - Level (CRITICAL → full pipeline)
    #   - smart-storage config (critical → PostgreSQL)
    #   - DI rules (CRITICAL → email notifier)
    #
    # Your handler? Just processes the payment. That's IOP.
    ```

## Plugin Standard

Every plugin follows the EVOID plugin standard:

1. `pyproject.toml` with `evoid>=0.4.0` dependency
2. `evoid_plugin.json` manifest
3. `register_plugin()` entry point
4. IOP-compliant code (data + functions)

See [Plugin Standard](plugin-standard.md) for details.
