# Contributing to EVOID

Thanks for your interest in contributing to EVOID.

## Development Setup

```bash
# Clone
git clone https://github.com/EvolveBeyond/EVOID.git
cd EVOID

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linter
uv run ruff check .
```

## Project Structure

```
evoid/
  core/           # IOP runtime (Intent, Pipeline, Processor, Context, Events, Extend)
  native/         # Native IOP syntax (create_service, on)
  web/            # Web syntax (route, controller)
  adapters/       # Framework adapters (ASGI, Robyn, Telegram, WebSocket, MCP, CLI)
  engines/        # Plugin engines (storage, cache, auth, di, logger, metrics, schema, serializer)
  processors/     # Built-in processors (validate, auth, rate limit, circuit breaker, etc.)
  contracts/      # Plugin interfaces (pure types)
  config/         # TOML + Python config loading
  testing/        # pytest plugin + WebUI dashboard
  project/        # Project scaffolding (evo init, evo service new)
tests/            # Test suite
examples/         # Usage examples
docs/             # Documentation (Astro-based)
```

## Code Style

- Python 3.12+ only
- Type hints required
- Async-first (all I/O is async)
- No classes with behavior — dataclasses and functions only
- Keep processors as pure functions

## Testing

```bash
# Run all tests
uv run pytest

# Run specific test
uv run pytest tests/test_core.py -v

# Run with coverage
uv run pytest --cov=evoid
```

## Pull Request Process

1. Create a feature branch from `main`
2. Write tests for new functionality
3. Ensure all tests pass
4. Update documentation if needed
5. Submit PR with clear description

## Architecture Principles

- **Data carries intent** — Intent is a frozen dataclass, not a class with methods
- **Pipeline is composition** — Processors are pure functions composed together
- **No stateful objects** — Registries are dicts, not singleton classes
- **Extensibility without inheritance** — Use `before/after/replace` to modify pipelines
