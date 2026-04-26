# TICKET-47: Structured JSON Logging (structlog)

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 4
- **Assignee:** Backend Lead
- **Domain:** Logging / SRE
- **Priority:** P2 - Medium
- **Assumptions:**
  - Logs will be ingested by a cloud provider like Datadog or BetterStack.
- **Affected areas:** `api/app/core/logging.py`, All service modules.

## Current State / Existing System

- **Implemented:** Default Python `logging` (TICKET-01).
- **Missing:** Machine-readable logs. Current logs are difficult to parse, search, or filter at scale.

## Context / Problem

In a multi-service environment, we need to search for all logs related to a single `request_id` or `user_id` across API and workers. Plain-text logs make this impossible. Structured JSON logging transforms logs into searchable data.

## Why This Is Needed

- **Business Impact:** Enables complex troubleshooting of system-wide issues (e.g., "Why were these 5 messages delayed?").
- **Architectural Impact:** Standardizes the logging format across the entire modular monolith.

## Scope

### In-scope

- Integrate `structlog` into the FastAPI logging pipeline.
- Configuration:
  - **Development:** Colorful, human-readable console output.
  - **Production:** Strict JSON output to `stdout`.
- Automatic context injection:
  - `request_id`, `user_id`.
  - `method`, `path`, `status_code`.
  - `duration_ms`.
  - `worker_job_id` (for Taskiq jobs).
- Replace all `print()` and standard `logger.info()` calls with `structlog`.

### Out-of-scope

- Log transport implementation (handled by cloud provider's log collector).

## Dependencies / Parallelism

- **Dependencies:** TICKET-43 (Production Config).
- **Parallelism:** Can be done in parallel with TICKET-46.

## Rules / Constraints

- Logs must NEVER contain sensitive data (passwords, auth tokens).
- Log level should be configurable via an ENV variable.

## What Needs To Be Built

1. `api/app/core/logging_setup.py`.
2. Middleware to generate and propagate `request_id`.
3. Logging utility wrapper for easy use across the codebase.

## Proposal

Configure `structlog` to use a series of processors (TimeStamper, JSONRenderer). For Taskiq, use a custom receiver to attach the job ID to the logging context.

## Implementation Breakdown

1. **Config Implementation:** Setup the Pydantic-driven logging config.
2. **Middleware:** Add the request tracking middleware.
3. **Refactor:** Update existing modules to use the new logger.
4. **Validation:** Run the app in production mode and pipe logs to `jq` to verify structure.

## Acceptance Criteria

- [ ] All production logs are valid JSON.
- [ ] Every log entry contains the `request_id` derived from the HTTP header.
- [ ] Worker logs include the `task_name` and `job_id`.
- [ ] Logs are correctly leveled (DEBUG, INFO, ERROR).

## Test Cases

### Happy Path

- Call Chat API -> See a JSON log entry with `path: "/chat"`, `user_id: 123`, and `duration_ms`.

### Failure Path

- Large log burst -> Ensure the JSON serialization doesn't slow down the main request loop.

### Regression Tests

- Verify that logs are still human-readable in the local development terminal.
