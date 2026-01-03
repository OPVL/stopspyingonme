# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Common Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r dev-requirements.txt
```

### Database Operations
```bash
# Initialize database (creates extensions)
python scripts/init_db.py

# Run migrations
alembic upgrade head

# Create new migration (after model changes)
alembic revision --autogenerate -m "Description of changes"

# Rollback one migration
alembic downgrade -1

# Seed development data
python scripts/seed_db.py                      # Default scenario
python scripts/seed_db.py --scenario edge_cases
python scripts/seed_db.py --scenario performance
```

### Running the Application
```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access points:
# - API: http://localhost:8000
# - Interactive docs: http://localhost:8000/docs
# - Health check: http://localhost:8000/health
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api/test_auth.py -v

# Run specific test
pytest tests/test_api/test_auth.py::test_magic_link_flow -v

# View coverage report
open htmlcov/index.html  # macOS
```

### Code Quality
```bash
# Run all linting checks (use this before committing)
./scripts/lint.sh

# Individual tools:
black app/ tests/          # Format code
isort app/ tests/          # Sort imports
flake8 app/ tests/         # Lint code
mypy app/                  # Type check

# Pre-commit hooks (one-time setup)
./scripts/setup-pre-commit.sh
```

## Architecture Overview

### Technology Stack
- **Framework**: FastAPI with async/await throughout
- **Database**: PostgreSQL 14+ with SQLAlchemy 2.0 (async ORM)
- **Migrations**: Alembic with async support
- **Authentication**: Magic links + WebAuthn/Passkeys (passwordless)
- **Session Management**: Signed cookies stored in database
- **Testing**: pytest with async fixtures and Faker factories

### Core Design Principles

**Privacy & Security First**:
- All sensitive fields encrypted using PostgreSQL `pgcrypto`
- Tokens are hashed (SHA-256), never stored in plaintext
- Structured logging without PII or sensitive data
- Single-use magic links with 15-minute expiry
- Sessions have expiration and are cleaned up automatically

**Shared Hosting Constraints**:
- Conservative database connection pooling (max 10 connections)
- Cron-based background jobs instead of separate workers
- Minimal memory footprint
- Graceful degradation for resource constraints

**Async-First Architecture**:
- All database operations use async SQLAlchemy
- All I/O operations (email, etc.) use async/await
- FastAPI endpoints are all async
- Tests use pytest-asyncio

### Project Structure
```
app/
├── api/v1/              # Versioned API endpoints
│   ├── auth.py         # Authentication (magic links, passkeys)
│   └── health.py       # Health checks with metrics
├── models/             # SQLAlchemy ORM models
│   ├── user.py         # User accounts
│   ├── destination.py  # Email forwarding destinations
│   ├── alias.py        # Email aliases
│   ├── session.py      # User sessions
│   ├── magic_link_token.py  # Magic link tokens
│   └── passkey.py      # WebAuthn credentials
├── schemas/            # Pydantic validation schemas
├── services/           # Business logic layer
│   ├── email.py        # Email sending
│   ├── magic_link.py   # Magic link generation/verification
│   ├── session.py      # Session management
│   └── webauthn.py     # WebAuthn operations
├── middleware/         # Custom middleware
│   ├── logging.py      # Request logging with correlation IDs
│   └── session.py      # Session management
├── config/             # Settings and configuration
├── db/                 # Database session management
├── utils/              # Utility functions
├── dependencies.py     # FastAPI dependency injection
├── exceptions.py       # Custom exception classes
└── main.py            # FastAPI application factory

tests/
├── conftest.py         # Test fixtures and configuration
├── factories.py        # Faker-based test data factories
├── mocks/             # Mock implementations (email, etc.)
├── test_api/          # API endpoint tests
├── test_models/       # Database model tests
├── test_schemas/      # Pydantic validation tests
└── test_services/     # Business logic tests
```

### Database Models & Relationships

```
User (1) ──────── (N) Destination
 │                     │
 │                     │
 │ (1)             (1) │
 │                     │
 └─── (N) Alias ───────┘
 │
 │ (1)
 └─── (N) Session
 │
 │ (1)
 └─── (N) Passkey

MagicLinkToken (standalone, references email)
```

**Key Model Details**:
- **User**: Core user accounts, identified by email
- **Destination**: Verified email addresses for forwarding (must be verified)
- **Alias**: Email aliases (e.g., `name@domain`) that forward to destinations
- **Session**: User authentication sessions with hashed tokens
- **MagicLinkToken**: Single-use passwordless login tokens (15-min expiry)
- **Passkey**: WebAuthn/FIDO2 credentials for biometric authentication

### API Design Patterns

**Versioned Endpoints**: All routes under `/api/v1/`

**Error Format**: RFC7807 Problem Details format with:
- `type`: Error type URL
- `title`: Human-readable summary
- `status`: HTTP status code
- `detail`: Error details
- `instance`: Request URL
- `error_code`: Machine-readable code
- `request_id`: Correlation ID for logging

**Pagination**: Cursor-based with `page`, `per_page`, `total`, `has_next`, `has_prev`

### Authentication Flows

**Magic Link Flow**:
1. User requests magic link with email
2. Token generated, hashed, stored in DB with 15-min expiry
3. Email sent with link containing token
4. User clicks link to verify token
5. If valid: create/find user, create session, set cookie, delete token

**Passkey/WebAuthn Flow**:
1. **Registration**: Generate WebAuthn creation options, browser creates credential, store public key
2. **Authentication**: Generate request options, browser signs challenge, verify signature, create session

## Code Quality Standards

**Line Length**: 88 characters (unified across black, isort, flake8, mypy)

**Type Hints**: Required for all public functions (enforced by mypy strict mode)

**Test Coverage**: >80% for core modules (auth, session, models, services)

**Async Patterns**:
- Always use async/await for I/O operations
- Use async context managers for database sessions
- All database operations through async SQLAlchemy

**Security Practices**:
- Never store passwords (passwordless authentication only)
- Hash all tokens before storage (SHA-256)
- Encrypt sensitive fields with PostgreSQL pgcrypto
- Use environment variables for secrets
- Validate all user inputs with Pydantic schemas

**Idempotency**: Operations should be idempotent where possible, especially database migrations

## Testing Approach

**Test Database**: Tests use SQLite in-memory database (configured in `conftest.py`)

**Test Factories**: Use Faker-based factories from `tests/factories.py`:
```python
user = await UserFactory.create(db, email="test@example.com")
destination = await DestinationFactory.create(db, user=user)
alias = await AliasFactory.create(db, user=user, destination=destination)
```

**Mock Services**: Email service is mocked in tests (`tests/mocks/email.py`)

**Test Categories**:
- Unit tests: Individual functions with mocked dependencies
- Integration tests: Database operations with real async sessions
- API tests: Full HTTP request/response cycles
- Service tests: Business logic with edge cases

**Test Structure**: Tests mirror the app structure (`test_api/`, `test_models/`, etc.)

## Important Configuration

**Environment Variables** (see `.env.example`):
- `SECRET_KEY`: Cryptographically secure secret (generate with `python scripts/generate_secret_key.py`)
- `DATABASE_URL`: PostgreSQL connection string (format: `postgresql+asyncpg://user:pass@host/dbname`)
- `RELAY_HOST`, `RELAY_PORT`, `RELAY_USER`, `RELAY_PASSWORD`: SMTP server for email
- `FROM_EMAIL`: Email address for system emails
- `ENVIRONMENT`: `development` or `production`

**Configuration Files**:
- `pyproject.toml`: All tool configurations (black, isort, mypy, pytest, coverage)
- `alembic.ini`: Database migration configuration
- `.pre-commit-config.yaml`: Pre-commit hook configuration

## Development Best Practices

**Before Creating PRs**:
1. Run `./scripts/lint.sh` to ensure code quality
2. Run `pytest --cov=app` to ensure tests pass with >80% coverage
3. If you modified models, create a migration with `alembic revision --autogenerate`
4. Update documentation if adding new features

**Commit Messages**: Follow conventional commits format (`feat:`, `fix:`, `docs:`, `test:`, etc.)

**Dependencies**: Must be AGPL-3.0 compatible (this is an AGPL-licensed project)

**SOLID Principles**: The codebase follows SOLID principles (see `.amazonq/rules/` for detailed guidelines)

## Troubleshooting

**Database connection fails**:
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Run `python scripts/init_db.py` to verify connection

**Tests failing with database errors**:
- Tests use SQLite in-memory (no PostgreSQL needed)
- Ensure `pytest-asyncio` is installed
- Check `conftest.py` for test database configuration

**Import errors**:
- Activate virtual environment: `source .venv/bin/activate`
- Ensure all dependencies installed: `pip install -r requirements.txt -r dev-requirements.txt`

**Magic links not working in development**:
- Check SMTP settings in `.env`
- Email service is mocked in tests (see `tests/mocks/email.py`)

**WebAuthn/Passkey fails**:
- Requires HTTPS in production
- Works with `localhost` in development
- Check browser console for credential errors

## Additional Notes

**Legacy SMTP Server**: The original `server.py` is still available for backward compatibility but is not the main application

**Docker Support**: `docker-compose.yml` available for running with PostgreSQL container

**Documentation**: See `docs/DEVELOPMENT.md` for comprehensive developer guide with architecture details, flows, and troubleshooting
