# TICKET-41: User Feedback Loop (Helpful/Not Helpful)

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 3
- **Assignee:** Fullstack Developer
- **Domain:** UX / Analytics
- **Priority:** P3 - Low
- **Assumptions:**
  - Correction Modal UI is ready (TICKET-35).
- **Affected areas:** `web/components/chat/modals/`, `api/app/modules/chat/feedback.py`.

## Current State / Existing System

- **Implemented:** Correction modal (TICKET-35).
- **Missing:** Any way for the user to tell us if the AI's grammar correction was actually correct or helpful.

## Context / Problem

AI makes mistakes. If we provide a wrong correction, we need to know so we can improve our prompts and identify model hallucinations. Simple Binary Feedback (Up/Down) is the first step in creating a self-improving pedagogical loop.

## Why This Is Needed

- **Business Impact:** Helps detect and reduce "hallucinated grammar rules" that could damage project credibility.
- **Architectural Impact:** Adds a "User Feedback" capture point.

## Scope

### In-scope

- Add "✓ Helpful" and "✗ Not Helpful" buttons to the `CorrectionModal`.
- Implement `POST /api/messages/{id}/correction/feedback` endpoint.
- Store results in `message_corrections.marked_helpful`.
- Logic to hide the buttons and show a "Thank you" state after voting.
- Optional: Small "Report error" text for non-helpful votes.

### Out-of-scope

- Detailed comment system for feedback.

## Dependencies / Parallelism

- **Dependencies:** TICKET-35 (Modal UI), TICKET-36 (Persistence).
- **Parallelism:** Can be done after the modal UI is functional.

## Rules / Constraints

- Feedback must be recorded instantly (optimistic UI update).

## What Needs To Be Built

1. Integration in `web/components/chat/modals/correction-modal.tsx`.
2. API route and repository method for feedback update.

## Proposal

Use a standard "thumbs up/down" pattern. When "Not Helpful" is pressed, optionally trigger a "Why?" dropdown with high-level categories (Wrong correction, Hard to understand, Repetitive).

## Implementation Breakdown

1. **Frontend UI:** Add the buttons and the `onClick` handler.
2. **API Logic:** Create the simple update route.
3. **Telemetry:** Log non-helpful corrections to a "Review Queue" for developers.
4. **Validation:** Click "Helpful" and verify the DB column changes to `TRUE`.

## Acceptance Criteria

- [ ] Users can successfully submit a helpful/unhelpful rating.
- [ ] The rating is persisted in the database.
- [ ] Subsequent opens of the same modal show the previously selected rating.

## Test Cases

### Happy Path

- Open modal -> Click Helpful -> Buttons replaced by "Thanks!".

### Failure Path

- API call fails -> Show a subtle "Try again" toast or error.

### Regression Tests

- Ensure User A cannot vote on User B's correction.
