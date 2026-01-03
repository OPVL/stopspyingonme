# Implementation Guidelines

## Code Generation Rules
- Minimal implementations addressing exact requirements
- Async-first with sync fallbacks where needed
- Error handling with RFC7807 format
- Comprehensive test coverage for new code

## Security Implementation
- HMAC signature verification for webhooks
- Token-based auth with proper expiration
- Input validation using Pydantic models
- SQL injection prevention via SQLAlchemy ORM

## Performance Constraints
- Conservative database connection pooling
- Pagination for all list endpoints
- Efficient queries with proper indexing
- Cron-based background jobs initially

## Deployment Readiness
- Docker Compose for local development
- Health/readiness endpoints required
- Environment-based configuration
- Migration scripts with rollback support
