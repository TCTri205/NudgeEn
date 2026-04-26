# TICKET-53: Performance Load Testing

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 5
- **Assignee:** DevOps Engineer
- **Domain:** Performance / SRE
- **Priority:** P1 - High
- **Assumptions:**
  - Database and Redis are at production tier.
- **Affected areas:** All API endpoints, Taskiq workers.

## Current State / Existing System

- **Implemented:** Functional system (EPIC-00 through EPIC-04).
- **Missing:** Any data on how the system behaves under pressure. We don't know the maximum number of concurrent users we can support before latency degrades.

## Context / Problem

For the Beta launch, we expect a potential spike in users. If the system slows down or crashes under load (e.g., due to unoptimized SQL or slow LLM orchestration), we will lose early adopter trust. We need to find our "Breaking Point" through controlled simulation.

## Why This Is Needed

- **Business Impact:** Ensures a smooth launch day and prevents costly emergency scaling.
- **Architectural Impact:** Validates the "Modular Monolith" efficiency and connection pooling settings (TICKET-49).

## Scope

### In-scope

- Write load testing scripts using `k6` or `Locust`.
- Scenarios:
  - **Gradual Ramp-up:** from 1 to 200 concurrent users.
  - **Spike Test:** sudden jump to 500 users.
  - **Endurance Test:** sustained 50 users for 2 hours.
- Measure:
  - **TTFB (Time to First Byte):** For Chat SSE streams.
  - **DB CPU/Memory:** Under full load.
  - **Taskiq Throughput:** Jobs processed per minute.
- Fix identified bottlenecks (e.g., missing indexes revealed by slow queries).

### Out-of-scope

- Testing of LLM API internal limits (focus on our app's orchestration only).

## Dependencies / Parallelism

- **Dependencies:** TICKET-44 (Production Deployment), TICKET-49 (Pooling).
- **Parallelism:** Can be done in parallel with security audits.

## Rules / Constraints

- Never run load tests directly against the production database while real users are active. Use a "Load Test" environment that mirrors Production specs.

## What Needs To Be Built

1. `tests/load/chat-flow.js` (k6 script).
2. Report summarizing findings and optimizations made.

## Proposal

Use `k6` because it supports testing WebSockets/SSE easily. Focus on the `POST /chat` endpoint as it is the most resource-intensive. Utilize the `structlog` metrics (TICKET-47) to identify which middleware is slowest.

## Implementation Breakdown

1. **Scripting:** Code the user flow (Login -> Create Conversation -> Send 5 Messages).
2. **Execution:** Run against the Staging environment with production-sized DB.
3. **Analysis:** Review Prometheus metrics (TICKET-48) to find hotspots.
4. **Validation:** Re-run the test after fixes to confirm improvement.

## Acceptance Criteria

- [ ] System sustains 200 concurrent users with a P95 "Stream Start" latency of < 500ms.
- [ ] Database CPU usage stays below 70% during the peak load test.
- [ ] No "500 Internal Server Error" responses due to resource exhaustion.

## Test Cases

### Happy Path

- 100 users chatting -> System remains responsive and fluid.

### Failure Path

- 500 users -> System slows down but does not crash (Graceful degradation).

### Regression Tests

- Verify that background workers don't starve the API for database connections.
