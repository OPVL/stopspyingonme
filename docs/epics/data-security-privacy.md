# Epic: Data Security & Privacy

## Context
- Privacy-first architecture: minimize data collection, encrypt sensitive data at rest, enforce retention policies.
- PostgreSQL with pgcrypto for column-level encryption; key management via environment or secrets manager.
- Automated cleanup jobs for failed emails (7d), spam quarantine (30d), Overflow Hold (30d), and configurable metadata retention.
- Audit logging for security events and GDPR compliance.
- Shared-hosting friendly; pluggable for enhanced security later.

## Tickets

### SP-01 pgcrypto Setup & Schema
- Enable pgcrypto extension; create encryption/decryption functions.
- Apply to sensitive columns: `failed_emails.email_content`, `spam_quarantine.email_content`, header snapshots.
- Tests: encryption/decryption round-trip; key rotation preparation.
**Acceptance Criteria**
- Encrypted columns not readable without decryption key.
- Schema migration safe and reversible.

### SP-02 Encryption Key Management
- Store master key in environment variable or secrets manager (AWS Secrets Manager, Vault-compatible).
- Key rotation strategy documented; implement key versioning support.
- Tests: key loading; fallback on missing key (fail safely).
**Acceptance Criteria**
- Keys never committed to repository; deployment guide includes key generation.
- Graceful error on missing key with clear instructions.

### SP-03 Subject Hashing
- Hash email subjects using SHA-256 before storing in `email_logs.subject_hash`.
- Store hash only; no plaintext subjects persisted.
- Tests: hash consistency; search by hash (when applicable).
**Acceptance Criteria**
- Hashing applied consistently across all ingest paths.
- Subject hash allows deduplication without exposing content.

### SP-04 Header-Only Snapshot Storage
- Store encrypted header blocks (no body) for message verification.
- Link to message logs via `header_snapshot_id`.
- Retention aligned with message metadata retention policy.
- Tests: snapshot stored encrypted; viewer decrypts correctly; access control enforced.
**Acceptance Criteria**
- Body explicitly excluded; only headers captured.
- Snapshots purged on schedule.

### SP-05 Failed Email Temporary Storage
- Encrypt and store failed email content for retry (7-day retention).
- Include retry schedule, attempt count, last error.
- Tests: storage encrypted; purge after 7 days; retry access.
**Acceptance Criteria**
- Content not readable without decryption; purge job idempotent.

### SP-06 Spam Quarantine Temporary Storage
- Encrypt and store spam-flagged content (30-day retention).
- Include spam score, reason, release/delete actions.
- Tests: storage encrypted; purge after 30 days; release functional.
**Acceptance Criteria**
- Quarantine distinct from Overflow Hold; clear labels in storage and UI.

### SP-07 Overflow Hold Temporary Storage
- Store metadata pointer + encrypted message (30-day retention).
- Distinguish from spam quarantine with clear status field.
- Tests: storage; purge after 30 days; release functional.
**Acceptance Criteria**
- Over-limit, non-spam messages only; messaging clarifies this distinction.

### SP-08 Retention Policy Configuration
- Configurable retention periods: failed emails (7d default), spam (30d), Overflow Hold (30d), metadata logs (90d default), audit logs (1 year default).
- Environment-driven; per-user overrides (future).
- Tests: config loading; policy applied correctly.
**Acceptance Criteria**
- Policies documented; safe defaults for privacy.

### SP-09 Cleanup Job: Failed Emails
- Background job purges failed emails older than retention period.
- Runs daily; idempotent; logs purge actions.
- Tests: purge correctness; idempotency; no data loss within retention.
**Acceptance Criteria**
- Cron-friendly for shared hosting; safe error handling.

### SP-10 Cleanup Job: Spam Quarantine
- Background job purges spam quarantine older than 30 days.
- Runs daily; idempotent; logs purge actions.
- Tests: purge correctness; idempotency; retention respected.
**Acceptance Criteria**
- Logs show purge summary; no performance impact on large datasets.

### SP-11 Cleanup Job: Overflow Hold
- Background job purges Overflow Hold messages older than 30 days.
- Notifies user before final purge (1-day warning).
- Tests: purge correctness; notification sent; idempotency.
**Acceptance Criteria**
- Warning notification uses dedicated persona (not Porter).

### SP-12 Cleanup Job: Metadata Logs
- Purge message logs older than retention period (90d default, configurable).
- Preserve aggregated statistics; delete detail rows.
- Tests: purge correctness; stats preserved; idempotency.
**Acceptance Criteria**
- User-configurable retention via settings (future); deployment default safe.

### SP-13 Cleanup Job: Audit Logs
- Purge audit logs older than retention period (1 year default).
- Optionally archive to external storage before purge.
- Tests: purge correctness; optional archive; idempotency.
**Acceptance Criteria**
- Critical security events flagged for longer retention.

### SP-14 Audit Logging Framework
- Centralized audit log table: actor, action, target, timestamp, IP, result, metadata.
- Log security events: login, passkey add/remove, export, delete, limit changes, abuse reports, domain verifications.
- Tests: log entries created; query performance; retention applied.
**Acceptance Criteria**
- Structured logging; minimal PII; searchable by actor, action, date.

### SP-15 Audit Log Viewer (Dashboard)
- UI to view recent audit events; filter by action type, date.
- Export audit log for user (self-service).
- Tests: viewer renders; filter functional; export authorized.
**Acceptance Criteria**
- Accessible from settings page; clear event descriptions.

### SP-16 Data Minimization Review
- Document what data is collected and why; ensure no unnecessary fields.
- Review all database columns for privacy impact.
- Tests: documentation accuracy.
**Acceptance Criteria**
- Each field justified; alternatives considered; documented in privacy policy.

### SP-17 GDPR Compliance
- Right to access: export includes all user data.
- Right to erasure: delete account flow purges all data.
- Right to rectification: settings allow updating user data.
- Data portability: export in machine-readable format (JSON + CSV).
- Tests: export completeness; delete completeness; format compliance.
**Acceptance Criteria**
- Export/delete flows meet GDPR requirements; documented in privacy policy.

### SP-18 Data Processing Agreement (DPA) Template
- Template for users requiring DPAs (enterprise, BYO domain).
- Documents data handling, retention, security measures.
- Tests: template accuracy; covers common requirements.
**Acceptance Criteria**
- DPA optional for self-hosting; available on request for first-party hosting.

### SP-19 Password-Free Architecture Docs
- Document passkey + magic link approach; explain security benefits.
- No password storage, no password reset flows, no password leaks.
- Tests: documentation clarity.
**Acceptance Criteria**
- Aligns with style guide voice; builds trust without marketing fluff.

### SP-20 TLS/SSL Enforcement
- Enforce HTTPS for all web traffic; HSTS headers.
- STARTTLS for SMTP relay connections.
- Tests: HTTP redirects to HTTPS; SMTP TLS negotiation.
**Acceptance Criteria**
- Shared hosting config includes TLS cert setup instructions.

### SP-21 SPF/DKIM/DMARC Validation
- Validate incoming messages; log results in header snapshots.
- Do not reject solely on validation failure (per spec); inform user via custom headers.
- Tests: validation logic; header summary correct.
**Acceptance Criteria**
- Validation results accessible via header viewer.

### SP-22 Rate Limiting (Abuse Prevention)
- Rate limits on sensitive endpoints: login, verification, webhook test, alias creation.
- Shared-hosting friendly (in-memory leaky bucket); pluggable for Redis.
- Tests: limits enforced; reset periods respected; helpful error messages.
**Acceptance Criteria**
- Limits prevent abuse without frustrating legitimate users.

### SP-23 CSRF Protection
- Implement CSRF tokens for state-changing requests.
- SameSite cookie attributes; secure headers.
- Tests: CSRF token validation; invalid token rejection.
**Acceptance Criteria**
- All POST/PUT/DELETE endpoints protected; forms include tokens.

### SP-24 SQL Injection Prevention
- Use parameterized queries exclusively; ORM or query builder with escaping.
- Review all raw SQL for safety.
- Tests: automated SQL injection tests; code review.
**Acceptance Criteria**
- No string concatenation in queries; ORM practices enforced.

### SP-25 Secrets Management
- Document secure storage: environment variables, secrets manager, encrypted config.
- Rotation procedures for SMTP credentials, encryption keys, webhook secrets.
- Tests: secrets loading; fallback behavior.
**Acceptance Criteria**
- Secrets never logged; deployment guide includes generation commands.

### SP-26 Security Headers
- Implement recommended headers: CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy.
- Tests: headers present; policies enforced.
**Acceptance Criteria**
- Headers configured for shared hosting; docs explain each header.

### SP-27 Vulnerability Scanning & Updates
- Dependency scanning (Dependabot, Snyk); automated updates for security patches.
- Document update procedures for shared hosting.
- Tests: scanner integrated; alerts configured.
**Acceptance Criteria**
- Dependencies kept current; critical patches applied promptly.

### SP-28 Incident Response Plan
- Document procedures for security incidents: detection, containment, notification, recovery.
- Include user notification templates.
- Tests: plan completeness; contact procedures clear.
**Acceptance Criteria**
- Plan accessible to operators; covers common scenarios.

### SP-29 Privacy Policy & Terms
- Draft privacy policy covering data collection, retention, sharing, user rights.
- Terms of service for hosted version; separate license for self-hosted.
- Tests: legal review (future); clarity for non-lawyers.
**Acceptance Criteria**
- Written in plain language per style guide; legally sound.

### SP-30 Docs & User Education
- User-facing docs: "How we protect your privacy" "Understanding encryption" "Your data rights".
- Technical docs: encryption implementation, key management, retention policies.
- Tests: documentation clarity; examples accurate.
**Acceptance Criteria**
- Builds trust through transparency; no false claims.

## Ordering (Suggested)
SP-01 → SP-02 → SP-03 → SP-04 → SP-05 → SP-06 → SP-07 → SP-08 → SP-09 → SP-10 → SP-11 → SP-12 → SP-13 → SP-14 → SP-15 → SP-20 → SP-21 → SP-22 → SP-23 → SP-24 → SP-25 → SP-26 → SP-16 → SP-17 → SP-18 → SP-19 → SP-27 → SP-28 → SP-29 → SP-30

## Open Questions
- Preferred secrets manager for production (AWS Secrets Manager, HashiCorp Vault, or env vars only)?
- Metadata retention default: 90 days acceptable or prefer longer (180d)?
- Archive audit logs before purge or hard delete?
- External vulnerability scanning service preference?
