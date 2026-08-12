# Changelog

All notable changes to EVOID will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.10] - 2026-08-12

### Fixed
- **PyPI publish** — bump version to 0.6.10 (0.6.9 already exists on PyPI with different hash)
- CI: msgpack dependency resolved, all serializer tests pass

## [0.6.9] - 2026-08-12

### Security
- **Pipeline security fix** — `add_intent()` now delegates to `resolve_pipeline()` for all intent levels
  - Previously `add_intent()` with `level=CRITICAL` bypassed security processors (returned `(intent.name,)`)
  - Now all levels (EPHEMERAL, STANDARD, CRITICAL) use `resolve_pipeline()` → single source of truth
  - CRITICAL: `validate → authorize → audit → protect → handler`
  - STANDARD: `validate → authorize → handler`
  - EPHEMERAL: `validate → handler`
  - Default processors (`validate`, `authorize`, `audit`, `protect`) are fail-open (return `skipped: True` when no engine configured)

### Removed
- **Dead handler system** — `evoid/engines/handler.py` and `evoid/core/startup.py` removed
  - These modules were never called by `execute()` — actual path: `extend.add_intent_with_pipeline` → `_pipeline_overrides` + `_processors`
  - Removed unused `HandlerRegistry`, `set_handler()`, `get_handler()`, `clear_handler()`
  - Removed dead `_register_handlers()` call from `startup.py`

### Changed
- `add_intent()` → `resolve_pipeline()` delegation (no direct `_DEFAULT_PROCESSORS` access)
- `msgpack` promoted from optional extra to **required dependency** (needed for serializer engine tests)

### Fixed
- CI: msgpack serializer tests now pass (msgpack always available)

### Tests
- Added 18 regression tests in `test_intent_pipeline_security.py` covering real runtime path
  - `execute()` → `get_pipeline_config()` → `execute_pipeline()` → processor registry
- Tests verify: pipeline composition, processor registry, level-based resolution, override behavior, `add_intent` delegation

## [0.6.6] - 2026-07-26

### Added
- **Gateway auto-created on `evo init`** — entry point for all external requests (port 8000)
- **Auto-increment ports** — gateway=8000, api=8001, worker=8002 (no collisions)
- **AsyncAPI adapter** — Intent schemas → AsyncAPI 3.0 spec (`/docs`, `/docs/openapi`)
- **MCP JSON-RPC endpoint** — `/mcp` for AI agent discovery (initialize, tools/list, tools/call)
- **`evo check` command** — validates all registered intents have their processors
- **Default processors** — validate, authorize, audit, protect registered on import
- **PRE_PROCESS / POST_PROCESS events** — per-processor observability hooks
- **Result.warnings** surfaced in JSON response when non-empty
- **404 handling** — unknown paths return 404 instead of silent success
- **Annotation `@body(body: dict)`** — passes body as single dict, not unpacked kwargs

### Changed
- `run()` is now sync (was async) — uvicorn.run() is blocking, no asyncio.run() needed
- Template: `@app.get()` → `@get()` (Service is dataclass, no methods)
- Template: no more `asyncio.run()` wrapper
- Strict mode: `Config.strict` field threaded through runtime → pipeline

### Fixed
- Annotation bug: `validate_annotations` uses `intent_name`, not `fn.__name__`
- Auto-append intent name to custom pipeline (handler always runs)
- Scaffold crash: `@app.get` → `@get` (Service is dataclass, not app)

## [0.5.0] - 2026-07-24

### Changed
- `tomli_w` is now a core dependency (required for project scaffolding)
- Version bumped to 0.5.0

### Fixed
- Duplicate `delete` function in ASGI adapter (dead code removed)
- Documentation version mismatches across README, wiki, and docs
- SECURITY.md supported versions updated
- CONTRIBUTING.md project structure updated to match actual layout
- "Zero dependencies" claims corrected across all docs (tomli_w is required)

## [0.4.1] - 2026-07-18

### Changed
- **Zero core dependencies** — aiosqlite, tomli_w moved to optional extras
- Python 3.12+ required (was 3.13+)
- Development Status: Beta (was Alpha)

### Added
- `evo install` command for installing optional dependencies
- Python-native config (`evoid_config.py`) with `config()` builder
- Plugin manifest system (`evoid_plugin.json`)
- Plugin discovery (search PyPI, discover installed)
- SQLite optional dependency

### Fixed
- TestCase pytest collection warning (`__test__ = False`)

## [0.4.0] - 2026-07-18

### Added
- **Intent Schema Export** — Export Intent schemas as JSON Schema for AI agents
- **MCP Server** — Expose Intents as tools for AI agents
- **Plugin Lifecycle Hooks** — 6 events with security model (read-only context)
- **IOP Testing System** — pytest plugin with `tc()` helper and WebUI dashboard

### Changed
- Pipeline emits pre_execute/post_execute events
- Intent registration emits intent_registered event
- All exports available from top-level `evoid` module

## [0.3.3] - 2026-07-17

### Changed
- Pipeline execution uses three code paths (fast/timeout/inspect) instead of one
- Context uses fast counter-based IDs instead of UUID4
- Message bus history is capped at 1000 entries
- Processor and intent registries return references instead of copies
- Resolver caches default pipeline configs per intent level

### Fixed
- `native.execute_service` now correctly resolves intent by name instead of passing string to `execute()`

## [0.3.0] - 2025-07-10

### Added
- Core IOP runtime (Intent, Pipeline, Processor, Context)
- Three intent levels (ephemeral, standard, critical)
- Pipeline extension system (before, after, replace)
- Web adapters (ASGI, Robyn)
- CLI (`evo` command)
- Plugin system with schema, storage, cache, serializer engines

## [0.1.0] - 2025-07-01

### Added
- Initial release
- Core IOP concepts
- Basic pipeline execution
