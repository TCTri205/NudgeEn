# Domain Detection

Use this guide to decide which domain workers or skills must be involved.

## Frontend

Route work to frontend when the requirement touches:

- UI screens, routes, layouts, navigation
- forms, validation, client state, data fetching in the UI
- components, design systems, accessibility, rendering, hydration
- Next.js, React, Tailwind, shadcn/ui, TanStack React Query, Zustand

## Backend

Route work to backend when the requirement touches:

- APIs, controllers, route handlers, services, business logic
- database schema, persistence, queues, jobs, auth, permissions
- contracts between frontend and backend
- server-side validation, data modeling, transactional flows

## Infra

(Includes DevOps and CI/CD. Canonical token across this skill: `infra`.)

Route work to infra when the requirement touches:

- deployment, CI/CD, environments, secrets, networking
- containers, Kubernetes, Terraform, Helm, cloud services
- observability, alerts, scaling, runtime configuration
- release automation and operational readiness

## AI

Route work to AI when the requirement touches:

- prompts, models, evaluations, agents, tool use, RAG
- vector stores, retrieval flows, inference pipelines
- LLM safety, guardrails, cost controls, evaluation loops
- AI-assisted workflow orchestration

### AI vs Backend boundary

- **AI domain** owns prompt design, model selection, evaluation harnesses, RAG retrieval logic,
  guardrails, and cost/safety controls.
- **Backend domain** owns the FastAPI service, request/response contracts, persistence of AI
  outputs, auth/permissions around AI calls, and queue/job plumbing — even when the handler
  internally calls Anthropic.
- A FastAPI endpoint that *invokes* an LLM with a fixed prompt is backend.
- Designing or tuning the prompt, eval set, or retrieval pipeline behind that endpoint is AI.
- When both apply, split into two tasks: one AI (prompt + eval) and one backend (endpoint + wiring).

## Cross-domain patterns

- A new frontend screen backed by a new API usually means frontend + backend.
- A feature requiring queues, jobs, or deployment changes usually means backend + infra.
- An AI feature exposed in the product UI usually means AI + backend + frontend.
- If the requirement changes architecture or project structure, read `project/codebase.md` before
  finalizing domain routing.
