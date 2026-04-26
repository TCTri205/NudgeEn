# TICKET-51: Production Rate Limiting Enforcement

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 4
- **Assignee:** Backend Lead / Security
- **Domain:** API Security
- **Priority:** P1 - High
- **Assumptions:**
  - Redis is deployed and reachable.
- **Affected areas:** `api/app/middleware/rate_limit.py`, Auth routes, Chat routes.

## Current State / Existing System

- **Implemented:** Placeholder logic for rate limiting (TICKET-19).
- **Missing:** Hardened, Redis-backed enforcement that differentiates between public and authenticated traffic.

## Context / Problem

Public APIs are targets for abuse. Without rate limiting, a single malicious user could spam our `POST /chat` endpoint, racking up massive LLM costs and degrading performance for everyone. We need "Fortress-Level" protection.

## Why This Is Needed

- **Business Impact:** Controls LLM costs and prevents Denial of Service (DoS).
- **Architectural Impact:** Implements the "Security Gateway" pattern.

## Scope

### In-scope

- **Authenticated Routes:**
  - Limit by `user_id`.
  - Tiered limits: Free users (e.g., 5 msgs/min) vs Premium (e.g., 50 msgs/min).
- **Public Routes:**
  - Limit by IP Address.
  - Strict limits on `/login` and `/register` to prevent brute force.
- **Redis Implementation:**
  - Use `FastAPI-Limiter` or a custom Redis-lua sliding window script.
- **Feedback:** Return `429 Too Many Requests` with a clear message and `Retry-After` header.

### Out-of-scope

- WAF (Web Application Firewall) configuration.

## Dependencies / Parallelism

- **Dependencies:** TICKET-11 (Rate Limiter setup), TICKET-44 (Deployment).
- **Parallelism:** Can be done in parallel with security headers (TICKET-52).

## Rules / Constraints

- Rate limits should be configurable via Environment Variables.
- Errors must be informative but not leak system internals.

## What Needs To Be Built

1. Middleware refactor to support IP and User-based switching.
2. Configuration mapping for different routes (Sensitive vs Generic).

## Proposal

Use Redis-based sliding window rate limiting. For the user chat endpoint, use a "Token Bucket" strategy where users accumulate chat credits over time.

## Implementation Breakdown

1. **Redis Link:** Ensure the production Redis instance is the backend for all limits.
2. **Strategy Setup:** Define the limits for each endpoint category.
3. **Integration:** Apply the dependencies to the FastAPI app routers.
4. **Validation:** Use a script to spam the API and verify a 429 response is returned exactly when expected.

## Acceptance Criteria

- [ ] Exceeding a limit returns a 429 status code.
- [ ] Limits are enforced globally across all API instances (via Redis).
- [ ] IP-based limiting works even behind a load balancer (X-Forwarded-For).
- [ ] Rate limit data is visible in the Redis dashboard.

## Test Cases

### Happy Path

- Send 5 messages in 1 second -> Receive 429 for the 6th message.

### Failure Path

- Redis goes down -> The API should "Fail Open" (allow request) but log a critical error (Availability over strict blocking).

### Regression Tests

- Verify that rate limiting does not interfere with legal SSE streaming connections (TICKET-14).
