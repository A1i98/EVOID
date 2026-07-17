# EVOID Architecture — What Belongs Where

> The core question: what does the runtime handle, and what does the adapter handle?

## [S1] Core Principle

**EVOID is a runtime, not a framework.**

- **Runtime** = Intent → Pipeline → Processor → Result
- **Adapter** = converts external data (HTTP, CLI, Telegram) to Intent
- **User** = writes custom adapters for their specific needs

The runtime does NOT know about cookies, headers, forms, files, CORS, or any HTTP-specific thing. That's the adapter's job.

## [S2] What Each Layer Handles

### Layer 1: Adapter (user-provided, framework-specific)
The adapter is the ONLY layer that touches HTTP specifics:
- Extract path params from URL
- Extract query params from query string
- Extract body from request
- Extract cookies from headers
- Extract headers from request
- Parse form data
- Handle file uploads
- Set response status codes
- Set response headers

**The adapter puts all extracted data into `intent.metadata`.**

### Layer 2: EVOID Runtime (framework-agnostic)
The runtime NEVER touches HTTP. It only:
- Receives an Intent with metadata
- Runs the Intent through the Pipeline
- Each Processor reads/writes `ctx.metadata` and `ctx.state`
- Returns a Result

### Layer 3: Processor (user-provided, cross-cutting)
Processors handle logic that's independent of the transport:
- Validation (any kind)
- Authorization
- Logging
- Rate limiting
- Caching
- Any business logic that doesn't depend on HTTP

## [S3] What This Means for Documentation

### Pages we CAN write (no code changes):
These document patterns and best practices:

1. **Custom Adapters** — How to write an adapter for any framework
2. **Cookie Parameters** — How to extract cookies in your adapter
3. **Header Parameters** — How to extract headers in your adapter
4. **Form Data** — How to parse forms in your adapter
5. **File Upload** — How to handle files in your adapter
6. **CORS** — How to add CORS in your adapter or processor
7. **Static Files** — How to serve static files in your adapter
8. **Streaming** — How to handle SSE/WebSocket in your adapter

### Pages we CANNOT write (need runtime changes):
These require changes to the core runtime:

1. **Response Model** — Typed response validation (needs response system)
2. **Dependencies/DI** — Injectable dependencies (needs DI container)
3. **Security** — Auth engine (needs auth system)
4. **Middleware Pipeline** — Pre/post middleware (needs middleware system)
5. **Background Tasks** — Task queue (needs task engine)

## [S4] The Adapter Contract

An adapter must:
1. Convert external data to Intent (with metadata)
2. Call `core.runtime.execute(intent)`
3. Convert Result back to external response

The adapter puts data in `intent.metadata`:
```python
intent.metadata = {
    "method": "GET",
    "path": "/users/123",
    "path_params": {"user_id": "123"},
    "query_params": {"format": "json"},
    "body": {...},
    "headers": {...},
    "cookies": {...},      # adapter's responsibility
    "content_type": "...", # adapter's responsibility
}
```

The runtime reads from `intent.metadata` but never writes HTTP-specific data.

## [S5] Updated Phase 2B Plan

Instead of "add cookie/header/form/file support to ASGI adapter", the plan is:

### Write documentation pages that teach users:
1. **How to write a custom adapter** — step-by-step guide
2. **How to extract cookies** — example adapter code
3. **How to extract headers** — example adapter code
4. **How to parse forms** — example adapter code
5. **How to handle files** — example adapter code
6. **How to add CORS** — processor or adapter pattern
7. **How to serve static files** — adapter integration
8. **How to stream responses** — SSE/WebSocket adapter

### These pages show:
- The adapter contract (what data goes where)
- Real examples with Starlette/FastAPI adapters
- How processors consume the extracted data
- The separation of concerns (adapter vs runtime vs processor)

## [S6] What the ASGI Adapter Currently Does

The built-in ASGI adapter (`evoid/adapters/asgi.py`) is a **reference implementation**, not a production adapter. It handles:
- Basic path/query/body extraction
- JSON response
- Health check endpoint

Users are expected to:
1. Use the reference adapter as a starting point
2. Extend it for their needs (cookies, headers, forms)
3. Or write their own adapter for their framework

This is by design — EVOID is a runtime, not a framework with a fixed adapter.
