# Developer Guide

This guide provides comprehensive information for developers working on the Stop Spying On Me codebase.

## Architecture Overview

### Technology Stack

- **Framework**: FastAPI 0.104+ with async/await support
- **Database**: PostgreSQL 14+ with SQLAlchemy 2.0 ORM
- **Migrations**: Alembic with async support
- **Authentication**: Magic links + WebAuthn/Passkeys
- **Session Management**: Signed cookies with database storage
- **Email**: Async SMTP with Jinja2 templates
- **Testing**: pytest with async fixtures and Faker factories
- **Code Quality**: Black, isort, flake8, mypy with unified 88-char line length

### Core Principles

The codebase follows SOLID principles with specific focus on:

1. **Privacy & Security First**: All sensitive data encrypted, minimal data retention
2. **Shared Hosting Constraints**: Conservative resource usage, cron over workers
3. **Async-First Architecture**: All I/O operations use async/await patterns
4. **Test-Driven Development**: >80% coverage requirement for core modules

## Project Structure

```
stopspyingonme/
├── app/                           # Main application package
│   ├── api/v1/                   # Versioned API endpoints
│   │   ├── auth.py              # Authentication endpoints
│   │   └── health.py            # Health check endpoints
│   ├── config/                   # Configuration management
│   │   ├── main.py              # Settings classes
│   │   └── environments.py      # Environment-specific configs
│   ├── db/                       # Database configuration
│   │   ├── base.py              # Base model imports
│   │   └── session.py           # Async session management
│   ├── middleware/               # Custom middleware
│   │   ├── logging.py           # Request logging with correlation IDs
│   │   └── session.py           # Session management middleware
│   ├── models/                   # SQLAlchemy models
│   │   ├── base.py              # Base model with common fields
│   │   ├── user.py              # User accounts
│   │   ├── destination.py       # Email forwarding destinations
│   │   ├── alias.py             # Email aliases
│   │   ├── session.py           # User sessions
│   │   ├── magic_link_token.py  # Magic link authentication
│   │   └── passkey.py           # WebAuthn credentials
│   ├── schemas/                  # Pydantic validation schemas
│   │   ├── base.py              # Common schemas (pagination, errors)
│   │   ├── auth.py              # Authentication schemas
│   │   ├── alias.py             # Alias management schemas
│   │   └── destination.py       # Destination schemas
│   ├── services/                 # Business logic layer
│   │   ├── email.py             # Email sending service
│   │   ├── magic_link.py        # Magic link generation/verification
│   │   ├── session.py           # Session management
│   │   └── webauthn.py          # WebAuthn operations
│   ├── templates/                # Jinja2 email templates
│   │   ├── email/               # Email templates
│   │   ├── auth/                # Authentication pages
│   │   └── dashboard/           # Dashboard templates
│   ├── utils/                    # Utility functions
│   │   └── logging.py           # Logging configuration
│   ├── dependencies.py          # FastAPI dependency injection
│   ├── exceptions.py            # Custom exception classes
│   └── main.py                  # FastAPI application factory
├── alembic/                      # Database migrations
│   ├── versions/                # Migration files
│   ├── env.py                   # Alembic configuration
│   └── script.py.mako          # Migration template
├── tests/                        # Test suite
│   ├── mocks/                   # Mock implementations
│   ├── test_api/                # API endpoint tests
│   ├── test_models/             # Model tests
│   ├── test_schemas/            # Schema validation tests
│   ├── test_services/           # Service layer tests
│   ├── conftest.py              # Test configuration and fixtures
│   └── factories.py             # Test data factories
├── scripts/                      # Utility scripts
│   ├── init_db.py               # Database initialization
│   ├── seed_db.py               # Development data seeding
│   ├── generate_secret_key.py   # Secret key generation
│   └── lint.sh                  # Code quality checks
└── docs/                         # Documentation
    ├── specs/                   # Technical specifications
    ├── epics/                   # Feature epic documentation
    └── current-state.md         # Current implementation status
```

## Database Models & Relationships

### Entity Relationship Overview

```
User (1) ──────── (N) Destination
 │                     │
 │                     │
 │ (1)             (1) │
 │                     │
 └─── (N) Alias ───────┘
 │
 │ (1)
 │
 └─── (N) Session
 │
 │ (1)
 │
 └─── (N) Passkey

MagicLinkToken (standalone, references email)
```

### Model Details

#### User
- **Purpose**: Core user accounts
- **Key Fields**: `email` (unique), `created_at`, `updated_at`
- **Relationships**: Has many destinations, aliases, sessions, passkeys
- **Encryption**: Email addresses stored in plaintext (needed for lookups)

#### Destination
- **Purpose**: Verified email addresses for forwarding
- **Key Fields**: `email`, `verified_at`, `user_id`
- **Relationships**: Belongs to user, has many aliases
- **Validation**: Email format validation, uniqueness per user

#### Alias
- **Purpose**: Email aliases that forward to destinations
- **Key Fields**: `name`, `domain`, `is_active`, `user_id`, `destination_id`
- **Relationships**: Belongs to user and destination
- **Constraints**: Unique name+domain combination
- **Validation**: Custom alias name rules (see specs/alias-naming-rules.md)

#### Session
- **Purpose**: User authentication sessions
- **Key Fields**: `token_hash`, `expires_at`, `user_id`
- **Security**: Tokens are hashed using SHA-256, never stored in plaintext
- **Cleanup**: Expired sessions automatically cleaned up

#### MagicLinkToken
- **Purpose**: Passwordless authentication tokens
- **Key Fields**: `email`, `token_hash`, `expires_at`
- **Security**: Single-use tokens with 15-minute expiry
- **Cleanup**: Tokens deleted after use or expiry

#### Passkey
- **Purpose**: WebAuthn/FIDO2 credentials
- **Key Fields**: `credential_id`, `public_key`, `sign_count`, `name`
- **Security**: Credential IDs and public keys stored as binary data
- **Features**: Sign count tracking for cloning detection

## Authentication Flows

### Magic Link Authentication

```mermaid
sequenceDiagram
    participant U as User
    participant A as API
    participant E as Email Service
    participant D as Database

    U->>A: POST /auth/request-magic-link
    A->>D: Create MagicLinkToken
    A->>E: Send magic link email
    A->>U: 200 OK (email sent)

    U->>A: GET /auth/verify-magic-link?token=...
    A->>D: Verify token (not expired, not used)
    A->>D: Create/find User
    A->>D: Create Session
    A->>D: Delete MagicLinkToken
    A->>U: Set session cookie, redirect
```

### WebAuthn/Passkey Authentication

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant A as API
    participant D as Database

    Note over U,D: Registration Flow
    U->>A: POST /auth/passkey/register-options
    A->>U: WebAuthn creation options
    U->>B: navigator.credentials.create()
    B->>U: New credential
    U->>A: POST /auth/passkey/register
    A->>D: Store Passkey

    Note over U,D: Authentication Flow
    U->>A: POST /auth/passkey/authenticate-options
    A->>D: Get user's passkeys
    A->>U: WebAuthn request options
    U->>B: navigator.credentials.get()
    B->>U: Signed assertion
    U->>A: POST /auth/passkey/authenticate
    A->>D: Verify signature, create Session
    A->>U: Set session cookie
```

## API Design Patterns

### Request/Response Structure

All API endpoints follow consistent patterns:

```python
# Request schemas inherit from BaseModel
class CreateAliasRequest(BaseModel):
    name: str = Field(..., description="Alias name")
    domain: str = Field(..., description="Domain name")
    destination_id: int = Field(..., description="Destination ID")

# Response schemas include metadata
class AliasResponse(BaseModel):
    id: int
    name: str
    domain: str
    full_address: str  # Computed field
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### Error Handling

All errors follow RFC7807 Problem Details format:

```python
{
    "type": "https://api.quitspyingon.me/errors/validation-error",
    "title": "Validation Error",
    "status": 400,
    "detail": "The alias name contains invalid characters",
    "instance": "/api/v1/aliases",
    "request_id": "req_123456789",
    "errors": [
        {
            "field": "name",
            "message": "Must contain only letters, numbers, and hyphens"
        }
    ]
}
```

### Pagination

List endpoints use cursor-based pagination:

```python
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
```

## Testing Strategy

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── factories.py             # Faker-based data factories
├── mocks/                   # Mock implementations
│   └── email.py            # Mock email service
├── test_api/               # API endpoint tests
├── test_models/            # Database model tests
├── test_schemas/           # Pydantic validation tests
└── test_services/          # Business logic tests
```

### Test Categories

1. **Unit Tests**: Individual functions with mocked dependencies
2. **Integration Tests**: Database operations with real async sessions
3. **API Tests**: Full HTTP request/response cycles
4. **Service Tests**: Business logic with edge cases

### Test Data Factories

Use Faker-based factories for realistic test data:

```python
# Create test user with related data
user = await UserFactory.create(db, email="test@example.com")
destination = await DestinationFactory.create(db, user=user)
alias = await AliasFactory.create(db, user=user, destination=destination)
```

### Coverage Requirements

- **Core modules**: 80% minimum coverage
- **Critical paths**: 100% coverage (auth, session, email)
- **Edge cases**: All error conditions must be tested
- **Database operations**: Success and failure scenarios

## Development Workflow

### Setting Up Development Environment

1. **Clone and setup**:
   ```bash
   git clone <repo-url>
   cd stopspyingonme
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt -r dev-requirements.txt
   ```

2. **Database setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   python scripts/init_db.py
   alembic upgrade head
   ```

3. **Seed development data**:
   ```bash
   python scripts/seed_db.py --scenario default
   ```

4. **Run development server**:
   ```bash
   uvicorn app.main:app --reload
   ```

### Code Quality Workflow

Before committing, always run:

```bash
# Format and lint code
./scripts/lint.sh

# Run tests with coverage
pytest --cov=app --cov-report=html

# Check types
mypy app/
```

### Database Migrations

Creating new migrations:

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new model"

# Create empty migration for data changes
alembic revision -m "Update existing data"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Configuration Management

### Environment-Specific Settings

Settings are managed through Pydantic with environment-specific overrides:

```python
# app/config/main.py
class Settings(BaseSettings):
    environment: str = "development"
    database_url: str
    secret_key: str

    class Config:
        env_file = ".env"

# app/config/environments.py
class DevelopmentSettings(Settings):
    debug: bool = True
    log_level: str = "DEBUG"

class ProductionSettings(Settings):
    debug: bool = False
    log_level: str = "INFO"
```

### Required Environment Variables

```bash
# Core settings
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname

# Email settings
RELAY_HOST=smtp.example.com
RELAY_PORT=587
RELAY_USER=your-smtp-user
RELAY_PASSWORD=your-smtp-password
FROM_EMAIL=noreply@quitspyingon.me

# Optional settings
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=true
```

## Troubleshooting

### Common Issues

#### Database Connection Issues

**Problem**: `asyncpg.exceptions.InvalidCatalogNameError`
**Solution**: Database doesn't exist, create it manually or check DATABASE_URL

**Problem**: `alembic.util.exc.CommandError: Can't locate revision identified by`
**Solution**: Reset alembic version table or run `alembic stamp head`

#### Docker Issues

**Problem**: `docker-compose up` fails with port conflicts
**Solution**: Check if PostgreSQL is running locally on port 5432

**Problem**: Container can't connect to database
**Solution**: Ensure database container is fully started before app container

#### Authentication Issues

**Problem**: Magic links not working in development
**Solution**: Check email service configuration and SMTP credentials

**Problem**: WebAuthn registration fails
**Solution**: Ensure HTTPS in production, localhost works for development

#### Test Issues

**Problem**: Tests fail with database connection errors
**Solution**: Tests use SQLite in-memory, check test database configuration

**Problem**: Async test fixtures not working
**Solution**: Ensure `pytest-asyncio` is installed and configured properly

### Performance Considerations

#### Database Optimization

- Use connection pooling (max 10 connections for shared hosting)
- Add indexes for frequently queried fields
- Use `select_related()` for foreign key relationships
- Implement pagination for large result sets

#### Memory Management

- Dispose of database engines properly in tests
- Use async context managers for database sessions
- Clean up expired tokens and sessions regularly

## Contributing Guidelines

### Code Style

- **Line length**: 88 characters (unified across all tools)
- **Import sorting**: isort with black profile
- **Type hints**: Required for all public functions
- **Docstrings**: Google style for public APIs

### Commit Messages

Follow conventional commits format:

```
feat: add email alias validation
fix: resolve session expiry bug
docs: update API documentation
test: add edge case tests for authentication
```

### Pull Request Process

1. Create feature branch from `main`
2. Implement changes with tests
3. Run full test suite and linting
4. Update documentation if needed
5. Submit PR with clear description

### Security Considerations

- Never commit secrets or credentials
- Use environment variables for configuration
- Encrypt sensitive database fields
- Validate all user inputs
- Follow OWASP security guidelines
- Regular dependency security audits

## Deployment Notes

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure proper database connection pooling
- [ ] Set up SSL/TLS certificates
- [ ] Configure email service credentials
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Test WebAuthn with HTTPS

### Shared Hosting Constraints

The application is designed for shared hosting environments:

- Conservative database connection limits (max 10)
- Cron-based background jobs instead of workers
- Minimal memory footprint
- Graceful degradation for resource constraints

This architecture ensures reliable operation in resource-constrained environments while maintaining security and performance standards.
