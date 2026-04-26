# TICKET-48: Prometheus Metrics & Health Checks

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 4
- **Assignee:** DevOps Engineer
- **Domain:** Monitoring / SRE
- **Priority:** P1 - High
- **Assumptions:**
  - Deployment platform supports custom health-check endpoints.
- **Affected areas:** `api/app/main.py`, `api/app/api/health_router.py`.

## Current State / Existing System

- **Implemented:** Basic FastAPI startup (TICKET-01).
- **Missing:** Explicit signals for "Liveness," "Readiness," and business-level metrics (e.g., LLM latency).

## Context / Problem

In production, load balancers need to know if a service is healthy. If the database connection drops but the API process is still running, we should signal a "Not Ready" state so traffic is stopped. Additionally, we need raw data on request rates and response times to set up alerts.

## Why This Is Needed

- **Business Impact:** Enables auto-healing (reboots) and capacity planning.
- **Architectural Impact:** Exposes service state to the orchestration layer (Kubernetes, Render, etc.).

## Scope

### In-scope

- Implement standard Health Check endpoints:
  - `/health/live`: Simple 200 OK (App is running).
  - `/health/ready`: Checks DB + Redis connections (App is ready to handle traffic).
- Integrate `starlette-prometheus` or `prometheus-fastapi-instrumentator`.
- Export basic metrics on `/metrics`:
  - `http_requests_total` (by status/path).
  - `http_request_duration_seconds`.
  - `ai_response_time` (custom gauge).
  - `task_queue_depth` (gauge for Redis).

### Out-of-scope

- Multi-region latency aggregation.

## Dependencies / Parallelism

- **Dependencies:** TICKET-44 (Deployment).
- **Parallelism:** Can be done while the infrastructure is being provisioned.

## Rules / Constraints

- `/metrics` endpoint should be protected or internal-only.
- Health checks must have a short timeout (< 2s) to avoid cascading failures.

## What Needs To Be Built

1. `api/app/core/metrics.py`: Metrics collector definitions.
2. `api/app/api/v1/endpoints/health.py`: Health check logic.

## Proposal

Use `prometheus-fastapi-instrumentator` for auto-metrics. For health checks, create a small utility that runs `SELECT 1` on the DB and `PING` on Redis.

## Implementation Breakdown

1. **Instrumentator Setup:** Hook the metrics exporter into the FastAPI app.
2. **Health Check logic:** Implement the DB/Redis check functions.
3. **Configuration:** Setup the load balancer to poll `/health/ready` every 30s.
4. **Validation:** Visit `/metrics` in the browser and see the raw prometheus text.

## Acceptance Criteria

- [ ] `/health/ready` returns 503 if the database is down.
- [ ] `/metrics` displays request counts and latencies.
- [ ] Load balancer correctly detects service health and routes traffic accordingly.
- [ ] Metric generation adds < 1ms overhead to the request cycle.

## Test Cases

### Happy Path

- All services up -> `/health/ready` returns 200.

### Failure Path

- Postgres disconnected -> `/health/ready` returns 503 -> Load balancer removes instance.

### Regression Tests

- Verify custom metrics (e.g., Gemini latency) are correctly scoped per provider.
