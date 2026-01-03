# Epic: Foundation & Codebase Setup

**Epic ID**: EPIC-00
**Priority**: Critical (Prerequisite for all other epics)
**Estimated Effort**: 2-3 weeks
**Dependencies**: None

## Overview

Establish the foundational codebase architecture for quitspyingonme with a modular, maintainable structure that supports shared hosting deployment while remaining extensible for future scaling. This epic focuses on setting up the core technical infrastructure including the web framework, database layer, authentication system, configuration management, and development environment.

## Goals

- Create a clean, modular Python project structure
- Establish FastAPI application with RESTful API patterns
- Implement PostgreSQL database models with SQLAlchemy ORM
- Set up migration management with Alembic
- Configure environment-based settings management
- Implement secure session handling with signed cookies
- Build authentication foundation (magic links + WebAuthn)
- Create development environment with Docker Compose
- Establish testing framework with comprehensive fixtures
- Set up basic CI/CD pipeline

## Technical Stack

- **Framework**: FastAPI (async support, automatic API docs, good for webhooks)
- **ORM**: SQLAlchemy 2.0+ (async-capable, widely supported)
- **Migrations**: Alembic (standard SQLAlchemy migration tool)
- **Templates**: Jinja2 (for server-side rendering)
- **Sessions**: Custom signed-cookie implementation (Redis-ready interface)
- **WebAuthn**: py_webauthn library
- **Database**: PostgreSQL 14+ with pgcrypto extension
- **Dev Environment**: Docker Compose (Postgres + app container)
- **Testing**: pytest + pytest-asyncio + pytest-cov
- **Code Quality**: black, isort, flake8, mypy

## Project Structure

```
stopspyingonme/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   ├── config.py                  # Configuration management
│   ├── dependencies.py            # FastAPI dependency injection
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py          # Main API router
│   │   │   ├── auth.py            # Auth endpoints
│   │   │   ├── aliases.py         # Alias management
│   │   │   ├── destinations.py    # Destination endpoints
│   │   │   ├── messages.py        # Message logs
│   │   │   ├── webhooks.py        # Webhook config
│   │   │   └── account.py         # Account settings
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                # Base model with timestamps
│   │   ├── user.py                # User accounts
│   │   ├── alias.py               # Email aliases
│   │   ├── destination.py         # Forwarding destinations
│   │   ├── message_log.py         # Message logs
│   │   ├── spam_quarantine.py     # Quarantined messages
│   │   ├── failed_email.py        # Failed forwarding
│   │   ├── usage_counter.py       # Bandwidth tracking
│   │   ├── webhook.py             # Webhook subscriptions
│   │   └── audit_log.py           # Audit events
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py                # Auth request/response schemas
│   │   ├── alias.py               # Alias schemas
│   │   ├── destination.py         # Destination schemas
│   │   └── ...                    # Other Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py                # Auth business logic
│   │   ├── session.py             # Session management
│   │   ├── alias.py               # Alias operations
│   │   ├── email.py               # Email sending (magic links, Porter)
│   │   └── crypto.py              # Encryption helpers
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py             # Database session management
│   │   └── base.py                # Declarative base
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── session.py             # Session middleware
│   │   ├── rate_limit.py          # Rate limiting
│   │   └── logging.py             # Request logging
│   ├── templates/
│   │   ├── base.html              # Base template
│   │   ├── auth/
│   │   ├── dashboard/
│   │   └── email/                 # Email templates (magic links, Porter)
│   ├── static/
│   │   ├── css/
│   │   │   └── tailwind.css
│   │   └── js/
│   └── utils/
│       ├── __init__.py
│       ├── validation.py          # Input validation helpers
│       └── constants.py           # System constants
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── factories.py               # Test data factories
│   ├── test_api/
│   │   ├── test_auth.py
│   │   ├── test_aliases.py
│   │   └── ...
│   ├── test_services/
│   │   ├── test_auth.py
│   │   ├── test_session.py
│   │   └── ...
│   └── test_models/
├── docker/
│   ├── Dockerfile.dev
│   └── Dockerfile.prod
├── scripts/
│   ├── init_db.py                 # Database initialization
│   └── generate_secret_key.py    # Secret key generation
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── pyproject.toml                 # Python project config (black, isort, mypy)
├── requirements.txt
├── dev-requirements.txt
└── README.md
```

## Tickets

### T1: Project Structure & Configuration (Priority: Critical, Est: 4h)

**Description**: Set up the base project structure with proper Python packaging and configuration management.

**Tasks**:
- Create directory structure as outlined above
- Set up `pyproject.toml` with black, isort, mypy, flake8 configs
- Create `.env.example` with all required environment variables
- Implement `app/config.py` with Pydantic Settings for environment-based config
- Add `.gitignore` for Python, Docker, IDE files
- Update `README.md` with setup instructions

**Acceptance Criteria**:
- [ ] All directories created with `__init__.py` files
- [ ] Configuration loads from environment variables with validation
- [ ] `.env.example` documents all required settings (DATABASE_URL, SECRET_KEY, SMTP_*, etc.)
- [ ] Code formatters and linters run without errors
- [ ] README has clear "Getting Started" section

---

### T2: Database Layer & SQLAlchemy Setup (Priority: Critical, Est: 6h)

**Description**: Configure SQLAlchemy async engine with connection pooling and create base model classes.

**Tasks**:
- Install SQLAlchemy 2.0+ with asyncpg driver
- Create `app/db/session.py` with async engine and session factory
- Implement `app/models/base.py` with declarative base and timestamp mixin
- Add database dependency injection for FastAPI routes
- Configure connection pooling for shared hosting constraints
- Add health check endpoint that tests database connectivity

**Acceptance Criteria**:
- [ ] Async SQLAlchemy engine connects to PostgreSQL
- [ ] Session factory creates scoped async sessions
- [ ] Base model includes `id`, `created_at`, `updated_at` fields
- [ ] Connection pool configured with max 10 connections (shared hosting)
- [ ] Health check endpoint returns database status
- [ ] No sessions leak (proper cleanup in dependencies)

---

### T3: Alembic Migration Framework (Priority: Critical, Est: 4h)

**Description**: Set up Alembic for database schema migrations with async support.

**Tasks**:
- Initialize Alembic with `alembic init alembic`
- Configure `alembic/env.py` for async migrations
- Update `alembic.ini` to use config.py database URL
- Create initial migration with pgcrypto extension
- Add migration running instructions to README
- Create `scripts/init_db.py` for fresh database setup

**Acceptance Criteria**:
- [ ] Alembic generates migrations from SQLAlchemy models
- [ ] Migrations run successfully with `alembic upgrade head`
- [ ] Initial migration enables pgcrypto extension
- [ ] Downgrade migrations work correctly
- [ ] `init_db.py` script creates database and runs migrations
- [ ] Migration history tracked in `alembic_version` table

---

### T4: Core Database Models (Priority: Critical, Est: 8h)

**Description**: Implement SQLAlchemy models for core entities (users, aliases, destinations, sessions).

**Tasks**:
- Create `app/models/user.py` with User model (id, email, created_at, etc.)
- Create `app/models/alias.py` with Alias model (name, domain, user_id, destination_id, is_active)
- Create `app/models/destination.py` with Destination model (email, verified_at, verification_token)
- Create `app/models/session.py` with Session model (token_hash, user_id, expires_at, user_agent)
- Add proper indexes for query performance
- Add relationships between models
- Generate migration for these models

**Acceptance Criteria**:
- [ ] All models inherit from base model with timestamps
- [ ] Foreign key relationships defined with proper cascade rules
- [ ] Indexes on frequently queried columns (user_id, alias name+domain, token hashes)
- [ ] Models match database schema from design document
- [ ] Migration creates all tables with correct constraints
- [ ] Models include proper type hints for mypy

---

### T5: FastAPI Application & Routing (Priority: Critical, Est: 6h)

**Description**: Initialize FastAPI application with middleware, exception handlers, and API versioning.

**Tasks**:
- Create `app/main.py` with FastAPI app initialization
- Set up CORS middleware for dashboard
- Add request ID middleware for tracing
- Configure exception handlers for common errors (404, 422, 500)
- Create `app/api/v1/router.py` with versioned API structure
- Mount `/api/v1` prefix for all API routes
- Add `/health` and `/docs` endpoints
- Configure Jinja2 templates for FastAPI

**Acceptance Criteria**:
- [ ] FastAPI app starts on `uvicorn app.main:app`
- [ ] API documentation available at `/docs`
- [ ] Health endpoint returns 200 with system status
- [ ] CORS configured for local development
- [ ] Request IDs added to all responses
- [ ] Exception handlers return consistent JSON error format
- [ ] Jinja2 templates render with `TemplateResponse`

---

### T6: Session Management System (Priority: High, Est: 8h)

**Description**: Implement secure signed-cookie session system with Redis-ready interface.

**Tasks**:
- Create `app/services/session.py` with session create/verify/destroy
- Implement signed-cookie serialization with `itsdangerous`
- Add session middleware to attach current user to requests
- Create session storage interface (in-memory initially, Redis-ready)
- Implement session rotation on auth actions
- Add session expiration checks (30-day default, configurable)
- Store session metadata (IP, user agent, last activity)

**Acceptance Criteria**:
- [ ] Sessions created with cryptographically secure tokens
- [ ] Cookies signed with SECRET_KEY, tamper-proof
- [ ] Session middleware populates `request.state.user`
- [ ] Sessions expire after 30 days of inactivity
- [ ] Session rotation generates new token on login
- [ ] Storage interface can swap to Redis without code changes
- [ ] Sessions include httpOnly, secure, sameSite flags

---

### T7: Magic Link Authentication (Priority: High, Est: 8h)

**Description**: Implement passwordless magic link authentication flow.

**Tasks**:
- Create `app/api/v1/auth.py` with `/auth/request-magic-link` endpoint
- Generate secure random tokens with expiration (15 minutes)
- Store magic link tokens in database with hashing
- Create email template for magic link (Porter persona)
- Implement `/auth/verify-magic-link` endpoint
- Create session on successful verification
- Add rate limiting to prevent abuse (5 requests per hour per email)
- Implement token cleanup job specification

**Acceptance Criteria**:
- [ ] POST `/api/v1/auth/request-magic-link` sends email with link
- [ ] Magic link tokens hashed before database storage
- [ ] Tokens expire after 15 minutes
- [ ] Verification creates new session and redirects to dashboard
- [ ] Invalid/expired tokens show friendly error message
- [ ] Rate limiting prevents spam (5 req/hr per email)
- [ ] Email template matches visual style guide

---

### T8: WebAuthn/Passkey Foundation (Priority: High, Est: 10h)

**Description**: Implement WebAuthn registration and authentication using py_webauthn library.

**Tasks**:
- Install py_webauthn library
- Create `app/models/passkey.py` for storing WebAuthn credentials
- Implement passkey registration flow (challenge generation, credential verification)
- Implement passkey authentication flow
- Add API endpoints: `/auth/passkey/register-options`, `/auth/passkey/register`, `/auth/passkey/authenticate-options`, `/auth/passkey/authenticate`
- Store credential public keys and metadata
- Generate migration for passkey model
- Add user-friendly error handling for WebAuthn failures

**Acceptance Criteria**:
- [ ] Passkey registration creates credential in database
- [ ] Passkeys linked to user accounts with friendly names
- [ ] Authentication with passkey creates session
- [ ] Challenge/response flow prevents replay attacks
- [ ] Supports multiple passkeys per user
- [ ] Browser compatibility detection (graceful degradation)
- [ ] Credential counter stored to detect cloning attempts
- [ ] Works with hardware keys and platform authenticators

---

### T9: Pydantic Schemas & Validation (Priority: High, Est: 6h)

**Description**: Create Pydantic schemas for request/response validation across all API endpoints.

**Tasks**:
- Create `app/schemas/auth.py` with MagicLinkRequest, PasskeyRegister, SessionResponse
- Create `app/schemas/alias.py` with AliasCreate, AliasUpdate, AliasResponse
- Create `app/schemas/destination.py` with DestinationCreate, DestinationUpdate
- Add custom validators for email addresses, alias names
- Implement response models with field exclusions (no sensitive data)
- Add OpenAPI examples for documentation
- Create base response schemas with pagination metadata

**Acceptance Criteria**:
- [ ] All API endpoints use Pydantic models for validation
- [ ] Request validation returns 422 with clear error messages
- [ ] Alias name validation matches alias-naming-rules.md spec
- [ ] Email validation rejects invalid formats
- [ ] Response models exclude sensitive fields (password hashes, tokens)
- [ ] API docs show example requests/responses
- [ ] Pagination schemas include total, page, per_page fields

---

### T10: Authentication Middleware & Dependencies (Priority: High, Est: 4h)

**Description**: Create FastAPI dependencies for authentication and authorization.

**Tasks**:
- Create `app/dependencies.py` with `get_current_user` dependency
- Implement `require_auth` dependency that raises 401 if not authenticated
- Add optional authentication dependency for public routes
- Create `get_db` dependency for database sessions
- Implement rate limiting dependency using slowapi or custom
- Add request context helpers (get IP, user agent)

**Acceptance Criteria**:
- [ ] `require_auth` dependency injects current user into route handlers
- [ ] Unauthenticated requests to protected routes return 401
- [ ] Database session cleanup happens automatically after requests
- [ ] Rate limiting applied to auth endpoints
- [ ] Dependencies properly typed for IDE support
- [ ] Circular dependency issues avoided

---

### T11: Email Service Layer (Priority: High, Est: 6h)

**Description**: Create email sending service for magic links, verification emails, and notifications.

**Tasks**:
- Create `app/services/email.py` with SMTP client wrapper
- Implement async email sending with connection pooling
- Create Jinja2 email templates (plain text, no HTML for Porter)
- Add template rendering with context
- Implement email queue specification (synchronous initially, async-ready)
- Add error handling and retry logic
- Configure SMTP settings from environment

**Acceptance Criteria**:
- [ ] Emails sent via configured SMTP relay
- [ ] Porter persona template for verification emails
- [ ] Magic link template includes expiration time
- [ ] From address configurable per email type
- [ ] Connection errors handled gracefully
- [ ] Email sending logged for debugging
- [ ] Interface ready for background job queue migration

---

### T12: Development Environment with Docker Compose (Priority: High, Est: 6h)

**Description**: Create Docker Compose setup for local development with Postgres and app container.

**Tasks**:
- Create `docker-compose.yml` with Postgres 14 service
- Add pgAdmin service for database management
- Create `docker/Dockerfile.dev` for app container
- Mount source code as volume for hot reload
- Configure networking between containers
- Add `docker/Dockerfile.prod` for production builds
- Document Docker commands in README

**Acceptance Criteria**:
- [ ] `docker-compose up` starts Postgres and app
- [ ] Database persists data in named volume
- [ ] App hot reloads on code changes
- [ ] Environment variables loaded from `.env` file
- [ ] pgAdmin accessible at `http://localhost:5050`
- [ ] Postgres accessible from host for debugging
- [ ] Production Dockerfile builds optimized image

---

### T13: Testing Framework & Fixtures (Priority: High, Est: 8h)

**Description**: Set up pytest with fixtures for database, authentication, and API testing.

**Tasks**:
- Create `tests/conftest.py` with database fixtures (test DB, session, rollback)
- Implement test data factories with Faker
- Create authenticated client fixture for API tests
- Add fixtures for common models (user, alias, destination)
- Configure pytest-asyncio for async tests
- Set up pytest-cov for coverage reporting
- Create sample tests for auth endpoints

**Acceptance Criteria**:
- [ ] Tests run with `pytest` command
- [ ] Each test runs in transaction, rolled back after
- [ ] Test database separate from development database
- [ ] Factory fixtures create realistic test data
- [ ] Authenticated client fixture handles session cookies
- [ ] Coverage report generated with `pytest --cov`
- [ ] Sample tests pass and demonstrate patterns
- [ ] Async tests work with pytest-asyncio

---

### T14: Logging & Error Tracking (Priority: Medium, Est: 4h)

**Description**: Configure structured logging and error tracking for debugging and monitoring.

**Tasks**:
- Configure Python logging with JSON formatter for production
- Add request logging middleware with timing
- Create log correlation with request IDs
- Implement error context capture (user ID, request path, params)
- Add logging levels per module
- Configure log output (stdout for Docker, file for shared hosting)
- Document logging configuration in README

**Acceptance Criteria**:
- [ ] All requests logged with method, path, status, duration
- [ ] Errors logged with full context and stack traces
- [ ] Request ID included in all log entries for correlation
- [ ] Sensitive data (passwords, tokens) excluded from logs
- [ ] Log level configurable via environment variable
- [ ] JSON logs in production, human-readable in development
- [ ] Logs include user ID when authenticated

---

### T15: Configuration & Secrets Management (Priority: Medium, Est: 4h)

**Description**: Implement secure configuration and secrets management for all environments.

**Tasks**:
- Create `app/config.py` with Pydantic Settings classes
- Organize settings by concern (database, email, auth, app)
- Implement environment-specific configs (dev, staging, prod)
- Generate strong SECRET_KEY with script
- Document all configuration options in `.env.example`
- Add validation for required settings
- Create configuration loading order (env vars > .env file > defaults)

**Acceptance Criteria**:
- [ ] Configuration loaded from environment variables
- [ ] Missing required settings raise clear errors on startup
- [ ] SECRET_KEY generated with cryptographic randomness
- [ ] Database URL supports both postgres:// and postgresql:// schemes
- [ ] All sensitive values (keys, passwords) loaded from environment
- [ ] Configuration includes sensible defaults for development
- [ ] Settings classes use Pydantic validation

---

### T16: Basic CI/CD Pipeline (Priority: Medium, Est: 6h)

**Description**: Set up GitHub Actions for automated testing, linting, and type checking.

**Tasks**:
- Create `.github/workflows/test.yml` for CI pipeline
- Add job for running pytest with coverage
- Add job for code quality (black, isort, flake8, mypy)
- Configure matrix testing for Python 3.14, 3.11
- Add coverage reporting with codecov or similar
- Create pull request status checks
- Document CI/CD setup in README

**Acceptance Criteria**:
- [ ] CI runs on every push and pull request
- [ ] Tests must pass before merging
- [ ] Code formatting checked with black
- [ ] Import sorting checked with isort
- [ ] Linting passes with flake8
- [ ] Type checking passes with mypy
- [ ] Coverage report posted to PR comments
- [ ] Badge shows build status in README

---

### T17: API Error Handling & Standards (Priority: Medium, Est: 4h)

**Description**: Implement consistent error handling and response formats across the API.

**Tasks**:
- Create `app/exceptions.py` with custom exception classes
- Implement exception handlers for common errors (NotFound, Unauthorized, ValidationError)
- Define standard error response format (RFC 7807 Problem Details)
- Add error codes for client handling
- Create debug mode for detailed errors in development
- Document error format and codes in API docs
- Add logging for all errors

**Acceptance Criteria**:
- [ ] All errors return consistent JSON format
- [ ] Error responses include: type, title, status, detail, instance
- [ ] Client-safe error messages (no stack traces in production)
- [ ] Error codes help clients handle specific scenarios
- [ ] 404 errors return proper Not Found messages
- [ ] Validation errors list all field issues
- [ ] Unexpected errors return 500 with request ID for support

---

### T18: Health Check & Monitoring Endpoints (Priority: Medium, Est: 3h)

**Description**: Create health check and status endpoints for monitoring and deployment verification.

**Tasks**:
- Implement `/health` endpoint with database connectivity check
- Add `/health/ready` for readiness probe (database + migrations)
- Add `/health/live` for liveness probe (basic app responsiveness)
- Create `/version` endpoint with build info
- Add `/metrics` endpoint for basic metrics (requests, errors, latency)
- Document health check usage for deployment monitoring

**Acceptance Criteria**:
- [ ] `/health` returns 200 when system healthy, 503 when degraded
- [ ] Health checks test database connectivity
- [ ] Readiness probe fails if migrations not applied
- [ ] Liveness probe responds quickly without external dependencies
- [ ] Version endpoint shows commit hash and build timestamp
- [ ] Metrics endpoint provides Prometheus-compatible format
- [ ] Health checks don't require authentication

---

### T19: Database Seeding & Sample Data (Priority: Low, Est: 4h)

**Description**: Create scripts for seeding development database with sample data.

**Tasks**:
- Create `scripts/seed_db.py` for development data
- Generate sample users with verified emails
- Create sample aliases with various states (active, paused, deleted)
- Add sample destinations (verified and pending)
- Create sample message logs and spam quarantine entries
- Add command to reset database to clean state
- Document seeding process in README

**Acceptance Criteria**:
- [ ] `python scripts/seed_db.py` populates development database
- [ ] Sample data covers common scenarios for testing
- [ ] Seeding is idempotent (can run multiple times safely)
- [ ] Generated data realistic but clearly fake
- [ ] Includes edge cases (rate-limited users, full quarantine, etc.)
- [ ] Can generate specific test scenarios with CLI args
- [ ] Never runs in production environment

---

### T20: Documentation & Developer Guide (Priority: Low, Est: 4h)

**Description**: Create comprehensive documentation for developers working on the codebase.

**Tasks**:
- Update README with setup instructions (Docker, local, testing)
- Create `docs/DEVELOPMENT.md` with architecture overview
- Document database models and relationships
- Create API endpoint guide with examples
- Document authentication flows (magic link, passkey)
- Add troubleshooting section for common issues
- Create contribution guidelines

**Acceptance Criteria**:
- [ ] README includes quick start guide (< 5 minutes to running app)
- [ ] Development docs explain project structure
- [ ] Database schema documented with ERD or descriptions
- [ ] API examples use curl and Python requests
- [ ] Authentication flow diagrams included
- [ ] Troubleshooting covers Docker, database, and auth issues
- [ ] Code style and testing guidelines documented

---

## Ordering & Dependencies

**Phase 1: Core Infrastructure** (T1-T4)
- T1: Project Structure → T2: Database Layer → T3: Alembic → T4: Core Models

**Phase 2: API Foundation** (T5, T9-T10, T17-T18)
- T5: FastAPI App → T9: Pydantic Schemas → T10: Auth Dependencies → T17: Error Handling → T18: Health Checks

**Phase 3: Authentication** (T6-T8, T11)
- T6: Session Management → T7: Magic Links (requires T11) → T8: WebAuthn
- T11: Email Service (parallel to T6-T8)

**Phase 4: Development Environment** (T12-T16, T19-T20)
- T12: Docker Compose → T13: Testing Framework → T14: Logging → T15: Config Management
- T16: CI/CD (requires T13) → T19: Database Seeding → T20: Documentation

**Critical Path**: T1 → T2 → T3 → T4 → T5 → T6 → T7

## Open Questions

1. **Database Migrations**: Should we create incremental migrations as we build features, or one comprehensive initial migration with the full schema?
   - Recommendation: Comprehensive initial migration (easier rollback during development)

2. **API Authentication**: Should API endpoints accept Bearer tokens in addition to session cookies for webhook integrations?
   - Recommendation: Yes, add token-based auth for webhook testing and integrations

3. **Email Provider**: Should we abstract SMTP sending to support multiple providers (Postmark, SendGrid, etc.)?
   - Recommendation: Start with direct SMTP, add adapter pattern when second provider needed

4. **Session Storage**: Should we include Redis in docker-compose.yml from the start even if not used?
   - Recommendation: Add Redis container but keep in-memory sessions initially (easier development)

5. **Background Jobs**: Should we set up a job queue (RQ/Celery) in foundation or defer to background-jobs epic?
   - Recommendation: Defer to background-jobs epic; keep foundation synchronous

6. **File Uploads**: Do we need file upload handling for importing contacts or aliases?
   - Recommendation: Not in foundation; add if needed in alias management epic

7. **WebSocket Support**: Should we include WebSocket setup for real-time dashboard updates?
   - Recommendation: Defer to future enhancement; polling sufficient for MVP

8. **API Versioning**: Should we support multiple API versions simultaneously from the start?
   - Recommendation: No, single `/api/v1` version; add v2 when breaking changes needed

## Success Metrics

- [ ] Application starts without errors in Docker Compose
- [ ] All 20 tickets completed with passing tests
- [ ] Code coverage > 80% for core modules
- [ ] API documentation accurate and complete at `/docs`
- [ ] New developer can run app locally in < 10 minutes
- [ ] CI pipeline runs in < 5 minutes
- [ ] Zero critical security issues from linters/scanners
- [ ] Authentication flows work end-to-end (magic link + passkey)
- [ ] Database migrations apply cleanly up and down

## Notes

- This epic establishes patterns that all future epics will follow
- Keep shared hosting constraints in mind (connection pooling, no WebSockets, cron-based jobs)
- Prioritize developer experience: clear errors, fast tests, good documentation
- Privacy-first: no analytics, minimal logging, encrypt sensitive data
- All code must be AGPL-3.0 compatible
