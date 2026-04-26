# NudgeEn - Architecture Characteristics & Pattern Recommendation

## Architecture Characteristics Worksheet

| Field | Value |
| --- | --- |
| **System/Project** | NudgeEn |
| **Domain/Quantum** | EdTech / AI Language Learning (Text Reading/Writing) |
| **Team** | 5-9 members |
| **Date** | 2026-04-26 |
| **Next Review** | After Sprint 2, once the first end-to-end AI pipeline exists |

## Driving Characteristics (Top 7)

| # | Characteristic | Top 3 | Rationale |
| --- | --- | --- | --- |
| 1 | **Scalability** | Yes | The system must support high concurrent chat traffic and growing message volume. |
| 2 | **Recoverability** | Yes | Background tasks must survive API restarts and worker crashes. |
| 3 | **Extensibility** | Yes | The product will likely add providers, modalities, analytics, and richer pedagogy. |
| 4 | **Responsiveness** |  | Chat UX needs low TTFB and smooth streaming. |
| 5 | **Data Integrity** |  | User profile, memory, and message history must remain consistent. |
| 6 | **Security** |  | Auth, abuse monitoring, and PII scrubbing are foundational. |
| 7 | **Observability** |  | Queue lag, model failures, and DB pressure must be visible. |

## Implicit Characteristics

| Characteristic | Notes |
| --- | --- |
| **Maintainability** | A modular monolith keeps complexity lower than microservices for the current team size. |
| **Cost Awareness** | Managed infrastructure is acceptable when it lowers operational risk. |
| **Evolvability** | Internal modules and queue boundaries should support future product expansion. |

## Trade-off Analysis

### 1. Robustness vs Complexity

| What You Gain | What It Costs |
| --- | --- |
| Durable queue-backed background processing and safer recovery. | More moving parts: API, Redis, workers, DB pooling, retries. |

Mitigation:

- use managed Postgres and Redis
- keep one logical backend codebase
- avoid microservices until team and product truly require them

### 2. Extensibility vs Upfront Design

| What You Gain | What It Costs |
| --- | --- |
| Easier addition of providers, jobs, and modules later. | Need clearer interfaces and ownership from the start. |

Mitigation:

- repository pattern for persistence
- strategy pattern for AI providers
- explicit module boundaries in the application layer

### 3. Security vs Responsiveness

| What You Gain | What It Costs |
| --- | --- |
| Safety gating before expensive or unsafe model responses. | Sequential checks add latency to the chat path. |

Mitigation:

- keep gatekeeper lightweight
- use streaming UX to mask some latency
- push every non-essential task to workers

## Recommended Architecture Pattern

### Modular Monolith + Distributed Runtime

Recommended production direction:

- `Next.js Web` for web and auth boundary
- `FastAPI API` for chat orchestration
- `PostgreSQL` as source of truth
- `Redis` for cache, rate limiting, and queue transport
- `Taskiq Workers` for async workloads

```text
Browser
  |
  v
Next.js Web/BFF
  |
  v
FastAPI API
  | \
  |  \--> PostgreSQL
  |
  \----> Redis broker/cache ----> Taskiq Workers
```

## Key Design Patterns

### 1. Distribution Pattern: Decoupled Workers

The API process handles user interaction and streaming only. Heavy logic such as memory extraction, summaries, and analytics is pushed to workers.

### 2. Strategy Pattern: AI Provider Switching

Supports primary/fallback model routing without reshaping the whole application.

### 3. Repository Pattern: Database Abstraction

Keeps persistence details contained and supports strict transaction handling.

## Scalability & Growth Path

| Level | Component Configuration | Usage Target |
| --- | --- | --- |
| **Initial Production** | Managed Postgres + managed Redis + 1 worker | Early beta to ~1k DAU |
| **Professional** | Pooled Postgres + Redis HA + 2-6 workers | ~1k to 50k DAU |
| **Scale** | Read replicas + split worker pools + deeper observability | 50k+ DAU |

## Summary

This architecture gives NudgeEn a strong balance of scalability, recoverability, extensibility, and implementation control without the overhead of premature microservices.
