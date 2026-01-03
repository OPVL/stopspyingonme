# Epic: Webhooks & Integrations

## Context
- Outgoing, user-configured webhooks deliver event notifications: received, forwarded, failed, spam, usage thresholds, over-limit/Overflow Hold, oversize.
- HMAC-signed payloads with retry/backoff and delivery logs.
- Shared-hosting friendly; pluggable for worker-based retries later.
- Align copy and UX with visual style guide; personas for emails are separate and not part of webhooks.

## Tickets

### WI-01 Webhook Config CRUD
- Endpoints/UI to create, update, enable/disable, and delete webhook endpoints per user.
- Fields: `url`, `secret`, `is_active`, event filters.
- Tests: CRUD operations; validation of URL and secret requirements.
**Acceptance Criteria**
- Secrets stored securely; event filters determine which events are sent.

### WI-02 HMAC Signing & Headers
- Implement HMAC-SHA256 signature using per-webhook secret.
- Headers: `X-QSM-Signature`, `X-QSM-Timestamp`, and optional `X-QSM-Key-Id`.
- Tests: signature correctness; timestamp skew handling.
**Acceptance Criteria**
- Receivers can verify signatures with documented process.

### WI-03 Event Schema
- Standard payload shape for events (see spec file): ids, timestamps, actor, alias, destinations (when relevant), sizes, status, reason codes.
- Tests: schema validation per event type.
**Acceptance Criteria**
- Schema consistent across events; versioned for evolution.

### WI-04 Delivery & Retry
- Attempt delivery with exponential backoff; idempotency keys to avoid duplicate processing.
- Retry schedule: 1m, 5m, 30m, 2h (configurable).
- Tests: retry on 5xx; stop on 2xx; idempotency respected.
**Acceptance Criteria**
- Delivery resilience without overwhelming shared-hosting resources.

### WI-05 Delivery Logs & Dashboard
- Store minimal delivery logs: status code, attempts, last error, last timestamp.
- UI to view recent deliveries and filter by status.
- Tests: logs persisted; UI renders and filters.
**Acceptance Criteria**
- Logs contain minimal data; no payload content stored beyond summaries.

### WI-06 Test Webhook Button
- Send a sample event to verify setup; show result inline.
- Tests: send and display status.
**Acceptance Criteria**
- Clear feedback; encourages verification during setup.

### WI-07 Provider Integrations Notes
- Document inbound provider setup (Cloudflare/Postmark) and how it relates to outgoing webhooks.
- Clarify that outbound webhooks are user-configured notifications.
**Acceptance Criteria**
- Documentation ties together inbound/outbound flows without confusion.

### WI-08 Config & Defaults
- `.env` entries: retry schedule, max attempts, log retention, skew tolerance.
- Tests: config loads; defaults applied.
**Acceptance Criteria**
- Defaults safe for shared hosting.

### WI-09 Docs
- User docs for setting up webhooks; verifying signatures; troubleshooting failures.
- Technical docs for headers, signature algorithm, and schema versioning.
**Acceptance Criteria**
- Clear, step-by-step guidance aligned with the style guide.

## Ordering (Suggested)
WI-01 → WI-02 → WI-03 → WI-04 → WI-05 → WI-06 → WI-08 → WI-07 → WI-09

## Open Questions
- Per-event filtering granularity: allow selecting specific statuses (e.g., only `failed`)?
- Log retention length for delivery logs?
- Maximum concurrent deliveries per user on shared hosting?
