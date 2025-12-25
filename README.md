# Stop Spying On Me - Email Privacy Service

A modern email privacy service built with FastAPI that provides secure email alias forwarding with comprehensive privacy controls.

## Quick Start

### 1. Prerequisites

- Python 3.14+
- PostgreSQL 14+ (for production)
- Git

### 2. Clone and Setup

```bash
git clone <repository-url>
cd stopspyingonme

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r dev-requirements.txt  # For development
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Generate a secure secret key
python scripts/generate_secret_key.py

# Edit .env with your settings
```

Required environment variables:
- `SECRET_KEY`: Cryptographically secure secret (use script above)
- `DATABASE_URL`: PostgreSQL connection string
- `RELAY_HOST`, `RELAY_PORT`: Your SMTP server for forwarding
- `RELAY_USER`, `RELAY_PASSWORD`: SMTP credentials
- `FROM_EMAIL`: Email address for system emails

### 4. Database Setup

```bash
# Initialize database (creates extensions)
python scripts/init_db.py

# Run migrations
alembic upgrade head
```

### 5. Development Server

```bash
# Start the FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000 for the API and http://localhost:8000/docs for interactive documentation.

### 6. Seed Development Data (Optional)

```bash
# Populate database with sample data for development
python scripts/seed_db.py

# Or use specific scenarios
python scripts/seed_db.py --scenario edge_cases
python scripts/seed_db.py --scenario performance
```

Available scenarios:
- `default`: Basic sample users, destinations, and aliases
- `edge_cases`: Edge cases like rate-limited users, unverified destinations
- `performance`: Large dataset (100 users) for performance testing

## Docker Development

```bash
# Start with Docker Compose (includes PostgreSQL)
docker-compose up -d

# Run migrations in container
docker-compose exec app alembic upgrade head
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api/test_main.py -v
```

## Code Quality

The project uses unified linting rules with consistent 88-character line length:

```bash
# Run all code quality checks
./scripts/lint.sh

# Individual tools
black .                    # Format code
isort .                    # Sort imports
flake8 app/                   # Lint code
mypy app/                  # Type check
```

### Linting Configuration

- **Line length**: 88 characters (unified across all tools)
- **Import sorting**: isort with black profile
- **Type checking**: mypy with strict settings
- **Code formatting**: black with Python 3.14+ target

All linting rules are configured in `pyproject.toml` and `setup.cfg` for maximum compatibility.

## Project Structure

```
stopspyingonme/
├── app/                    # Main application package
│   ├── api/v1/            # API endpoints (versioned)
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   ├── db/                # Database configuration
│   ├── middleware/        # Custom middleware
│   ├── templates/         # Jinja2 templates
│   ├── static/            # Static files
│   └── utils/             # Utility functions
├── alembic/               # Database migrations
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── docker/                # Docker configurations
└── docs/                  # Documentation
```

## Architecture

- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy 2.0 ORM
- **Migrations**: Alembic
- **Authentication**: Magic links + WebAuthn
- **Sessions**: Signed cookies
- **Templates**: Jinja2
- **Testing**: pytest with async support

## API Documentation

- Interactive docs: http://localhost:8000/docs
- OpenAPI spec: http://localhost:8000/openapi.json
- Health check: http://localhost:8000/health

## Development Guidelines

- Follow the core principles in `.amazonq/rules/`
- Maintain >80% test coverage for core modules
- Use async/await patterns throughout
- Implement proper error handling with RFC7807 format
- Encrypt sensitive data with PostgreSQL pgcrypto
- Run `./scripts/lint.sh` before committing
- Pre-commit hooks automatically enforce code quality
- See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for comprehensive developer guide

### Pre-commit Setup

```bash
# Install pre-commit hooks (one-time setup)
./scripts/setup-pre-commit.sh

# Hooks will run automatically on git commit
# To run manually on all files:
pre-commit run --all-files
```

## Troubleshooting

### Common Issues

**Database connection fails**:
- Ensure PostgreSQL is running and accessible
- Check `DATABASE_URL` in `.env` file
- Run `python scripts/init_db.py` to test connection

**Docker Compose issues**:
- Port 5432 conflict: Stop local PostgreSQL or change port in `docker-compose.yml`
- Permission errors: Ensure Docker has proper permissions
- Database not ready: Wait for PostgreSQL container to fully start

**Authentication not working**:
- Check SMTP settings in `.env` for magic links
- Ensure `SECRET_KEY` is set and secure
- For WebAuthn: Use HTTPS in production, localhost works for development

**Tests failing**:
- Run `pytest --tb=short` for concise error output
- Check test database configuration in `conftest.py`
- Ensure all dependencies installed: `pip install -r dev-requirements.txt`

**Import errors**:
- Activate virtual environment: `source .venv/bin/activate`
- Ensure project root in Python path
- Check for circular imports in modules

For detailed troubleshooting, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md#troubleshooting).

## Legacy SMTP Server

The original SMTP server (`server.py`) is still available for backward compatibility:

```bash
python server.py
```

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.

For commercial licensing options, contact: [contact@quitspyingon.me]
