# TICKET-49: Database Connection Pooling (Supavisor/Bouncer)

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 4
- **Assignee:** Backend Lead / DevOps
- **Domain:** Performance / Database
- **Priority:** P1 - High
- **Assumptions:**
  - PostgreSQL is the production DB.
- **Affected areas:** `api/app/core/database.py`, Deployment configuration.

## Current State / Existing System

- **Implemented:** Direct connections to PostgreSQL (TICKET-03).
- **Missing:** A connection pooler (proxy). Each instance of the API or Worker opens its own set of connections, which can quickly exhaust the Postgres `max_connections` limit under load.

## Context / Problem

PostgreSQL connections are expensive (memory-wise). A sudden spike in users or a large background job burst could cause the database to reject new connections. We need a pooler (like Supavisor for Supabase or PgBouncer) to multiplex many client connections over a few server connections.

## Why This Is Needed

- **Business Impact:** Prevents "Internal Server Error (500)" crashes during high traffic.
- **Architectural Impact:** Standardizes the database access pattern for a high-concurrency "Modular Monolith."

## Scope

### In-scope

- Configure a connection pooler in the production cloud:
  - If using Supabase: Enable "Supavisor".
  - If self-hosting: Setup "PgBouncer" as a sidecar or managed service.
- Update `DATABASE_URL` in production to use the pooler's port (usually 5432 or 6543).
- Configure pooling mode: **Transaction mode** is recommended for FastAPI/Taskiq.
- Logic to tune `pool_size` and `max_overflow` in the SQLAlchemy engine.

### Out-of-scope

- Read-replica load balancing (future optimization).

## Dependencies / Parallelism

- **Dependencies:** TICKET-44 (Production Deployment), TICKET-51 (Rate Limiting).
- **Parallelism:** Can be done once the production DB is provisioned.

## Rules / Constraints

- Never use "Session mode" with pooled background jobs (can lead to connection leaks).
- Keep the server-side pool size small (e.g., 20-50) to allow for overhead.

## What Needs To Be Built

1. Updated `Settings` model for `SQLALCHEMY_DATABASE_URL` to support pooling proxies.
2. Deployment yaml/config for the PgBouncer instance (if not managed).

## Proposal

Use a managed Postgres service that includes a built-in pooler. Update the backend code to use the `pool_pre_ping=True` and `pool_recycle` settings to keep pooled connections fresh.

## Implementation Breakdown

1. **Config Update:** Verify the new connection string works via a local tunnel.
2. **Platform Setup:** Enable the pooler in the cloud dashboard.
3. **Load Test:** Use a tool (e.g., `locust` or `k6`) to simulate 100 concurrent connections and verify no "Connection Refused" errors occur.
4. **Validation:** Check the Postgres `pg_stat_activity` view to see pooled vs direct connections.

## Acceptance Criteria

- [ ] Application connects successfully through the pooling proxy.
- [ ] Database connection count remains stable even during high request bursts.
- [ ] No "Too many clients" errors are logged by Postgres.
- [ ] Latency overhead of the proxy is < 5ms.

## Test Cases

### Happy Path

- 50 concurrent requests -> Pooler handles them -> DB sees only 10 actual connections.

### Failure Path

- Pooler goes down -> Application health check fails -> Deployment auto-restarts the service.

### Regression Tests

- Ensure that `alembic` migrations still work through the pooler (or use a direct bypass for migrations).
