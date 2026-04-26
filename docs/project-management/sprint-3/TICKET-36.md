# TICKET-36: Correction Persistence & Severity Classification

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 3
- **Assignee:** Backend Lead / AI
- **Domain:** Data Layer / AI
- **Priority:** P1 - High
- **Assumptions:**
  - Database schema for `message_corrections` is finalized (TICKET-04 update).
- **Affected areas:** `api/app/modules/chat/repository.py`, AI Post-processing.

## Current State / Existing System

- **Implemented:** Message persistence (TICKET-16).
- **Missing:** Any way to store the educational metadata (corrections) separately from the chat reply.

## Context / Problem

We need to track corrections not just for UI display, but for long-term analytics. Are users improving? Which grammar rules are they struggling with? This requires a dedicated, relational table that links corrections to messages with severity and categorization.

## Why This Is Needed

- **Business Impact:** Enables the "Weekly Progress Card" and "Learning Dashboard."
- **Architectural Impact:** Standardizes the relational link between conversational and pedagogical data.

## Scope

### In-scope

- Implement `message_corrections` table:
  - `message_id` (FK).
  - `original_text`, `improved_text`, `explanation`.
  - `grammar_rule` (e.g., 'tense', 'article').
  - `severity` (minor, moderate, major).
  - `viewed` (boolean).
- Logic to derive `severity` if the LLM doesn't provide it (e.g., count character diff).
- API endpoint to fetch corrections for a specific message: `GET /messages/{id}/correction`.

### Out-of-scope

- Automated grammar rule mapping (simple string categories for now).

## Dependencies / Parallelism

- **Dependencies:** TICKET-16 (Message Persistence).
- **Parallelism:** Can be done while the Frontend UI is in progress.

## Rules / Constraints

- One message can have at most ONE primary correction object for MVP.
- All writes must be async.

## What Needs To Be Built

1. `api/app/modules/chat/models.py`: Update with `MessageCorrection` model.
2. `api/app/modules/chat/repository.py`: CRUD for corrections.
3. Refactor of the "Save Message" service to include correction persistence.

## Proposal

When the `StructuredOutputParser` (TICKET-32) finishes, it will return a `Correction` object. The service should save the message first, then use the resulting `message_id` to save the correction in a separate table within the same transaction.

## Implementation Breakdown

1. **Schema:** Add the `message_corrections` table via Alembic.
2. **Logic:** Implement the repository methods.
3. **Integration:** Update the chat completion logic to trigger the save.
4. **Validation:** Manually query the DB to ensure corrections are linked correctly.

## Acceptance Criteria

- [ ] Each correction is saved with its linked message ID.
- [ ] `grammar_rule` and `severity` are correctly populated.
- [ ] The `viewed` flag defaults to `false`.
- [ ] Retrieving a message with an associated correction is fast (< 10ms).

## Test Cases

### Happy Path

- Full turn -> DB has 1 Message, 1 Correction linked to it.

### Failure Path

- Message save succeeds but Correction fails -> Use transaction rollback to ensure data integrity.

### Regression Tests

- Ensure deleting a message deletes its associated correction (Cascade).
