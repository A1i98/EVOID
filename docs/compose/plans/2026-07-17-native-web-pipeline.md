# Native Package + Web Pipeline — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `evoid/native/` as the top-level IOP syntax package (the "mother syntax" that works on ALL adapters), and reorganize `evoid/web/` to use it. Web-specific features (route, controller, pipeline) are sub-modules of `evoid.web` that consume `native`.

**Architecture:** `evoid.native` = core IOP syntax (Service, create_service, on, execute_service) — adapter-agnostic. `evoid.web` = web-specific layer (route decorators, controller decorators, web pipeline) that imports from `native` and adds HTTP semantics. `iop_style.py` is deleted — replaced by `native`.

**Tech Stack:** Python 3.13+, Starlette (ASGI), existing EVOID core

## Global Constraints

- IOP compliance mandatory: data = frozen dataclass, processors = Callable, pipeline = tuple of strings
- User communicates in Persian — respond in Persian
- No new dependencies
- `native` is adapter-agnostic — works on web, CLI, Telegram, anything
- Tutorial remains English-only

---

## File Structure

```
evoid/
├── __init__.py                    # MODIFY: add native re-exports
├── native/
│   ├── __init__.py                # CREATE: IOP mother syntax (Service, create_service, on, execute_service, run)
│   └── pipeline.py                # CREATE: auto-detect adapter, create web pipeline
├── web/
│   ├── __init__.py                # MODIFY: import from native, re-export web stuff
│   ├── route.py                   # KEEP: @route decorators, import Service from native
│   ├── controller.py              # KEEP: @controller decorators, import Service from native
│   └── iop_style.py               # DELETE: replaced by evoid.native
├── core/                          # UNCHANGED
├── adapters/                      # UNCHANGED
└── ...

examples/
├── 09_fastapi_style/main.py       # MODIFY: from evoid.web.route import ...
├── 10_nestjs_style/main.py        # MODIFY: from evoid.web.controller import ...
└── 11_iop_style/main.py           # MODIFY: from evoid.native import ...
```

---

### Task 1: Create `evoid/native/__init__.py` — IOP Mother Syntax

**Covers:** Core IOP syntax package, replaces iop_style.py, adapter-agnostic

**Files:**
- Create: `evoid/native/__init__.py`

**Interfaces:**
- Consumes: `evoid.core.intent.Intent`, `evoid.core.intent.Level`, `evoid.core.register`, `evoid.core.register_processor`, `evoid.core.Context`, `evoid.core.runtime.execute`
- Produces: `Service`, `create_service`, `on`, `execute_service`, `run`

- [ ] **Step 1: Create native package directory**

```bash
mkdir -p evoid/native
```

- [ ] **Step 2: Write `evoid/native/__init__.py`**

```python
"""Native — IOP mother syntax.

The base syntax for ALL Intent-Oriented Programming in EVOID.
Works on ANY adapter: web, CLI, Telegram, WebSocket, MQTT, etc.

Usage:
    from evoid.native import create_service, on

    app = create_service("my-service")
    on(app, Intent(name="hello"), handler)
    await execute_service(app, "hello")

This is NOT web-specific. It's the IOP foundation.
Web features live in evoid.web (route, controller, pipeline).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

from ..core.intent import Intent, Level
from ..core import register, register_processor, Context
from ..core.runtime import execute as _execute


# Handler type: takes Intent, returns result
Handler = Callable[[Intent], Awaitable[Any]]


@dataclass
class Service:
    """Service — pure data (name + intents + handlers).

    This is the IOP-level Service, NOT evoid.core.Service (which is for
    inter-service communication via message bus).
    """

    name: str
    intents: list[Intent] = field(default_factory=list)
    handlers: dict[str, Handler] = field(default_factory=dict)


def create_service(name: str) -> Service:
    """Create a service — IOP mother syntax."""
    return Service(name=name)


def on(service: Service, intent: Intent, handler: Handler) -> None:
    """Register a handler for an intent."""
    service.intents.append(intent)
    service.handlers[intent.name] = handler
    register(intent)
    register_processor(intent.name, handler)


async def execute_service(service: Service, intent_name: str, **kwargs: Any) -> Any:
    """Execute an intent by name."""
    return await _execute(intent_name, **kwargs)


async def run(service: Service, host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the service via auto-detected adapter.

    Auto-detects: FastAPI/Starlette (ASGI) or Robyn.
    For explicit adapter choice, use evoid.native.pipeline directly.
    """
    from .pipeline import detect, create_web_pipeline

    pipeline = create_web_pipeline(service)
    await pipeline.run(host=host, port=port)
```

- [ ] **Step 3: Verify syntax**

```bash
python -c "from evoid.native import Service, create_service, on, execute_service, run; print('native OK')"
```

Expected: `native OK`

- [ ] **Step 4: Commit**

```bash
git add evoid/native/__init__.py
git commit -m "feat(native): create IOP mother syntax package"
```

---

### Task 2: Create `evoid/native/pipeline.py` — Web Pipeline

**Covers:** Auto-detect framework, web pipeline, adapter selection

**Files:**
- Create: `evoid/native/pipeline.py`

**Interfaces:**
- Consumes: `evoid.native.Service`, `evoid.adapters.asgi`, `evoid.adapters.robyn`
- Produces: `WebPipeline`, `detect()`, `create_web_pipeline()`

- [ ] **Step 1: Write `evoid/native/pipeline.py`**

```python
"""Web Pipeline — Auto-detect framework, wire native service to web adapter.

Usage:
    from evoid.native.pipeline import detect, create_web_pipeline

    pipeline = create_web_pipeline(service)
    await pipeline.run(port=8000)

Auto-detects: FastAPI/Starlette (ASGI) or Robyn.
Override: adapter="asgi" | "robyn"
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class WebPipeline:
    """Web pipeline — wires native Service to web framework."""

    service: Any  # native.Service
    adapter: str = "auto"
    host: str = "0.0.0.0"
    port: int = 8000

    async def run(self, host: str | None = None, port: int | None = None) -> None:
        """Run the web pipeline."""
        h = host or self.host
        p = port or self.port

        if self.adapter == "robyn":
            await self._run_robyn(h, p)
        else:
            await self._run_asgi(h, p)

    async def _run_asgi(self, host: str, port: int) -> None:
        from ..adapters.asgi import create_app
        import uvicorn

        handlers = {}
        for intent in self.service.intents:
            handlers[intent.name] = self.service.handlers[intent.name]

        asgi_app = create_app(name=self.service.name, handlers=handlers)
        print(f"Starting {self.service.name} on http://{host}:{port}")
        uvicorn.run(asgi_app, host=host, port=port)

    async def _run_robyn(self, host: str, port: int) -> None:
        from ..adapters.robyn import create_app

        app = create_app(name=self.service.name)
        for intent in self.service.intents:
            handler = self.service.handlers[intent.name]
            method = intent.metadata.get("method", "GET").lower()
            path = intent.metadata.get("path", "/")

            route_fn = getattr(app, method, None)
            if route_fn:
                route_fn(path)(handler)

        app.start(host=host, port=port)


def detect() -> str:
    """Auto-detect which web framework is installed.

    Returns "robyn" if Robyn is installed, "asgi" otherwise.
    """
    try:
        import robyn  # noqa: F401
        return "robyn"
    except ImportError:
        return "asgi"


def create_web_pipeline(
    service: Any,
    adapter: str | None = None,
    host: str = "0.0.0.0",
    port: int = 8000,
) -> WebPipeline:
    """Create a web pipeline for a native service.

    Args:
        service: native.Service with registered intents and handlers
        adapter: "auto" (default), "asgi", or "robyn"
        host: Bind host
        port: Bind port
    """
    resolved_adapter = adapter or detect()

    return WebPipeline(
        service=service,
        adapter=resolved_adapter,
        host=host,
        port=port,
    )
```

- [ ] **Step 2: Verify imports**

```bash
python -c "from evoid.native.pipeline import detect, create_web_pipeline, WebPipeline; print('pipeline OK')"
```

Expected: `pipeline OK`

- [ ] **Step 3: Commit**

```bash
git add evoid/native/pipeline.py
git commit -m "feat(native): add web pipeline with auto-detect framework"
```

---

### Task 3: Update `evoid/web/route.py` — Import Service from Native

**Coves:** route.py uses native.Service instead of its own Service

**Files:**
- Modify: `evoid/web/route.py`

**Interfaces:**
- Consumes: `evoid.native.Service` (via `from ..native import Service`)
- Produces: Same API (get, post, put, delete, etc.) but Service comes from native

- [ ] **Step 1: Update `evoid/web/route.py` imports**

Replace the top section of route.py:

```python
"""@route Syntax — Function-based routes, IOP underneath.

IOP: Decorators auto-create Intents from route path + method.
User just writes @get("/path") — Intent is created automatically.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Awaitable

from ..core.intent import Intent, Level
from ..core import register, register_processor, Context
from ..core.extend import (
    before as _before,
    after as _after,
    before_processor as _before_processor,
    after_processor as _after_processor,
    replace_pipeline as _replace_pipeline,
)
from ..native import Service  # IOP mother syntax


# Handler type
Handler = Callable[..., Awaitable[Any]]


@dataclass
class App:
    """App — pure data (name)."""

    name: str


def _create_intent(method: str, path: str, level: str = "standard") -> Intent:
    """Auto-create Intent from method + path."""
    intent_level = Level(level) if level in ("ephemeral", "standard", "critical") else Level.STANDARD
    return Intent(
        name=f"{method.upper()}:{path}",
        level=intent_level,
        metadata={"method": method, "path": path},
    )


def get(path: str, level: str = "standard") -> Callable:
    """GET endpoint — auto-creates Intent."""
    def decorator(func: Handler) -> Handler:
        intent = _create_intent("GET", path, level)
        register(intent)

        async def processor(ctx: Context) -> Any:
            params = ctx.metadata.get("params", {})
            return await func(**params)

        register_processor(intent.name, processor)
        func._evoid_intent = intent
        return func
    return decorator


def post(path: str, level: str = "standard") -> Callable:
    """POST endpoint — auto-creates Intent."""
    def decorator(func: Handler) -> Handler:
        intent = _create_intent("POST", path, level)
        register(intent)

        async def processor(ctx: Context) -> Any:
            body = ctx.metadata.get("body", {})
            return await func(**body)

        register_processor(intent.name, processor)
        func._evoid_intent = intent
        return func
    return decorator


def put(path: str, level: str = "standard") -> Callable:
    """PUT endpoint — auto-creates Intent."""
    def decorator(func: Handler) -> Handler:
        intent = _create_intent("PUT", path, level)
        register(intent)

        async def processor(ctx: Context) -> Any:
            body = ctx.metadata.get("body", {})
            return await func(**body)

        register_processor(intent.name, processor)
        func._evoid_intent = intent
        return func
    return decorator


def delete(path: str, level: str = "standard") -> Callable:
    """DELETE endpoint — auto-creates Intent."""
    def decorator(func: Handler) -> Handler:
        intent = _create_intent("DELETE", path, level)
        register(intent)

        async def processor(ctx: Context) -> Any:
            params = ctx.metadata.get("params", {})
            return await func(**params)

        register_processor(intent.name, processor)
        func._evoid_intent = intent
        return func
    return decorator


def before(route: str, processor: str) -> None:
    _before(route, processor)


def after(route: str, processor: str) -> None:
    _after(route, processor)


def before_handler(route: str, target: str, processor: str) -> None:
    _before_processor(route, target, processor)


def after_handler(route: str, target: str, processor: str) -> None:
    _after_processor(route, target, processor)


def replace_pipeline(route: str, processors: list[str]) -> None:
    _replace_pipeline(route, processors)


async def run(app: App, host: str = "0.0.0.0", port: int = 8000) -> None:
    from ..adapters.asgi import create_app
    import uvicorn

    asgi_app = create_app(name=app.name)
    print(f"Starting {app.name} on http://{host}:{port}")
    uvicorn.run(asgi_app, host=host, port=port)
```

Key change: `from ..native import Service` replaces the local `Service` function. The `Service` is now the IOP mother syntax from `evoid.native`.

- [ ] **Step 2: Verify imports**

```bash
python -c "from evoid.web.route import Service, get, post, put, delete; print('route OK')"
```

Expected: `route OK`

- [ ] **Step 3: Commit**

```bash
git add evoid/web/route.py
git commit -m "refactor(web): route.py imports Service from native"
```

---

### Task 4: Update `evoid/web/controller.py` — Import Service from Native

**Covers:** controller.py uses native.Service

**Files:**
- Modify: `evoid/web/controller.py`

**Interfaces:**
- Consumes: `evoid.native.Service`
- Produces: Same API (Controller, GET, POST, etc.)

- [ ] **Step 1: Update `evoid/web/controller.py` imports**

Same pattern as route.py — replace local Service with `from ..native import Service`:

```python
"""@controller Syntax — Class-based routes, IOP underneath."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Awaitable

from ..core.intent import Intent, Level
from ..core import register, register_processor, Context
from ..core.extend import (
    before as _before,
    after as _after,
    before_processor as _before_processor,
    after_processor as _after_processor,
    replace_pipeline as _replace_pipeline,
)
from ..native import Service  # IOP mother syntax


Handler = Callable[..., Awaitable[Any]]


@dataclass
class App:
    name: str


def _create_intent(method: str, path: str, level: str = "standard") -> Intent:
    intent_level = Level(level) if level in ("ephemeral", "standard", "critical") else Level.STANDARD
    return Intent(
        name=f"{method.upper()}:{path}",
        level=intent_level,
        metadata={"method": method, "path": path},
    )


def Controller(prefix: str = "", level: str = "standard") -> Callable:
    def decorator(cls: type) -> type:
        for attr_name in dir(cls):
            if attr_name.startswith("_"):
                continue
            attr = getattr(cls, attr_name)
            if not callable(attr):
                continue
            if hasattr(attr, "_evoid_routes"):
                for route_info in attr._evoid_routes:
                    method = route_info["method"]
                    route_path = route_info["path"]
                    route_level = route_info.get("level", level)
                    full_path = prefix + route_path if prefix else route_path
                    intent = _create_intent(method, full_path, route_level)
                    register(intent)
                    instance = cls()
                    original_method = getattr(instance, attr_name)

                    async def processor(ctx: Context, m=original_method) -> Any:
                        body = ctx.metadata.get("body", {})
                        return await m(**body) if body else await m()

                    register_processor(intent.name, processor)
        return cls
    return decorator


def GET(path: str = "", level: str = "standard") -> Callable:
    def decorator(func: Handler) -> Handler:
        if not hasattr(func, "_evoid_routes"):
            func._evoid_routes = []
        func._evoid_routes.append({"method": "GET", "path": path, "level": level})
        return func
    return decorator


def POST(path: str = "", level: str = "standard") -> Callable:
    def decorator(func: Handler) -> Handler:
        if not hasattr(func, "_evoid_routes"):
            func._evoid_routes = []
        func._evoid_routes.append({"method": "POST", "path": path, "level": level})
        return func
    return decorator


def PUT(path: str = "", level: str = "standard") -> Callable:
    def decorator(func: Handler) -> Handler:
        if not hasattr(func, "_evoid_routes"):
            func._evoid_routes = []
        func._evoid_routes.append({"method": "PUT", "path": path, "level": level})
        return func
    return decorator


def DELETE(path: str = "", level: str = "standard") -> Callable:
    def decorator(func: Handler) -> Handler:
        if not hasattr(func, "_evoid_routes"):
            func._evoid_routes = []
        func._evoid_routes.append({"method": "DELETE", "path": path, "level": level})
        return func
    return decorator


def before(route: str, processor: str) -> None:
    _before(route, processor)

def after(route: str, processor: str) -> None:
    _after(route, processor)

def before_handler(route: str, target: str, processor: str) -> None:
    _before_processor(route, target, processor)

def after_handler(route: str, target: str, processor: str) -> None:
    _after_processor(route, target, processor)

def replace_pipeline(route: str, processors: list[str]) -> None:
    _replace_pipeline(route, processors)


async def run(app: App, host: str = "0.0.0.0", port: int = 8000) -> None:
    from ..adapters.asgi import create_app
    import uvicorn

    asgi_app = create_app(name=app.name)
    print(f"Starting {app.name} on http://{host}:{port}")
    uvicorn.run(asgi_app, host=host, port=port)
```

- [ ] **Step 2: Verify imports**

```bash
python -c "from evoid.web.controller import Controller, GET, POST, PUT, DELETE; print('controller OK')"
```

Expected: `controller OK`

- [ ] **Step 3: Commit**

```bash
git add evoid/web/controller.py
git commit -m "refactor(web): controller.py imports Service from native"
```

---

### Task 5: Update `evoid/web/__init__.py` — Re-export Native

**Covers:** Web init imports from native, provides backward-compat aliases

**Files:**
- Modify: `evoid/web/__init__.py`

- [ ] **Step 1: Rewrite `evoid/web/__init__.py`**

```python
"""Web — Web-specific features for EVOID services.

Primary entry points:
    evoid.native        — IOP mother syntax (adapter-agnostic)
    evoid.web.route     — Function-based routes (@get, @post)
    evoid.web.controller — Class-based controllers (@Controller)
    evoid.web.pipeline  — Web pipeline (auto-detect framework)

Backward-compat aliases:
    from evoid.web import NativeService, create_service  → use evoid.native
    from evoid.web import RouteService, get, post        → use evoid.web.route
    from evoid.web import ControllerService, Controller  → use evoid.web.controller
"""

from ..native import (
    Service as NativeService,
    create_service,
    on,
    execute_service,
    run as run_native,
)
from .route import (
    App as RouteApp,
    Service as RouteService,
    get,
    post,
    put,
    delete,
    before,
    after,
    before_handler,
    after_handler,
    replace_pipeline,
    run as run_route,
)
from .controller import (
    App as ControllerApp,
    Service as ControllerService,
    Controller,
    GET,
    POST,
    PUT,
    DELETE,
    run as run_controller,
)
from ..native.pipeline import (
    WebPipeline,
    detect,
    create_web_pipeline,
)

__all__ = [
    # Native IOP syntax (from evoid.native)
    "NativeService",
    "create_service",
    "on",
    "execute_service",
    "run_native",
    # @route syntax
    "RouteService",
    "RouteApp",
    "get",
    "post",
    "put",
    "delete",
    "before",
    "after",
    "before_handler",
    "after_handler",
    "replace_pipeline",
    "run_route",
    # @controller syntax
    "ControllerService",
    "ControllerApp",
    "Controller",
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "run_controller",
    # Web pipeline
    "WebPipeline",
    "detect",
    "create_web_pipeline",
]
```

- [ ] **Step 2: Verify all imports**

```bash
python -c "
from evoid.web import (
    NativeService, create_service, on, execute_service,
    RouteService, get, post, put, delete,
    ControllerService, Controller, GET, POST, PUT, DELETE,
    WebPipeline, detect, create_web_pipeline,
)
print('All web imports OK')
"
```

Expected: `All web imports OK`

- [ ] **Step 3: Commit**

```bash
git add evoid/web/__init__.py
git commit -m "feat(web): update init to export from native package"
```

---

### Task 6: Update `evoid/__init__.py` — Add Native Re-exports

**Covers:** Top-level package exports native syntax

**Files:**
- Modify: `evoid/__init__.py`

- [ ] **Step 1: Add native imports to `evoid/__init__.py`**

Add after the existing `# Parallel` block:

```python
# Native (IOP mother syntax)
from .native import (
    Service as NativeService,
    create_service,
    on as native_on,
    execute_service,
)
```

Add to `__all__`:

```python
    # Native
    "NativeService",
    "create_service",
    "native_on",
    "execute_service",
```

- [ ] **Step 2: Verify top-level imports**

```bash
python -c "from evoid import NativeService, create_service, native_on, execute_service; print('top-level native OK')"
```

Expected: `top-level native OK`

- [ ] **Step 3: Commit**

```bash
git add evoid/__init__.py
git commit -m "feat: add native IOP syntax to top-level exports"
```

---

### Task 7: Delete iop_style.py + Update Examples

**Covers:** Remove old file, update all examples to new import paths

**Files:**
- Delete: `evoid/web/iop_style.py`
- Modify: `examples/11_iop_style/main.py`
- Modify: `examples/09_fastapi_style/main.py`
- Modify: `examples/10_nestjs_style/main.py`

- [ ] **Step 1: Delete iop_style.py**

```bash
rm evoid/web/iop_style.py
```

- [ ] **Step 2: Update `examples/11_iop_style/main.py`**

Change:
```python
from evoid.web.iop_style import create_service, on, run
```
To:
```python
from evoid.native import create_service, on, run
```

- [ ] **Step 3: Update `examples/09_fastapi_style/main.py`**

Change:
```python
from evoid.web.route import Service, get, post, run
```
To:
```python
from evoid.web.route import get, post, run
from evoid.native import create_service as Service
```

Or simpler — keep the existing import since `evoid.web.route` still exports `Service`:
```python
from evoid.web.route import Service, get, post, run
```

(This still works because route.py now imports Service from native and re-exports it.)

- [ ] **Step 4: Update `examples/10_nestjs_style/main.py`**

Same — the import `from evoid.web.controller import Service, Controller, GET, POST, run` still works.

- [ ] **Step 5: Verify no broken imports**

```bash
python -c "from evoid.web import *; print('web package OK')"
python -c "from evoid.native import create_service, on, run; print('native OK')"
python -c "from evoid.native.pipeline import detect, create_web_pipeline; print('pipeline OK')"
python -c "from evoid.web.route import get, post; print('route OK')"
python -c "from evoid.web.controller import Controller, GET; print('controller OK')"
python -c "from evoid import NativeService, create_service; print('top-level OK')"
```

Expected: all `OK`

- [ ] **Step 6: Run tests if available**

```bash
python -m pytest tests/ -v --tb=short 2>/dev/null || echo "No tests found"
```

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "refactor: delete iop_style.py, update examples to use native package"
```

---

### Task 8: Update Tutorial Imports

**Covers:** Tutorial code examples use new import paths

**Files:**
- Check: `docs/tutorial/*.md` for old imports
- Modify: any files with `evoid.web.route`, `evoid.web.controller`, `evoid.web.iop_style`

- [ ] **Step 1: Search for old imports**

```bash
grep -r "evoid.web.route\|evoid.web.controller\|evoid.web.iop_style" docs/ || echo "No old imports found"
```

- [ ] **Step 2: Update any found references**

- `from evoid.web.route import` → stays the same (still works)
- `from evoid.web.controller import` → stays the same (still works)
- `from evoid.web.iop_style import` → `from evoid.native import`

- [ ] **Step 3: Commit**

```bash
git add docs/
git commit -m "docs: update tutorial imports to use native package"
```
