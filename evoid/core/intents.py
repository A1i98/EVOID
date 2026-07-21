"""Standard Intents for engine categories.

IOP: Every engine operation is an Intent.
Plugins register handlers for these Intents.
Users choose which handler via config or code.
"""

from __future__ import annotations

from .intent import Intent, Level


# ============================================================
# Storage Intents
# ============================================================

STORAGE_READ = Intent(
    name="storage.read",
    level=Level.STANDARD,
    timeout=10.0,
)

STORAGE_WRITE = Intent(
    name="storage.write",
    level=Level.STANDARD,
    timeout=10.0,
)

STORAGE_DELETE = Intent(
    name="storage.delete",
    level=Level.STANDARD,
    timeout=10.0,
)

STORAGE_HEALTH = Intent(
    name="storage.health",
    level=Level.EPHEMERAL,
    timeout=5.0,
)


# ============================================================
# Cache Intents
# ============================================================

CACHE_GET = Intent(
    name="cache.get",
    level=Level.EPHEMERAL,
    timeout=5.0,
)

CACHE_SET = Intent(
    name="cache.set",
    level=Level.EPHEMERAL,
    timeout=5.0,
)

CACHE_DELETE = Intent(
    name="cache.delete",
    level=Level.EPHEMERAL,
    timeout=5.0,
)

CACHE_EXISTS = Intent(
    name="cache.exists",
    level=Level.EPHEMERAL,
    timeout=5.0,
)

CACHE_HEALTH = Intent(
    name="cache.health",
    level=Level.EPHEMERAL,
    timeout=5.0,
)


# ============================================================
# Schema Intents
# ============================================================

SCHEMA_VALIDATE = Intent(
    name="schema.validate",
    level=Level.STANDARD,
    timeout=10.0,
)

SCHEMA_EXPORT = Intent(
    name="schema.export",
    level=Level.EPHEMERAL,
    timeout=5.0,
)


# ============================================================
# Serializer Intents
# ============================================================

SERIALIZE_ENCODE = Intent(
    name="serializer.encode",
    level=Level.STANDARD,
    timeout=10.0,
)

SERIALIZE_DECODE = Intent(
    name="serializer.decode",
    level=Level.STANDARD,
    timeout=10.0,
)


# ============================================================
# Auth Intents
# ============================================================

AUTH_AUTHENTICATE = Intent(
    name="auth.authenticate",
    level=Level.CRITICAL,
    timeout=30.0,
)

AUTH_AUTHORIZE = Intent(
    name="auth.authorize",
    level=Level.CRITICAL,
    timeout=30.0,
)


# ============================================================
# Logger Intents
# ============================================================

LOG_INFO = Intent(
    name="log.info",
    level=Level.EPHEMERAL,
    timeout=5.0,
)

LOG_WARNING = Intent(
    name="log.warning",
    level=Level.EPHEMERAL,
    timeout=5.0,
)

LOG_ERROR = Intent(
    name="log.error",
    level=Level.EPHEMERAL,
    timeout=5.0,
)


# ============================================================
# Metrics Intents
# ============================================================

METRICS_RECORD = Intent(
    name="metrics.record",
    level=Level.EPHEMERAL,
    timeout=5.0,
)

METRICS_QUERY = Intent(
    name="metrics.query",
    level=Level.EPHEMERAL,
    timeout=5.0,
)
