# quitspyingonme - MVP Implementation Plan

## Overview
Comprehensive breakdown of epics and tickets for building the MVP of quitspyingonme, a privacy-focused email aliasing service. Focus on shared hosting deployment with simple flat pricing, no payments integration initially, and a test user pool for refinement.

---

## Epic Summary

### 1. Authentication & Accounts (13 tickets)
**Status**: Design complete
**File**: [docs/epics/authentication-accounts.md](epics/authentication-accounts.md)

Magic link + WebAuthn passkey authentication, session management (signed cookies), account export/delete with self-serve flows and stubbed admin approval. No passwords, privacy-first design.

**Key Decisions**:
- Signed cookie sessions (Redis-ready interface for future)
- SMTP relay for magic links (same as forwarding path)
- Porter persona for verification emails only
- Self-serve export/delete with auto-approving admin stub

**Key Tickets**: AA-01 (Magic Link API), AA-04/AA-05 (Passkey), AA-08/AA-09 (Export/Delete)

---

### 2. Alias & Routing Management (15 tickets)
**Status**: Design complete
**File**: [docs/epics/alias-routing-management.md](epics/alias-routing-management.md)
**Spec**: [docs/specs/alias-naming-rules.md](specs/alias-naming-rules.md)

CRUD for aliases with strict naming rules, multi-destination routing, destination verification via Porter, custom domain management with DNS verification.

**Key Decisions**:
- Readable aliases (user-defined or generated, e.g., `mint-bison-42`)
- No `+` patterns in alias local-part; reserved names blocked
- PII warning at creation
- Length: 3–32 chars; lowercase a–z, 0–9, hyphen

**Key Tickets**: AR-01 (Alias CRUD), AR-02 (Random generation), AR-06 (Destination verification), AR-07 (Custom domains)

---

### 3. Email Ingest & Forwarding (Shared Hosting) (14 tickets)
**Status**: Design complete
**File**: [docs/epics/email-ingest-forwarding-shared-hosting.md](epics/email-ingest-forwarding-shared-hosting.md)
**Specs**: [docs/specs/provider-selection.md](specs/provider-selection.md), [docs/specs/mail-validation-and-headers.md](specs/mail-validation-and-headers.md)

Cloudflare Email Routing webhook receiver, alias validation, size/bandwidth enforcement, spam filtering, metadata logging, SMTP relay forwarding, failure handling with retries.

**Key Decisions**:
- Cloudflare Email Routing primary (Postmark via adapter)
- Encrypted header-only snapshots for verification
- Inject `X-QSM-Validation` and `X-QSM-Inspect` headers
- SPF/DKIM/DMARC: log-only, notify user
- Oversize (>50MB): soft-bounce to sender, notify user

**Key Tickets**: IF-01 (Webhook receiver), IF-02 (Alias validation), IF-07 (Forwarding), IF-14 (Header viewer)

---

### 4. Spam Filtering & Quarantine (23 tickets)
**Status**: Design complete
**File**: [docs/epics/spam-filtering-quarantine.md](epics/spam-filtering-quarantine.md)
**Spec**: [docs/specs/spam-filtering-mvp.md](specs/spam-filtering-mvp.md)

Provider flags + heuristics, configurable thresholds, 30-day quarantine with release/delete, user controls (sensitivity, allow/deny lists), statistics, future ML path.

**Key Decisions**:
- Score-based (0–100); default threshold 50
- Provider flag = auto-quarantine
- User-adjustable sensitivity and lists
- Distinct from Overflow Hold in UI/messaging

**Key Tickets**: SF-01 (Scoring framework), SF-06 (Quarantine list), SF-10 (Toggle), SF-12 (Allow/deny lists)

---

### 5. Bandwidth & Subscription Enforcement (12 tickets)
**Status**: Design complete
**File**: [docs/epics/bandwidth-subscription-enforcement.md](epics/bandwidth-subscription-enforcement.md)
**Specs**: [docs/specs/plan-tiers.md](specs/plan-tiers.md), [docs/specs/bandwidth-enforcement.md](specs/bandwidth-enforcement.md), [docs/specs/sliding-thresholds.md](specs/sliding-thresholds.md)

Monthly usage tracking (bytes + emails), plan limits enforcement, Overflow Hold (default over-limit action), sliding early-cycle warnings + global 80% threshold, usage notifications.

**Key Decisions**:
- Overflow Hold (30d retention) default over-limit action
- Sliding thresholds: 60%/<25% elapsed, 70%/25-50%, 80%/50-75%, global 80%
- Usage warning emails enabled for MVP
- Separate notification persona (not Porter)

**Plan Tiers**:
- Starter: 10k emails/mo, 5GB/mo, spam add-on $5/mo, $12/mo
- Standard: 50k emails/mo, 25GB/mo, spam included, $29/mo
- Pro: 200k emails/mo, 100GB/mo, spam included, $79/mo

**Key Tickets**: BS-01 (Usage counters), BS-03 (Enforcement modes), BS-04 (Notifications), BS-08 (Dashboard)

---

### 6. Webhooks & Integrations (9 tickets)
**Status**: Design complete
**File**: [docs/epics/webhooks-integrations.md](epics/webhooks-integrations.md)
**Spec**: [docs/specs/webhook-events.md](specs/webhook-events.md)

User-configured webhooks with HMAC-SHA256 signatures, retry/backoff, delivery logs, test endpoint. Events: received, forwarded, failed, spam, usage thresholds, over-limit, oversize, hold actions.

**Key Decisions**:
- HMAC-signed payloads with `X-QSM-Signature` header
- Retry schedule: 1m, 5m, 30m, 2h
- Event schema versioned
- Privacy-first: no email content in payloads

**Key Tickets**: WI-01 (Config CRUD), WI-02 (HMAC signing), WI-04 (Delivery/retry), WI-06 (Test button)

---

### 7. Dashboard: Aliases & Destinations (22 tickets)
**Status**: Design complete
**File**: [docs/epics/dashboard-aliases-destinations.md](epics/dashboard-aliases-destinations.md)

Aliases list with search/filter/sort, CRUD flows, destinations management with verification, custom domain setup/verification, responsive design, accessibility (WCAG AA).

**Key Decisions**:
- Pagination (not infinite scroll)
- Inline editing for quick edits
- Slide-out panel for alias detail
- PII warning at creation

**Key Tickets**: AD-01 (Aliases list), AD-03 (Create flow), AD-09 (Add destination), AD-14 (Custom domain), AD-19 (Accessibility)

---

### 8. Dashboard: Bandwidth & Message Flow (19 tickets)
**Status**: Design complete
**File**: [docs/epics/dashboard-bandwidth-message-flow.md](epics/dashboard-bandwidth-message-flow.md)

Usage widgets/charts, message activity logs (metadata only), header viewer, Overflow Hold/spam quarantine views, failed messages, events list, export logs.

**Key Decisions**:
- Privacy-first: metadata only, no email content
- Subject hashes stored, not plaintext
- Header snapshots for verification
- Distinguish Overflow Hold from spam quarantine clearly

**Key Tickets**: BM-01 (Usage widget), BM-03 (Message log), BM-05 (Header viewer), BM-06 (Overflow Hold view)

---

### 9. Dashboard: Settings & Account (25 tickets)
**Status**: Design complete
**File**: [docs/epics/dashboard-settings-account.md](epics/dashboard-settings-account.md)

Account overview, passkey management, webhook config/logs, notification preferences, export/delete flows, security/privacy settings, multi-step confirmations for destructive actions.

**Key Decisions**:
- Export: JSON + CSV, 7-day expiry
- Delete: soft-delete with purge job, requires re-auth + email confirmation
- Webhook secret displayed once, masked thereafter
- Default metadata retention: 90 days (configurable)

**Key Tickets**: SA-02 (Passkey management), SA-05 (Webhook config), SA-12/SA-13 (Export), SA-14/SA-15 (Delete)

---

### 10. Data Security & Privacy (30 tickets)
**Status**: Design complete
**File**: [docs/epics/data-security-privacy.md](epics/data-security-privacy.md)

pgcrypto encryption, key management, retention policies, cleanup jobs, audit logging, GDPR compliance, TLS enforcement, security headers, vulnerability scanning.

**Key Decisions**:
- PostgreSQL pgcrypto for column-level encryption
- Subject hashing (SHA-256)
- Retention: failed emails 7d, spam/Overflow Hold 30d, metadata 90d, audit 1yr
- Password-free architecture (passkeys + magic links)

**Key Tickets**: SP-01 (pgcrypto setup), SP-02 (Key management), SP-08 (Retention config), SP-14 (Audit logging), SP-17 (GDPR)

---

### 11. Background Jobs & Workers (30 tickets)
**Status**: Design complete
**File**: [docs/epics/background-jobs-workers.md](epics/background-jobs-workers.md)

Cron-friendly job framework with CLI runner, job locking, retry schedules, cleanup jobs, rollups, webhook delivery, notifications. Pluggable for future worker queues (Celery/RQ).

**Key Decisions**:
- Shared-hosting first: cron jobs, not workers
- Idempotent jobs with database advisory locks
- Retry schedules: email 1h/6h/24h/48h, webhooks 1m/5m/30m/2h
- Staggered execution to avoid resource spikes

**Key Tickets**: BJ-01 (Job framework), BJ-03 (Email retry), BJ-04 (Overflow Hold expiry), BJ-10 (Bandwidth rollup), BJ-11 (Threshold checks)

---

### 12. Shared Hosting Deployment (30 tickets)
**Status**: Design complete
**File**: [docs/epics/deployment-shared-hosting.md](epics/deployment-shared-hosting.md)

cPanel deployment with Passenger/CGI, PostgreSQL setup, Cloudflare + SMTP relay config, cron jobs, encryption keys, TLS/SSL, security hardening, monitoring, backups.

**Key Decisions**:
- Passenger for Python app (CGI fallback)
- Cloudflare Email Routing for inbound
- SMTP relay for outbound (Gmail/SendGrid/Mailgun)
- Cron for background jobs
- Health check endpoint for monitoring

**Key Tickets**: SH-01 (Python env), SH-03 (Passenger), SH-07 (Cloudflare setup), SH-09 (Cron jobs), SH-20 (Deployment checklist)

---

## Supporting Specifications

### Personas
**File**: [docs/specs/notification-personas.md](specs/notification-personas.md)

- **Porter**: Verification only (magic links, destination verification)
- **Usage Warnings**: TBD persona for thresholds, Overflow Hold notices
- **Spam Quarantine**: TBD persona for spam notifications
- **Abuse Reports**: TBD persona for acknowledgments

### Email Verification
**File**: [docs/specs/email-verification.md](specs/email-verification.md)

Plain-text emails from Porter, no tracking, includes verification link + expiry notice + abuse report line.

### Abuse Reporting
**File**: [docs/specs/abuse-reporting.md](specs/abuse-reporting.md)

Auto-accepting endpoint for MVP; logs audit event and flags account for review.

---

## Current State
**File**: [docs/current-state.md](docs/current-state.md)

- Minimal SMTP-forwarding prototype complete ([README.md](../README.md))
- Design document finalized ([email-privacy-design.md](../email-privacy-design.md))
- Visual style guide established ([visual-style-guide.md](../visual-style-guide.md))

---

## Epic Totals

| Epic                                | Tickets | Status                       |
| ----------------------------------- | ------- | ---------------------------- |
| Authentication & Accounts           | 13      | Design complete              |
| Alias & Routing Management          | 15      | Design complete              |
| Email Ingest & Forwarding           | 14      | Design complete              |
| Spam Filtering & Quarantine         | 23      | Design complete              |
| Bandwidth & Subscription            | 12      | Design complete              |
| Webhooks & Integrations             | 9       | Design complete              |
| Dashboard: Aliases & Destinations   | 22      | Design complete              |
| Dashboard: Bandwidth & Message Flow | 19      | Design complete              |
| Dashboard: Settings & Account       | 25      | Design complete              |
| Data Security & Privacy             | 30      | Design complete              |
| Background Jobs & Workers           | 30      | Design complete              |
| Shared Hosting Deployment           | 30      | Design complete              |
| **TOTAL**                           | **242** | **Ready for implementation** |

---

## Implementation Priority

### Phase 1: Foundation (Weeks 1-4)
1. **Authentication & Accounts** (AA-01 → AA-13)
   - Magic links, passkeys, sessions, settings page
2. **Alias & Routing Management** (AR-01 → AR-08)
   - Alias CRUD, destination verification, basic routing
3. **Data Security & Privacy** (SP-01 → SP-08, SP-14, SP-20, SP-23, SP-24, SP-25)
   - Encryption setup, retention policies, audit logging, core security

### Phase 2: Mail Flow (Weeks 5-8)
4. **Email Ingest & Forwarding** (IF-01 → IF-14)
   - Cloudflare webhook, validation, forwarding, header viewer
5. **Spam Filtering & Quarantine** (SF-01 → SF-09, SF-19)
   - Basic scoring, quarantine, release/delete, webhook integration
6. **Background Jobs & Workers** (BJ-01 → BJ-03, BJ-09, BJ-13)
   - Job framework, email retry, basic cleanup

### Phase 3: Enforcement & Monitoring (Weeks 9-10)
7. **Bandwidth & Subscription** (BS-01 → BS-12)
   - Usage tracking, Overflow Hold, notifications, dashboard
8. **Background Jobs** (BJ-04 → BJ-12, BJ-15, BJ-21)
   - Cleanup jobs, rollups, threshold checks, webhook retries

### Phase 4: Dashboard & UX (Weeks 11-14)
9. **Dashboard: Aliases & Destinations** (AD-01 → AD-22)
   - Primary user interface for alias/destination/domain management
10. **Dashboard: Bandwidth & Message Flow** (BM-01 → BM-19)
    - Usage widgets, message logs, quarantine/hold views
11. **Dashboard: Settings & Account** (SA-01 → SA-25)
    - Webhooks, preferences, export/delete flows

### Phase 5: Integration & Polish (Weeks 15-16)
12. **Webhooks & Integrations** (WI-01 → WI-09)
    - User webhook config, delivery, testing
13. **Spam Filtering** (SF-10 → SF-20)
    - User controls, stats, notifications, docs
14. **Data Security & Privacy** (SP-09 → SP-13, SP-15 → SP-22, SP-26 → SP-30)
    - Remaining cleanup jobs, audit viewer, compliance, docs

### Phase 6: Deployment (Weeks 17-18)
15. **Shared Hosting Deployment** (SH-01 → SH-30)
    - Production deployment, monitoring, documentation
16. **Background Jobs** (BJ-14, BJ-16 → BJ-20, BJ-22 → BJ-30)
    - Remaining jobs, monitoring, optimization, testing

---

## Open Questions for Resolution

### Provider & Infrastructure
- **Secrets manager**: env vars only or AWS Secrets Manager/Vault?
- **SMTP relay**: Gmail (simple), SendGrid (scalable), Mailgun (reliable)?
- **Shared hosting providers**: Hostinger, Bluehost, SiteGround for docs?
- **Monitoring service**: self-hosted, free tier, or paid?

### Configuration Defaults
- **Metadata retention**: 90 days acceptable or prefer 180d?
- **Spam threshold**: 50 (balanced) or 70 (conservative)?
- **DNS recheck frequency**: daily or more frequent for pending domains?
- **Job execution timeout**: 5 minutes suitable for shared hosting?
- **Max users per shared hosting instance**: threshold for requiring VPS?

### Features & Behavior
- **Message log sort**: newest first or oldest first?
- **Spam notification default**: off, daily digest, or instant?
- **Allow/deny wildcards**: support in MVP (*.example.com)?
- **Account delete**: immediate hard delete or soft-delete with grace period (7d)?
- **Webhook secret**: regenerate-able without creating new webhook?
- **Audit log archive**: before purge or hard delete?
- **Vulnerability scanning**: external service preference?

### Personas
- **Usage warnings persona**: Gauge, Meter, Sentinel, or Signalman?
- **Spam notifications persona**: TBD
- **Abuse acknowledgment persona**: TBD

---

## Key Design Principles

### Privacy-First
- Minimize data collection: metadata only, no email content except failures/spam (encrypted, time-limited)
- Subject hashing (SHA-256), not plaintext storage
- Header-only snapshots for verification
- Automatic retention/purge enforcement
- GDPR-compliant export/delete

### Honest & Direct
- Visual style guide voice: no marketing fluff, no dark patterns
- Clear error messages and reason codes
- Transparent about what data is stored and why
- Explain Overflow Hold vs spam quarantine clearly
- PII warnings when creating aliases

### Shared-Hosting Friendly
- Cron jobs instead of workers (initially)
- In-memory rate limiting (Redis-ready)
- Signed cookie sessions (Redis-ready)
- Efficient database queries and batching
- Idempotent jobs with locking

### Accessible & Inclusive
- WCAG AA compliance (4.5:1 contrast minimum)
- Keyboard navigation with visible focus indicators
- Screen reader labels throughout
- Touch targets ≥44px for mobile
- Responsive design at all breakpoints

### Security-Hardened
- Password-free architecture (passkeys + magic links)
- TLS/SSL enforcement, HSTS
- pgcrypto encryption for sensitive data
- CSRF protection on all state-changing requests
- SQL injection prevention (parameterized queries only)
- Security headers (CSP, X-Frame-Options, etc.)
- Rate limiting on sensitive endpoints
- Audit logging for security events

---

## Next Steps

1. **Resolve open questions** (provider choices, defaults, personas)
2. **Create project structure** (directories, initial files)
3. **Set up development environment** (Python, PostgreSQL, dependencies)
4. **Implement Phase 1 tickets** (authentication, alias management, core security)
5. **Set up CI/CD** (testing, linting, deployment automation)
6. **Begin iterative development** following phase priority

---

## Documentation Structure

```
docs/
├── current-state.md              # Project snapshot
├── epics/                        # Epic breakdowns with tickets
│   ├── authentication-accounts.md
│   ├── alias-routing-management.md
│   ├── email-ingest-forwarding-shared-hosting.md
│   ├── spam-filtering-quarantine.md
│   ├── bandwidth-subscription-enforcement.md
│   ├── webhooks-integrations.md
│   ├── dashboard-aliases-destinations.md
│   ├── dashboard-bandwidth-message-flow.md
│   ├── dashboard-settings-account.md
│   ├── data-security-privacy.md
│   ├── background-jobs-workers.md
│   └── deployment-shared-hosting.md
└── specs/                        # Supporting specifications
    ├── alias-naming-rules.md
    ├── email-verification.md
    ├── abuse-reporting.md
    ├── provider-selection.md
    ├── mail-validation-and-headers.md
    ├── spam-filtering-mvp.md
    ├── plan-tiers.md
    ├── bandwidth-enforcement.md
    ├── sliding-thresholds.md
    ├── notification-personas.md
    └── webhook-events.md
```

---

**Generated**: December 24, 2025
**Status**: Design phase complete, ready for implementation planning and ticket creation in project management tool
