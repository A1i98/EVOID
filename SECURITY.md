# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.3.x   | Yes       |
| < 0.3   | No        |

## Reporting a Vulnerability

If you discover a security vulnerability in EVOID, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, email: pakrohk@gmail.com

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Response Timeline

- **Acknowledgment:** Within 48 hours
- **Assessment:** Within 1 week
- **Fix or mitigation:** Depends on severity

## Security Considerations

EVOID is a runtime framework. When using it:

- **Input validation** — Use `schema_validator` processor or manual validation at trust boundaries
- **Authorization** — Use `auth_checker` processor for access control
- **Secrets** — Never store secrets in Intent metadata. Use environment variables or a secrets manager
- **Rate limiting** — Use `rate_limiter` processor to prevent abuse
- **Timeouts** — Set Intent timeouts to prevent runaway processors

## Scope

Security issues in EVOID core (intent resolution, pipeline execution, context isolation) are in scope.

Issues in user code, third-party plugins, or optional dependencies (Redis, SQLAlchemy, etc.) are out of scope.
