# Interface Segregation Rules

## API Boundaries (I)
- Separate auth, routing, usage, webhook interfaces
- Minimal endpoint responsibilities
- Clear request/response schemas
- Consistent pagination patterns

## Service Interfaces (I)
- Email service: validate, route, forward only
- Auth service: login, register, session only
- Usage service: track, enforce, report only
- Webhook service: subscribe, deliver, retry only

## Data Access (I)
- Repository pattern per domain entity
- Async session management separation
- Read/write operation isolation
- Migration script boundaries
