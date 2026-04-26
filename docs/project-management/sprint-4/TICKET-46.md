# TICKET-46: Sentry Error Tracking Integration

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 4
- **Assignee:** Lead Developer
- **Domain:** Observability / SRE
- **Priority:** P1 - High
- **Assumptions:**
  - Sentry project (DSN) is created.
- **Affected areas:** `api/app/main.py`, `web/sentry.client.config.ts`, Error Handlers.

## Current State / Existing System

- **Implemented:** Console-based error logging (TICKET-47).
- **Missing:** Real-time visibility into production exceptions, grouping of duplicate errors, or stack trace visualization across frontend and backend.

## Context / Problem

When an error happens in production (e.g., Gemini API timeout, DB deadlocks), we need to know *immediately*. Manual log diving is too slow. Sentry provides the necessary infrastructure to track, group, and alert on errors automatically.

## Why This Is Needed

- **Business Impact:** Reduces "Time to Resolution" (TTR) for critical bugs.
- **Architectural Impact:** Standardizes error reporting and enables cross-service trace linking.

## Scope

### In-scope

- **Backend (FastAPI):**
  - Install `sentry-sdk[fastapi]`.
  - Initialize with `dsn` and `traces_sample_rate`.
  - Configure custom tags: `user_id`, `plan_type`.
- **Frontend (Next.js):**
  - Setup `sentry-wizard` for Next.js.
  - Configure client-side and server-side capture.
  - Upload source maps to Sentry for readable stack traces.
- **Security:**
  - Implement `before_send` PII scrubber to remove user message content from logs.
- **Alerts:**
  - Configure Slack integration for all "Critical" and "Error" level events.

### Out-of-scope

- Sentry Performance Monitoring (will be addressed in a future optimization sprint).

## Dependencies / Parallelism

- **Dependencies:** TICKET-43 (Production Config).
- **Parallelism:** Can be done in parallel with TICKET-47 (Logging).

## Rules / Constraints

- Never log user-provided English text (PII) to Sentry.
- Sample rate in production should be < 1.0 (e.g., 0.1 for traces) to save on quota.

## What Needs To Be Built

1. Global exception middleware for FastAPI that reports to Sentry.
2. Error boundary components in Next.js.
3. Configuration files: `api/app/core/sentry.py` and `web/sentry.conf.js`.

## Proposal

Use the official Sentry SDKs. For PII scrubbing, use Sentry's data scrubbing rules in the UI *and* a local `before_send` hook to ensure the message body is never sent.

## Implementation Breakdown

1. **SDK Setup:** Add dependencies and initialize in `main.py`.
2. **Context Enrichment:** Add a middleware to attach `user_id` to the Sentry scope.
3. **Frontend Hook:** Add Sentry to the custom `_error.tsx` and `_app.tsx` pages.
4. **Validation:** Manually throw a `/test-error` endpoint and verify the alert enters Slack.

## Acceptance Criteria

- [ ] Exceptions on both Frontend and Backend are captured in the Sentry dashboard.
- [ ] Stack traces are accurate and correctly mapped to source code (Source Maps).
- [ ] No private user data (messages, emails) is visible in the Sentry issue details.
- [ ] Slack notifications are received for unhandled exceptions.

## Test Cases

### Happy Path

- Trigger error -> Sentry captures -> Slack pings -> Developer sees the exact line of code.

### Failure Path

- No internet/DSN blocked -> App continues to function normally (no crash-on-failure).

### Regression Tests

- Verify that standard 404/401 responses are NOT sent to Sentry (noise reduction).
