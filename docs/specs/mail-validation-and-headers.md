# Spec: Mail Validation & Headers (Privacy-First)

## Goals
- Inform users about SPF/DKIM/DMARC results with minimal data retention.
- Preserve headers for user verification without storing email bodies.

## Header Snapshot
- Store **encrypted header-only snapshot** per message: raw header block as received.
- No body storage unless in failure or spam quarantine.
- Retention: align with metadata retention; purge on schedule.

## Custom Headers (Injected on Forward)
- `X-QSM-Validation`: summary string, e.g., `spf=fail; dkim=pass; dmarc=none; spam=flagged`.
- `X-QSM-Inspect`: URL to header viewer in the app, e.g., `https://app/headers/<message-id>`.
- `X-QSM-Reason`: present only when a notable condition exists (e.g., `oversize-rejected`, `bandwidth-exceeded`, `alias-inactive`) for notifications.

## User Notification
- Dashboard event created for validation failures or notable conditions.
- Optional email notice using a dedicated notification persona (not Porter) with link to inspect headers, configurable.

## Validation Policy (MVP)
- SPF/DKIM/DMARC: **log-only**; do not reject delivery solely on failure.
- Spam: handled via MVP spec; include `spam` in summary header when quarantined or flagged.
- Oversize: reject and attempt soft-bounce to sender; notify user via dashboard and optional email.

## Privacy
- Snapshots encrypted at rest; access-controlled viewer.
- Avoid storing PII beyond headers; hash subjects in metadata.

## Future
- Allow users to download header snapshots.
- Stricter DMARC enforcement as an opt-in policy.
