# Epic: Spam Filtering & Quarantine

## Context
- Rudimentary MVP spam filtering to inform mail flow design (already spec'd).
- This epic covers full implementation: scoring, quarantine, release/delete, user controls, and future ML path.
- Integrates with Cloudflare/Postmark spam flags and simple heuristics.
- UI must distinguish spam quarantine from Overflow Hold clearly.

## Tickets

### SF-01 Spam Scoring Framework
- Centralized scoring logic: provider flags + heuristics = spam score (0-100).
- Threshold configurable (default: 50 = quarantine).
- Tests: scoring logic; threshold application; reason codes.
**Acceptance Criteria**
- Explainable scores; each factor contributes documented amount.

### SF-02 Provider Flag Integration
- Parse Cloudflare/Postmark spam indicators; map to internal score.
- Provider flag = automatic quarantine (unless user overrides).
- Tests: flag parsing; score contribution; override config.
**Acceptance Criteria**
- Provider signals trusted by default; user can adjust sensitivity.

### SF-03 Heuristic Rules
- Known bad sender domains (config list); missing/malformed headers; excessive recipients.
- Simple pattern matching; no ML in MVP.
- Tests: each heuristic; score accumulation; rule configuration.
**Acceptance Criteria**
- Rules maintainable via config; no code changes for updates.

### SF-04 Spam Decision Logic
- If score ≥ threshold OR provider flag → quarantine.
- Else → continue normal flow.
- Tests: decision accuracy; edge cases (score = threshold).
**Acceptance Criteria**
- Consistent decision boundary; logged for transparency.

### SF-05 Quarantine Storage
- Encrypt and store message content with spam score, reason, expiry (30d).
- Link to alias and user.
- Tests: storage encrypted; expiry enforced; access control.
**Acceptance Criteria**
- Minimal data retained; encrypted at rest; purge on schedule.

### SF-06 Quarantine List (Dashboard)
- Display quarantined messages: from, alias, score, reason, days remaining.
- Actions: release (mark not spam), delete.
- Tests: list renders; sorting/filtering; actions functional.
**Acceptance Criteria**
- Clear distinction from Overflow Hold: "Flagged as spam" vs "Over limit".

### SF-07 Release from Quarantine
- Forward message to destinations; optionally train filter (future).
- Mark as released; log action.
- Tests: release triggers forwarding; status updates; training hook.
**Acceptance Criteria**
- User feedback improves future filtering (future ML).

### SF-08 Delete from Quarantine
- Permanently delete message; no recovery.
- Confirmation required.
- Tests: deletion persists; confirmation enforced; audit logged.
**Acceptance Criteria**
- Clear warning; no accidental deletion.

### SF-09 Bulk Actions
- Select multiple quarantined messages; release or delete in batch.
- Confirmation for bulk delete.
- Tests: batch processing; partial failures handled; confirmation required.
**Acceptance Criteria**
- Efficient for high-volume users; progress indicator.

### SF-10 Spam Filtering Toggle
- Per-user setting: enable/disable spam filtering; per-plan feature.
- When disabled, all messages forwarded (still log potential spam flag).
- Tests: toggle persists; enforcement respected; audit logged.
**Acceptance Criteria**
- User control; plan restrictions enforced (Starter = add-on, Standard+ = included).

### SF-11 Sensitivity Adjustment
- User-configurable threshold (low/medium/high or numeric).
- Lower threshold = more aggressive filtering.
- Tests: threshold adjustment; decision changes; persistence.
**Acceptance Criteria**
- Clear guidance on trade-offs (false positives vs spam leakage).

### SF-12 Allow List / Deny List
- User-managed lists: always allow (whitelist), always block (blacklist).
- Applied before scoring; overrides provider flags.
- Tests: list management; precedence correct; wildcards supported.
**Acceptance Criteria**
- Simple UI; supports domains and email addresses; wildcards optional.

### SF-13 Spam Statistics
- Dashboard widget: spam caught this month, release rate, top spam sources.
- Tests: stats accurate; updates in real-time (or on rollup).
**Acceptance Criteria**
- Builds user trust in filtering; identifies patterns.

### SF-14 False Positive Reporting
- "Not spam" action logs feedback; optionally trains filter (future).
- Tests: feedback logged; training hook prepared.
**Acceptance Criteria**
- User feedback collected; future ML training path clear.

### SF-15 Spam Notifications
- Optional notification when spam is quarantined (email or dashboard-only).
- Configurable frequency: instant, daily digest, off.
- Tests: notification delivery; frequency respected; opt-out functional.
**Acceptance Criteria**
- Dedicated persona for spam notifications (not Porter).

### SF-16 Quarantine Expiry Warning
- Notify user 3 days before quarantine purge.
- Include count and link to review.
- Tests: warning sent; timing correct; link functional.
**Acceptance Criteria**
- Prevents surprise data loss; encourages review.

### SF-17 Quarantine Export
- Export quarantined messages metadata (not content) for analysis.
- Tests: export format; access control; retention.
**Acceptance Criteria**
- Helps users identify patterns; CSV format.

### SF-18 Spam Source Analysis
- Identify top spam sources (domains, IPs if available).
- Suggest adding to deny list.
- Tests: analysis accuracy; suggestions actionable.
**Acceptance Criteria**
- Empowers users to block repeat offenders.

### SF-19 Integration with Webhooks
- Emit `spam` event when message quarantined.
- Include score, reason, quarantine_id.
- Tests: event schema; delivery; idempotency.
**Acceptance Criteria**
- Consistent with other webhook events; documented.

### SF-20 Spam Filtering Docs
- User-facing: how spam filtering works, adjusting settings, managing lists.
- Technical: scoring algorithm, thresholds, provider integration.
- Tests: documentation clarity; examples accurate.
**Acceptance Criteria**
- Builds trust through transparency; no black-box filtering.

### SF-21 Future: ML Integration Path
- Design hook for ML-based scoring (external service or self-hosted model).
- Document API contract; fallback to heuristics if unavailable.
- Tests: hook design; fallback functional.
**Acceptance Criteria**
- Pluggable architecture; no code changes for ML addition.

### SF-22 Future: Bayesian Filter
- Implement simple Bayesian spam filter trained on user feedback.
- Per-user training data; privacy-preserving.
- Tests: training; scoring; accuracy improvement.
**Acceptance Criteria**
- Optional feature; improves over time with user feedback.

### SF-23 Future: Spam Trap Integration
- Integrate with public spam trap data sources (Spamhaus, etc.).
- Real-time lookups or cached lists.
- Tests: lookup performance; accuracy; rate limits.
**Acceptance Criteria**
- Enhances filtering without privacy compromise.

## Ordering (Suggested)
SF-01 → SF-02 → SF-03 → SF-04 → SF-05 → SF-06 → SF-07 → SF-08 → SF-09 → SF-10 → SF-11 → SF-12 → SF-13 → SF-14 → SF-15 → SF-16 → SF-17 → SF-18 → SF-19 → SF-20 → SF-21 → SF-22 → SF-23

## Open Questions
- Default spam threshold: 50 (balanced) or 70 (conservative)?
- Quarantine notification default: off, daily digest, or instant?
- Allow/deny list: support wildcards (*.example.com) in MVP?
- ML integration timeline: post-MVP or part of Phase 2?
