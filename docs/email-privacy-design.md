# Email Privacy Service - Design Document

## Project Overview
A privacy-focused email aliasing service that allows users to create proxy email addresses that forward to their real inbox, preventing email address exposure and tracking email usage patterns.

## Business Model
- **First-party hosting**: Paid subscription (no free tier)
  - Unlimited aliases and destination addresses
  - Shared subdomain (e.g., `user-alias@mail.yourdomain.com`)
  - Option to bring your own domain (BYO domain)
  - Bandwidth limits with pay-as-you-go overages
  - Optional spam filtering add-on ($X/month)
  - 50MB email size limit
- **Self-hosted**: AGPL-3.0 licensed
  - No limits on usage
  - Requires users to supply their own domain
  - Full control over infrastructure

## Licensing

**AGPL-3.0 Open Source**
- Self-hosted deployment with full source code access
- Requires source disclosure for any hosted modifications
- Allows personal and organizational self-hosting
- Commercial hosting services must provide source code to users
- Commercial licensing available for proprietary integrations

**Dual Licensing Strategy**
- AGPL-3.0 for open source community and self-hosting
- Separate commercial license for businesses wanting proprietary use
- Contact for commercial licensing: [xxxxxx@quitspyingon.me]

## MVP Scope (Phase 1)

### Core Features
- Create email aliases that forward to real email address(es)
- Receive-only email forwarding
- User authentication via passkey and magic link (no passwords)
- Simple web dashboard to view aliases and message flow
- Alias management: create, disable/enable, delete, add notes/labels
- Multi-destination routing (one alias → multiple verified emails)
- Email verification for destination addresses
- Basic metadata tracking (from, to, timestamp, delivery status)
- Bandwidth tracking and enforcement
- Webhooks for incoming emails (power users)

### Technical Stack
- **Backend**: Python (Flask/FastAPI)
- **Database**: PostgreSQL (primary choice for ACID compliance and encryption support)
- **Frontend**: Server-side templates (Jinja2) with Tailwind CSS
- **Email**: Hybrid approach (Cloudflare/Postmark for shared hosting, custom MTA for Docker)
- **Deployment**: 
  - Shared hosting compatible (cPanel)
  - Docker containerized (Proxmox, etc.)

### Architecture Components

#### 1. Mail Transfer Agent (MTA)

**Deployment-Specific Approaches:**

**Shared Hosting (cPanel):**
- Use Cloudflare Email Routing or Postmark for incoming mail
- Webhook to Python app for processing
- App validates alias, checks bandwidth limits
- Forward via authenticated SMTP relay

**VPS/Docker:**
- Custom SMTP receiver (Python aiosmtpd or Postfix)
- Listen on port 25
- Accept mail for `*@yourdomain.com` and custom domains
- Direct processing without third-party involvement

**Common Processing:**
- Validate alias exists and is active
- Check user bandwidth limits (reject if exceeded)
- Verify email size ≤ 50MB
- Optional spam filtering (if user subscribed)
- Forward to verified destination email(s)
- Trigger webhooks if configured
- Log metadata only

#### 2. Web Application
- **Authentication Service**
  - Passkey (WebAuthn) implementation
  - Magic link via email
  - Session management (JWT or secure cookies)
  
- **Alias Management API**
  - CRUD operations for aliases
  - Toggle active/inactive status
  - Set expiration dates
  - Add notes/labels
  - Generate random alias names
  - Multi-destination routing configuration
  
- **Destination Email Management**
  - Add/remove destination emails
  - Email verification flow
  - Link destinations to aliases
  
- **Custom Domain Management**
  - Add custom domain
  - DNS verification (TXT/MX records)
  - Domain status tracking
  
- **Webhook Management**
  - Configure webhook URLs
  - HMAC signature generation
  - Test webhook delivery
  
- **Dashboard**
  - List all aliases with status
  - View message flow (metadata only)
  - Create new aliases
  - Bandwidth usage display
  - Manage account settings

#### 3. Database Schema (PostgreSQL)

```sql
-- Users table
users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,  -- Real email address
  created_at TIMESTAMP,
  last_login TIMESTAMP,
  is_active BOOLEAN DEFAULT true
)

-- Passkeys table (WebAuthn credentials)
passkeys (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  credential_id TEXT UNIQUE NOT NULL,
  public_key TEXT NOT NULL,
  counter BIGINT DEFAULT 0,
  created_at TIMESTAMP
)

-- Magic links table
magic_links (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  token VARCHAR(255) UNIQUE NOT NULL,
  expires_at TIMESTAMP,
  used BOOLEAN DEFAULT false
)

-- Aliases table
aliases (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  alias_email VARCHAR(255) UNIQUE NOT NULL,  -- The proxy email
  is_active BOOLEAN DEFAULT true,
  note TEXT,                                   -- User's note about usage
  labels TEXT[],                               -- Array of labels
  expires_at TIMESTAMP NULL,
  created_at TIMESTAMP,
  last_used_at TIMESTAMP
)

-- Destination emails (verified addresses)
destination_emails (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  email VARCHAR(255) NOT NULL,
  is_verified BOOLEAN DEFAULT false,
  verification_token VARCHAR(255),
  verified_at TIMESTAMP NULL,
  created_at TIMESTAMP,
  UNIQUE(user_id, email)
)

-- Alias routing (many-to-many)
alias_destinations (
  alias_id UUID REFERENCES aliases(id) ON DELETE CASCADE,
  destination_id UUID REFERENCES destination_emails(id) ON DELETE CASCADE,
  created_at TIMESTAMP,
  PRIMARY KEY (alias_id, destination_id)
)

-- Custom domains
custom_domains (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  domain VARCHAR(255) UNIQUE NOT NULL,
  is_verified BOOLEAN DEFAULT false,
  verification_token VARCHAR(255),
  verified_at TIMESTAMP NULL,
  created_at TIMESTAMP
)

-- Webhooks
webhooks (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  url TEXT NOT NULL,
  secret VARCHAR(255),  -- For HMAC signature
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP
)

-- Bandwidth tracking
bandwidth_usage (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  month DATE NOT NULL,  -- First day of month
  bytes_used BIGINT DEFAULT 0,
  emails_received INT DEFAULT 0,
  emails_forwarded INT DEFAULT 0,
  UNIQUE(user_id, month)
)

-- User subscriptions
subscriptions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  plan_type VARCHAR(50) NOT NULL,  -- standard, premium, etc.
  bandwidth_limit BIGINT,  -- bytes per month
  spam_filtering_enabled BOOLEAN DEFAULT false,
  status VARCHAR(50),  -- active, cancelled, suspended
  current_period_start TIMESTAMP,
  current_period_end TIMESTAMP,
  created_at TIMESTAMP
)

-- Email metadata (encrypted at rest)
email_logs (
  id UUID PRIMARY KEY,
  alias_id UUID REFERENCES aliases(id),
  from_address VARCHAR(255),
  subject_hash VARCHAR(64),  -- Hashed for privacy
  size_bytes BIGINT,
  received_at TIMESTAMP,
  forwarded_at TIMESTAMP NULL,
  status VARCHAR(50),  -- received, forwarded, failed, bounced, spam
  failure_reason TEXT NULL
)

-- Failed emails (temporary storage)
failed_emails (
  id UUID PRIMARY KEY,
  alias_id UUID REFERENCES aliases(id),
  email_content TEXT,  -- Encrypted full email
  from_address VARCHAR(255),
  received_at TIMESTAMP,
  retry_count INT DEFAULT 0,
  last_retry_at TIMESTAMP NULL,
  will_delete_at TIMESTAMP  -- Auto-delete after 7 days
)

-- Spam filtered emails (temporary storage, 30 days)
spam_quarantine (
  id UUID PRIMARY KEY,
  alias_id UUID REFERENCES aliases(id),
  email_content TEXT,  -- Encrypted full email
  from_address VARCHAR(255),
  spam_score FLOAT,
  received_at TIMESTAMP,
  will_delete_at TIMESTAMP,  -- Auto-delete after 30 days
  released BOOLEAN DEFAULT false
)
```

#### 4. Security & Privacy

**Encryption at Rest**
- Use PostgreSQL's `pgcrypto` extension for column-level encryption
- Encrypt: `email_content` in failed_emails and spam_quarantine
- Key management: Environment variables or secrets manager

**Data Minimization**
- Store only essential metadata
- Hash email subjects instead of storing plaintext
- Auto-delete failed emails after 7 days
- Auto-delete spam quarantine after 30 days
- No email content storage except temporary failures/spam

**Transport Security**
- TLS/SSL for all web traffic (HTTPS)
- STARTTLS for SMTP connections
- Validate SPF/DKIM on incoming mail

**User Privacy Rights**
- Export all user data (GDPR compliance)
- Delete account and all associated data
- View all stored information via dashboard

**Webhook Security**
- HMAC-SHA256 signatures for webhook payloads
- User-provided secret for signature verification
- Retry logic with exponential backoff

#### 5. Email Flow

```
Incoming Email Flow:
1. External sender → MTA (Cloudflare/Postmark or your SMTP server)
2. Webhook/Direct → Python app
3. Validate:
   - Alias exists and is active
   - User subscription is active
   - Bandwidth limit not exceeded
   - Email size ≤ 50MB
4. Optional: Spam filtering (if enabled)
   - If spam: quarantine for 30 days
5. Log metadata (from, timestamp, size)
6. Update bandwidth usage
7. Forward to all verified destination emails
8. Trigger webhooks (if configured)
9. Log forwarding status
10. If failed: store encrypted email, schedule retry

Retry Logic:
- Retry failed emails: 1h, 6h, 24h, 48h intervals
- After 7 days: delete permanently
- Notify user of persistent failures

Cleanup Jobs:
- Delete failed emails after 7 days
- Delete spam quarantine after 30 days
- Purge old email logs (configurable retention)
```

#### 6. Deployment Options

**Shared Hosting (cPanel)**
- Python app via Passenger or CGI
- PostgreSQL database
- Cron jobs for email retry and cleanup
- Cloudflare Email Routing or Postmark webhook receiver
- Environment config for deployment mode

**Docker (Self-hosted)**
```yaml
services:
  - web: Python app (Flask/FastAPI)
  - db: PostgreSQL with pgcrypto
  - mta: Custom SMTP server (Python aiosmtpd)
  - worker: Background tasks (Celery + Redis)
  - redis: Cache and task queue
```

**Configuration**
- Environment variables for secrets
- Config file for domain, SMTP settings, deployment mode
- Multi-tenancy support for first-party hosting

---

## Full Version (Phase 2)

### Additional Features
- **Bidirectional email**: Send from aliases with reply-to rewriting
- **Browser extension**: Create aliases on-demand from any webpage
- **Advanced analytics**:
  - Email origin tracking
  - Detect if email sold to third parties
  - Spider/Sankey diagrams for email flow visualization
  - Statistics dashboard
- **API for power users**: RESTful API with authentication
- **Reply-to rewriting**: Maintain anonymity when replying
- **Catch-all aliases**: `*@subdomain.yourdomain.com`
- **PGP encryption**: Optional end-to-end encryption
- **Email search**: Search through metadata
- **Alias templates**: Quick creation with patterns

### Technical Additions
- **Frontend**: Full React SPA with Tailwind
- **Visualization**: D3.js or Recharts for data viz
- **Browser Extension**: React + WebExtension API
- **Background Workers**: Celery for async tasks
- **Caching**: Redis for performance
- **Rate Limiting**: Prevent abuse
- **Monitoring**: Prometheus + Grafana
- **Payment Integration**: Stripe for subscriptions

---

## Next Steps

1. Set up project structure
2. Implement basic SMTP receiver (Docker version)
3. Build authentication system (magic link first, then passkey)
4. Create database models and migrations
5. Build alias management API
6. Implement email verification flow
7. Create bandwidth tracking system
8. Build webhook system
9. Create simple dashboard UI
10. Test email forwarding flow
11. Add encryption and security hardening
12. Implement Cloudflare/Postmark webhook receiver
13. Create Docker deployment
14. Document self-hosting setup
15. Add spam filtering integration
