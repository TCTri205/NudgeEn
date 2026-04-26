# NudgeEn Architecture

> Canonical architecture reference for the project.

## 1. Architecture Summary

NudgeEn should use a **modular monolith at code level** and a **distributed runtime at deployment level**:

- One web application: `Next.js Web`
- One API service: `FastAPI API`
- One worker service type: `Taskiq Workers`
- Two infrastructure dependencies: `PostgreSQL` and `Redis`

This is the right balance for the current product:

- simpler than microservices
- scalable enough for bursty chat traffic
- safe for background AI tasks
- easier to keep consistent with a small team

## 2. High-Level Topology

```text
                         +----------------------+
                         |      Browser         |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |   Next.js Web         |
                         | - Auth.js            |
                         | - UI                 |
                         | - session boundary   |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |     FastAPI API      |
                         | - chat endpoint      |
                         | - gatekeeper         |
                         | - orchestration      |
                         | - SSE streaming      |
                         +-----+-----------+----+
                               |           |
                               |           |
                               v           v
                     +----------------+  +----------------+
                     | PostgreSQL     |  | Redis          |
                     | system of      |  | cache + broker |
                     | record         |  +--------+-------+
                     +--------+-------+           |
                              ^                   v
                              |         +----------------------+
                              +---------+  Taskiq Workers      |
                                        | - memory extraction  |
                                        | - weekly summaries   |
                                        | - analytics jobs     |
                                        | - retry processing   |
                                        +----------------------+
```

## 3. Module Boundaries

The codebase should remain one logical backend with strict internal modules:

- `auth`: identity, session, account lifecycle
- `chat`: conversation lifecycle, message persistence, streaming
- `persona`: vibe selection, prompt assembly, response policies
- `guardrails`: safety classification, scope enforcement, abuse events
- `memory`: extraction, profile updates, memory deletion
- `pedagogy`: subtle corrections, progress summaries
- `billing_or_limits`: quota, rate limits, plan enforcement
- `platform`: config, logging, tracing, queues, persistence adapters

Rule:

- modules can depend on `platform`
- modules cannot bypass each other through direct table writes
- cross-module work should go through application services or domain events

## 4. Request Path vs Background Path

### Synchronous path

Use the synchronous path only for work required to answer the current chat turn:

1. Web app authenticates user via Auth.js.
2. BFF forwards the request to FastAPI with validated user context.
3. FastAPI loads the active conversation slice from PostgreSQL.
4. Guardrail check runs first.
5. Persona response is generated.
6. Response starts streaming back to the client.
7. Minimal durable write happens for the user message and assistant reply.
8. Background jobs are enqueued for post-processing.

### Asynchronous path

Use workers for anything not required for first response token:

- memory extraction and profile merge
- correction enrichment if not generated inline
- weekly progress card generation
- event aggregation and analytics materialization
- abuse review and anomaly scoring

This split is the key performance decision in the architecture.

## 5. Why PostgreSQL

PostgreSQL should be the single source of truth for durable data:

- users and auth-linked identities
- conversations
- messages
- user profile and extracted memories
- correction records
- job audit trail
- rate-limit counters that require durability

Why it fits:

- transactional consistency for chat/message/profile updates
- JSONB for flexible memory/profile storage
- mature indexing and query planning
- clean scaling path with read replicas and connection pooling

## 6. Why Redis

Redis should be used only for short-lived and high-throughput concerns:

- Taskiq broker
- ephemeral cache
- sliding-window rate limiting
- short-lived idempotency/result cache
- presence / typing hints if needed later

Redis must not become a second source of truth for business data.

## 7. Queue and Worker Model

Use `Taskiq + Redis` with explicit job classes in **Taskiq Workers**:

- `memory.extract_after_message`
- `memory.rebuild_profile`
- `summary.generate_weekly_check`
- `analytics.aggregate_conversation_metrics`
- `safety.review_flagged_interaction`

Worker rules:

- every job is idempotent
- every job has retry policy with exponential backoff
- poisoned jobs go to dead-letter storage or dead-letter stream
- every job emits structured logs with `job_id`, `user_id`, `conversation_id`

Prefer separate worker concurrency pools later:

- light jobs: analytics, small profile merges
- heavy jobs: LLM extraction, long summaries

## 8. Recommended Data Model

Core tables:

- `users`
- `accounts`
- `sessions`
- `conversations`
- `messages`
- `message_corrections`
- `user_profiles`
- `user_memories`
- `weekly_progress_cards`
- `job_runs`
- `abuse_events`

Key design choices:

- store each message as its own row
- keep `user_profiles` as a current projection
- keep `user_memories` as append-oriented normalized facts
- use JSONB only where flexibility is useful, not everywhere
- add `created_at`, `updated_at`, `version` to mutable aggregates

## 9. Chat Flow

Recommended chat transaction:

1. Persist inbound user message with client idempotency key.
2. Run guardrail classification.
3. Build prompt from recent messages + compacted memory/profile summary.
4. Call primary model.
5. Stream tokens to client.
6. Persist final assistant message and correction payload.
7. Enqueue memory and analytics jobs after commit.

Important:

- enqueue jobs only after the main database transaction commits
- do not let worker execution depend on uncommitted state

## 10. Scaling Strategy

### Horizontal scaling

- scale web instances independently
- scale API instances for concurrent chat load
- scale workers independently by queue depth and job latency

### Database scaling

- use PgBouncer or Supavisor from the start
- optimize hot queries with targeted indexes
- add read replicas only after actual read pressure appears

### Queue scaling

- monitor queue lag and retry rate
- split queues by priority when needed:
  - `realtime-low-latency`
  - `default`
  - `heavy-llm`

## 11. Reliability and Consistency

Required safeguards:

- idempotency key per chat send request
- outbox-style event enqueue after commit
- retries with bounded maximum attempts
- timeout budgets for external LLM calls
- fallback provider for degraded response path
- graceful degraded UX when async subsystems are delayed

Consistency rules:

- PostgreSQL is authoritative
- Redis loss must not corrupt durable state
- workers may run a job more than once without corrupting data

## 12. Security and Privacy

- Auth.js owns user authentication at the web boundary
- FastAPI trusts only signed, validated identity context
- PII scrubbing must happen before memory facts are persisted
- store only the minimal profile summary needed for product behavior
- support hard delete for user memory/profile on request
- log security-sensitive events without leaking message content where avoidable

## 13. Observability

Minimum required telemetry:

- request logs with request id and user id
- job logs with job id and retry count
- metrics: p95 latency, token cost, queue lag, worker failures, DB pool saturation
- traces spanning web -> API -> DB/Redis -> worker when practical
- Sentry or equivalent for exception capture

## 14. Deployment Recommendation

Recommended first production layout:

- `Vercel`: Next.js web
- `Render/Railway/Fly`: FastAPI API
- `Render/Railway/Fly`: worker process
- `Managed PostgreSQL`: Supabase, Neon, RDS, or equivalent
- `Managed Redis`: Upstash or equivalent

Environment separation:

- `dev`
- `staging`
- `prod`

Each environment needs isolated:

- database
- redis
- API keys
- auth secrets

## 15. Architecture Decision

Chosen architecture:

- **modular monolith**
- **distributed runtime**
- **PostgreSQL as source of truth**
- **Redis as broker/cache**
- **queue + worker mandatory from initial production architecture**

This is the recommended target because it maximizes scalability and operational clarity without the cost of premature microservices.
