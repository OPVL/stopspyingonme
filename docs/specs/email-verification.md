# Spec: Email Verification (Porter)

## Sender Persona
- **Name**: Porter (Verification)
- **Address**: configurable (e.g., `porter@your-domain`)
- **Purpose**: Grants passage when checks pass; consistent, trustworthy voice.

## Delivery Path
- SMTP relay-first (same path as forwarding and magic-link), with optional provider override via config.
- Plain text only; no tracking pixels or link tracking.

## Subject
- `Confirm your email for alias forwarding`

## Body (Plain Text)
```
Hey — it's Porter.

You're verifying this address to receive forwarded emails from your alias.

Confirm here: <VERIFICATION_LINK>
This link expires in <TTL_HOURS> hours.

If this wasn't you, report abuse so we can flag the account:
<ABUSE_REPORT_URL>

We don't read your emails or sell your data.
```

## Abuse Report
- URL: `/abuse?email=<dest>&token=<short-id>` (exact route to be defined; stubbed in docs for now).
- Auto-accept in MVP; logs an audit event and flags the originating account for review.

## Tokens
- Single-use, signed tokens with TTL (configurable).
- Resend invalidates prior token; latest token only is accepted.

## Config Knobs
- `VERIFICATION_FROM_NAME` default: `Porter (Verification)`
- `VERIFICATION_FROM_ADDRESS` default: `porter@your-domain`
- `VERIFICATION_TOKEN_TTL_HOURS` default: `24`
- `ABUSE_REPORT_URL_BASE` default: site base + `/abuse`

## Style & Voice
- Follow visual style guide tone: direct, honest, helpful.
- Be explicit and human; avoid marketing language.

## Future
- Localized copy; customizable templates.
- Optionally separate persona for magic links, but default remains Porter for consistency.
