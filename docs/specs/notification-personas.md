# Spec: Notification Personas

## Principle
Use distinct personas for different communication types to keep intent clear.

## Porter (Verification)
- Role: Verification only (magic links, destination email verification).
- Voice: Calm, trustworthy, concise.

## Usage Warnings Persona (TBD)
- Role: Threshold crossings, over-limit notices, Overflow Hold explanations.
- Name ideas: "Gauge", "Meter", "Sentinel", "Signalman".
- Voice: Direct, helpful; clarifies non-spam nature of holds.

## Spam Quarantine Persona (TBD)
- Role: Inform about spam quarantine and release/delete options.
- Voice: Precise, no fear-mongering; explains why flagged.

## Abuse Report Acknowledgment (TBD)
- Role: Confirm receipt of abuse report and next steps.
- Voice: Respectful, non-confrontational.

## Config
- Per-persona `FROM_NAME` and `FROM_ADDRESS` settings; defaults documented.
- Each channel can be disabled or routed to dashboard-only.

## Future
- Localized personas; allow custom branding.
