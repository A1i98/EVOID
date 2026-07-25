---
title: 'Roadmap'
description: 'Current priorities and planned features.'
---

# Roadmap

This page tracks stated priorities. Items are added only when the maintainer confirms them.

## Current Priorities

- **Documentation completeness**: CLI reference, annotation system, error reference, configuration reference, glossary
- **Plugin ecosystem maturity**: publish remaining plugins to PyPI, improve plugin standard
- **Tutorial coherence**: progressive pain-point structure across all 3 phases
- **IOP compliance**: ensure all code examples follow IOP principles

## Planned

- **Auth Engine**: dedicated auth plugin with JWT, OAuth2, and BYO providers
- **Background Tasks**: task scheduling with lifecycle hooks
- **WebSocket adapter**: first-class WebSocket support beyond Godot
- **CLI improvements**: `evo service delete`, `evo service rename`

## Deferred

- **Rust runtime**: performance-critical paths via PyO3 (separate repo)
- **Multi-language support**: Go, Rust, TypeScript implementations
- **Visual pipeline editor**: drag-and-drop pipeline composition

## How to Influence the Roadmap

Open a [GitHub Issue](https://github.com/EvolveBeyond/EVOID/issues) with the `enhancement` label. Describe:

1. What you want to build
2. Why current capabilities don't cover it
3. Whether you'd contribute the implementation

## Related

- [GitHub Issues](https://github.com/EvolveBeyond/EVOID/issues): active discussions
- [Plugin Collection](../learn/plugin-collection.md): what's available today
