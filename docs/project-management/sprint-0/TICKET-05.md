# TICKET-05: Taskiq Background Worker Setup

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 0
- **Assignee:** Backend Lead
- **Domain:** Infrastructure / Workers
- **Priority:** P1 - High
- **Assumptions:**
  - Redis is available and configured (TICKET-03).
  - FastAPI skeleton is ready (TICKET-01).
- **Affected areas:** `workers/`, `api/app/core/broker.py`, Redis.

## Current State / Existing System

- **Implemented:** Redis connection logic (TICKET-03).
- **Missing:** Asynchronous task processing framework; API currently handles all requests synchronously.

## Context / Problem

NudgeEn will perform heavy tasks like LLM memory extraction and analytics which shouldn't block the API response. We need a robust worker system to handle these out-of-band operations.

## Why This Is Needed

- **Business Impact:** Enhances UI responsiveness by offloading slow tasks.
- **Architectural Impact:** Implements the "Producer-Consumer" pattern, allowing the system to scale background processing independently of the API.

## Scope

### In-scope

- Create a `workers/` directory as a separate entry point.
- Initialize `Taskiq` with `RedisBroker`.
- Define a sample task (e.g., `process_analytics`).
- Setup worker lifecycle management (start/stop).
- Configure Pydantic settings for the broker URL.

### Out-of-scope

- Actual feature tasks (Memory extraction, Persona updates).
- Task results persistence (if different from core DB).

## Dependencies / Parallelism

- **Dependencies:** TICKET-03 (Redis Setup).
- **Parallelism:** Can be done in parallel with TICKET-04 (Alembic Setup).

## Rules / Constraints

- No direct database writes from workers without using the platform's session management.
- Task results should be handled carefully (Taskiq state management or DB updates).
- Must follow the graceful shutdown patterns described in EPIC-00.

## What Needs To Be Built

1. `api/app/core/broker.py`: Define the `RedisBroker` instance.
2. `workers/app/worker.py`: Worker initialization and task discovery.
3. `workers/app/tasks/sample.py`: A basic idempotent task.
4. Update `docker-compose.yml` (if applicable) to include a `worker` service.

## Proposal

Use Taskiq's `RedisBroker` for low-latency task dispatching. The API will use the broker to `.publish()` tasks, and a separate worker process will consume them. Use `taskiq-dependencies` for shared resources like database sessions.

## Implementation Breakdown

1. **Infrastructure:** Install `taskiq`, `taskiq-redis`, `taskiq-dependencies`.
2. **Broker Setup:** Configure the Redis broker in the platform layer.
3. **Worker Code:** Create the worker entry point that imports and registers tasks.
4. **Sample Task:** Implement a simple logging task to verify the pipe.
5. **Validation:** Dispatch a task from a FastAPI endpoint and verify worker output.

## Acceptance Criteria

- [ ] Taskiq worker process starts and connects to Redis.
- [ ] A task can be published from the FastAPI backend and received by the worker.
- [ ] The sample task executes successfully and logs its completion.
- [ ] Worker supports horizontal scaling (multiple instances consuming from the same queue).

## Test Cases

### Happy Path

- Dispatch task -> Worker receives -> Task logs "Success".
- Worker restarts -> Reconnects to Redis and resumes processing.

### Failure Path

- Redis is down -> Dispatch fails with clear error.
- Task crashes -> Worker remains alive and continues processing other tasks.

### Regression Tests

- Ensure task payloads are JSON serializable.
