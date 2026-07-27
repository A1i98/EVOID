---
title: 'Testing'
description: 'Test Intents directly, mock processors, inspect pipelines. See [Testing Reference](../learn/testing.md) for full details.'
---

# Testing

Test Intents directly, mock processors, inspect pipelines.

> **Full reference:** [Testing Reference](../learn/testing.md) — `tc()` helper, TestCase, pytest integration, native & @route styles.

## Quick Start

```python
# tests/test_api.py
from evoid.testing import tc
from myapp import GET_USER

def test_get_user():
    return tc(GET_USER, expect={"id": 1})
```

```bash
pytest tests/ -v
```

## Testing Patterns

| Pattern | Code |
|---------|------|
| Direct execution | `await execute(intent)` — test pipelines without HTTP |
| Mocking | `unittest.mock.AsyncMock` — replace processors for isolation |
| Pipeline inspection | `Config(inspect=True)` — per-processor timing and state |
| Error testing | `tc(intent, expect_error=ValueError)` |

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Direct execution | Test pipelines without HTTP |
| Mocking | Replace processors for isolation |
| Pipeline inspection | Per-processor timing and state |
| pytest integration | Async test support |

## Next: Serialization

Let's handle data serialization — [Serialization](serialization.md).