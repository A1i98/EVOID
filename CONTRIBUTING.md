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
  core/           # IOP runtime (Intent, Pipeline, Processor, Context)
  native/         # Native IOP syntax (create_service, on)
  web/            # Web adapters (route, controller, pipeline)
  adapters/       # Framework adapters (ASGI, Robyn, Telegram, WebSocket)
  engines/        # Plugin engines (schema, storage, cache, serializer, logger)
  processors/     # Built-in processors (validate, auth, rate limit, etc.)
  contracts/      # Plugin interfaces (pure types)
  config/         # Configuration loading
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
