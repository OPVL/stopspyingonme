# Stop Spying On Me - Email Privacy Service

A modern email privacy service built with FastAPI that provides secure email alias forwarding with comprehensive privacy controls.

## Quick Start

### 1. Prerequisites

- Python 3.11+
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

```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy .
```

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

## Legacy SMTP Server

The original SMTP server (`server.py`) is still available for backward compatibility:

```bash
python server.py
```

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.

For commercial licensing options, contact: [contact@quitspyingon.me]