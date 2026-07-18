---
title: 'Testing'
description: 'Test Intents directly, mock processors, inspect pipelines.'
---

# Testing

Test Intents directly, mock processors, inspect pipelines.

## Testing Intents Directly

No HTTP needed — test the pipeline directly:

```python
import asyncio
from evoid import execute, Intent, Level

async def test_create_order():
    result = await execute(
        Intent(name="create_order", level=Level.STANDARD),
        sandwich="BLT",
        qty=2,
    )

    assert result.success
    assert result.value["status"] == "confirmed"
    assert result.value["total"] == 17.98

asyncio.run(test_create_order())
```

## Mocking Processors

Replace processors for isolated testing:

```python
from unittest.mock import AsyncMock, patch

async def test_order_without_db():
    # Mock the database processor
    mock_db = AsyncMock(return_value={"checked": True})

    with patch("my_app.processors.check_inventory", mock_db):
        result = await execute(ORDER, sandwich="BLT", qty=1)
        assert result.success
        mock_db.assert_called_once()
```

## Pipeline Inspection

See what processors run and how long they take:

```python
from evoid import execute, Intent, Level
from evoid.core.runtime import Config

async def test_with_inspection():
    config = Config(inspect=True)
    result = await execute(ORDER, config=config, sandwich="BLT", qty=1)

    # Per-processor timing
    for step in result.steps:
        print(f"{step.name}: {step.duration:.4f}s {'OK' if step.success else 'FAIL'}")
```

## Testing with pytest

```python
import pytest
from evoid import execute, Intent, Level

@pytest.mark.asyncio
async def test_menu():
    result = await execute(VIEW_MENU)
    assert result.success
    assert len(result.value["menu"]) > 0

@pytest.mark.asyncio
async def test_order():
    result = await execute(ORDER, sandwich="BLT", qty=1)
    assert result.success
    assert result.value["status"] == "confirmed"

@pytest.mark.asyncio
async def test_invalid_sandwich():
    result = await execute(ORDER, sandwich="INVALID", qty=1)
    assert not result.success
    assert "not on menu" in str(result.error)
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Direct execution | Test pipelines without HTTP |
| Mocking | Replace processors for isolation |
| Pipeline inspection | Per-processor timing and state |
| pytest integration | Async test support |

## Next: Serialization

Let's handle data serialization — [Serialization](serialization.md).
