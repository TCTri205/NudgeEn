# TICKET-33: Profile Rebuild Job

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 2
- **Assignee:** Backend Lead / Data
- **Domain:** Data Reliability
- **Priority:** P2 - Medium
- **Assumptions:**
  - `user_memories` is the source of truth.
  - Taskiq worker is functional (TICKET-05).
- **Affected areas:** `workers/app/tasks/maintenance.py`, `user_profiles` table.

## Current State / Existing System

- **Implemented:** User profile JSON projection (TICKET-26).
- **Missing:** Any way to recover if the JSON projection goes out of sync with the raw facts in the `user_memories` table.

## Context / Problem

In a distributed system, sometimes the async update from a worker to the profile projection fails or the logic changes. We need a "maintenance mode" task that can iterate over a user's entire memory history and regenerate their profile JSON from scratch to ensure consistency.

## Why This Is Needed

- **Business Impact:** Prevents "profile rot" where the AI forgets things it once knew or gets stuck with incorrect data.
- **Architectural Impact:** Provides a self-healing mechanism for our CQRS read-model.

## Scope

### In-scope

- Implement a Taskiq task `rebuild_user_profile(user_id)`.
- Logic to query all rows in `user_memories` for the user.
- Re-run the aggregation logic (ranking, filtering, summarization).
- Update the `user_profiles.profile` field with the new result.
- Implement specialized logging for track rebuild success/failure.

### Out-of-scope

- Re-running the LLM extraction from raw messages (this uses existing extracted facts).

## Dependencies / Parallelism

- **Dependencies:** TICKET-26 (Profile Projection).
- **Parallelism:** Can be done as a lower priority task at the end of Sprint 2.

## Rules / Constraints

- Must be safe to run while the user is actively chatting (idempotent write).
- Should not lock the `user_profiles` row for more than 100ms.

## What Needs To Be Built

1. `api/app/modules/memory/maintenance_service.py`: Rebuild logic.
2. `workers/app/tasks/maintenance.py`: The worker task wrapper.
3. (Optional) Admin CLI command to trigger the rebuild.

## Proposal

Calculate the new profile state in memory by aggregating all `user_memories` entries. Once the new JSON is prepared, perform a single atomic `UPDATE` on the `user_profiles` table.

## Implementation Breakdown

1. **Logic Implementation:** Write the aggregation code (topics -> latest detail).
2. **Async Task:** Wrap the logic in a Taskiq worker.
3. **Trigger:** Create a hidden API endpoint or CLI tool to trigger the rebuild.
4. **Validation:** Change a fact manually in `user_memories`, run rebuild, verify `user_profiles` reflects the manual change.

## Acceptance Criteria

- [ ] Profile JSON is 100% consistent with the `user_memories` table after the job completes.
- [ ] No data loss occurs during the rebuild.
- [ ] Rebuild for a user with 500+ facts takes < 2 seconds.

## Test Cases

### Happy Path

- Manually delete a fact from the JSON -> Run Rebuild -> Fact is restored from `user_memories`.

### Failure Path

- User has no memories -> Profile is reset to default (safe empty state).

### Regression Tests

- Verify that current session tokens or preferences (like vibe) are NOT lost unless specified.
