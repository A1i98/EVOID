"""Testing — IOP-native testing with pytest compatibility.

Tests are functions that return Intent test cases.
pytest collects and runs them. WebUI displays results.

Usage:
    # tests/test_api.py
    from evoid.testing import tc
    from myapp import GET_USER

    def test_get_user():
        return tc(GET_USER, expect={"id": 1})

    # Run: pytest tests/ -v
    # WebUI: pytest tests/ --evoid-webui
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..core.intent import Intent
from ..core.pipeline import Result


@dataclass(frozen=True)
class TestCase:
    """A single test case — pure data."""

    name: str
    intent: Intent
    expect: Any = None
    expect_error: type | None = None
    tags: tuple[str, ...] = ()


def tc(intent: Intent, expect: Any = None, expect_error: type | None = None, **kwargs: Any) -> TestCase:
    """Create a test case from an Intent.

    Usage in pytest:
        def test_get_user():
            return tc(GET_USER, expect={"id": 1})
    """
    tags = kwargs.get("tags", ())
    if isinstance(tags, str):
        tags = (tags,)

    return TestCase(
        name=kwargs.get("name", intent.name),
        intent=intent,
        expect=expect,
        expect_error=expect_error,
        tags=tuple(tags),
    )


def check_result(result: Result, case: TestCase) -> bool:
    """Check if a test result matches expectations."""
    if case.expect_error is not None:
        return not result.success and isinstance(result.error, case.expect_error)

    if not result.success:
        return False

    if case.expect is not None:
        return result.value == case.expect

    return result.success
