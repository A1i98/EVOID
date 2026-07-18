"""pytest plugin — Collect and run IOP test cases.

Automatically discovers test functions that return TestCase objects.
Runs them through the IOP pipeline and reports results.

Usage:
    pytest tests/ -v                    # Normal pytest
    pytest tests/ --evoid-webui         # With WebUI
    pytest tests/ --evoid-inspect       # With pipeline traces
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import pytest

from . import TestCase, check_result


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command line options."""
    parser.addoption(
        "--evoid-webui",
        action="store_true",
        default=False,
        help="Open test dashboard WebUI after tests",
    )
    parser.addoption(
        "--evoid-inspect",
        action="store_true",
        default=False,
        help="Capture pipeline execution traces",
    )
    parser.addoption(
        "--evoid-port",
        type=int,
        default=8001,
        help="WebUI port (default: 8001)",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Wrap test items that return TestCase."""
    for item in items:
        if isinstance(item, pytest.Function):
            # Check if the test function returns a TestCase
            original_runtest = item.runtest

            def make_wrapper(func):
                def wrapper():
                    result = func()
                    if isinstance(result, TestCase):
                        return _run_test_case(result, config)
                    return result
                return wrapper

            # We'll handle this in the hook instead
            pass


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item: pytest.Item) -> Any:
    """Execute test and handle TestCase results."""
    outcome = yield

    # If the test already failed, skip
    if outcome.excinfo is not None:
        return

    # Check if the test function returned a TestCase
    if hasattr(item, "_evoid_testcase"):
        case = item._evoid_testcase
        result = _run_test_case(case, item.config)
        if not result["success"]:
            pytest.fail(result["error"])


def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    """Add test case info to report."""
    if hasattr(item, "_evoid_testcase"):
        case = item._evoid_testcase
        if call.when == "call":
            item.add_marker(pytest.mark.evoid)


def _run_test_case(case: TestCase, config: pytest.Config) -> dict[str, Any]:
    """Run a single test case through the IOP pipeline."""
    from ..core.runtime import execute
    from ..core.extend import add_intent_with_pipeline
    from ..core.processor import get as get_processor

    start = time.monotonic()

    # Ensure pipeline includes the handler
    if get_processor(case.intent.name) is not None:
        add_intent_with_pipeline(
            case.intent,
            processors=[case.intent.name],
        )

    # Execute
    try:
        result = asyncio.run(execute(case.intent))
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "duration": time.monotonic() - start,
        }

    passed = check_result(result, case)

    return {
        "success": passed,
        "error": None if passed else f"Expected {case.expect}, got {result.value}" if case.expect is not None else str(result.error),
        "duration": time.monotonic() - start,
        "result": result,
    }


# ============================================================
# WebUI (optional)
# ============================================================

_results_store: list[dict] = []


def _store_result(item: pytest.Item, result: dict) -> None:
    """Store test result for WebUI."""
    _results_store.append({
        "name": item.name,
        "outcome": "passed" if result["success"] else "failed",
        "duration": result["duration"],
        "error": result.get("error"),
    })


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Open WebUI if requested."""
    if session.config.getoption("--evoid-webui", default=False):
        try:
            from .webui import serve
            port = session.config.getoption("--evoid-port", default=8001)
            serve(_results_store, port=port)
        except ImportError:
            print("WebUI not installed. Run: uv add 'evoid[testing-webui]'")
