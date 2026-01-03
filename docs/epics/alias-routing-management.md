# Epic: Alias & Routing Management

## Context
- Core MVP feature: create/manage aliases that forward to one or more verified destination emails.
- Flows must align with shared-hosting constraints; keep interfaces pluggable for future Docker/VPS.
- All UI must follow the visual style guide in [visual-style-guide.md](../../visual-style-guide.md).

## Alias Rules (Confirmed)
- Readable aliases (user-defined or generator-provided) with strict uniqueness.
- RFC-compliant local-part subset: lowercase a–z, digits 0–9, hyphen `-`; no plus `+` patterns.
- Length: 3–32 chars; must not start or end with hyphen; no consecutive hyphens.
- Block reserved local-parts (non-exhaustive): `admin`, `support`, `postmaster`, `abuse`, `help`, `security`, `billing`, `sales`, `info`, `contact`, `hostmaster`, `webmaster`, `root`, `mailer-daemon`, `no-reply`.
- PII warning at creation: remind users that personally identifiable aliases reduce privacy.
- Destination emails may include `+` (allowed); restriction applies to alias local-part only.
- Verification sender persona: Porter. Default From name "Porter (Verification)"; configurable address (e.g., porter@your-domain). Magic links may also be sent by Porter for consistency.

**Notes**: Use Porter persona for the sender by default; plain-text email, no tracking.

## Tickets

### AR-01 Alias CRUD API
- Endpoints: create, read (list/detail), update (labels/notes/status/expiry), delete.
- Validations: unique `alias_email`, status toggle (active/inactive), optional `expires_at`.
- Reserved names and format rules (local-part length, allowed chars); collision handling.
- Tests: create with defaults; update fields; delete; invalid formats rejected; uniqueness enforced.
**Acceptance Criteria**
- Creation enforces Alias Rules; reserved names rejected with helpful error copy per style guide.
- Uniqueness enforced case-insensitively; returns conflict error with guidance.
- Update cannot violate rules (e.g., changing to reserved or invalid format).
- UI shows PII warning before finalizing creation.

### AR-02 Random Alias Generation
- Endpoint/utility to generate pronounceable/random alias names; optional prefix/label.
- Prevent collisions; respect reserved words and format constraints.
- Configurable generation strategy (length, dictionary vs random).
- Tests: generation within rules; uniqueness under load; determinism for seeded mode (if provided).
**Acceptance Criteria**
- Generator produces names within Alias Rules (chars/length/no `+`/no reserved).
- Collision handling retries and caps attempts; returns 409 if exhausted.
- Optional readable pattern (e.g., adjective-noun-NN) configurable.

### AR-03 Labels & Notes
- Support text `note` and array `labels` on alias.
- Simple filtering by label in list endpoint.
- Tests: add/remove labels; filter behavior; note persistence.
**Acceptance Criteria**
- Labels normalized to lowercase; duplicates prevented.
- Filtering by single label returns matching aliases; empty label filter returns all.

### AR-04 Alias Status & Expiration
- Toggle `is_active`; optional `expires_at` with automatic deactivation on expiry.
- Background job ensures expiration is enforced.
- Tests: status toggle effects; expired aliases deactivated; non-expired remain active.
**Acceptance Criteria**
- Expired aliases treated as inactive by ingest validation.
- Background job idempotently deactivates expired aliases daily.

### AR-05 Multi-Destination Routing Model
- Many-to-many mapping via `alias_destinations` table; order not required (fan-out all verified).
- Only `is_verified=true` destinations are used for forwarding.
- Tests: link/unlink destinations; only verified routed; cascade on alias delete.
**Acceptance Criteria**
- Attempting to route to unverified destination is blocked with clear error.
- Deleting alias cascades and removes link records.

### AR-06 Destination Email CRUD + Verification Flow
- Endpoints: add/remove/list user destination emails; send verification email; confirm token.
- Deliver verification emails via SMTP relay (provider override configurable, same path used by magic-link).
- UI pages for add/verify/remove following style guide.
- Tests: add pending; send verification; confirm; prevent duplicate per user; removal cascades from alias routing.
**Acceptance Criteria**
- Plain-text verification email (no tracking) aligned to brand voice; includes link, expiry notice, and abuse-report line.
- Default sender uses Porter persona (From name "Porter (Verification)", address configurable, e.g., porter@your-domain).
- Verification tokens are single-use with TTL; resends invalidate prior token.

### AR-07 Custom Domain Management
- Endpoints: add custom domain; issue DNS verification token (TXT/MX requirements);
- Domain status tracking: pending/verified/failed; recheck endpoint.
- UI for domain onboarding and status.
- Tests: token issuance; status transitions; uniqueness; linkage to user.
**Acceptance Criteria**
- DNS instructions rendered clearly; status reflects last check time.
- Recheck endpoint performs DNS query and updates status atomically.

### AR-08 Alias-Destination Linking API
- Endpoints: attach/detach destination(s) to alias; list current routing.
- Validates destination ownership and verification before attach.
- Tests: attach verified only; detach; list reflects state.
**Acceptance Criteria**
- Attaching unverified or foreign-owned destination returns forbidden.
- List endpoint returns only verified linked destinations.

### AR-09 Frontend: Aliases Page (Dashboard)
- List/search/filter aliases; create/edit/delete; toggle status; set expiry; manage labels/notes.
- Action to generate random alias; inline feedback; follows style guide.
- Tests: render list; create/edit flows; accessibility checks (focus states, keyboard navigation).
**Acceptance Criteria**
- Creation flow shows PII warning and reserved-name validation inline.
- Keyboard-accessible controls; visible focus indicators per accessibility guidance.

### AR-10 Frontend: Destinations Page (Dashboard)
- Add destination email; show verification state; resend verification; remove.
- Clear copy aligned with brand voice; helpful error messages.
- Tests: render states; resend works; remove updates routing.
**Acceptance Criteria**
- Resend throttled (rate limit) and clearly indicates new token.
- Remove prevents routing and updates alias list counts.

### AR-11 Frontend: Domain Status (Dashboard)
- Add domain; show DNS instructions; display verification status and last check.
- Button to recheck; link to docs.
- Tests: render instructions; status polling; recheck triggers.
**Acceptance Criteria**
- Displays verification outcome banners using style guide colors.
- Polling interval configurable; manual recheck overrides schedule.

### AR-12 Routing Validation in Ingest Path (Hook)
- Validation function used by mail ingest: alias exists + active + not expired; destinations verified.
- Surfaces clear failure reasons (inactive/expired/no verified destinations) for logs.
- Tests: each failure mode; happy path returns destinations.
**Acceptance Criteria**
- Logs include reason codes for rejection consistent with downstream reporting.
- Returns verified destinations only; fails closed on ambiguous states.

### AR-13 Rate Limiting & Abuse Controls (Alias Ops)
- Per-user rate limits on alias creation/deletion; destination verification requests.
- Audit logs for alias create/delete, link/unlink, domain add/verify.
- Tests: limits enforced; audit entries written.
**Acceptance Criteria**
- Shared-hosting friendly rate limiter (in-process with leaky-bucket approximation) pluggable for Redis later.
- Audit entries include actor, action, target, timestamp.

### AR-14 Config & Defaults
- Config for alias format rules (allowed chars, length), generation strategy, verification email sender/from, DNS verification TTL.
- Update .env template and docs.
- Tests: config load; defaults suitable for shared hosting; overrides respected.
**Acceptance Criteria**
- Config exposes reserved-name list and char/length rules; defaults match Alias Rules.
- Verification sender name/address configurable and validated.

### AR-15 Docs
- User-facing docs: how aliases/destinations/domains work, verification steps, limitations.
- Technical docs: API endpoints, validation rules, audit events.
- Align copy and examples with style guide.
**Acceptance Criteria**
- Includes explicit PII warning and reserved-name list.
- Plain-language steps with no marketing fluff per style guide.

## Ordering (Suggested)
AR-01 → AR-02 → AR-06 → AR-08 → AR-12 → AR-09 → AR-10 → AR-07 → AR-11 → AR-13 → AR-14 → AR-03 → AR-04 → AR-05 → AR-15

## Notes
- Destination verification and magic-link should reuse the same mail-sending backend path to keep dev close to shared hosting behavior.
- Catch-all aliases are Phase 2; ensure model design doesn't block future `*@subdomain.domain` patterns.

## Open Questions
- Preferred alias format: purely random (e.g., `yx9f3`) vs readable (e.g., `mint-bison-42`)? Any reserved prefixes?
- Reserved local-parts list (e.g., `admin`, `support`, `postmaster`) to block?
- Default alias length and allowed character set (a-z, 0-9, hyphen)?
- Destination verification email content and sender address (brand voice, `from` display name)?
