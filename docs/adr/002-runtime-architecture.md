# ADR-002: Runtime Architecture for Scalable Chat Processing

## Status

Accepted

## Context

NudgeEn needs low-latency chat responses, durable user data, and background AI processing that can scale independently. A single-process application would be simpler initially, but it would couple user-facing latency to memory extraction, summaries, retries, and analytics work.

The project also wants production readiness from the beginning:

- PostgreSQL
- Redis
- queue
- worker
- room for higher concurrency

## Decision

Adopt a **modular monolith** architecture with a **distributed runtime**:

- `Next.js` for web UI and auth boundary
- `FastAPI` for the main application API
- `PostgreSQL` as the system of record
- `Redis` for cache, rate limiting, and queue transport
- `Taskiq workers` for asynchronous workloads

## Rationale

- Keeps domain logic unified in one backend codebase.
- Avoids premature microservice boundaries.
- Preserves low chat latency by moving non-critical work off the request path.
- Supports horizontal scaling of API and worker processes separately.
- Uses infrastructure with well-understood operational behavior.

## Consequences

Positive:

- better scalability under bursty chat usage
- safer recovery model for background jobs
- cleaner operational split between online and offline workloads

Negative:

- higher deployment complexity than a single service
- need for idempotency, retries, and queue monitoring
- more infrastructure to configure across environments

## Guardrails

- PostgreSQL remains the only durable source of truth.
- Redis is not used as a business-data database.
- All worker jobs must be idempotent.
- Background jobs are enqueued only after successful DB commit.
