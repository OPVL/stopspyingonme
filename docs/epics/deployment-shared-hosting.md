# Epic: Shared Hosting Deployment

## Context
- Initial MVP deployment target: cPanel-based shared hosting (common, affordable, low barrier to entry).
- Constraints: limited shell access, cron jobs instead of workers, Passenger/CGI for Python apps, no direct port 25 access.
- Provider dependencies: Cloudflare Email Routing (inbound) and authenticated SMTP relay (outbound).
- Must be production-ready with security hardening, monitoring, and documentation.

## Tickets

### SH-01 Python Environment Setup
- Document Python version requirements (3.10+ recommended).
- Setup virtualenv or venv for dependencies isolation.
- Install requirements.txt via pip.
- Tests: environment creation; dependencies installed; activation documented.
**Acceptance Criteria**
- Works with common shared hosting Python installations.
- Fallback instructions for hosts with older Python versions.

### SH-02 PostgreSQL Database Setup
- Provision PostgreSQL database via hosting control panel.
- Enable pgcrypto extension; run schema migrations.
- Tests: connection; extension enabled; tables created.
**Acceptance Criteria**
- Database credentials stored securely in .env; connection pooling configured.

### SH-03 Application Deployment (Passenger)
- Configure Passenger to run Flask/FastAPI app.
- Set up passenger_wsgi.py or .htaccess for WSGI/ASGI.
- Tests: app starts; routes accessible; logs functional.
**Acceptance Criteria**
- App accessible via HTTPS; startup time acceptable; restarts handled.

### SH-04 Alternative: CGI Deployment
- Fallback for hosts without Passenger: CGI script wrapper.
- Performance considerations documented.
- Tests: CGI invocation; request handling; environment variables.
**Acceptance Criteria**
- Works but discouraged; performance limitations noted.

### SH-05 Environment Configuration
- .env file setup with all required variables: database, SMTP, encryption keys, secrets.
- Template provided with safe defaults and required overrides flagged.
- Tests: config loading; missing required vars fail gracefully.
**Acceptance Criteria**
- .env never committed; .env.example provided; generation commands included.

### SH-06 Static Assets
- Serve static files (CSS, JS) via hosting's static file serving or CDN.
- Tailwind CSS compilation documented.
- Tests: assets load; paths correct; cache headers set.
**Acceptance Criteria**
- Static assets served efficiently; no app server load for static files.

### SH-07 Cloudflare Email Routing Setup
- Document DNS configuration: MX records pointing to Cloudflare.
- Configure webhook to Python app URL.
- Email routing rules: catch-all or per-alias.
- Tests: inbound email delivered to webhook; signature verified.
**Acceptance Criteria**
- Step-by-step DNS setup; webhook URL HTTPS-only; signature validation enabled.

### SH-08 SMTP Relay Configuration
- Document SMTP relay setup (Gmail, SendGrid, Mailgun, etc.).
- Test outbound email delivery; handle rate limits.
- Tests: relay auth; TLS negotiation; delivery success.
**Acceptance Criteria**
- Multiple relay options documented; rate limit guidance included.

### SH-09 Cron Job Setup
- Document all background jobs with recommended schedules.
- Provide example crontab entries.
- Configure cron via hosting control panel.
- Tests: jobs execute; logs written; locking functional.
**Acceptance Criteria**
- Jobs staggered to avoid resource spikes; logs accessible for debugging.

### SH-10 Encryption Key Generation
- Provide script to generate encryption keys securely.
- Document key storage and rotation procedures.
- Tests: key generation; strength validation.
**Acceptance Criteria**
- Keys generated with sufficient entropy; stored securely; never logged.

### SH-11 TLS/SSL Certificate Setup
- Document certificate provisioning (Let's Encrypt via cPanel, hosting-provided).
- Enable HTTPS; enforce HSTS.
- Tests: HTTPS functional; HTTP redirects; certificate valid.
**Acceptance Criteria**
- Auto-renewal configured; mixed content warnings resolved.

### SH-12 Security Hardening
- Disable directory listing; protect .env and sensitive files via .htaccess.
- Set restrictive file permissions.
- Configure security headers.
- Tests: sensitive files inaccessible; headers present.
**Acceptance Criteria**
- .env, config files, and database credentials not web-accessible.

### SH-13 Error Handling & Logging
- Configure Python logging to file accessible via cPanel File Manager or FTP.
- Log rotation setup.
- Tests: logs written; rotation functional; errors captured.
**Acceptance Criteria**
- Structured logging; errors include stack traces; sensitive data redacted.

### SH-14 Database Migrations
- Document schema migration process; provide migration scripts.
- Backup before migrations; rollback procedure.
- Tests: migrations run; rollback functional; backup/restore verified.
**Acceptance Criteria**
- Safe to run migrations in production; downtime minimized.

### SH-15 Monitoring & Alerting
- Document basic monitoring: cron job logs, app error logs, database connection health.
- Optional integration with uptime monitoring services (UptimeRobot, Pingdom).
- Tests: monitoring checks functional; alerts configured.
**Acceptance Criteria**
- Operators notified of critical failures; health check endpoint available.

### SH-16 Backup Strategy
- Document database backup procedures (cPanel backups, pg_dump).
- Backup frequency recommendations; retention policy.
- Tests: backup creation; restore verified.
**Acceptance Criteria**
- Automated daily backups; offsite storage recommended; restore tested.

### SH-17 Resource Limits & Optimization
- Document shared hosting resource constraints (CPU, memory, execution time).
- Optimize queries, batch processing, and caching.
- Tests: resource usage profiled; optimization documented.
**Acceptance Criteria**
- App stays within typical shared hosting limits; performance acceptable.

### SH-18 Rate Limiting Configuration
- Configure rate limits suitable for shared hosting resources.
- In-memory leaky bucket implementation; no Redis required.
- Tests: limits enforced; performance impact minimal.
**Acceptance Criteria**
- Prevents abuse without exhausting host resources.

### SH-19 Dependency Management
- Document dependency installation and updates.
- Pin versions in requirements.txt; security update procedures.
- Tests: dependency installation; version pinning; update process.
**Acceptance Criteria**
- Reproducible builds; clear update instructions; security patches prioritized.

### SH-20 Initial Deployment Checklist
- Step-by-step checklist: environment setup, database provisioning, app deployment, DNS configuration, cron setup, testing.
- Tests: checklist completeness; order logical.
**Acceptance Criteria**
- New deployments follow checklist reliably; nothing missed.

### SH-21 Health Check Endpoint
- Implement `/health` endpoint checking database connection, SMTP relay, disk space (optional).
- Tests: endpoint responds; checks accurate; failures reported.
**Acceptance Criteria**
- Returns 200 on healthy, 503 on unhealthy; includes status details.

### SH-22 Admin Tools & Scripts
- Provide scripts for common tasks: user creation, password reset (N/A), data export, manual job triggers.
- Tests: scripts functional; documented.
**Acceptance Criteria**
- Operators can perform routine tasks without database access.

### SH-23 Troubleshooting Guide
- Common issues and solutions: webhook not receiving emails, SMTP auth failures, cron jobs not running, database connection errors.
- Tests: guide completeness; solutions accurate.
**Acceptance Criteria**
- Covers 80% of common deployment issues; solutions actionable.

### SH-24 Performance Benchmarking
- Document expected performance on typical shared hosting (response times, throughput).
- Provide benchmarking tools/scripts.
- Tests: benchmarks run; results realistic.
**Acceptance Criteria**
- Baseline performance documented; helps identify regressions.

### SH-25 Scaling Guidance
- Document when to migrate off shared hosting (traffic thresholds, resource exhaustion signs).
- Migration path to VPS/Docker outlined.
- Tests: documentation clarity.
**Acceptance Criteria**
- Clear indicators for scaling up; migration steps outlined.

### SH-26 Multi-Tenancy Setup (First-Party Hosting)
- Document configuration for hosting multiple users on single shared hosting instance.
- Isolation considerations; resource allocation.
- Tests: multi-user setup; isolation verified.
**Acceptance Criteria**
- Single deployment serves test pool; scales to small user base.

### SH-27 Deployment Automation
- Optional scripts to automate deployment steps (environment setup, config, migrations).
- Tests: automation scripts functional; idempotent.
**Acceptance Criteria**
- Reduces manual steps; safe to re-run.

### SH-28 Rollback Procedures
- Document rollback steps for failed deployments: code revert, database rollback, config restore.
- Tests: rollback procedures tested; downtime minimized.
**Acceptance Criteria**
- Clear rollback plan; can recover from failed deployment quickly.

### SH-29 Security Auditing
- Checklist for security review: TLS, secrets management, file permissions, SQL injection prevention, CSRF protection.
- Tests: audit checklist; common vulnerabilities addressed.
**Acceptance Criteria**
- Pre-deployment security review documented; critical issues resolved.

### SH-30 Production Readiness Review
- Final checklist before go-live: monitoring, backups, error handling, security, documentation, support channels.
- Tests: checklist completeness.
**Acceptance Criteria**
- Confidence in production deployment; all critical items addressed.

## Ordering (Suggested)
SH-01 → SH-02 → SH-05 → SH-10 → SH-03 → SH-06 → SH-07 → SH-08 → SH-11 → SH-12 → SH-09 → SH-13 → SH-14 → SH-21 → SH-15 → SH-16 → SH-17 → SH-18 → SH-19 → SH-20 → SH-22 → SH-23 → SH-24 → SH-25 → SH-26 → SH-27 → SH-28 → SH-29 → SH-04 → SH-30

## Open Questions
- Preferred shared hosting providers for documentation (Hostinger, Bluehost, SiteGround)?
- SMTP relay recommendation: Gmail (simple), SendGrid (scalable), Mailgun (reliable)?
- Monitoring service preference: self-hosted, free tier external, paid?
- Maximum users per shared hosting instance before requiring VPS?
