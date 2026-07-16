# EVOID Documentation Roadmap

> What to write next, in what order, and what runtime features block each page.

## Current State: 32 pages

### Getting Started (4)
- installation, quickstart, what-is-iop, why-evoid

### Learn (5)
- configuration, intent, pipeline, plugins, processors

### Styles (3)
- controller, native, route

### Tutorial (18)
- first-steps, path-params, query-params, request-body, response-status-code
- body-multiple-params, handling-errors, path-operation-config
- bigger-applications, metadata, testing
- native-iop, controller-style, pipeline-extensions, custom-processors
- intent-levels, messaging, parallel

### Other (2)
- api.md, examples.md

---

## What's Missing (FastAPI Tutorial Comparison)

### Tier 1: Write Now (no runtime changes)
These pages document existing EVOID features. **Can be written immediately.**

| # | Page | What It Covers | EVOID Approach |
|---|------|---------------|----------------|
| 1 | Query Parameter Models | Validate query params with schemas | `ctx.state` validation in processor |
| 2 | Body Fields | Field-level validation, aliases, defaults | Schema engine plugin (future) |
| 3 | Body Nested Models | Nested object validation | Schema engine plugin (future) |
| 4 | Schema Extra Examples | Example data for documentation | Intent metadata examples |
| 5 | Extra Data Types | UUID, datetime, etc. in handlers | Python type hints + adapter parsing |
| 6 | JSON Encoder | Custom serialization | Serializer engine plugin |
| 7 | Body Updates | PATCH-style partial updates | Intent metadata merge pattern |
| 8 | Debugging | Debugging EVOID services | Loguru integration, pipeline tracing |

### Tier 2: Need Minor Runtime Work
These need small additions to the existing codebase.

| # | Page | What's Missing | Effort |
|---|------|---------------|--------|
| 9 | Cookie Parameters | ASGI adapter extracts cookies → metadata | Small: add to asgi.py |
| 10 | Header Parameters | ASGI adapter extracts headers → metadata | Small: add to asgi.py |
| 11 | Extra Models | Multiple response formats | Medium: response wrapper |
| 12 | Form Data | Multipart form parsing in adapter | Medium: add to asgi.py |
| 13 | Request Files | Binary file upload handling | Medium: add to asgi.py |
| 14 | Request Forms and Files | Combined form + file | Medium: extends above |
| 15 | CORS | Cross-origin headers config | Small: middleware processor |
| 16 | Static Files | Serve files from directory | Small: Starlette StaticFiles |

### Tier 3: Need Significant Runtime Work
These need new subsystems in the runtime.

| # | Page | What's Missing | Effort |
|---|------|---------------|--------|
| 17 | Dependencies (DI) | Injectable dependencies with `Depends()` | Large: DI container |
| 18 | Security / Auth | OAuth2, JWT, API keys, password hashing | Large: auth engine |
| 19 | Middleware Pipeline | Pre/post request middleware chain | Large: middleware system |
| 20 | Response Model | Typed response schemas, validation | Large: response system |
| 21 | Streaming (SSE) | Server-Sent Events adapter | Large: new adapter |
| 22 | Background Tasks | Async task queue | Large: task engine |
| 23 | String Validations | Regex, min/max length on params | Medium: validation processor |
| 24 | Numeric Validations | Ge, le, gt, lt on numeric params | Medium: validation processor |

### N/A (Not Applicable)
| # | Page | Why N/A |
|---|------|---------|
| 25 | SQL Databases | Infrastructure, not runtime scope |
| 26 | Frontend | Not a web framework |
| 27 | FastAPI-specific features | CLI, deployment, OpenAPI customization |

---

## Recommended Writing Order

### Phase 2A: Tier 1 Pages (8 pages, no code changes)
Write these NOW — they document what already exists:

1. **Query Parameter Models** — show validation patterns with `ctx.state`
2. **Body Fields** — field-level control, defaults, aliases
3. **Body Nested Models** — nested object handling
4. **Schema Extra Examples** — documentation metadata
5. **Extra Data Types** — UUID, datetime, list handling
6. **JSON Encoder** — serialization patterns
7. **Body Updates** — PATCH/partial update patterns
8. **Debugging** — loguru, pipeline tracing, debug mode

### Phase 2B: Tier 2 Pages (8 pages, minor runtime work)
After implementing small adapter additions:

9. **Cookie Parameters** — add cookie extraction to ASGI adapter
10. **Header Parameters** — add header extraction to ASGI adapter
11. **CORS** — add CORS middleware processor
12. **Static Files** — add Starlette StaticFiles integration
13. **Form Data** — add form parsing to ASGI adapter
14. **Request Files** — add file upload to ASGI adapter
15. **Request Forms and Files** — combined form + file
16. **Extra Models** — multiple response formats

### Phase 2C: Tier 3 Pages (8 pages, significant runtime work)
After implementing new subsystems:

17. **Dependencies** — DI container system
18. **Security** — auth engine (OAuth2, JWT, API keys)
19. **Middleware** — middleware pipeline system
20. **Response Model** — typed response validation
21. **Streaming** — SSE adapter
22. **Background Tasks** — task queue engine
23. **String Validations** — validation processor
24. **Numeric Validations** — validation processor

---

## GitHub Issues to Create

Each Tier 2 and Tier 3 feature needs a GitHub issue with:
- Feature name and description
- EVOID syntax proposal (how it would look in code)
- Priority (P0/P1/P2)
- Estimated effort (S/M/L)

### P0 (Core — needed for complete tutorial coverage)
1. Cookie/Header parameter extraction
2. CORS middleware
3. Form data + file upload
4. Static file serving

### P1 (Important — makes EVOID production-ready)
5. DI container / Dependencies
6. Auth engine (Security)
7. Middleware pipeline
8. Response model validation

### P2 (Nice-to-have — advanced features)
9. Streaming / SSE
10. Background tasks
11. String/Numeric validations
12. JSON encoder customization
