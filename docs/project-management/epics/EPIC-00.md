# EPIC-00: Infrastructure & Project Setup

- **Status:** In Progress
- **Priority:** P0 - Critical Path
- **Source requirement:** PRD-v1.md, ARCHITECTURE.md
- **Impacted domains:** Platform, Infrastructure, All Modules

---

## Summary

Establish the foundational infrastructure, project structure, and documentation standards that enable all subsequent development. This epic creates the technical and organizational bedrock upon which all other epics will be built, ensuring architectural consistency, team alignment, and operational readiness from day one. This epic is unique in that it is not a user-facing feature but rather the **enabling platform** that makes all other epics possible.

---

## Current State / Gap

- **Implemented:** Documentation structure and architectural guidelines (PRD, ARCHITECTURE.md, TECHSTACK.md, PRINCIPLES.md).
- **Missing:** Physical code structure for FastAPI backend, Next.js frontend, database connections, worker processes, CI/CD pipelines, and code quality tooling. No development environment setup exists yet.

---

## Problem / Opportunity

Without a solid infrastructure foundation, feature development will be inconsistent, slow, and prone to technical debt. The team needs a clear "how to build" framework before implementing user-facing features. Starting feature work without this foundation would lead to architectural drift, integration issues, and costly rework.

---

## Desired Outcome

After this epic is complete, any developer should be able to:
- Clone the repository and run the full development environment with a single command
- Follow established patterns to add new features consistently
- Rely on automated code quality checks and CI/CD pipelines
- Understand architectural decisions through documented ADRs

This outcome matters because it reduces onboarding time from days to hours and ensures all future development follows a coherent architecture.

---

## Users / Use Cases

- **Primary users:** Development team (backend, frontend, full-stack engineers)
- **Main use cases:**
  - Local development environment setup
  - Code quality enforcement (linting, formatting, type checking)
  - Automated testing and deployment
  - Database schema management
  - Background task processing
- **Important edge cases:**
  - New team member onboarding
  - Environment variable management across dev/staging/prod
  - Handling database migrations safely

---

## Scope

### In scope

- ✅ Project documentation architecture (PRD, Architecture, Tech Stack, Principles)
- ✅ Architecture decision records (ADRs) framework and process
- ✅ Development environment setup and standards
- ✅ CI/CD pipeline foundation (build, test, deploy)
- ✅ Code quality gates (linting, formatting, type checking)
- ✅ Repository structure and organization patterns
- ✅ Environment separation (dev, staging, prod)
- ✅ Initial FastAPI backend project skeleton
- ✅ Initial Next.js web application skeleton
- ✅ Database schema design and migration framework (Alembic)
- ✅ Redis configuration and connection patterns
- ✅ Taskiq worker process setup and patterns
- ✅ Test framework setup (unit, integration)
- ✅ Environment configuration management (12-factor app)
- ✅ Secrets management strategy (not implementation of actual secrets)

### Out of scope

- ❌ Actual authentication implementation (EPIC-01)
- ❌ Production user-facing features (EPIC-02+)
- ❌ Database provisioning in cloud environments (configuration only)
- ❌ SSL/TLS certificate management
- ❌ Monitoring dashboards (configuration patterns only, not full implementation)

---

## Capability Slices

- **Slice 1: Project Skeletons** — FastAPI backend structure, Next.js frontend structure, module boundaries
- **Slice 2: Data Layer** — PostgreSQL connection, Redis connection, Alembic migrations, repository pattern
- **Slice 3: Worker Infrastructure** — Taskiq setup, background task patterns, queue management
- **Slice 4: Code Quality & CI/CD** — Linting, formatting, type checking, GitHub Actions pipelines, pre-commit hooks
- **Slice 5: Documentation & Standards** — ADR framework, setup guides, architecture documentation

---

## Facts / Assumptions / Constraints / Unknowns

- **Facts:**
  - Python 3.12+ and Node.js 18+ are required runtimes
  - PostgreSQL 16 and Redis 7 are the chosen data stores
  - Modular monolith pattern is the architectural decision
- **Assumptions:**
  - Team members have access to required development tools
  - Local development can use Docker for database services
  - GitHub is the version control and CI/CD platform
- **Constraints:**
  - Must follow 12-factor app principles
  - Must support async/await patterns throughout
  - Must maintain clear module boundaries (no circular dependencies)
- **Unknowns:**
  - Exact production hosting provider (Render vs Railway vs Fly.io)
  - Final database connection pool sizes for production

---

## Proposed Solution

Implement a modular monolith with physical separation at deployment. The structure will be:

```
nudgeen-platform/
├── web/                          # Next.js frontend
├── api/                          # FastAPI backend
├── workers/                      # Taskiq workers
├── docker-compose.yml            # Local development
└── docs/                         # Project documentation
```

Key architectural decisions:
- PostgreSQL as single source of truth (async SQLAlchemy)
- Redis for queue transport, caching, and rate limiting only
- Taskiq for background job processing
- Alembic for database migrations
- GitHub Actions for CI/CD
- Ruff (backend) and ESLint/Prettier (frontend) for code quality

Tradeoffs:
- Chose managed services over self-hosted for production (faster setup, less ops overhead)
- Chose async-first patterns (better scalability, slight complexity increase)
- Chose modular monolith over microservices (simpler deployment, easier refactoring later)

---

## Dependencies / Rollout / Risks

### Dependencies

- **External:**
  - Python 3.12+ runtime
  - Node.js 18+ runtime
  - PostgreSQL 16 (managed or local)
  - Redis 7 (managed or local)
  - No external API keys required for setup

- **Internal:**
  - None — this is the foundational epic

### Rollout notes

- Rollout is internal (developer-facing), not user-facing
- All components should be functional in local development first
- Staging environment setup deferred to EPIC-05

### Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Over-engineering initial structure | Delay | Medium | Keep initial implementation minimal, iterate based on needs |
| Inconsistent patterns across modules | Technical debt | High | Enforce via code review and linter rules |
| Local development complexity | Slow onboarding | Medium | Well-documented setup, Docker for consistency |
| Team disagreement on architecture | Rework | Low | ADR process for major decisions |

---

## Epic Done Criteria

- [ ] FastAPI project skeleton with proper module structure exists
- [ ] Next.js project with TypeScript and Auth.js initialized
- [ ] PostgreSQL and Redis connections working locally
- [ ] Database migration framework operational (Alembic)
- [ ] Taskiq worker skeleton with example task functional
- [ ] Module boundaries documented in ARCHITECTURE.md
- [ ] Development environment runs with single command (`docker-compose up` or equivalent)
- [ ] Code quality tools configured and passing (lint, format, type check)
- [ ] CI pipeline runs tests and checks on PRs
- [ ] Environment configuration uses 12-factor pattern
- [ ] Initial core database tables created via migrations
- [ ] Repository pattern examples documented
- [ ] ADR-001 created (architecture decision record template)
- [ ] Project README with setup instructions complete

---

## Task Writer Handoff

- **Epic slug:** EPIC-00
- **Epic file path:** `docs/project-management/epics/EPIC-00.md`
- **Original requirement:** PRD-v1.md infrastructure requirements
- **Epic summary:** Foundational infrastructure and project setup
- **Impacted domains:** Platform, Infrastructure, All Modules
- **Desired outcome:** Developer can clone repo and run full environment with one command
- **In-scope outcomes:** Project skeletons, database setup, worker setup, CI/CD, code quality
- **Non-goals:** User-facing features, authentication flows, AI integration
- **Capability slices:** 5 slices (skeletons, data layer, workers, CI/CD, documentation)
- **Facts:** Python 3.12+, Node.js 18+, PostgreSQL 16, Redis 7, modular monolith
- **Assumptions:** Team has dev tools, Docker for local DB, GitHub for CI/CD
- **Constraints:** 12-factor, async-first, clear module boundaries
- **Unknowns:** Production host provider, exact pool sizes
- **Proposed solution summary:** Modular monolith with FastAPI + Next.js + Taskiq + PostgreSQL + Redis
- **Dependencies:** None (foundational epic)
- **Rollout notes:** Internal developer-facing rollout
- **Risks:** Over-engineering, inconsistent patterns, dev complexity
- **Task splitting hints:** Split by technical layer (skeleton → database → workers → CI/CD → docs)
- **Validation expectations:** All acceptance criteria must be testable with binary pass/fail

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-26 | System | Initial version based on project documentation analysis |
| 2.0 | 2026-04-27 | Assistant | Standardized to epic-template.md format |
