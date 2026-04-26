# TICKET-22: "Wipe My Memory" Endpoint

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 1
- **Assignee:** Backend Lead
- **Domain:** Data Privacy
- **Priority:** P2 - Medium
- **Assumptions:**
  - Messaging and Memory tables exist (TICKET-16 and EPIC-03).
  - User is authenticated.
- **Affected areas:** `api/app/modules/persona/`, `api/app/modules/memory/`, PostgreSQL database.

## Current State / Existing System

- **Implemented:** Principles of user privacy and data ownership documented in PRD.
- **Missing:** Any technical mechanism for a user to delete their extracted memories or reset their persona context.

## Context / Problem

To comply with GDPR and privacy best practices, users must have control over the data the AI "knows" about them. A "Wipe My Memory" feature allows users to clear their personalized AI state without necessarily deleting their entire account.

## Why This Is Needed

- **Business Impact:** Ensures legal compliance and user agency over their AI interactions.
- **Architectural Impact:** Requires a clean, cross-module deletion strategy to ensure consistent state reset.

## Scope

### In-scope

- Implement `POST /api/user/wipe-memory` endpoint.
- Logic to delete all rows in `user_memories` belonging to the current user.
- Logic to reset the `extracted_memories` and `summary` fields in the `user_profiles` table.
- Implement soft-deletion or anonymization of the user's `messages` and `conversations`.
- Return a confirmation of successful deletion.

### Out-of-scope

- Total account deletion (addressed in a different ticket).
- Deletion of logs or audit trails.

## Dependencies / Parallelism

- **Dependencies:** TICKET-01 (FastAPI Skeleton), TICKET-03 (PostgreSQL Setup).
- **Parallelism:** Can be done at the end of Sprint 1.

## Rules / Constraints

- Deletion must be permanent and irreversible for memory entries.
- Must use a transaction to ensure all related data is cleared or none is.
- Sensitive identifiers (user IDs) must be verified against the session before deletion.

## What Needs To Be Built

1. `api/app/modules/user/router.py`: Add the `/wipe-memory` route.
2. `api/app/modules/memory/service.py`: Method to clear user memories.
3. `api/app/modules/persona/service.py`: Method to reset persona profile.
4. (Optional) Frontend button in the Settings page to trigger the endpoint.

## Proposal

Implement a service-level transaction that coordinates the deletion across the `memory` and `persona` modules. For messages, set a `deleted_at` timestamp or replace message content with "[DELETED]".

## Implementation Breakdown

1. **Service Integration:** Create the cross-module deletion service.
2. **Endpoint:** Expose the logic via a protected FastAPI route.
3. **UI:** Add a "Danger Zone" section to the settings with a "Wipe My Memory" button.
4. **Validation:** Verify that after a wipe, a new chat message doesn't reference any previous user details.

## Acceptance Criteria

- [ ] `user_memories` table has 0 rows for the user after the wipe.
- [ ] `user_profiles` record for the user is reset to default state.
- [ ] The API returns 204 No Content or 200 OK with confirmation.
- [ ] AI no longer exhibits knowledge of previously shared secrets/facts in subsequent messages.

## Test Cases

### Happy Path

- Share fact -> Fact appears in DB -> Click Wipe -> Fact removed from DB.

### Failure Path

- Unauthenticated request to purge -> 401 Unauthorized.
- Database timeout during purge -> Transaction rolls back, data remains intact.

### Regression Tests

- Ensure wiping User A doesn't accidentally clear User B's memory.
