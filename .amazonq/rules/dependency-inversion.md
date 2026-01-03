# Dependency Inversion Rules

## Abstractions Over Concretions (D)
- Depend on email provider interfaces, not implementations
- Database session injection via FastAPI dependencies
- Configuration injection over hardcoded values
- Mock-friendly service boundaries for testing

## Inversion Patterns (D)
- Repository interfaces injected into services
- SMTP client abstraction for testing
- Webhook delivery abstraction with retry policies
- Encryption service interface for key rotation

## Testing Dependencies (D)
- Factory patterns for test data
- Async test fixtures with cleanup
- Mock providers for external services
- In-memory alternatives for CI/CD
