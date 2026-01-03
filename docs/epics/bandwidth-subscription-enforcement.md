# Epic: Bandwidth & Subscription Enforcement

## Context
- Simple, flat plan tiers to minimize friction; payments deferred for MVP.
- Track monthly usage (bytes + email counts) per user; enforce limits with privacy-first logging.
- Shared-hosting friendly implementation; pluggable for future Redis/worker queues.
- UI must align with the visual style guide.
 - Enforcement default: **Overflow Hold** (formerly "quarantine") — non-spam, over-limit messages are held for up to 30 days with clear user messaging.

## Tickets

### BS-01 Usage Counters (Bytes & Emails)
- Data model to record per-user monthly `bytes_used` and `emails_received`/`emails_forwarded`.
- Increment counters during ingest and after successful forward; avoid double-count.
- Tests: increments on receive/forward; month rollover.
**Acceptance Criteria**
- Counters reflect accurate totals; month boundary handled; idempotent updates.

### BS-02 Plan Limits & Config
- Central config for plan tiers: limits in bytes/mo and emails/mo; spam filter included/toggle.
- Environment-driven defaults; per-user plan assignment.
- Tests: config loading; per-user limit resolution.
**Acceptance Criteria**
- Limits retrieved deterministically for a user; configuration overridable.

### BS-03 Enforcement Modes
- Determine action when over limit: `hold` (Overflow Hold, default), `reject`, or `allow-with-flag`.
- Provide reason codes for enforcement outcomes.
- Tests: each mode behavior; reason code logged.
**Acceptance Criteria**
- Over-limit messages follow configured path; user-facing notice generated with clear explanation that hold is non-spam and time-limited.

### BS-04 Notifications & UX
- Dashboard event and banner for thresholds; sliding early-cycle warnings + global 80% rule.
- Notification emails use a dedicated persona (not Porter); copy clarifies Overflow Hold vs spam quarantine.
- Tests: threshold logic; event creation.
**Acceptance Criteria**
- Clear, human copy aligned to style guide; distinguishes hold from spam; links to manage auto-unsubscribe (future).
 - Usage warning emails are ENABLED for MVP by default and can be toggled via config.

### BS-05 Oversize Policy Integration
- Enforce 50MB max size; soft-bounce sender and notify user.
- Align reason codes with mail validation headers (`X-QSM-Reason=oversize`).
- Tests: oversize path integrated; bounce + notification.
**Acceptance Criteria**
- Consistent rejection behavior; dashboard reflects event.

### BS-06 Admin/Test Overrides
- Flag test users to ignore limits (no overage) while still tracking usage.
- Admin override hooks (stub) per user to lift limits temporarily.
- Tests: override respected; tracking unaffected.
**Acceptance Criteria**
- Overrides do not alter counters; only enforcement decisions.

### BS-07 Usage Rollup Job
- Background task to compute daily/weekly rollups for faster dashboard queries.
- Shared-hosting cron-friendly; pluggable for worker later.
- Tests: rollup correctness; idempotent runs.
**Acceptance Criteria**
- Rollups available; dashboard reads aggregated values.

### BS-08 Dashboard: Bandwidth Usage
- UI page shows monthly usage, thresholds, plan limits, and events.
- Accessible components per style guide; simple charts later.
- Tests: render with sample data; keyboard navigation.
**Acceptance Criteria**
- Usage clearly visible; events actionable with helpful guidance.

### BS-09 Subscription Status & Plan Display
- Show current plan tier, limits, spam filter status; link to docs.
- No payment integration; settings page provides clarity only.
- Tests: render plan details.
**Acceptance Criteria**
- Accurate plan display; no upsell language.

### BS-10 Webhooks: Usage Events
- Emit webhook events when crossing thresholds and on enforcement actions.
- HMAC-signed payloads; retries/backoff.
- Tests: event shape; signing; retry.
**Acceptance Criteria**
- Webhooks conform to existing webhook spec; idempotency ensured.

### BS-11 Config & Defaults
- `.env` template entries for thresholds, enforcement mode, overrides, and notification toggles.
- Docs describe safe defaults for shared-hosting.
- Tests: config loads; defaults applied.
**Acceptance Criteria**
- Sensible defaults; overrides via env verified.

### BS-12 Documentation
- User docs: how limits work, notifications, oversize policy.
- Technical docs: event codes, enforcement paths, rollup job.
- Style guide language throughout.
**Acceptance Criteria**
- Clear, direct explanations; example thresholds shown.

## Ordering (Suggested)
BS-01 → BS-02 → BS-03 → BS-05 → BS-04 → BS-06 → BS-07 → BS-08 → BS-09 → BS-10 → BS-11 → BS-12

## Open Questions
- Confirm default plan tiers and overage policy for initial test pool.
- Enforcement preference finalized: default `hold` (Overflow Hold) for 30 days; OK?
- Threshold strategy: adopt sliding early-cycle warnings + global 80% rule; confirm boundaries.
