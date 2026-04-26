# TICKET-19: Redis Sliding Window Rate Limiter

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 1
- **Assignee:** Backend Lead
- **Domain:** Infrastructure / Safety
- **Priority:** P0 - Critical
- **Assumptions:**
  - Redis is accessible via the platform layer (TICKET-03).
  - User ID is available in the request context (from Auth.js session).
- **Affected areas:** `api/app/core/rate_limit.py`, Redis, API Middleware.

## Current State / Existing System

- **Implemented:** Redis connection pool (TICKET-03).
- **Missing:** Rate limiting logic; the system currently allows unlimited messages per user.

## Context / Problem

AI model usage (Groq/Gemini) incurs costs and has throughput limits. To protect our infrastructure and budget, we must implement a per-user rate limit using a sliding window algorithm to ensure fair usage and prevent abuse.

## Why This Is Needed

- **Business Impact:** Directly controls API costs and prevents "runaway" usage from scripted bots.
- **Architectural Impact:** Leverages Redis for high-performance, atomic rate tracking across multiple API instances.

## Scope

### In-scope

- Implement a sliding window counter using Redis Sorted Sets (`ZADD`, `ZREM`, `ZCOUNT`).
- Define the default limit: 50 messages per 24 hours per user.
- Create a FastAPI dependency or middleware to check limits before processing chat requests.
- Return `HTTP 429 Too Many Requests` when limits are exceeded.
- Include `Retry-After` header indicating when the window will open.

### Out-of-scope

- Per-IP rate limiting (addressed separately if needed).
- Dynamic limits based on user tier (future enhancement).

## Dependencies / Parallelism

- **Dependencies:** TICKET-03 (Redis Setup), TICKET-01 (FastAPI Skeleton).
- **Parallelism:** Can be done in parallel with Sprint 1 frontend work.

## Rules / Constraints

- Must be atomic to prevent race conditions during high-concurrency bursts.
- Rate limit keys project-prefixed (e.g., `nudgeen:limiter:user:{id}`).
- Key TTL should match the window size (24 hours).

## What Needs To Be Built

1. `api/app/core/limiter.py`: Logic for the sliding window check.
2. `api/app/middleware/rate_limit.py`: Integration with FastAPI.
3. Configuration for `RATE_LIMIT_MESSAGES` and `RATE_LIMIT_WINDOW`.

## Proposal

Use a Redis sorted set where each element is a timestamp of a request. Before adding a new request, remove timestamps older than (Now - Window). If the set size is >= Limit, reject the request.

## Implementation Breakdown

1. **Limiter Core:** Write the `is_rate_limited(user_id)` function using Redis `PIPELINE`.
2. **Middleware:** Attach the limiter to the chat endpoint.
3. **Error Handling:** Define a custom exception for rate limiting that generates the 429 response.
4. **Validation:** Load-test the endpoint with 50+ requests and check for blocking.

## Acceptance Criteria

- [ ] User is successfully blocked after the 50th request within a rolling 24-hour period.
- [ ] Response headers include `X-RateLimit-Limit`, `X-RateLimit-Remaining`.
- [ ] Blocks are automatically lifted as older requests age out of the 24-hour window.
- [ ] The limiter handles concurrent requests correctly without overcounting.

## Test Cases

### Happy Path

- 49 requests -> All pass.
- 50th request -> Pass.
- 51st request -> 429 Error.

### Failure Path

- Redis connection failure -> System should fail-closed (block) or fail-open (allow) based on safety preference (currently fail-open to ensure UX).

### Regression Tests

- Verify that rate limiting for User A does not affect User B.
