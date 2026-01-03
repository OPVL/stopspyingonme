# Core Principles

## Privacy & Security First
- Encrypt sensitive fields with PostgreSQL `pgcrypto`
- Never store email bodies beyond approved scopes
- Hash tokens, use short expiry, rotate sessions
- Structured logs without PII/sensitive data
- WCAG AA accessibility targets

## Architecture Constraints
- Shared hosting: conservative DB pooling, cron over workers
- FastAPI + async SQLAlchemy + Alembic
- `/api/v1` versioning, RFC7807 error format
- Signed cookies, CSRF protection, rate limiting
- Async I/O with graceful fallbacks

## Code Quality
- Test coverage >80% for core modules
- Idempotent operations, deterministic migrations
- Minimal, maintainable implementations
- AGPL-3.0 compatible dependencies
