# Spec: Provider Selection (Inbound Email)

## Recommendation
- **Primary**: Cloudflare Email Routing for MVP
  - Pros: DNS-level catch-all support, cost-effective, simple webhook integration, common in shared-hosting setups.
  - Cons: Limited advanced parsing features; provider retains minimal logs.
- **Alternative**: Postmark Inbound (adapter-supported)
  - Pros: Robust parsing, reliable delivery, detailed payloads.
  - Cons: Paid service; additional data passes through provider.

## Abstraction
- Normalize provider payloads to an internal message model (from, alias to, subject hash, size, headers, content pointer).
- Keep provider adapters thin; ensure parity tests across Cloudflare and Postmark.

## Privacy Considerations
- Minimize stored data: header-only snapshot (encrypted) + metadata; no body retained unless in failure/quarantine.
- Document provider-side logs and retention; provide opt-out guidance.

## Configuration
- `INBOUND_PROVIDER` = `cloudflare` (default) | `postmark`
- Provider-specific secrets and signature validation toggles.

## Future
- Add adapters for other providers; make signature verification mandatory in production.
