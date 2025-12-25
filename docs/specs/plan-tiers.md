# Spec: Plan Tiers (Simple, Flat)

## Proposed Tiers (Config-Driven)
- **Starter**: 10k emails/mo, 5 GB/mo; spam filtering add-on $5/mo; base $12/mo.
- **Standard**: 50k emails/mo, 25 GB/mo; spam filtering included; base $29/mo.
- **Pro**: 200k emails/mo, 100 GB/mo; spam filtering included; base $79/mo.

## Overage (Optional)
- Default overage: $0.20/GB and $0.10 per 1k emails; disabled for test users.
- For MVP, overage billing deferred; limits enforced without charging.

## Config Knobs
- `PLAN_TIER` per user (`starter|standard|pro`).
- `EMAIL_LIMIT_PER_MONTH`, `BYTES_LIMIT_PER_MONTH` per tier.
- `SPAM_FILTER_INCLUDED` per tier.
- `OVERAGE_ENABLED` (default false for test pool).

## Display
- Dashboard shows plan tier, limits, and whether spam filtering is included.
- No payment links; documentation explains simplicity and privacy.

## Future
- Add Stripe integration; proration and plan changes.
- Custom tiers for BYO domain customers.
