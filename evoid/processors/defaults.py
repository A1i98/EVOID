"""Default Processors — Register built-in processors under pipeline names.

IOP: These are the processors that _DEFAULT_PROCESSORS references.
They run by default when no custom pipeline is specified.

- validate: schema validation (schema_validator)
- authorize: auth check (auth_checker)
- audit: logging only (logger_processor)
- protect: rate limiting (rate_limiter)
"""

from __future__ import annotations

from ..core.processor import register as register_processor
from .schema_validator import process as _validate
from .auth_checker import process as _authorize
from .logger_processor import process as _audit
from .rate_limiter import process as _protect


def register_defaults() -> None:
    """Register default processors. Call once at startup."""
    register_processor("validate", _validate)
    register_processor("authorize", _authorize)
    register_processor("audit", _audit)
    register_processor("protect", _protect)


# Auto-register on import
register_defaults()
