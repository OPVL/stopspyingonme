# Spec: Abuse Reporting

## Goal
Allow recipients to report unwanted verification attempts to flag potentially harmful accounts.

## MVP Behavior
- Endpoint accepts `email` and `token` (short identifier tied to verification attempt).
- Auto-accepts and records an audit event with timestamp, IP (if available), and associated account/alias.
- Flags the account for review; no user-visible moderation UI yet.

## Inputs
- `email`: destination being verified.
- `token`: short id associated with the verification mail sent.

## Outputs
- Plain-text acknowledgment page/message: "Thanks — we've flagged this."
- No login required.

## Logging & Audit
- Record: `action=abuse_report`, `email`, `token`, `timestamp`, `ip`.
- Optional notification to admin mailbox.

## Rate Limiting
- Basic per-IP limit to prevent abuse of the reporting endpoint.

## Future
- Moderation queue and actions (suspend, require re-verification).
- Correlate reports across aliases/users for detection.
- Email feedback loop with providers (if applicable).
