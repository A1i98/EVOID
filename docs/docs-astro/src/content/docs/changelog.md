---
title: Changelog
description: All notable changes to EVOID.
---

All notable changes to EVOID will be documented on this page.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.10] - 2026-08-12

### Fixed
- **PyPI publish** — bump version to 0.6.10 (0.6.9 already exists on PyPI with different hash)
- CI: msgpack dependency resolved, all serializer tests pass

## [0.6.9] - 2026-08-12

### Security
- **Pipeline security hardening** — `add_intent()` now delegates to `resolve_pipeline()` ensuring ALL intents pass through security processors (CRITICAL level no longer bypasses `validate`/`authorize`)
- Security processors (`validate`, `authorize`) are fail-open: they only block when explicitly defined in the processor registry, maintaining backward compatibility

### Removed
- **Dead handler system** — deleted `evoid/engines/handler.py` and `evoid/core/startup.py` (never called by `execute()`, unused dead code)
- Removed `set_handler()` / `get_handler()` references from `evoid/engines/schema/native.py`

### Changed
- **Single source of truth for pipelines** — `add_intent()` no longer directly accesses `_DEFAULT_PROCESSORS`; it composes via `resolve_pipeline()` (one code path for all intent registration)
- `msgpack` promoted from optional dev dependency to required dependency (used by serializer engine)
- Plugin compatibility: all 15 plugins updated to `evoid>=0.6.9`, plugin versions bumped to 0.2.0

### Added
- **18 regression tests** in `tests/test_intent_pipeline_security.py` covering real runtime path (`execute()` → `get_pipeline_config()` → `execute_pipeline()` → processor registry)
- Tests verify: level-based pipeline composition, security not bypassed, handler executes exactly once, no duplicate processors, priority/timeout preserved

## [0.6.8] - 2026-08-11

### Fixed
- **Documentation overhaul** — comprehensive audit of all 96 docs pages (5 parts); corrected all code examples to match actual runtime behavior
- **Project root detection** — fixed `find_project_root()` to work from any subdirectory
- **ASGI route matching** — fixed decorator and parameterized route handling
- **Service startup** — import service `main.py` in `cmd_service_run` before starting server

### Changed
- DeepWiki badge added (updates faster for contributors)
- Documentation coherence and tutorial ordering improved
- Quick Start corrected to match actual `evo init` behavior + version badge updated to 0.6.7

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
