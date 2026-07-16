# EVOID Documentation Gap Analysis — FastAPI Comparison

> Compare FastAPI tutorial pages with EVOID docs. Create equivalent pages. Convert missing runtime features to GitHub project todos.

## [S1] Current State

### EVOID docs (24 pages)
- Getting Started: installation, quickstart, what-is-iop, why-evoid
- Learn: configuration, intent, pipeline, plugins, processors
- Styles: controller, native, route
- Tutorial: first-steps, path-params, request-body, native-iop, controller-style, pipeline-extensions, custom-processors, intent-levels, messaging, parallel

### FastAPI tutorial (41 core pages)
Full list in the FastAPI sidebar structure.

## [S2] Page-by-Page Comparison

| # | FastAPI Page | EVOID Equivalent | Status | Notes |
|---|---|---|---|---|
| 1 | First Steps | tutorial/first-steps.md | ✅ EXISTS | |
| 2 | Path Parameters | tutorial/path-params.md | ✅ EXISTS | |
| 3 | Query Parameters | — | ❌ MISSING | Needs EVOID equivalent |
| 4 | Request Body | tutorial/request-body.md | ✅ EXISTS | |
| 5 | String Validations | — | ❌ MISSING | May need runtime feature |
| 6 | Numeric Validations | — | ❌ MISSING | May need runtime feature |
| 7 | Query Parameter Models | — | ❌ MISSING | |
| 8 | Body Multiple Parameters | — | ❌ MISSING | |
| 9 | Body Fields | — | ❌ MISSING | May need schema engine |
| 10 | Body Nested Models | — | ❌ MISSING | May need schema engine |
| 11 | Schema Extra Example | — | ❌ MISSING | |
| 12 | Extra Data Types | — | ❌ MISSING | |
| 13 | Cookie Parameters | — | ❌ MISSING | Needs adapter feature |
| 14 | Header Parameters | — | ❌ MISSING | Needs adapter feature |
| 15 | Cookie/Header Models | — | ❌ MISSING | |
| 16 | Response Model | — | ❌ MISSING | Needs response system |
| 17 | Extra Models | — | ❌ MISSING | |
| 18 | Response Status Code | — | ❌ MISSING | Needs status code support |
| 19 | Form Data | — | ❌ MISSING | Needs adapter feature |
| 20 | Form Models | — | ❌ MISSING | |
| 21 | Request Files | — | ❌ MISSING | Needs adapter feature |
| 22 | Request Forms and Files | — | ❌ MISSING | |
| 23 | Handling Errors | — | ❌ MISSING | Needs error handling |
| 24 | Path Operation Configuration | — | ❌ MISSING | |
| 25 | JSON Encoder | — | ❌ MISSING | |
| 26 | Body Updates | — | ❌ MISSING | |
| 27 | Dependencies | — | ❌ MISSING | Needs DI system |
| 28 | Security | — | ❌ MISSING | Needs auth system |
| 29 | Middleware | — | ❌ MISSING | Needs middleware pipeline |
| 30 | CORS | — | ❌ MISSING | Needs CORS config |
| 31 | SQL Databases | — | N/A | Infrastructure, not core |
| 32 | Bigger Applications | — | ❌ MISSING | Multi-file patterns |
| 33 | Stream JSON Lines | — | ❌ MISSING | Needs streaming support |
| 34 | SSE | — | ❌ MISSING | Needs SSE adapter |
| 35 | Background Tasks | — | ❌ MISSING | Needs task queue |
| 36 | Metadata and Docs URLs | — | ❌ MISSING | |
| 37 | Frontend | — | N/A | Not web framework scope |
| 38 | Static Files | — | ❌ MISSING | Needs static file serving |
| 39 | Testing | — | ❌ MISSING | Needs test utilities |
| 40 | Debugging | — | ❌ MISSING | |

## [S3] Pages We Can Write Now (no runtime changes needed)

These pages document existing EVOID features using EVOID syntax:

1. **Query Parameters** — params in intent.metadata
2. **Response Status Code** — returning status from handlers
3. **Body Multiple Parameters** — multiple data sources in metadata
4. **Handling Errors** — error handling in pipeline
5. **Path Operation Configuration** — pipeline config per intent
6. **Bigger Applications** — multi-file project structure
7. **Metadata and Docs URLs** — service metadata
8. **Testing** — testing EVOID services

## [S4] Features Needing Runtime Work (→ GitHub Todos)

These require new runtime features before docs can be written:

1. **Schema Validation** — Query/Header/Cookie param models, body fields, nested models
2. **Response System** — Response models, status codes, extra models
3. **Cookie/Header Support** — Adapter-level param extraction
4. **Form Data** — Multipart form handling
5. **File Upload** — Binary file handling
6. **Dependencies** — DI system (may already exist via deps in Context)
7. **Security/Auth** — OAuth2, JWT, API keys
8. **Middleware Pipeline** — Pre/post request middleware
9. **CORS** — Cross-origin configuration
10. **Streaming** — SSE, JSON Lines streaming
11. **Background Tasks** — Async task queue
12. **Static Files** — Serve static assets
13. **JSON Encoder** — Custom serialization

## [S5] Implementation Plan

### Phase 1: Write docs for existing features (no code changes)
- Query Parameters
- Response Status Code
- Body Multiple Parameters
- Handling Errors
- Path Operation Configuration
- Bigger Applications
- Metadata
- Testing

### Phase 2: Create GitHub issues for missing features
- One issue per feature in [S4]
- Each issue includes: description, EVOID syntax proposal, priority

### Phase 3: Write docs for new features (as they're implemented)
- Each feature implementation → corresponding doc page
