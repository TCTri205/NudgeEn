# TICKET-03: Database & Redis Connection Setup

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 0
- **Assignee:** Backend Lead
- **Domain:** Data Layer
- **Priority:** P1 - High
- **Assumptions:**
  - PostgreSQL 16 and Redis 7 are running locally or via Docker.
  - `api/` skeleton (TICKET-01) is already created.
- **Affected areas:** `api/app/core/`, Base Configuration.

## Current State / Existing System

- **Implemented:** Architectural guidelines for using PostgreSQL and Redis in ARCHITECTURE.md.
- **Missing:** Any connection logic, pooling configuration, or environment variable handling for databases.

## Context / Problem

NudgeEn requires a persistent data store for users and conversations (PostgreSQL) and a fast in-memory store for queuing and caching (Redis). We need a centralized, async-aware way to manage these connections.

## Why This Is Needed

- **Business Impact:** Ensures data persistence and system reliability.
- **Architectural Impact:** Establishes the foundation for the Repository pattern and background task processing.

## Scope

### In-scope

- Implement async SQLAlchemy engine and session factory.
- Implement Redis connection pooling using `redis-py` (async).
- Define `DATABASE_URL` and `REDIS_URL` in `.env`.
- Create `api/app/core/database.py` and `api/app/core/redis.py`.
- Implement FastAPI dependencies for DB sessions.

### Out-of-scope

- Actual database migrations (TICKET-04).
- Domain models and repositories.

## Dependencies / Parallelism

- **Dependencies:** TICKET-01 (FastAPI Skeleton).
- **Parallelism:** Can be done in parallel with TICKET-02 (Next.js Setup).

## Rules / Constraints

- Must use `asyncpg` for PostgreSQL connection.
- Must use `sqlalchemy.ext.asyncio` for the ORM layer.
- Redis connections must be managed via a connection pool.
- Secrets and connection strings must NEVER be hardcoded.

## What Needs To Be Built

1. `api/app/core/database.py`: Async engine, `AsyncSessionLocal`, and `get_db` dependency.
2. `api/app/core/redis.py`: Async Redis client and `get_redis` dependency.
3. `api/app/core/config.py`: Pydantic settings for DB and Redis credentials.
4. `.env.template`: Document required environment variables.

## Proposal

Configure SQLAlchemy with `pool_size` and `max_overflow` to handle concurrent requests. For Redis, use the `Redis.from_url()` with `decode_responses=True` configuration.

## Implementation Breakdown

1. **Config Update:** Add database and redis settings to `Settings` class in `config.py`.
2. **PostgreSQL Setup:** Implement `database.py` with async engine.
3. **Redis Setup:** Implement `redis.py` with connection pool.
4. **FastAPI Integration:** Add dependencies to `main.py` or separate module routers.
5. **Validation:** Create a simple test script to ping both services.

## Acceptance Criteria

- [ ] PostgreSQL connection test succeeds.
- [ ] Redis "PING" command returns "PONG".
- [ ] FastAPI route successfully retrieves a DB session via dependency injection.
- [ ] Environment variables are correctly loaded from `.env`.

## Test Cases

### Happy Path

- DB and Redis are up -> App starts and connects.
- `GET /health/db` -> returns `{"postgres": "connected", "redis": "connected"}`.

### Failure Path

- Postgres is down -> App should log error and health check should fail.
- Invalid credentials -> Authentication error on connection attempt.

### Regression Tests

- Ensure no synchronous calls are made to the database from async endpoints.
