# TICKET-18: Message Idempotency & Deduplication

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 1
- **Assignee:** Backend Lead
- **Domain:** Infrastructure / Reliability
- **Priority:** P1 - High
- **Assumptions:**
  - Redis is available for caching idempotency keys (TICKET-03).
  - Client is capable of generating and sending a `request_id` (UUID).
- **Affected areas:** `api/app/middleware/idempotency.py`, Redis.

## Current State / Existing System

- **Implemented:** Generic Redis connection (TICKET-03).
- **Missing:** Any logic to handle duplicate requests; Currently, 10 identical POSTs will result in 10 identical DB entries and 10 LLM calls.

## Context / Problem

Mobile networks or poor connections often lead to retries. If the client retries a "Send Message" request because it didn't get an ACK, we don't want to generate a second AI response. Idempotency keys ensure that the same request is only processed once.

## Why This Is Needed

- **Business Impact:** Saves money by avoiding redundant LLM calls and prevents a confusing user experience (double messages).
- **Architectural Impact:** Adds a lightweight caching layer for request deduplication.

## Scope

### In-scope

- Implement an idempotency check using a `X-Request-ID` header.
- Store `request_id` in Redis with a short TTL (e.g., 1 hour or 24 hours).
- If `request_id` exists, return the cached result (or a 409/Silent Success).
- Implement a decorator or middleware for easy multi-endpoint usage.

### Out-of-scope

- Full result caching (just deduplicating the action for now).

## Dependencies / Parallelism

- **Dependencies:** TICKET-03 (Redis Setup), TICKET-01 (FastAPI Skeleton).
- **Parallelism:** Can be done alongside TICKET-16 (Persistence).

## Rules / Constraints

- Idempotency keys must be scoped to the user (e.g., `idemp:user:{id}:{request_id}`).
- TTL must be long enough to cover typical retry windows but short enough to clear Redis.
- The check MUST be atomic (`SET NX`).

## What Needs To Be Built

1. `api/app/core/idempotency.py`: helper utility for checking/setting keys.
2. Integration with chat routes.

## Proposal

Use Redis `SET` with the `NX` (Not eXists) flag and a `EX` (Expire) time. If `SET NX` returns 1, proceed. If it returns 0, the request is a duplicate.

## Implementation Breakdown

1. **Core Logic:** Write the Redis check/lock function.
2. **API Integration:** Add a check to the `POST /api/chat` endpoint.
3. **Client Update:** Ensure the web frontend generates and persists a UUID for each message until it receives a success.
4. **Validation:** Send 5 identical requests simultaneously and verify only 1 is processed.

## Acceptance Criteria

- [ ] Duplicate requests with the same `X-Request-ID` do not trigger multiple LLM calls.
- [ ] Duplicate requests do not create duplicate rows in the `messages` table.
- [ ] The system handles successfully processed vs currently processing duplicates differently (optional).

## Test Cases

### Happy Path

- Send message ID-123 -> Success.
- Send message ID-123 (again) -> 200 OK (cached) or 409, but NO double DB entry.

### Failure Path

- Redis is down -> Fallback to processing (prefer duplication over failure) or block based on strictness.

### Regression Tests

- Verify different users can use the same `request_id` values (scoped correctly).
