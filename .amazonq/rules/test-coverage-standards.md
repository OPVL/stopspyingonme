# Test Coverage Standards

## Coverage Requirements
- **Minimum coverage**: 80% for core modules (app/services/, app/models/, app/api/)
- **Critical paths**: 100% coverage for authentication, session management, and email services
- **Edge cases**: All error conditions, validation failures, and boundary conditions must be tested
- **Database operations**: All CRUD operations with success and failure scenarios

## Test Categories Required
- **Unit tests**: Individual functions and methods with mocked dependencies
- **Integration tests**: Database operations with real async sessions
- **API tests**: All endpoints with valid/invalid inputs and authentication states
- **Service tests**: Business logic with edge cases and error conditions

## Specific Coverage Areas
- **Authentication flows**: Magic link creation, verification, expiration, and invalid tokens
- **Session management**: Creation, verification, expiration, and cleanup
- **WebAuthn operations**: Registration, authentication, and credential validation
- **Email service**: Template rendering, SMTP failures, and async operations
- **Validation logic**: Pydantic schema validation with invalid inputs
- **Database constraints**: Foreign key violations, unique constraints, and transaction rollbacks

## Test Quality Standards
- Each test should verify one specific behaviour
- Use descriptive test names that explain the scenario
- Mock external dependencies (SMTP, database in unit tests)
- Test both success and failure paths
- Include boundary value testing for numeric inputs
- Verify error messages and status codes match specifications

## Coverage Exclusions
- Migration files and database initialization scripts
- Configuration and settings modules
- Development-only utilities and scripts
- Third-party library wrappers with minimal logic
