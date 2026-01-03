# Epic: Dashboard - Aliases & Destinations

## Context
- Primary user interface for managing aliases, destinations, and custom domains.
- All UI must follow the visual style guide: Signal Green actions, clear typography, accessible components, no dark patterns.
- Server-side templates (Jinja2) with Tailwind CSS; minimal JavaScript for progressive enhancement.
- Keyboard navigation and focus indicators required throughout.

## Tickets

### AD-01 Aliases List Page
- Display all user aliases with status, labels, last used timestamp, destination count.
- Sortable columns (created, last used, status); pagination or infinite scroll.
- Quick actions: toggle active/inactive, copy alias email, view details.
- Tests: render with sample data; sorting; pagination; keyboard navigation.
**Acceptance Criteria**
- Accessible table with clear column headers; no mystery icons without labels.
- Active/inactive status uses color + icon (not color alone).
- Empty state with helpful guidance to create first alias.

### AD-02 Search & Filter
- Search by alias email, labels, or notes (substring match).
- Filter by status (active/inactive/expired), labels, and custom domain.
- Clear all filters action; filters persist across page navigation.
- Tests: search accuracy; filter combinations; clear action.
**Acceptance Criteria**
- Results update without full page reload (optional progressive enhancement).
- No results state provides helpful suggestions.

### AD-03 Create Alias Flow
- Form with fields: alias email (manual or generate random), labels, note, expiry date (optional).
- PII warning displayed prominently before creation with acknowledge checkbox.
- Validation: enforce alias naming rules, uniqueness, reserved names blocked.
- Tests: manual entry; random generation; validation messages; PII warning shown.
**Acceptance Criteria**
- Error messages follow style guide voice and appear inline near fields.
- Generate button creates readable alias (e.g., `mint-bison-42`); retries on collision.
- Success redirects to alias detail or destination linking step.

### AD-04 Alias Detail View
- Show alias email, status, created/last used dates, labels, note, expiry, linked destinations.
- Actions: edit labels/note, toggle status, set/clear expiry, delete alias.
- Link to message flow for this alias (future phase).
- Tests: render detail; action buttons present; navigation.
**Acceptance Criteria**
- Copy alias email button with clipboard feedback.
- Linked destinations shown with verification status; link to manage destinations.

### AD-05 Edit Alias
- Update labels, note, and expiry date; cannot change alias email itself.
- Inline editing or modal with clear save/cancel actions.
- Tests: update fields; validation; persistence.
**Acceptance Criteria**
- Changes saved immediately or with clear "Save" button; feedback on success/error.

### AD-06 Delete Alias
- Confirmation step with clear warning: "This will stop forwarding. Past messages are unaffected."
- Requires re-typing alias or confirmation button.
- Tests: confirmation required; deletion cascades to routing links; audit logged.
**Acceptance Criteria**
- No accidental deletion; confirmation copy aligned with style guide (direct, honest).

### AD-07 Toggle Alias Status
- One-click enable/disable without confirmation (low-risk action).
- Visual feedback (status badge updates immediately).
- Tests: toggle persists; status reflected in list and detail views.
**Acceptance Criteria**
- Color + text/icon for status; accessible labels.

### AD-08 Destinations List
- Display all user destination emails with verification status, aliases using each.
- Actions: add destination, resend verification, remove destination.
- Tests: render list; verification badges; actions functional.
**Acceptance Criteria**
- Unverified destinations shown with clear "Verify" call-to-action and resend option.
- Removing a destination warns if it's linked to active aliases.

### AD-09 Add Destination Flow
- Form: email address input with validation.
- On submit, sends verification email (Porter) and shows pending state.
- Tests: validation; verification email sent; pending state shown.
**Acceptance Criteria**
- Porter verification email sent immediately; link expires per config (24h default).
- User sees "Check your inbox" message with option to resend.

### AD-10 Resend Verification
- Button to resend verification email; rate-limited per destination.
- Invalidates prior token; shows feedback.
- Tests: new token sent; rate limit enforced; feedback shown.
**Acceptance Criteria**
- Rate limit message is helpful, not punitive ("Try again in 2 minutes").

### AD-11 Remove Destination
- Confirmation if linked to active aliases; lists affected aliases.
- Cascade: removes from all alias routing configs.
- Tests: confirmation required; removal cascades; audit logged.
**Acceptance Criteria**
- Clear warning copy; allows user to cancel and unlink first if preferred.

### AD-12 Link Destinations to Alias
- From alias detail, show "Manage Destinations" action.
- UI shows all verified destinations with checkboxes; save links selected.
- Tests: selection persists; only verified can be linked; feedback on save.
**Acceptance Criteria**
- Cannot link unverified destinations; helpful message explains verification first.
- Multi-select interface with clear labels.

### AD-13 Custom Domains List
- Display user's custom domains with verification status, last checked timestamp.
- Actions: add domain, recheck verification, view DNS instructions, remove domain.
- Tests: render list; statuses; actions.
**Acceptance Criteria**
- Pending/verified/failed states clear; color + text (not color alone).

### AD-14 Add Custom Domain Flow
- Form: domain name input (validates format).
- On submit, generates verification TXT and MX records; shows DNS instructions.
- Tests: validation; instructions generated; pending state set.
**Acceptance Criteria**
- Instructions copyable and clear; includes expected propagation time (15m–48h).
- Links to help doc for common DNS providers.

### AD-15 DNS Instructions & Verification
- Page shows required records with copy buttons; recheck button triggers verification.
- Verification checks TXT and MX; updates status; shows last check time.
- Tests: recheck triggers DNS query; status updates; timestamps accurate.
**Acceptance Criteria**
- Recheck button rate-limited; clear feedback (checking... → success/failed).
- Failure messages explain what's missing or incorrect.

### AD-16 Remove Custom Domain
- Confirmation step; warns if aliases exist on this domain.
- Cascade: optionally disable aliases or prevent removal if active aliases present.
- Tests: confirmation; cascade behavior; audit logged.
**Acceptance Criteria**
- Clear warning; option to view and disable aliases first if preferred.

### AD-17 Navigation & Layout
- Sidebar or tabs: Aliases, Destinations, Domains, Settings, Bandwidth (other epic).
- Breadcrumbs for detail/edit flows; back button or link.
- Tests: navigation functional; active page highlighted.
**Acceptance Criteria**
- Consistent layout per style guide; max-width container, gutters, spacing scale.

### AD-18 Responsive Design
- Mobile/tablet breakpoints; stacked layouts for small screens.
- Touch targets ≥44px; no tiny buttons or links.
- Tests: render at mobile/tablet/desktop widths; touch targets meet spec.
**Acceptance Criteria**
- Functional on mobile without horizontal scroll; table alternatives (cards) on small screens.

### AD-19 Accessibility
- Keyboard navigation: tab order logical, focus indicators visible.
- Screen reader labels for icons and actions; ARIA landmarks.
- Color contrast meets WCAG AA (4.5:1 minimum).
- Tests: keyboard-only navigation; screen reader testing; contrast checks.
**Acceptance Criteria**
- All interactive elements reachable via keyboard; no focus traps.

### AD-20 Error States & Loading
- Show loading spinners or skeletons during async actions.
- Error messages inline and at top of page when relevant; retry actions when applicable.
- Tests: loading states; error display; retry buttons functional.
**Acceptance Criteria**
- Errors are helpful and actionable per style guide ("Check your connection" not "Error 500").

### AD-21 Empty States
- Aliases: "Create your first alias to start hiding your email."
- Destinations: "Add a destination email to receive forwarded messages."
- Domains: "Add a custom domain to use your own branding."
- Tests: empty states render; call-to-action buttons functional.
**Acceptance Criteria**
- Copy aligned with style guide; encouraging but not sales-y.

### AD-22 Docs & Help Links
- Contextual help links: "How do aliases work?" "Verifying your domain".
- Link to main documentation; tooltips for complex fields.
- Tests: links functional; tooltips accessible.
**Acceptance Criteria**
- Help content clear and concise; no jargon.

## Ordering (Suggested)
AD-17 → AD-01 → AD-02 → AD-03 → AD-04 → AD-05 → AD-06 → AD-07 → AD-08 → AD-09 → AD-10 → AD-11 → AD-12 → AD-13 → AD-14 → AD-15 → AD-16 → AD-18 → AD-19 → AD-20 → AD-21 → AD-22

## UX Decisions (Confirmed)
- Pagination for aliases list (not infinite scroll).
- Inline editing for quick edits (labels/notes/expiry).
- Slide-out panel for alias detail view (not separate page).
