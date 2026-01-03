# Development Documentation Flow

## Workflow
1. **Start Work**: Read `docs/current-state.md` and `last-changes.md`
2. **Clear Log**: Empty `last-changes.md` contents
3. **Work & Log**: Append major decisions/milestones to `last-changes.md` as you work
4. **Finalize**: Add brief summary to `last-changes.md`
5. **Update State**: Update `docs/current-state.md` to reflect new application state

## last-changes.md Format
```markdown
# [Epic/Ticket Name] - [Date]

## Major Changes
- Key decision/milestone 1
- Key decision/milestone 2

## Technical Details
- Implementation notes
- Architecture changes
- Bug fixes

## Summary
Brief overview of what was accomplished and current state.
```

## current-state.md Updates
- Reflect actual implemented features
- Update architecture status
- Note any breaking changes
- Keep concise and factual
- **Critical Decisions**: Only very important architectural/strategic decisions go in "Critical Decisions Made" section

## Rules
- Always read both files before starting work
- Log significant decisions as you work, not just at the end
- Be information-dense, avoid verbose descriptions
- Update current-state.md to match reality after changes
- **Important callouts for current-state.md must be very important decisions that affect the entire project**
