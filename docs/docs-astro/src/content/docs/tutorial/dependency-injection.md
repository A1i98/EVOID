---
title: 'Dependency Injection'
description: 'Manage dependencies through the pipeline — data carries what it needs.'
---

# Dependency Injection

Manage dependencies through the pipeline — data carries what it needs.

Sandy's online shop works. But every handler creates its own database connection. When 100 customers order at once, 100 connections open. The server crashes. DI fixes this: one shared connection, injected per request.

!!! info "DI = kitchen supplies"
    Think of `ctx.deps` as the kitchen's supply closet. A processor stocks it (injects the database, the cache, the auth provider). The handler grabs what it needs. Each request gets its own closet — no sharing, no conflicts.

## The IOP Way: Pipeline Injection

Define what your Intent needs, then wire it through the pipeline:

```python
from evoid import Intent, Level, add_intent, register_processor
from evoid.core import Context

# Processor: inject DB session into context
async def inject_db(ctx: Context) -> dict:
    ctx.deps["db"] = create_session()
    return {"db_ready": True}

# Handler: reads injected dependency
async def handle_get_user(ctx: Context) -> dict:
    user_id = ctx.intent.metadata.get("user_id")
    db = ctx.deps["db"]
    user = await db.get_user(user_id)
    return {"id": user.id, "name": user.name}

# Wire it: Intent → Pipeline → Processor → Handler
GET_USER = Intent(
    name="get_user",
    level=Level.STANDARD,
    pipeline=("inject_db", "handle_get_user"),
)

add_intent(GET_USER, handle_get_user)
register_processor("inject_db", inject_db)
```

**That's IOP.** The Intent declares its pipeline. The pipeline provides dependencies. The handler consumes them.

## Wiring with before()

Use `before()` to attach processors to specific intents:

```python
from evoid.core.extend import before

register_processor("inject_db", inject_db)

# Attach to specific intents
before("get_user", "inject_db")
before("create_user", "inject_db")

# Or use intent name pattern
before("GET:/users/{id}", "inject_db")
```

## Request-Scoped Dependencies

Each pipeline execution gets its own Context — `ctx.deps` is naturally request-scoped:

```python
async def inject_auth(ctx: Context) -> dict:
    token = ctx.intent.metadata.get("authorization")
    ctx.deps["auth"] = await verify_token(token)
    return {"auth_ready": True}

async def inject_db(ctx: Context) -> dict:
    ctx.deps["db"] = create_session()
    return {"db_ready": True}

# Chain multiple injectors in the pipeline
GET_ORDER = Intent(
    name="get_order",
    level=Level.CRITICAL,
    pipeline=("inject_auth", "inject_db", "handle_get_order"),
)
```

!!! warning "Lifecycle"
    Dependencies in `ctx.deps` exist for one pipeline execution. They are not shared between requests.

## Shared State Between Processors

Use `ctx.state` for data flow between processors. Use `ctx.deps` for service instances:

```python
async def fetch_user(ctx: Context) -> dict:
    """Processor 1: fetch user, store in state."""
    user_id = ctx.intent.metadata.get("user_id")
    ctx.state["user"] = await ctx.deps["db"].get_user(user_id)
    return {"fetched": True}

async def check_permissions(ctx: Context) -> dict:
    """Processor 2: read state, enforce access."""
    user = ctx.state["user"]
    if user.role != "admin":
        raise PermissionError("Admin access required")
    return {"authorized": True}

GET_ADMIN_RESOURCE = Intent(
    name="get_admin_resource",
    level=Level.CRITICAL,
    pipeline=("inject_db", "fetch_user", "check_permissions", "handle_admin"),
)
```

!!! info "state vs deps"
    `ctx.state` = data flow between processors (write in one, read in next).
    `ctx.deps` = service instances injected for the request (DB, auth, cache).

## Singleton Dependencies

For services that hold connections (database pools, HTTP clients), create once at module level:

```python
# services/cache.py
from evoid import register_processor
from evoid.core import Context

# Module-level singleton — one instance for the process
_cache_client = create_redis_client()

async def inject_cache(ctx: Context) -> dict:
    """Inject the singleton cache client."""
    ctx.deps["cache"] = _cache_client
    return {"cache_injected": True}

register_processor("inject_cache", inject_cache)
```

## @route Style

`@route` decorators auto-create Intents. Use `ctx` for injected dependencies:

```python
from evoid import register_processor
from evoid.adapters.asgi import get, post
from evoid.web.route import Service
from evoid.core import Context
from evoid.core.extend import before

app = Service("api")

async def inject_db(ctx: Context) -> dict:
    ctx.deps["db"] = create_session()
    return {"db_injected": True}

register_processor("inject_db", inject_db)
before("GET:/orders/{id}", "inject_db")

@get("/orders/{id}")
async def get_order(id: int, ctx: Context) -> dict:
    db = ctx.deps["db"]
    order = await db.get_order(id)
    return {"id": order.id, "status": order.status}
```

## @controller Style

Group related routes under a prefix:

```python
from evoid.web.controller import Service, Controller, GET, POST

app = Service("api")

@Controller("/orders")
class OrderController:
    @GET("/{order_id}")
    async def get_order(self, order_id: int, ctx: Context) -> dict:
        db = ctx.deps["db"]
        return {"id": order_id}

    @POST("/")
    async def create_order(self, item_id: int, quantity: int, ctx: Context) -> dict:
        return {"status": "created"}
```

## Summary

| Pattern | Best For | Mechanism |
|---------|----------|-----------|
| Pipeline injection | Per-request services | Processor writes `ctx.deps`, handler reads |
| `ctx.state` | Data between processors | Write in one, read in next |
| Module singleton | Connection pools | One instance per process |
| `before()` | Wiring processors to intents | `before("intent_name", "processor_name")` |
| Pipeline composition | Chaining injectors | `pipeline=("inject_db", "handle")` |

## Plugins and DI

The `evoid-di` plugin takes this further — three levels of dependency injection with fault tolerance:

```python
from evoid_di import di

# Level 1: Simple — name in, instance out
di.register("db", create_db)
db = di.resolve("db")

# Level 2: Scoped — singleton, transient, or per-user
di.register("db", create_db, scope="singleton")  # One connection for all requests
di.register("session", create_session, scope="per_user")  # One session per user

# Level 3: Context-aware — different impl based on Intent level
di = DIEngine(rules_config=rules, implementations=impls)
# CRITICAL intent → PostgreSQL (ACID, audit-friendly)
# STANDARD intent → SQLite (simple, fast)
# EPHEMERAL intent → Redis (temporary, fast)
```

### Fault Tolerance

DI provides automatic failover when services fail:

```python
# Define fallback chain
di.set_fallback("storage.postgresql", ["storage.sqlite", "cache.redis"])

# Health checking
di.set_health_check("cache.redis", lambda: redis.ping())

# Auto-fallback on failure (never crashes)
storage = di.resolve_with_fallback("storage.postgresql")
# Tries: postgresql → sqlite → redis → cluster peers → None

# Resolve first available from list
cache = di.resolve_any("cache.redis", "cache.memory", "storage.sqlite")
```

### Cluster Integration

Cluster nodes share services via DI:

```python
from evoid_cluster import ClusterBridge

bridge = ClusterBridge(config)
await bridge.start()

# Cluster connects its registry to DI
# Remote services become available as fallbacks
storage = di.resolve("storage.postgresql")
# If not local, checks cluster peers automatically
```

### Creating Plugins with DI

All official plugins register with DI automatically. To create your own:

```python
from evoid_di import di

def register_handlers(config=None):
    # 1. Register with DI
    di.register("storage.mydb", lambda: MyStorage(config), scope="singleton")

    # 2. Define fallback chain
    di.set_fallback("storage.mydb", ["storage.sqlite", "cache.redis"])

    # 3. Optional: health check
    di.set_health_check("storage.mydb", lambda: my_storage.ping())

    # 4. Wire to EVOID intents
    from evoid.core import register as register_intent, register_processor

    async def handle_read(ctx):
        storage = di.resolve("storage.mydb")  # resolve via DI
        return await storage.read(ctx.intent.metadata.get("key"))

    register_processor("storage.read", handle_read)
```

**Benefits:**
- Automatic fallback when service fails
- Load balancing across cluster nodes
- Health checking and auto-reconnect
- Smart-storage integration

!!! info "IOP: level-aware DI"
    ```python
    # Same database interface, different backends per level
    # The Intent level determines which database you get
    
    PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)
    # → DI injects PostgreSQL (ACID transactions for money)
    
    GET_PROFILE = Intent(name="get_profile", level=Level.STANDARD)
    # → DI injects SQLite (simple user data)
    
    CACHE_CHECK = Intent(name="cache_check", level=Level.EPHEMERAL)
    # → DI injects Redis (temporary, fast)
    
    # Your handler doesn't know which database it got.
    # It just calls ctx.deps["db"].read(...)
    # The DI plugin figured out the rest based on the level.
    ```

## Scaling Up: From SQLite to PostgreSQL

Sandy's shop handles 10 customers with SQLite. Then 100 come. Then 1000. SQLite locks the database on every write. Orders queue up. The server slows down.

Sandy needs PostgreSQL for production traffic. But she doesn't want to rewrite her handlers. IOP solves this: swap the engine in config, same code.

```bash
evo install postgresql
```

```toml
# evoid.toml — switch from SQLite to PostgreSQL
[engines]
storage = "postgresql"

[engines.options.postgresql]
url = "postgres://localhost:5432/sandy_shop"
```

Her handlers still call `ctx.deps["db"].read(...)`. They don't know which database they got. The DI plugin decided based on config.

### Smart Storage: Route by Level

When Sandy has both SQLite (cheap, fast for simple data) and PostgreSQL (ACID for payments), she needs to route Intents to the right database. The `evoid-smart-storage` plugin does this automatically:

```bash
evo install smart-storage
```

```toml
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

Sandy's payment Intent (CRITICAL) goes to PostgreSQL. Her session check (EPHEMERAL) goes to Redis. Her profile read (STANDARD) goes to SQLite. Same handler code, different backends.
