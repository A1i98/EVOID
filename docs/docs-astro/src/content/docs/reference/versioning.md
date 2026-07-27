---
title: 'Versioning Policy'
description: 'SemVer rules, breaking change criteria, deprecation window.'
---

# Versioning Policy

EVOID follows [Semantic Versioning 2.0.0](https://semver.org/).

## Version Format

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: incompatible API changes
- **MINOR**: new functionality (backward-compatible)
- **PATCH**: bug fixes (backward-compatible)

## What Counts as Breaking

These changes require a MAJOR version bump:

- Renaming or removing a built-in processor (`validate`, `authorize`, `audit`, `protect`)
- Changing the order of processors in `_DEFAULT_PROCESSORS`
- Removing or renaming fields on `Result` (`success`, `value`, `error`, `processors`, `duration`)
- Changing `Context` fields that processors depend on (`ctx.state`, `ctx.deps`, `ctx.metadata`)
- Changing the Intent dataclass fields (`name`, `level`, `metadata`, `timeout`, `priority`)
- Removing or renaming public API functions (`execute`, `register`, `register_processor`, `add_intent`)
- Changing the default pipeline for any level
- Changing `PermissionError` or `ValueError` semantics in pipeline execution

## What Is NOT Breaking

These can ship in MINOR or PATCH:

- Adding new processors or Intent levels
- Adding new fields to `Result` or `Context`
- Adding new plugins or engines
- Adding new CLI commands
- Adding new annotations (`@intent`, `@requires`, etc.)
- Performance improvements
- Documentation changes

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.6.x | Yes |
| 0.5.x | Yes |
| < 0.5 | No |

## Deprecation Window

When a feature is deprecated:

1. **MINOR release**: feature deprecated with warning, still works
2. **Next MINOR release**: feature removed

Minimum deprecation window: 1 minor release (approximately 1-2 weeks at current development pace).

## Current Version

Check `evoid/__init__.py` or run `evo version`.

```bash
evo version
# EVOID 0.6.6
```

## Related

- [CHANGELOG](/EVOID/changelog): version history
- [Security Policy](/EVOID/security): vulnerability reporting
