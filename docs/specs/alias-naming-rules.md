# Spec: Alias Naming Rules

## Purpose
Define strict, readable alias rules for MVP to protect privacy and ensure reliable routing under shared-hosting constraints.

## Rules
- **Uniqueness**: Aliases must be globally unique (case-insensitive).
- **Character set**: Lowercase `a–z`, digits `0–9`, hyphen `-`.
- **Length**: 3–32 characters.
- **Hyphen usage**: Cannot start or end with `-`; no consecutive hyphens `--`.
- **No plus**: `+` patterns disallowed in alias local-part to avoid ambiguous routing.
- **RFC subset**: Complies with email local-part per RFC 5321/5322 (subset enforced above).
- **Reserved local-parts** (blocked):
  - `admin`, `support`, `postmaster`, `abuse`, `help`, `security`, `billing`, `sales`, `info`, `contact`, `hostmaster`, `webmaster`, `root`, `mailer-daemon`, `no-reply`
- **PII warning**: Creation flow must display a reminder that personally identifiable aliases (e.g., full names) reduce privacy.
- **Destination emails**: May include `+`; restriction applies only to alias local-part.

## Generation Guidance
- **Readable by default**: Prefer adjective-noun-number (e.g., `mint-bison-42`) patterns.
- **Collision handling**: Retry with new number suffix; cap attempts; return conflict if exhausted.
- **Configurable**: Length, dictionary source, and numeric suffix range should be configurable.

## Validation
- Single source of truth validator shared by API, UI, and ingest path.
- Error messages must follow the brand voice and style guide.

## Future Considerations
- Catch-all aliases for subdomains (Phase 2).
- Allow optional underscore `_` only if routing stack proves safe; default remains blocked.
