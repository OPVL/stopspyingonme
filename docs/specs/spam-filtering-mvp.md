# Spec: Spam Filtering (MVP)

## Goal
Provide a minimal, explainable spam filtering path that informs the mail flow for MVP without heavy dependencies.

## Inputs
- Provider flags (if present): Cloudflare/Postmark spam indicators.
- Simple heuristics:
  - Known bad sender domains (config list)
  - Suspicious headers (e.g., missing `Date`, malformed `From`)
  - Excessive recipients (if provided)

## Decision
- If provider flag indicates spam OR heuristics exceed threshold → mark as `spam` and quarantine.
- Else → continue normal validation/forwarding.

## Quarantine
- Store encrypted pointer to content; minimal metadata.
- Retention: 30 days; allow "release" or "delete" action via dashboard.
- Log spam score/reason for transparency.

## Config
- `SPAM_ENABLED` (default: true for plans that include spam filtering; else false)
- `SPAM_THRESHOLD` (default: 1 flag)
- `SPAM_BAD_SENDER_DOMAINS` (comma list)

## Events
- Emit webhook `spam` event with reason and score.

## UI Notes
- Dashboard shows quarantine items count and simple reason.
- Release action forwards message to destinations and marks `released`.

## Future
- Integrate with reputable filtering service; Bayesian or ML scoring.
- Per-user training and allow-lists/deny-lists.
