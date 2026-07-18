---
title: Changelog
description: All notable changes to EVOID.
---

All notable changes to EVOID will be documented on this page.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
