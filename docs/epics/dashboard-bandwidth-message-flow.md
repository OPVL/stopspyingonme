# Epic: Dashboard - Bandwidth & Message Flow

## Context
- Display monthly usage metrics, message activity logs (metadata only), and events.
- Privacy-first: no email content shown; only metadata (from, to, timestamps, sizes, statuses).
- Align with visual style guide; accessible components; server-side templates with progressive enhancement.
- Integrate with Overflow Hold, spam quarantine, and header viewer.

## Tickets

### BM-01 Usage Overview Widget
- Display current month usage: bytes and emails (received/forwarded).
- Progress bars with thresholds (60%/70%/80% sliding + global 80%) color-coded.
- Shows plan limits and percentage used.
- Tests: render with sample data; color coding; responsive.
**Acceptance Criteria**
- Visual indicators use color + text/icons (not color alone).
- Over-limit state clearly marked; links to Overflow Hold view if applicable.

### BM-02 Usage History Chart
- Simple bar/line chart showing daily or weekly usage over current billing cycle.
- Toggle between bytes and email counts.
- Tests: chart renders; toggle functional; data accurate.
**Acceptance Criteria**
- Optional progressive enhancement (chart degrades to table if JS disabled).
- Chart uses accessible labels and patterns.

### BM-03 Message Activity Log (List)
- Displays recent message metadata: alias, from address, timestamp, size, status (received/forwarded/failed/spam/held/rejected).
- Pagination (default 50 per page).
- Quick filters: status, alias, date range.
- Tests: render list; pagination; filters; status badges.
**Acceptance Criteria**
- No email content or subjects shown; subject hashes only stored, not displayed.
- Status badges use consistent colors and icons per style guide.

### BM-04 Message Detail (Slide-out Panel)
- Click message to open panel showing: alias, from, destinations (if forwarded), timestamps, size, status, reason codes.
- Link to header viewer if available.
- Tests: panel opens; data rendered; close action functional.
**Acceptance Criteria**
- Panel accessible via keyboard; Esc key closes.
- Clear explanation of status and reason codes in plain language.

### BM-05 Header Viewer
- Separate page or modal showing encrypted header snapshot.
- Display parsed headers with badges for SPF/DKIM/DMARC results.
- Copy raw headers button.
- Tests: render headers; result badges; copy functional; access control enforced.
**Acceptance Criteria**
- Only message owner can view; headers formatted for readability.
- Validation results explained with links to help docs.

### BM-06 Overflow Hold View
- List messages currently in Overflow Hold with days remaining until purge.
- Actions: release (forward now), delete.
- Tests: list renders; actions functional; confirmation for bulk actions.
**Acceptance Criteria**
- Clear explanation that these are non-spam, over-limit messages.
- Days remaining prominently shown; warning as purge approaches.

### BM-07 Release from Overflow Hold
- Select message(s) and release; forwards to configured destinations immediately.
- Deducts from current month usage (or flags as manual release).
- Tests: release triggers forwarding; status updates; notification sent.
**Acceptance Criteria**
- Confirmation prompt with usage impact notice.
- Success feedback shows which destinations received message.

### BM-08 Spam Quarantine View
- List messages flagged as spam with spam score and days remaining (30d).
- Actions: release (mark not spam), delete.
- Tests: list renders; actions functional; spam scores shown.
**Acceptance Criteria**
- Distinguishes spam quarantine from Overflow Hold with clear copy.
- Release action forwards and optionally trains filter (future).

### BM-09 Failed Messages View
- List messages that failed forwarding with retry schedule and error reason.
- Manual retry action; view full error details.
- Tests: list renders; retry triggers; error details accessible.
**Acceptance Criteria**
- Error reasons helpful and actionable ("SMTP auth failed — check relay settings").
- Shows next scheduled retry time.

### BM-10 Search & Filter
- Search by alias, from address (partial match).
- Filter by status, date range, size range.
- Combined filters persist; clear all action.
- Tests: search accuracy; filter combinations; persistence.
**Acceptance Criteria**
- Fast searches on indexed fields; results update without full page reload (optional).

### BM-11 Events & Notifications List
- Display recent events: thresholds crossed, enforcement actions, verifications, domain checks.
- Click for details; mark as read/dismissed.
- Tests: list renders; details accessible; dismiss functional.
**Acceptance Criteria**
- Events categorized by type with icons and colors.
- Dismissal persists; unread count badge in navigation.

### BM-12 Export Message Logs
- Button to request CSV export of message metadata for date range.
- Queues job; notifies when ready; download link with expiry.
- Tests: export request; CSV format correct; download enforced access control.
**Acceptance Criteria**
- CSV includes metadata only (no content); format documented.
- Export respects user's data retention settings.

### BM-13 Responsive Design
- Mobile/tablet layouts for lists and charts; touch-friendly targets.
- Slide-out panels and modals adapt to screen size.
- Tests: render at breakpoints; touch targets ≥44px.
**Acceptance Criteria**
- Charts and tables stack/simplify on mobile without horizontal scroll.

### BM-14 Accessibility
- Keyboard navigation for all interactive elements; focus indicators.
- Screen reader labels for charts, badges, and status indicators.
- WCAG AA contrast for all text and UI elements.
- Tests: keyboard-only navigation; screen reader testing; contrast checks.
**Acceptance Criteria**
- All actions accessible via keyboard; no focus traps.

### BM-15 Empty States
- Usage: "No activity yet — create an alias to get started."
- Message log: "No messages received this month."
- Overflow Hold: "No messages on hold."
- Tests: empty states render; call-to-action links functional.
**Acceptance Criteria**
- Copy encouraging and aligned with style guide voice.

### BM-16 Loading & Error States
- Skeleton loaders for charts and lists; spinners for actions.
- Error messages inline and actionable; retry buttons when applicable.
- Tests: loading states; error display; retry functional.
**Acceptance Criteria**
- Errors are specific and helpful per style guide.

### BM-17 Real-time Updates (Optional)
- Poll for new messages/events; update counts without refresh (progressive enhancement).
- WebSocket or SSE for live updates (future).
- Tests: polling functional; updates reflected.
**Acceptance Criteria**
- Optional; degrades gracefully; manual refresh always available.

### BM-18 Config & Thresholds Display
- Show current plan tier and limits at top of bandwidth page.
- Link to manage plan (future payments integration).
- Tests: plan info renders; links functional.
**Acceptance Criteria**
- Clear display of limits and included features.

### BM-19 Docs & Help
- Contextual help: "What do status codes mean?" "Understanding SPF/DKIM/DMARC".
- Link to header viewer guide and overflow hold explanation.
- Tests: help links functional; content clear.
**Acceptance Criteria**
- Help content concise and jargon-free per style guide.

## Ordering (Suggested)
BM-01 → BM-02 → BM-18 → BM-03 → BM-04 → BM-05 → BM-10 → BM-06 → BM-07 → BM-08 → BM-09 → BM-11 → BM-12 → BM-13 → BM-14 → BM-15 → BM-16 → BM-17 → BM-19

## Open Questions
- Message log default sort: newest first or oldest first?
- Retention period for message metadata display (show last 90 days by default)?
- Real-time polling interval (30s, 60s)?
