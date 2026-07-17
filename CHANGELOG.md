# Changelog

All notable changes to EVOID will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Pipeline execution uses three code paths (fast/timeout/inspect) instead of one
- Context uses fast counter-based IDs instead of UUID4
- Message bus history is capped at 1000 entries
- Processor and intent registries return references instead of copies
- Resolver caches default pipeline configs per intent level

### Fixed
- `native.execute_service` now correctly resolves intent by name instead of passing string to `execute()`

## [0.3.3] - 2025-07-17

### Added
- Pipeline inspection mode (`inspect=True`)
- Parallel execution with priority ordering
- Intent queue with concurrency control
- Message bus with topic-based routing
- Native service style (`create_service`, `on`)
- Web pipeline with auto-detection (ASGI/Robyn)

### Changed
- Context removed `created_at` field for zero overhead
- Fork no longer copies `deps` dict (shared reference)

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
