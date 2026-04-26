# TICKET-09: Auth.js PostgreSQL Adapter

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 1
- **Assignee:** Lead Developer / DBA
- **Domain:** Data Layer / Authentication
- **Priority:** P0 - Critical
- **Assumptions:**
  - PostgreSQL connection is active (TICKET-03).
  - Database schema for Auth.js is well-defined in the official documentation.
- **Affected areas:** `web/auth.ts`, `api/alembic/`, `users`, `accounts`, `sessions` tables.

## Current State / Existing System

- **Implemented:** PostgreSQL connection strings and pool setup (Sprint 0).
- **Missing:** Database persistence for user sessions; currently using JWT storage (stateless).

## Context / Problem

For a production-grade application, we need to persist user sessions and multi-provider account data in our central PostgreSQL database. This allows for long-lived sessions, session revocation, and robust account management.

## Why This Is Needed

- **Business Impact:** Enables persistent user profiles and reliable session management across devices.
- **Architectural Impact:** Centralizes identity data in PostgreSQL, allowing the FastAPI backend to verify identity directly against the DB when needed.

## Scope

### In-scope

- Install and configure `@auth/pg-adapter`.
- Create the standard Auth.js tables in PostgreSQL: `users`, `accounts`, `sessions`, `verification_tokens`.
- Update `auth.ts` to use the `PostgresAdapter`.
- Test session creation and retrieval from the database.

### Out-of-scope

- Custom modifications to the standard Auth.js schema.
- Data migration from other identity providers.

## Dependencies / Parallelism

- **Dependencies:** TICKET-03 (PostgreSQL Setup).
- **Parallelism:** Can be done in parallel with TICKET-07 and TICKET-08.

## Rules / Constraints

- Must use the official `@auth/pg-adapter` implementation.
- All database modifications should be captured in Alembic migrations to keep the schema in sync.
- The `pg` pool used by the adapter should be configured with appropriate limits.

## What Needs To Be Built

1. Setup `@auth/pg-adapter` in the `web/` project.
2. Define the schema in `api/alembic/` (or via the adapter's provided SQL).
3. Update `auth.ts` to export the configured adapter.
4. Verify table population after a successful login.

## Proposal

Connect Auth.js directly to PostgreSQL using the `pg` pool. Ensure the table names and column types exactly match what the adapter expects to avoid runtime errors.

## Implementation Breakdown

1. **Infrastructure:** Install adapter package.
2. **Schema:** Run SQL or migrations to create necessary tables.
3. **Configuration:** Initialize the adapter in `web/auth.ts`.
4. **Validation:** Manually inspect the `accounts` and `users` tables after a test login.

## Acceptance Criteria

- [ ] Successful login creates a new row in the `users` and `accounts` tables.
- [ ] Active session creates a row in the `sessions` table.
- [ ] User remains logged in even after the Next.js server restarts.
- [ ] Logout removes the corresponding row from the `sessions` table.

## Test Cases

### Happy Path

- First login -> New user created in DB.
- Subsequent login -> Existing user record updated.

### Failure Path

- Database connection lost -> Auth.js handles failure gracefully (e.g., fallback to error page).
- Mismatched schema -> Informative error in server logs.

### Regression Tests

- Check for duplicate user creation on multiple logins with the same provider.
