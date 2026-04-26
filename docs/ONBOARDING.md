# ONBOARDING - NudgeEn Project

Welcome to the NudgeEn team. This guide explains the minimum context needed before making changes.

## Quick Start

1. Clone the repository.
2. Read these documents first:
   - [PRD-v1.md](./PRD-v1.md)
   - [ARCHITECTURE.md](./ARCHITECTURE.md)
   - [TECHSTACK.md](./TECHSTACK.md)
3. Review [adr/](./adr/) for architectural decisions.
4. Check the current sprint in [project-management/](./project-management/).

## Current Architecture Direction

- **Web:** Next.js Web + Auth.js
- **API:** FastAPI API
- **Database:** PostgreSQL
- **Cache/Broker:** Redis
- **Queue/Worker:** Taskiq Workers
- **LLM:** Gemini 2.5 Flash primary, Groq fallback

## Working Model

- Next.js owns UI and authentication boundary.
- FastAPI owns chat orchestration and durable writes.
- Workers own asynchronous workloads such as memory extraction and weekly summaries.
- PostgreSQL is the source of truth.
- Redis is used for queue transport, caching, and rate limiting.

## Workflow

- **PRD:** Product intent and scope live in [PRD-v1.md](./PRD-v1.md).
- **Architecture:** Runtime and module design live in [ARCHITECTURE.md](./ARCHITECTURE.md).
- **ADRs:** Decision history lives in [adr/](./adr/).
- **Roadmap/Sprints:** Delivery planning lives in [project-management/](./project-management/).
- **Commits:** Use conventional commits such as `feat:`, `fix:`, `docs:`.
