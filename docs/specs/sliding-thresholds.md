# Spec: Sliding Thresholds for Usage Warnings

## Goal
Provide early, sensible warnings throughout a billing cycle while enforcing a global 80% threshold.

## Definitions
- `usage`: percentage of monthly limit used (bytes or emails; compute separately and warn on whichever crosses thresholds).
- `elapsed`: fraction of billing period elapsed (0.0–1.0).

## Rules
- **Global threshold**: Warn at 80% usage at any time.
- **Early-cycle warnings**:
  - Elapsed < 0.25 → warn at 60% usage
  - 0.25 ≤ Elapsed < 0.50 → warn at 70% usage
  - 0.50 ≤ Elapsed < 0.75 → warn at 80% usage (same as global)
  - 0.75 ≤ Elapsed ≤ 1.0 → continue global 80% warnings; add "approaching reset" context
- Emit at 100% and over-limit regardless of elapsed.

## UX Copy
- Early-cycle: "You've used 60% early in your cycle — consider reducing volume (auto-unsubscribe) or adjusting your plan."
- Mid-cycle: "You're at 70% — keep an eye on your usage."
- Global: "80% reached — you may hit limits soon."
- Over-limit: "Over limit — messages are placed in Overflow Hold for up to 30 days."

## Actions
- Provide link to manage aliases and destinations.
- Provide link (future) to auto-unsubscribe assistant to reduce volume.

## Config
- Threshold values configurable per deployment with safe defaults above.
- Enable/disable early-cycle warnings.
 - Usage warning emails enabled for MVP; can be toggled.

## Implementation Notes
- Compute `elapsed` using plan period start/end.
- Warn on either counter crossing thresholds; de-duplicate events for the same period.
