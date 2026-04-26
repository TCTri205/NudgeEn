# TICKET-26: User Profile JSON Projection

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 2
- **Assignee:** Data Engineer / Backend
- **Domain:** Data Layer
- **Priority:** P1 - High
- **Assumptions:**
  - PostgreSQL supports `JSONB` for optimized queries.
  - Profile updates happen asynchronously (TICKET-25).
- **Affected areas:** `api/app/models/user_profile.py`, Profile Service.

## Current State / Existing System

- **Implemented:** `users` table and basic identity data (TICKET-09).
- **Missing:** A consolidated view of "what the AI knows about the user" for easy prompt injection.

## Context / Problem

Fetching dozens of individual "memory facts" (hobbies, goals, name) from a separate table every time the AI needs to generate a reply is inefficient. We need a "flattened" JSON projection of the user's current profile that can be loaded in a single query.

## Why This Is Needed

- **Business Impact:** Faster response times and better context consistency.
- **Architectural Impact:** Implements a CQRS-like pattern where `user_memories` is the write-only event log and `user_profiles.profile` is the optimized read-model.

## Scope

### In-scope

- Create/Update the `user_profiles` table with a `profile` JSONB column.
- Define the JSON schema:
  - `name`, `english_level`, `vibe_preference`.
  - `extracted_memories` (list of top 10 relevant facts).
  - `stats` (message count, days active).
- Implement a service to rebuild the projection from the `user_memories` table.
- Implement a service to update specific fields (e.g., changing vibe in settings).

### Out-of-scope

- History tracking of the JSON field (auditing).

## Dependencies / Parallelism

- **Dependencies:** TICKET-03 (PostgreSQL Setup).
- **Parallelism:** Can be done while Memory Extraction (TICKET-25) is being built.

## Rules / Constraints

- JSONB must be used to allow for future indexing (GIN/BTREE).
- Updates to the core user identity must automatically trigger a projection refresh.

## What Needs To Be Built

1. SQLAlchemy model for `UserProfile`.
2. `api/app/modules/persona/profile_service.py`: Logic to manage the JSON projection.
3. Migration script to create/alter the table.

## Proposal

Every time a new fact is extracted (TICKET-25), the worker should also update the corresponding `user_profiles` record, ensuring the "compact memory list" remains up-to-date and prioritized.

## Implementation Breakdown

1. **Schema Design:** Define the Pydantic schema for the profile JSON.
2. **CRUD Operations:** Implement get/update methods.
3. **Rebuild Logic:** Write a script to regenerate the JSON from all historical memories for a user.
4. **Validation:** Manually trigger an update and check the JSON content in Postgres.

## Acceptance Criteria

- [ ] User profile can be retrieved in a single `SELECT` by `user_id`.
- [ ] JSON contains all required fields: `name`, `level`, `vibe`, `memories`.
- [ ] Performance of retrieving the profile is < 5ms.
- [ ] The profile is automatically updated when onboarding (TICKET-24) completes.

## Test Cases

### Happy Path

- Update `name` via API -> JSON projection reflects change.
- New memories added -> JSON `extracted_memories` list updates to include them.

### Failure Path

- Invalid JSON structure passed to update -> Server returns 422 Unprocessable Entity.

### Regression Tests

- Ensure that updating the JSON profile doesn't overwrite or delete existing `user_memories` raw data.
