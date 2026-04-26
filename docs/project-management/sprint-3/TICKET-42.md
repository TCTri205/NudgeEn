# TICKET-42: Progress Data Export (CSV)

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 3
- **Assignee:** Backend Lead
- **Domain:** Data Portability
- **Priority:** P3 - Low
- **Assumptions:**
  - User wants an offline study list.
- **Affected areas:** `api/app/modules/user/export_router.py`, Settings.

## Current State / Existing System

- **Implemented:** Corrections and vocabulary tracking (TICKET-36, TICKET-40).
- **Missing:** Any way for a user to "take their learning with them" or review outside the app.

## Context / Problem

Users value ownership of their data. Allowing them to export their corrections and new vocabulary as a CSV/JSON file lets them import it into flashcard apps (like Anki) or simply study offline.

## Why This Is Needed

- **Business Impact:** Increases user trust and loyalty.
- **Architectural Impact:** Implementation of a "File Streaming" or "Blob Generation" response.

## Scope

### In-scope

- Implement `GET /api/user/export` endpoint.
- Generate a CSV containing:
  - Date.
  - Original Text.
  - Improved Text.
  - Grammar Rule.
  - Explanation.
- Generate a JSON alternative for developer-users.
- Add "Export My Learning Data" button in the Profile/Settings page.

### Out-of-scope

- PDF generation (future enhancement).

## Dependencies / Parallelism

- **Dependencies:** TICKET-36 (Persistence), TICKET-40 (Vocab).
- **Parallelism:** Low priority; do at the end of Sprint 3.

## Rules / Constraints

- Export must be authenticated and authorized (cannot export others' data).
- Handle large exports (1000+ rows) without timing out.

## What Needs To Be Built

1. `api/app/modules/user/export_service.py`: CSV generation logic.
2. `web/components/settings/export-panel.tsx`.

## Proposal

Use Python's `csv` module to build the string in memory and return it as a `StreamingResponse` from FastAPI with `Content-Disposition: attachment`.

## Implementation Breakdown

1. **Service:** Function to gather and format the data.
2. **Route:** FastAPI endpoint with proper headers.
3. **UI:** Simple button with an "Downloading..." state.
4. **Validation:** Download a file and verify it opens correctly in Excel/Google Sheets.

## Acceptance Criteria

- [ ] Export contains all relevant pedagogical data for the user.
- [ ] CSV format is standard (commas, quoted strings).
- [ ] Export is only accessible to the account owner.

## Test Cases

### Happy Path

- Click Export -> File downloads -> Contains correct correction history.

### Failure Path

- Empty history -> Download succeeds with just the header row.

### Regression Tests

- Verify PII scrubbing still applies if sensitive data was in messages (TICKET-21).
