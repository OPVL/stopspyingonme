# Spec: Webhook Events

## Headers
- `X-QSM-Signature`: HMAC-SHA256 of body using webhook secret.
- `X-QSM-Timestamp`: Unix epoch seconds.
- `X-QSM-Key-Id` (optional): Identifier for secret rotation.

## Envelope
```json
{
  "event": "received|forwarded|failed|spam|usage_threshold|over_limit|oversize|hold_release|hold_delete",
  "version": "1",
  "id": "evt_...",
  "timestamp": "2025-12-24T12:34:56Z",
  "user_id": "...",
  "alias_id": "...",
  "metadata": { /* minimal, no content */ }
}
```

## Events
- `received`: { from, alias, size_bytes, provider: { name, signature_verified }, header_snapshot_id }
- `forwarded`: { destinations: [ ... ], size_bytes, attempts }
- `failed`: { reason_code, attempts, next_retry_at }
- `spam`: { score, reason, quarantine_id }
- `usage_threshold`: { metric: "bytes|emails", threshold_percent, current_percent }
- `over_limit`: { enforcement: "hold|reject|allow-with-flag", reason_code }
- `oversize`: { size_bytes, limit_bytes }
- `hold_release`: { hold_id, released_to: [ ... ] }
- `hold_delete`: { hold_id }

## Privacy
- No email content in payloads; use ids/pointers for header/quarantine references.
- Minimal fields to inform without exposing PII.

## Idempotency
- `id` unique per event; receivers MUST treat duplicates as the same event.

## Future
- Add `bandwidth_rollup` summaries sparingly; consider rate limiting.
