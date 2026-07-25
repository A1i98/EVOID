---
title: 'Glossary'
description: 'Formal definitions of every EVOID concept.'
---

# Glossary

**Intent** — A frozen dataclass that declares what you want to achieve. Contains a name, level, metadata, and optional timeout. The runtime reads the Intent and decides how to execute it. [Learn more](../learn/intent.md)

**Level** — One of three protection tiers: `ephemeral` (fast, disposable, no auth), `standard` (balanced, auth required), or `critical` (full audit, protection, slower). The level determines which processors run by default. [Learn more](../learn/iop-levels.md)

**Processor** — A pure function that receives a `Context` and returns a result. Processors are independent building blocks. The pipeline composes them in order. [Learn more](../learn/processors.md)

**Pipeline** — A tuple of processor names executed in order for a given Intent. Resolved at execution time based on the Intent's level or explicit override. [Learn more](../learn/pipeline.md)

**Context** — A mutable databag that flows through the pipeline. Contains the Intent, shared state between processors, injected dependencies, metadata, and accumulated errors. [Learn more](../learn/pipeline.md)

**IOP** — Intent-Oriented Programming. A paradigm where data carries intent (what you want), not behavior (how to do it). The runtime reads the Intent's metadata and decides which processors run, which infrastructure to use, and which security level applies. IOP combines OOP state + FP transforms + intent-driven routing. [Learn more](../learn/intent.md)

**Coordination Tax** — The overhead of making independent systems work together. Every function must know which database, which cache, which auth, which format to use. IOP eliminates this by moving infrastructure decisions to the pipeline, configured once and applied everywhere. [Learn more](../getting-started/iop-philosophy.md)

**Registry** — A dict that maps names to handlers or processors. Intent names map to pipeline configs. Processor names map to functions. The runtime looks up names at execution time. [Learn more](../learn/pipeline.md)

**Plugin** — An optional package that extends EVOID with new engines, adapters, or processors. Plugins register with the runtime via `register()` and provide implementations for contracts like `StorageEngine` or `CacheEngine`. [Learn more](../learn/plugins.md)

**Adapter** — A module that bridges external events (HTTP, CLI, Telegram, WebSocket) to Intents. Adapters extract parameters, create Intents, and convert `Result` back to responses. [Learn more](../learn/adapters.md)

**Schema** — A machine-readable description of an Intent's structure. Exported as JSON Schema for AI agents via MCP. [Learn more](../learn/schema-export.md)
