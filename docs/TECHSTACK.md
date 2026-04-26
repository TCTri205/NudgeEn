# NudgeEn Tech Stack (MVP)

> **Last audited:** 2026-04-26 | Aligned with `PRD-v1.md` + `PRINCIPLES.md`

This document is the **definitive, critically-audited** technology stack for NudgeEn MVP. All decisions are weighed against the **Zero-Base Costing** and **Web-First** principles.

---

## 🏗️ Architecture Overview

```text
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (Vercel – free)                                   │
│  Next.js 15 (App Router) · TypeScript · Tailwind CSS v3     │
│  Auth: Auth.js v5 (OAuth2: Google/GitHub + Credentials)     │
├─────────────────────────────────────────────────────────────┤
│  BACKEND (Render – free web service, keep-alive cron)       │
│  FastAPI (Python 3.12) · Pydantic v2                        │
│  Streaming: SSE via StreamingResponse                        │
├─────────────────────────────────────────────────────────────┤
│  AI LAYER                                                   │
│  Orchestration: Raw asyncio (simple 3-agent DAG)            │
│  Primary:  Gemini 2.5 Flash (free tier)                     │
│  Fallback: Groq / Llama-3.1-8b (free tier, ~200ms)         │
│  Structured Output: Pydantic model → response_schema        │
│  Eval: LLM-as-a-Judge (Gemini, zero extra cost)             │
├─────────────────────────────────────────────────────────────┤
│  DATA LAYER                                                 │
│  Primary DB:  Turso (libSQL/SQLite-compatible, free tier)   │
│  ORM:         SQLAlchemy async (libsql-experimental driver) │
│  Migration principles: [DATABASE_GUIDELINES.md](./DATABASE_GUIDELINES.md) │
│  Migration path: Supabase/PostgreSQL when >1K active users  │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚖️ Component Decisions & Rationale

### 1. Frontend — Next.js 15 (App Router) + TypeScript

- **Why Next.js 15:** PRD mandates Vercel for CI/CD. App Router provides SSR for fast first paint, which matters for a web-first product (Principle 4). TypeScript adds safety for the JSON schema contracts between frontend and backend.
- **Why Tailwind CSS v3:** The chat UI (message bubbles, sparkle corrections, typing indicators, reactions) is component-dense. Tailwind dramatically accelerates iteration vs. vanilla CSS for this specific UI pattern. Zero cost, widely supported on Vercel.
- **Alternative considered — Full Next.js monolith (no FastAPI):** Tempting for simplicity. The Gemini JS SDK (`@google/generative-ai`) is mature, and `better-sqlite3` runs in Node.js. However, the Python ecosystem is **meaningfully superior** for multi-agent AI orchestration, and the PRD explicitly calls for FastAPI. The two-service complexity is an acceptable trade-off for long-term AI extensibility.

### 2. Backend — FastAPI (Python 3.12) + Pydantic v2

- **Why FastAPI:** Native `asyncio` is essential for concurrent LLM calls. The Google Gemini Python SDK is first-class; `response_schema` enforces Pydantic models directly. Python's AI/ML ecosystem (future LangGraph, evals, embeddings) has no equivalent in Node.js.
- **Why Pydantic v2:** Enforces the AI Structured Output schema at runtime (validates every LLM response before it reaches the client). Pydantic v2 is 5–50x faster than v1 due to Rust core — critical in a per-message hot path.
- **Streaming:** SSE via `StreamingResponse` delivers the "AI is typing..." UX (REQ-001) without WebSocket complexity. Render's free tier supports SSE. WebSockets on Render free tier are unreliable and not recommended.

### 3. Database — Turso (libSQL) ⚠️ REVISED

> **Previous decision (SQLite on Render) was critically flawed.**

**Root Cause:** Render's free tier uses an **ephemeral filesystem**. Any SQLite file written to disk is **wiped on every redeploy, restart, or spin-down** (which occurs after 15 minutes of inactivity on free tier). This makes local SQLite on Render completely unusable for production — user profiles and chat history would be destroyed regularly.

**Chosen Solution: Turso**

| Property | Turso Free Tier |
|---|---|
| Storage | 5 GB |
| Databases | 500 |
| Rows Read/month | 500 million |
| Rows Written/month | 10 million |
| Cold starts | **None** — always on |
| SQLite compatible | ✅ Yes (libSQL) |
| Encrypted at rest | ✅ Yes (by default) |

- **Why Turso over Supabase (Postgres):** Turso is API-compatible with SQLite. The codebase can use `libsql-experimental` as a drop-in driver for SQLAlchemy async, meaning near-zero refactoring. Supabase would require a full Postgres driver and schema migration via Alembic, adding Sprint 0 complexity.
- **Why Turso over Render Postgres (free):** Render's free Postgres **expires and is deleted after 30 days**. Turso free tier has no expiration.
- **Encryption at Rest:** Turso encrypts data by default. This directly resolves the PRD encryption requirement (REQ-012) without any SQLCipher implementation effort.
- **Migration Path:** When users exceed ~1K active, Turso's `ATTACH` migration or a pg_dump-equivalent export to Supabase/PostgreSQL is clean. The SQLAlchemy ORM layer means the application code requires no changes — only the connection string.

### 4. AI & Orchestration Layer — Raw asyncio

- **Why not LangChain/LangGraph:** For 3 agents in a fixed DAG (`Gatekeeper → Persona → Memory`), LangGraph adds dependency weight and debugging complexity with no topological benefit. Raw `asyncio` with Pydantic models is explicit, testable, and zero-overhead.
- **Escalation checkpoint:** If agent routing becomes dynamic (e.g., conditional Gatekeeper bypasses, multi-step memory queries), migrate to LangGraph at Sprint 2+.
- **Gemini 2.5 Flash:** Free tier is generous. `response_schema` parameter directly accepts a Pydantic model class, enforcing the AI Structured Output format (PRD §3.4) at the SDK level before it hits application code.
- **Groq fallback:** Llama-3.1-8b on Groq is free and returns responses in ~200ms. It is structurally simpler (less instruction-following) than Gemini, so the fallback persona behavior will be slightly degraded — acceptable for an error state (REQ-011).

### 5. Authentication — Auth.js v5

- Mandated by both PRD (REQ-007) and PRINCIPLES (Principle 1).
- Self-hosted within Next.js, zero cost, supports OAuth2 and Email/Password credentials.
- **Token passing to FastAPI:** Auth.js session JWT must be verified on the FastAPI side via a shared `AUTH_SECRET` environment variable using `python-jose`. This is a non-trivial integration detail to plan in Sprint 0.

---

## 🚨 Critical Risks & Mitigations

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| 1 | **Render cold starts (~30s)** break chat UX | High | `/health` keep-alive cron via [cron-job.org](https://cron-job.org) (free). Ping every 10 min. |
| 2 | **Auth.js JWT verification in FastAPI** | Medium | Use `python-jose` to decode the Auth.js JWT on every protected route. Validate `AUTH_SECRET` env var is shared between services. |
| 3 | **Groq fallback persona degradation** | Low | Fallback only triggers on Gemini timeout/error. Log all fallback events. User message: "Sorry, I'm feeling a bit sleepy. Can we chat in a minute?" (REQ-011). |
| 4 | **Turso write limits (10M rows/month)** | Low | MVP at 50 msg/day/user (REQ-010): 10M writes = ~200K active users. This is far beyond MVP scale. No action needed. |
| 5 | **Supabase inactivity pause** | — | *(Supabase was considered but rejected. Turso has no inactivity pause on free tier.)* |

---

## 📦 Full Dependency List

### Frontend (`/frontend`)

| Package | Purpose |
|---|---|
| `next` | Framework |
| `react`, `react-dom` | UI rendering |
| `typescript` | Type safety |
| `tailwindcss` | Styling |
| `next-auth` (Auth.js v5) | Authentication |
| `@tanstack/react-query` | Server state / chat cache |

### Backend (`/backend`)

| Package | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `pydantic[email]` v2 | Data validation & AI schema |
| `google-generativeai` | Gemini SDK |
| `groq` | Groq SDK (fallback) |
| `libsql-experimental` | Turso (libSQL) async driver |
| `sqlalchemy[asyncio]` | ORM |
| `alembic` | Schema migrations |
| `python-jose[cryptography]` | Auth.js JWT verification |
| `slowapi` | Rate limiting (REQ-010) |

---

## 💰 Zero-Cost Verification

| Service | Free Tier | Hard Limit |
|---|---|---|
| Vercel | Hobby (unlimited deploys) | 100GB bandwidth/month |
| Render | Free web service | Spins down after 15 min idle |
| Turso | 5GB, 500M reads/month | 10M writes/month |
| Gemini 2.5 Flash | 1M tokens/min, 1500 req/day | Rate limit → fall to Groq |
| Groq | Free (Llama-3.1-8b) | ~30 req/min |
| Auth.js | Self-hosted, $0 | N/A |

✅ **Total infrastructure cost at MVP scale: $0/month**
