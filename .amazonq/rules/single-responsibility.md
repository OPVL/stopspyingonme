# Single Responsibility Rules

## Authentication (S)
- Magic links + WebAuthn passkeys only
- Hash tokens, enforce expiry, rate limit per email
- Signed cookie sessions with rotation on auth
- Clear error messages, accessible UX

## Email Routing (S)
- Validate aliases per naming rules in specs/
- Encrypt header snapshots, no body retention
- Idempotent webhook processing
- SMTP relay forwarding with error handling

## Usage Enforcement (S)
- Track bandwidth by plan with sliding thresholds
- Default to Overflow Hold when limits exceeded
- Transparent warnings and audit logs
- Quarantine management with 30d retention

## Data Management (S)
- Encrypt sensitive columns with pgcrypto
- Implement retention/deletion policies
- Audit logs for sensitive actions
- Export/delete flows with confirmations
