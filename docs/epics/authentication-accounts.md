# Epic: Authentication & Accounts

## Context
- Use signed-cookie sessions now; keep interface pluggable to add Redis later.
- Local dev should mirror shared hosting: use SMTP relay (same as forwarding path) for magic-link emails; optionally enable a provider (e.g., Postmark) via config without changing code paths.
- Account export/delete are self-serve; stub admin-approval hook that auto-approves for now.
- UI work must follow the visual style guide in [visual-style-guide.md](../../visual-style-guide.md).

## Tickets

### AA-01 Magic Link Request API
- POST to request login link; rate limited per email + IP.
- Generate single-use token with TTL; store pending session intent.
- Send email via configured SMTP relay; provider override via config.
- Response is generic (no existence leak).
- Tests: token persisted; expiry enforced; rate-limit responses; generic response for unknown emails.

### AA-02 Magic Link Consume API
- Validate token (unused, unexpired, bound to email and intent).
- Create session (signed cookie) and mark token used; redirect to dashboard.
- Graceful error page for invalid/expired; follow style guide.
- Tests: valid flow; reused token; expired token; tampered token.

### AA-03 Session Management
- Middleware to load user from signed cookie; idle and absolute timeouts; logout endpoint clears cookie.
 - Document Porter persona defaults for magic links and how to override.

### AA-04 WebAuthn Passkey Enrollment
- Authenticated start/finish endpoints; stores credential ID/public key/counter; allow multiple credentials.
- Prevent duplicate credential IDs across users.
- Tests: registration flow; duplicate prevention; multiple credentials per user.

### AA-05 WebAuthn Passkey Authentication
- Begin/assert endpoints; verify assertion; update counter; issue session.
- Tests: successful assertion; counter mismatch; unknown credential.

### AA-06 Account Creation & Linking
- First successful magic-link login provisions account.
- Subsequent logins reuse existing account; passkey enrollment links to same user.
- Tests: first-login creates; repeat login reuses; passkey linking persists.

### AA-07 Account Settings Page
- Shows email, plan tier, last login; list passkeys with remove action.
- Supports add passkey flow entry; includes logout.
- Style guide compliance (colors/spacing/voice).
- Tests: renders user data; revoke removes credential; auth required.

### AA-08 UX Flows for Auth
- Pages/forms for request link, consume redirect result, passkey login/register prompts.
- Error/success states aligned to style guide copy and colors.
- Tests: bad-token messaging is non-leaky; pages render without JS dependency.

### AA-09 Account Export
- Authenticated request endpoint queues export job; status endpoint; download with expiry.
- Export includes profile, aliases, destinations, domains, webhooks, usage metadata, subscriptions (no email content).
- Tests: request recorded; download authorized; expiry enforced.

### AA-10 Account Delete
- Requires re-auth (magic-link recheck or passkey assertion); self-serve path.
- Triggers soft-delete then purge job; cascades linked records; schedules cleanup of encrypted retained artifacts.
- Tests: access revoked after delete; idempotent delete; purge queued.

### AA-11 Security & Abuse Controls
- Rate limits on login initiation and WebAuthn begin; audit log entries for login, passkey add/remove, export/delete requests.
- Tests: rate-limit responses; audit entries written.

### AA-12 Config & Secrets
- Central config for token TTL, session TTLs, rate limits, mail sender/from, allowed origins, optional provider override.
- Update .env template; document defaults suitable for shared hosting.
- Tests: config load with defaults; override via env.

### AA-13 Docs
- Add README/docs section for auth flows, config, and operational notes (rate limits, TTLs, abuse controls).
- Include quick sequence diagrams as text/ASCII if needed; align language with brand voice.
