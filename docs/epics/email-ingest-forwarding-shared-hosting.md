# Epic: Email Ingest & Forwarding (Shared Hosting)

## Context
- MVP targets shared hosting first; Docker/VPS packaging later.
- Ingest via provider webhook (Cloudflare Email Routing or Postmark) to Python app.
- App validates alias state, enforces size/bandwidth limits, optionally runs rudimentary spam filtering, logs metadata, forwards via authenticated SMTP relay, and triggers webhooks.
- UI copy and any error surfaces must align with the visual style guide.
 - Provider priority: start with Cloudflare Email Routing for catch-all domains and cost-effective inbound; support Postmark via normalized adapter.
 - Privacy-first headers: store encrypted header-only snapshots (no body) for user verification; expose a viewer via an app link.

## Tickets

### IF-01 Provider Webhook Receiver
- Implement HTTP endpoints compatible with Cloudflare Email Routing and Postmark payload formats.
- Verify request authenticity (signatures/headers when available); log verification result.
- Normalize incoming payload to internal message model (from, to, subject hash, size, content ref/stream).
- Tests: parse both providers; signature validation happy/negative paths; normalization correctness.
**Acceptance Criteria**
- Endpoint accepts provider payload without additional transformations from hosting.
- Signature or secret validation enabled when provider supports it; insecure mode flagged.
 - Cloudflare path documented and tested first; Postmark supported via adapter with parity tests.

### IF-02 Alias Validation Hook
- Validate alias: exists, active, not expired; destinations exist and are verified.
- Enforce alias naming constraints (no `+`, reserved names blocked) via shared validator.
- Tests: inactive/expired/no destinations; happy path returns destination list.
**Acceptance Criteria**
- Returns structured reason codes for rejection (inactive, expired, no_verified_destinations, invalid_alias).
 - When validation fails, prepare a custom header summary for user notification if forwarding proceeds or a dashboard event otherwise.

### IF-03 Size Limit Enforcement (≤ 50MB)
- Calculate total message size; reject with clear status if exceeded.
- Log failure reason and minimal metadata.
- Tests: boundary conditions; oversize rejection.
**Acceptance Criteria**
- Oversize messages are not forwarded and produce a provider-appropriate response.
 - Soft-bounce to sender with clear reason (size limit exceeded) when provider supports bounce; notify user with a dashboard event and optional email.

### IF-04 Bandwidth Tracking & Check
- Increment per-user monthly counters (bytes/emails) on receipt; check against plan limits.
- If exceeded, reject or quarantine based on config; log outcome.
- Tests: counters increment; limit breach behavior.
**Acceptance Criteria**
- Enforced according to current plan config; outcomes recorded for reporting.

### IF-05 Rudimentary Spam Filtering
- Integrate basic spam scoring path: use provider spam flag if present or simple heuristics (e.g., known bad senders, header patterns).
- If spam: place in quarantine (30 days) with encrypted content pointer; log spam decision.
- Tests: flag-based path; heuristic path; quarantine persistence.
**Acceptance Criteria**
- Spam decisions are explainable and logged; quarantine respects retention policy.
 - Spam decision included in header summary for forwarded messages via custom header.

### IF-06 Metadata Logging
- Store minimal metadata: from, to (alias), subject hash, size, timestamps, status transitions (received/forwarded/failed/spam).
- No content storage except pointers for failures/spam in temporary stores.
- Tests: log entries created and updated appropriately.
**Acceptance Criteria**
- Subject hashing and no plaintext subject stored; complies with privacy guidance.
 - Header-only snapshot stored encrypted for user verification; no body retained outside failure/quarantine stores.

### IF-07 Forwarding via SMTP Relay
- Construct outgoing message; preserve essential headers; set destination(s) to verified addresses.
- Use STARTTLS; authenticate with relay credentials; retry on transient errors per schedule.
- Tests: successful forwards; transient failure triggers retry scheduling.
**Acceptance Criteria**
- Forwarding honors provider rate/limits safely; errors produce clear status and logs.
 - Inject `X-QSM-Validation` header summarizing SPF/DKIM/DMARC results and include `X-QSM-Inspect` link to header viewer in the app.

### IF-08 Failure Handling & Retry
- On forwarding failure: store encrypted content pointer/summary in `failed_emails` and schedule retries (1h, 6h, 24h, 48h).
- After 7 days, purge failed content.
- Tests: retry schedule applied; purge job honors retention.
**Acceptance Criteria**
- Failures do not loop indefinitely; capped retries with final failure status.

### IF-09 Webhook Triggers (User-Configured)
- After processing, trigger user webhooks with HMAC-signed payload: received, forwarded, failed, spam.
- Implement retry/backoff for webhook delivery.
- Tests: signing correct; retries on 5xx; idempotency.
**Acceptance Criteria**
- Webhooks deliver consistent event schema and signature headers.

### IF-10 Abuse Report Correlation
- If a destination reports abuse (from Porter email), correlate events to originating account/alias; flag for review.
- Add audit entry and optional provider feedback loop (stubbed).
- Tests: correlation path and audit record creation.
**Acceptance Criteria**
- Flagging appears in moderation logs; no user-visible disruption beyond configured actions.

### IF-11 Provider Configuration Docs
- Document setup for Cloudflare Email Routing and Postmark: webhook URL, secrets, expected payloads.
- Shared-hosting notes: Passenger/CGI URL formats, HTTPS requirements.
- Tests: doc correctness (examples align with implemented endpoints).
**Acceptance Criteria**
- Copy is clear, step-by-step, brand-aligned, and free of marketing fluff.

### IF-12 Config & Defaults
- Centralize settings: provider secrets, size limit, bandwidth enforcement mode, retry schedule, relay credentials.
- .env template updated; shared-hosting defaults safe.
- Tests: config loading; environment overrides.
**Acceptance Criteria**
- Sensible defaults work without provider signatures (dev), with warnings.

### IF-13 Operational Logging & Observability
- Structured logs with event codes and durations; minimal PII.
- Basic health endpoint; queue depth metrics for retries.
- Tests: log shape; health responds.
**Acceptance Criteria**
- Logs can be tailed on shared hosting; metrics optional for later.

### IF-14 Header Snapshot & Viewer
- Store encrypted header-only snapshot per message (no body) to enable user verification of signatures.
- Provide a user-accessible header viewer page with clear explanations and result badges.
- Tests: snapshot stored; viewer renders; access control enforced.
**Acceptance Criteria**
- Minimal data retained; headers only; encrypted at rest; purge via retention policy.

## Ordering (Suggested)
IF-01 → IF-02 → IF-03 → IF-04 → IF-05 → IF-06 → IF-07 → IF-14 → IF-08 → IF-09 → IF-10 → IF-12 → IF-11 → IF-13

## Open Questions
- Provider priority: decided — start with Cloudflare Email Routing; Postmark via adapter.
- Header preservation: decided — store encrypted header-only snapshot and expose viewer link; inject summary header for forwarded messages.
- SPF/DKIM validation: decided — log results, do not reject delivery solely on failure; notify user via header summary and dashboard event.
- Oversize behavior: decided — reject with soft-bounce to sender if supported; notify user with dashboard event and optional email.
