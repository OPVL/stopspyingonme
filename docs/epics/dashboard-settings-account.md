# Epic: Dashboard - Settings & Account

## Context
- Central hub for account management, webhook configuration, notifications, and data privacy actions.
- Align with visual style guide; accessible; server-side templates.
- Includes passkey management, export/delete flows, and notification preferences.

## Tickets

### SA-01 Account Overview Page
- Display user email, plan tier, account creation date, last login.
- Link to passkey management, export, and delete flows.
- Tests: render user data; links functional.
**Acceptance Criteria**
- Clear summary without unnecessary details; direct language per style guide.

### SA-02 Passkey Management
- List registered passkeys with creation date and last used.
- Actions: add passkey, remove passkey.
- Tests: list renders; add/remove functional; WebAuthn flows work.
**Acceptance Criteria**
- Clear labels for each passkey (e.g., "MacBook Pro", "iPhone"); removal requires confirmation.
- Add passkey flow guides user through WebAuthn enrollment.

### SA-03 Add Passkey Flow
- Button triggers WebAuthn registration; guides user with clear prompts.
- On success, displays new passkey in list.
- Tests: enrollment flow; success feedback; error handling.
**Acceptance Criteria**
- Browser compatibility detected; fallback message if unsupported.
- Success message confirms passkey saved.

### SA-04 Remove Passkey
- Confirmation prompt with passkey label; requires re-auth or second passkey (if multiple exist).
- Prevents removing last authentication method.
- Tests: confirmation required; removal persists; audit logged.
**Acceptance Criteria**
- Warning if attempting to remove last passkey; requires adding another method first.

### SA-05 Webhook Configuration List
- Display user-configured webhooks: URL, status (active/paused), event filters, last delivery status.
- Actions: add, edit, disable/enable, delete, test.
- Tests: list renders; actions functional; status badges.
**Acceptance Criteria**
- Status indicators use color + text; last delivery shows success/fail with timestamp.

### SA-06 Add/Edit Webhook
- Form: URL, secret, event filters (checkboxes for received/forwarded/failed/spam/usage/etc.).
- Validation: URL format, secret requirements.
- Tests: validation; save persists; test delivery button functional.
**Acceptance Criteria**
- Secret displayed once on creation; masked thereafter; regenerate option.
- Event filter defaults to all events; granular selection available.

### SA-07 Test Webhook
- Button sends sample event to configured URL; displays response inline.
- Shows status code, response time, any errors.
- Tests: test delivery; response displayed; error handling.
**Acceptance Criteria**
- Sample payload documented; clear success/fail feedback.
- Timeout handling with helpful message.

### SA-08 Webhook Delivery Logs
- View recent webhook deliveries: event, timestamp, status code, attempts, error details.
- Filter by status (success/failed/retrying); pagination.
- Tests: list renders; filter functional; details accessible.
**Acceptance Criteria**
- Logs show enough detail to debug without exposing sensitive data.
- Failed deliveries show next retry time.

### SA-09 Delete Webhook
- Confirmation prompt; explains that past logs are retained per retention policy.
- Tests: confirmation; deletion persists; audit logged.
**Acceptance Criteria**
- Clear warning; no accidental deletion.

### SA-10 Notification Preferences
- Toggles for email notifications: usage thresholds, Overflow Hold, spam quarantine, failed deliveries, domain verification.
- Select which persona sends each type (or dashboard-only).
- Tests: toggles persist; updates respected by notification system.
**Acceptance Criteria**
- Each notification type has clear description of what triggers it.
- Dashboard-only option disables emails but shows events in dashboard.

### SA-11 Usage Warning Persona Config (Future)
- Select notification persona for usage warnings (currently enabled for MVP).
- Placeholder for future custom sender names.
- Tests: selection persists.
**Acceptance Criteria**
- MVP uses default persona; config respects override if set.

### SA-12 Account Export Request
- Button to request full data export; explains what's included (aliases, destinations, domains, webhooks, usage logs, subscriptions).
- Queues job; shows status; download link when ready.
- Tests: request queued; status updates; download functional; access control enforced.
**Acceptance Criteria**
- Export format documented (JSON + CSV); expiry clearly stated (7 days default).
- Progress indicator if export takes time.

### SA-13 Account Export Download
- Authenticated download link; enforces expiry.
- Export includes README explaining contents.
- Tests: download authorized; expiry enforced; format correct.
**Acceptance Criteria**
- Export is complete and accurate; includes all user data per spec.

### SA-14 Account Delete Flow
- Clear warning: "This will delete all aliases, destinations, domains, webhooks, and logs. Cannot be undone."
- Requires re-authentication (magic link or passkey assertion).
- Confirmation step: type account email to confirm.
- Tests: re-auth required; confirmation enforced; deletion cascades; audit logged.
**Acceptance Criteria**
- No accidental deletion; multiple confirmation steps.
- Soft-delete with purge job scheduled; immediate access revocation.

### SA-15 Account Delete Confirmation Page
- Final confirmation with checkbox: "I understand this action is permanent."
- Button labeled "Delete Account" (danger style).
- Tests: checkbox required; deletion triggers; feedback shown.
**Acceptance Criteria**
- Copy is direct and honest per style guide; no dark patterns.

### SA-16 Post-Delete Feedback
- Thank-you page with optional feedback form (why are you leaving?).
- No login required; anonymous submission.
- Tests: page renders; form submission works; responses stored anonymously.
**Acceptance Criteria**
- Feedback optional; respectful tone; no guilt-tripping.

### SA-17 Security Settings
- Display last login timestamp, active sessions (future), recent audit events.
- Option to view/download audit log.
- Tests: data renders; audit log accessible.
**Acceptance Criteria**
- Audit log shows key events: login, passkey changes, exports, deletes, limit changes.

### SA-18 Session Management (Future)
- List active sessions with device/location info.
- Revoke session action.
- Tests: list renders; revoke functional.
**Acceptance Criteria**
- Current session clearly marked; cannot revoke current session without re-auth.

### SA-19 Privacy Settings
- Toggle for metadata retention period (30/60/90 days or custom).
- Explain what's retained and why.
- Tests: toggle persists; affects retention jobs.
**Acceptance Criteria**
- Clear explanation of privacy trade-offs; defaults safe for most users.

### SA-20 Billing & Plan Display (No Payment MVP)
- Show current plan tier, limits, renewal date (placeholder for future).
- Link to plan comparison docs; note that payment integration coming soon.
- Tests: plan info renders; links functional.
**Acceptance Criteria**
- No fake "upgrade" buttons; honest about MVP status.

### SA-21 Responsive Design
- Forms and lists adapt to mobile/tablet; touch-friendly.
- Confirmation flows clear on small screens.
- Tests: render at breakpoints; usability on mobile.
**Acceptance Criteria**
- No horizontal scroll; touch targets ≥44px.

### SA-22 Accessibility
- Keyboard navigation for all forms and actions; focus indicators.
- Screen reader labels for toggles, buttons, and form fields.
- WCAG AA contrast.
- Tests: keyboard-only navigation; screen reader testing; contrast checks.
**Acceptance Criteria**
- All actions accessible via keyboard; form validation announced to screen readers.

### SA-23 Empty States
- Webhooks: "Add a webhook to receive real-time notifications."
- Passkeys: "Add a passkey for passwordless login."
- Tests: empty states render; CTAs functional.
**Acceptance Criteria**
- Copy encouraging and aligned with style guide.

### SA-24 Loading & Error States
- Loading indicators for async actions (export request, delete, test webhook).
- Error messages inline and actionable.
- Tests: loading states; error display; retry functional.
**Acceptance Criteria**
- Errors are specific and helpful per style guide.

### SA-25 Docs & Help
- Contextual help: "What's a webhook?" "Understanding account export" "Passkey security".
- Link to privacy policy and data handling docs.
- Tests: help links functional; content clear.
**Acceptance Criteria**
- Help content concise and jargon-free.

## Ordering (Suggested)
SA-01 → SA-02 → SA-03 → SA-04 → SA-17 → SA-05 → SA-06 → SA-07 → SA-08 → SA-09 → SA-10 → SA-11 → SA-19 → SA-20 → SA-12 → SA-13 → SA-14 → SA-15 → SA-16 → SA-21 → SA-22 → SA-23 → SA-24 → SA-18 → SA-25

## Open Questions
- Default metadata retention period (90 days suggested)?
- Should webhook secret be regenerate-able without creating new webhook?
- Account delete: immediate hard delete or soft-delete with grace period (e.g., 7 days)?
