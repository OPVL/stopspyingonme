# Spec: Bandwidth Enforcement

## Counters
- Track per-user monthly `bytes_used`, `emails_received`, `emails_forwarded`.
- Increment on receipt and on successful forward; avoid double-counting.
- Rollover at month boundary; create row if missing.

## Limits
- Resolved from plan tier config: bytes/month and emails/month.
- Thresholds for notices: 80%, 100%, and over-limit.

## Enforcement Modes
- `hold` (default): place over-limit messages in **Overflow Hold** (non-spam) for up to 30 days; allow release or discard later.
- `reject`: reject processing when over limit; create event.
- `allow-with-flag`: deliver but mark with event for visibility; only for admins/test users.

## Notifications
- Dashboard events at thresholds; email notices use dedicated persona (not Porter).
- Webhooks emitted for threshold crossings and enforcement.
 - Usage warning emails are enabled for MVP by default; deployments may disable via config.

## Reason Codes
- `bandwidth-exceeded`, `emails-exceeded`, `oversize`, `alias-inactive`, `no-verified-destinations`.
- Included in `X-QSM-Validation` summary and `X-QSM-Reason` when applicable; messages in hold tagged accordingly.

## Retention & Rollups
- Daily/weekly rollups for fast reads; cron-friendly on shared hosting.
- Overflow Hold retention: 30 days default.
- Purge events after configurable retention period.

## Privacy
- Store only counters and reason codes; no content beyond failure/quarantine.

## Future
- Overages billing and thresholds adjustments.
- Per-user custom limits.
