# Epic: Background Jobs & Workers

## Context
- Shared-hosting first: cron-friendly jobs that run as scheduled scripts.
- Pluggable architecture for future worker queues (Celery + Redis/RabbitMQ).
- Jobs must be idempotent, handle partial failures gracefully, and log progress.
- Cover retry schedules, cleanup, rollups, webhook delivery, and notifications.

## Tickets

### BJ-01 Job Framework & Registry
- Central job registry: maps job names to handler functions.
- CLI runner: `python jobs.py <job_name>` for cron invocation.
- Logging: structured logs with job name, start/end times, status, errors.
- Tests: registry lookup; runner invocation; logging format.
**Acceptance Criteria**
- Single entry point for all background jobs; cron-friendly.
- Each job returns success/failure exit code for monitoring.

### BJ-02 Job Locking (Shared Hosting)
- Prevent concurrent job runs using database advisory locks or lock files.
- Timeout handling: release lock if job crashes.
- Tests: concurrent run prevention; lock release on completion; timeout behavior.
**Acceptance Criteria**
- Safe for cron overlap scenarios; no duplicate processing.

### BJ-03 Email Forwarding Retry Job
- Retry failed forwards per schedule: 1h, 6h, 24h, 48h.
- Query `failed_emails` for pending retries; attempt forwarding; update attempt count and status.
- Purge after 7 days or max attempts exceeded.
- Tests: retry schedule respected; max attempts enforced; purge after retention.
**Acceptance Criteria**
- Idempotent; logs per-message outcome; notifies user on final failure.

### BJ-04 Overflow Hold Expiry Job
- Purge Overflow Hold messages older than 30 days.
- Send 1-day warning notification before final purge.
- Tests: warning sent; purge after 30 days; idempotency.
**Acceptance Criteria**
- Warning uses dedicated persona (not Porter); clear that purge is imminent.

### BJ-05 Spam Quarantine Expiry Job
- Purge spam quarantine older than 30 days.
- No pre-purge warning (already notified at quarantine time).
- Tests: purge correctness; idempotency; retention respected.
**Acceptance Criteria**
- Logs purge summary; efficient on large datasets.

### BJ-06 Failed Email Expiry Job
- Purge failed emails older than 7 days.
- Tests: purge correctness; idempotency; retention respected.
**Acceptance Criteria**
- Runs daily; logs purge count.

### BJ-07 Message Metadata Cleanup Job
- Purge message logs older than retention period (90d default).
- Preserve aggregated stats; delete detail rows.
- Tests: stats preserved; detail purged; configurable retention.
**Acceptance Criteria**
- User-configurable retention (future); deployment default safe.

### BJ-08 Header Snapshot Cleanup Job
- Purge header snapshots aligned with message metadata retention.
- Tests: snapshots purged; retention policy respected.
**Acceptance Criteria**
- Encrypted snapshots removed; no orphan records.

### BJ-09 Audit Log Cleanup Job
- Purge audit logs older than 1 year default.
- Optional archive to external storage before purge.
- Tests: archive functional; purge after archive; configurable retention.
**Acceptance Criteria**
- Critical events flagged for longer retention; archive format documented.

### BJ-10 Bandwidth Rollup Job
- Daily/weekly rollups: aggregate bytes_used and email counts per user.
- Optimize dashboard queries; purge stale rollups.
- Tests: rollup accuracy; idempotency; efficient on large datasets.
**Acceptance Criteria**
- Dashboard reads from rollups for performance; source data retained per policy.

### BJ-11 Usage Threshold Check Job
- Evaluate usage against thresholds (60%/70%/80%/100%); emit events for crossings.
- Sliding thresholds based on billing cycle elapsed.
- Deduplicate events: only emit once per threshold per cycle.
- Tests: threshold detection; sliding logic; deduplication.
**Acceptance Criteria**
- Events trigger dashboard notifications and optional emails.

### BJ-12 Alias Expiration Job
- Deactivate aliases where `expires_at < now()`.
- Tests: expiration applied; idempotency; audit logged.
**Acceptance Criteria**
- Runs daily; logs expired alias count.

### BJ-13 Magic Link Expiry Job
- Purge expired magic link tokens.
- Tests: expired tokens removed; active tokens preserved.
**Acceptance Criteria**
- Cleanup prevents table bloat; runs daily.

### BJ-14 Destination Verification Expiry Job
- Purge expired verification tokens for unverified destinations.
- Optionally remove unverified destinations after extended period (30d).
- Tests: token purge; optional destination removal; configurable grace period.
**Acceptance Criteria**
- Grace period prevents accidental removal; user notified before removal (optional).

### BJ-15 Webhook Retry Job
- Retry failed webhook deliveries per schedule: 1m, 5m, 30m, 2h.
- Update delivery logs; mark as permanently failed after max attempts.
- Tests: retry schedule; max attempts; idempotency; exponential backoff.
**Acceptance Criteria**
- Retries respect backoff; logs include attempt count and next retry time.

### BJ-16 Webhook Delivery Log Cleanup Job
- Purge webhook delivery logs older than retention period (30d default).
- Tests: purge correctness; configurable retention.
**Acceptance Criteria**
- Recent logs available for debugging; old logs pruned.

### BJ-17 Account Export Job
- Queue and process export requests; generate JSON + CSV; store with expiry link.
- Tests: export completeness; format correctness; expiry enforced.
**Acceptance Criteria**
- Export includes all user data per spec; progress tracked; user notified on completion.

### BJ-18 Account Deletion Job
- Process soft-delete accounts: purge all related data (aliases, destinations, domains, webhooks, logs).
- Cascade delete with audit trail; mark completion.
- Tests: cascade correctness; audit logged; idempotency.
**Acceptance Criteria**
- Irreversible after execution; immediate access revocation on soft-delete.

### BJ-19 Session Cleanup Job
- Purge expired sessions (past absolute or idle timeout).
- Tests: expired sessions removed; active sessions preserved.
**Acceptance Criteria**
- Runs daily; prevents session table bloat.

### BJ-20 DNS Verification Recheck Job
- Periodically recheck custom domain DNS for pending verifications (daily or on-demand).
- Update status; notify user on success/failure.
- Tests: recheck triggers DNS query; status updates; notification sent.
**Acceptance Criteria**
- Automatic recheck reduces manual work; user can also trigger manually.

### BJ-21 Notification Delivery Job
- Send queued email notifications (usage warnings, Overflow Hold notices, verification reminders).
- Batch to avoid SMTP rate limits; retry on transient failures.
- Tests: batch processing; retry logic; rate limit compliance.
**Acceptance Criteria**
- Shared-hosting friendly; respects SMTP relay limits.

### BJ-22 Job Monitoring & Alerting
- Log job execution times, success/failure rates, errors.
- Optional integration with monitoring service (future).
- Tests: metrics logged; format parseable.
**Acceptance Criteria**
- Operators can monitor job health; critical failures trigger alerts (future).

### BJ-23 Job Configuration
- Centralize job schedules, retry parameters, retention periods in config.
- Environment-driven; `.env` template includes job settings.
- Tests: config loading; overrides respected.
**Acceptance Criteria**
- Each job's schedule documented; defaults suitable for shared hosting.

### BJ-24 Cron Setup Documentation
- Document crontab entries for each job; recommended schedules.
- Shared-hosting specific notes (cPanel cron, execution limits).
- Tests: documentation accuracy; example crontab provided.
**Acceptance Criteria**
- Copy-paste crontab example included; explains each job's purpose.

### BJ-25 Worker Queue Migration Path
- Design job interface compatible with Celery/RQ for future migration.
- Document migration steps; feature flag to switch between cron and workers.
- Tests: compatibility; feature flag toggle.
**Acceptance Criteria**
- Jobs can run in either mode without code changes; config-driven switch.

### BJ-26 Job Failure Notifications
- Alert operators on repeated job failures (configurable threshold).
- Optional webhook or email to admin contact.
- Tests: failure detection; notification sent; threshold configurable.
**Acceptance Criteria**
- Prevents silent failures; alerts actionable.

### BJ-27 Idempotency & Replay Safety
- All jobs designed to be safely re-run; use database transactions and locks.
- Document idempotency guarantees per job.
- Tests: double execution produces same outcome; no duplicate side effects.
**Acceptance Criteria**
- Safe for cron overlap or manual re-runs; documented per job.

### BJ-28 Job Scheduling Best Practices
- Stagger job execution to avoid resource spikes.
- Prioritize critical jobs (retries, notifications) over cleanup.
- Tests: documentation completeness.
**Acceptance Criteria**
- Recommended schedule balances load; avoids midnight spike.

### BJ-29 Job Performance Optimization
- Batch processing for large datasets; pagination or chunking.
- Index optimization for job queries.
- Tests: performance benchmarks; optimization documented.
**Acceptance Criteria**
- Jobs complete within reasonable time on shared hosting; no resource exhaustion.

### BJ-30 Job Testing Harness
- CLI tool to manually trigger jobs for testing: `python jobs.py test <job_name>`.
- Dry-run mode: simulate without side effects.
- Tests: harness functional; dry-run safe.
**Acceptance Criteria**
- Developers can test jobs locally; dry-run shows what would be done.

## Ordering (Suggested)
BJ-01 → BJ-02 → BJ-23 → BJ-03 → BJ-04 → BJ-05 → BJ-06 → BJ-07 → BJ-08 → BJ-09 → BJ-10 → BJ-11 → BJ-12 → BJ-13 → BJ-14 → BJ-15 → BJ-16 → BJ-17 → BJ-18 → BJ-19 → BJ-20 → BJ-21 → BJ-22 → BJ-24 → BJ-25 → BJ-26 → BJ-27 → BJ-28 → BJ-29 → BJ-30

## Open Questions
- Preferred job failure alerting method (email, webhook, logging only)?
- DNS recheck frequency: daily or more frequent for pending domains?
- Worker queue preference for future: Celery, RQ, or custom solution?
- Job execution timeout defaults for shared hosting (e.g., 5 minutes)?
