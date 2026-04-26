# EPIC-00: Infrastructure & Project Setup

**Focus:** CI/CD, architecture baseline, documentation, environments  
**Status:** In Progress  
**Sprint:** Sprint 0 (Core Foundation)  
**Priority:** P0 - Critical Path

---

## Epic Description

Establish the foundational infrastructure, project structure, and documentation standards that enable all subsequent development. This epic creates the technical and organizational bedrock upon which all features will be built, ensuring architectural consistency, team alignment, and operational readiness from day one.

This epic is unique in that it is not a user-facing feature but rather the **enabling platform** that makes all other epics possible. It defines *how* we build, *where* we deploy, *what* patterns we follow, and *why* we make certain architectural choices.

---

## Business Value

- **Reduces Delivery Risk:** Clear architecture and patterns prevent costly rework and architectural drift.
- **Accelerates Onboarding:** Comprehensive documentation allows new team members to become productive quickly.
- **Ensures Consistency:** Single source of truth for technical decisions prevents conflicting implementations.
- **Enables Scalability:** Proper initial architecture supports growth without major rewrites.

---

## Scope

### In Scope

- ✅ Project documentation architecture (PRD, Architecture, Tech Stack, Principles)
- ✅ Architecture decision records (ADRs) framework and process
- ✅ Development environment setup and standards
- ✅ CI/CD pipeline foundation (build, test, deploy)
- ✅ Code quality gates (linting, formatting, type checking)
- ✅ Repository structure and organization patterns
- ✅ Environment separation (dev, staging, prod)
- ✅ Initial FastAPI backend project skeleton
- ✅ Initial Next.js web application skeleton
- ✅ Database schema design and migration framework
- ✅ Redis configuration and connection patterns
- ✅ Taskiq worker process setup and patterns
- ✅ Test framework setup (unit, integration)
- ✅ Environment configuration management (12-factor app)
- ✅ Secrets management strategy (not implementation of actual secrets)

### Out of Scope

- ❌ Actual authentication implementation (EPIC-01)
- ❌ Production user-facing features (EPIC-02+)
- ❌ Database provisioning in cloud environments (configuration only)
- ❌ SSL/TLS certificate management
- ❌ Monitoring dashboards (configuration patterns only, not full implementation)

---

## Key Requirements

### REQ-INF-01: Architecture Baseline

**From:** PRD-v1.md, ARCHITECTURE.md

- Establish modular monolith pattern with physical separation at deployment
- Define clear module boundaries: auth, chat, persona, guardrails, memory, pedagogy, billing_or_limits, platform
- Document dependency rules between modules
- Establish PostgreSQL as single source of truth
- Establish Redis for queue transport, caching, and rate limiting only

### REQ-INF-02: Development Environment

- Python 3.12+ with FastAPI base project
- Next.js TypeScript project with Auth.js shell
- Local development with Docker or equivalent for PostgreSQL and Redis
- Hot reload for both frontend and backend
- Environment variable management (.env schema)

### REQ-INF-03: Code Quality

- ESLint and Prettier for frontend
- Ruff for backend
- TypeScript strict mode enabled
- Type checking in CI pipeline
- Pre-commit hooks for formatting and linting

### REQ-INF-04: Database Schema Framework

- SQLAlchemy async ORM setup
- Alembic for migrations
- Initial schema for: users, accounts, sessions, conversations, messages
- Repository pattern implementation examples
- Connection pooling configuration (PgBouncer pattern)

### REQ-INF-05: Queue and Worker Framework

- Taskiq with Redis broker configuration
- Worker process structure and patterns
- Job idempotency patterns
- Retry policy configuration
- Dead-letter queue patterns

### REQ-INF-06: Documentation Standards

- ADR template and process
- API documentation standards (OpenAPI/Swagger)
- Code documentation standards
- Architecture decision tracking
- Changelog maintenance process

---

## Technical Design

### Component Architecture

```
nudgeen-platform/
├── web/                          # Next.js frontend
│   ├── src/
│   │   ├── app/                  # App Router pages
│   │   ├── components/           # Reusable UI components
│   │   ├── lib/                  # API clients, utilities
│   │   └── middleware.ts         # Auth and routing
│   ├── package.json
│   └── ...
│
├── api/                          # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # Application factory
│   │   ├── core/                 # Platform layer
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   └── logging.py
│   │   ├── modules/              # Feature modules
│   │   │   ├── auth/
│   │   │   ├── chat/
│   │   │   ├── persona/
│   │   │   └── ...
│   │   └── tests/
│   ├── alembic/                  # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
│
├── workers/                      # Taskiq workers
│   ├── app/
│   │   ├── tasks/
│   │   │   ├── memory.py
│   │   │   ├── summaries.py
│   │   │   └── analytics.py
│   │   └── worker.py
│   └── ...
│
├── docker-compose.yml            # Local development
├── docker-compose.prod.yml       # Production setup
├── docs/                         # Project documentation
└── .github/workflows/            # CI/CD pipelines
```

### Module Dependency Rules

**Allowed Dependencies:**

- Any module → `platform` (config, logging, DB, etc.)
- Application services → Multiple modules (orchestration)

**Prohibited Dependencies:**

- Module A → Module B's database tables (bypassing domain layer)
- Direct table writes across module boundaries
- Circular dependencies between modules

### Database Design

**Core Tables (Initial):**

```sql
-- users: Identity and account information
-- sessions: Auth.js session management
-- conversations: Chat thread metadata
-- messages: Individual chat messages (immutable)
-- user_profiles: Current user state projection
-- user_memories: Extracted memory facts
```

**Naming Conventions:**

- Tables: plural, snake_case (`user_profiles`)
- Columns: snake_case (`created_at`, `user_id`)
- Indexes: `idx_{table}_{column}`
- Foreign keys: `{referenced_table}_id`

### Queue Design

**Redis Usage Pattern:**

```python
# Taskiq broker configuration
broker = RedisBroker(url="redis://redis:6379/0")

# Queue separation
@broker.task(queue="realtime")
async def light_job():
    ...

@broker.task(queue="heavy")
async def llm_extraction():
    ...
```

**Worker Process Model:**

- Separate process from API
- Horizontal scaling via multiple worker instances
- Connection pooling to PostgreSQL
- Graceful shutdown handling

---

## Acceptance Criteria

### Must Have

- [ ] FastAPI project skeleton with proper structure
- [ ] Next.js project with TypeScript and Auth.js initialized
- [ ] PostgreSQL and Redis connection examples working locally
- [ ] Database migration framework operational (Alembic)
- [ ] Taskiq worker skeleton with example task
- [ ] Module boundaries documented in ARCHITECTURE.md
- [ ] Development environment runs with single command
- [ ] Code quality tools configured (lint, format, type check)
- [ ] CI pipeline runs tests and checks on PRs
- [ ] Environment configuration uses 12-factor pattern
- [ ] Initial core database tables created
- [ ] Repository pattern examples for core tables
- [ ] ADR-001 created (architecture decision record template)
- [ ] Project README with setup instructions

### Should Have

- [ ] Docker Compose for local development
- [ ] Pre-commit hooks configured
- [ ] Database seed script for local testing
- [ ] API health check endpoint
- [ ] Basic OpenAPI documentation generated
- [ ] Git commit message conventions documented
- [ ] Branch naming strategy defined

### Could Have

- [ ] GitHub Actions workflow templates
- [ ] Database backup/restore scripts
- [ ] Load testing setup
- [ ] Initial frontend component library (shadcn/ui)

### Won't Have (This Epic)

- ❌ User authentication flows (EPIC-01)
- ❌ Chat interface (EPIC-02)
- ❌ AI integration (EPIC-03)
- ❌ Memory extraction (EPIC-03)
- ❌ Correction system (EPIC-04)

---

## Dependencies

### External Dependencies

- Python 3.12+ runtime
- Node.js 18+ runtime
- PostgreSQL 16 (managed or local)
- Redis 7 (managed or local)
- No external API keys required for setup

### Internal Dependencies

- None - this is the foundational epic

---

## Timeline & Milestones

**Sprint 0: Core Foundation** (2026-04-26 - 2026-05-10)

| Milestone | Target Date | Deliverable |
|-----------|-------------|-------------|
| M1 | 2026-04-28 | Documentation structure normalized |
| M2 | 2026-04-30 | FastAPI and Next.js skeletons created |
| M3 | 2026-05-03 | Database and queue frameworks configured |
| M4 | 2026-05-06 | Development environment fully functional |
| M5 | 2026-05-08 | Code quality and CI pipeline operational |
| M6 | 2026-05-10 | Epic-00 acceptance criteria met |

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Over-engineering initial structure | Delay | Medium | Keep initial implementation minimal, iterate based on needs |
| Inconsistent patterns across modules | Technical debt | High | Enforce via code review and linter rules |
| Local development complexity | Slow onboarding | Medium | Well-documented setup, Docker for consistency |
| Team disagreement on architecture | Rework | Low | ADR process for major decisions |

---

## Success Metrics

- **Time to First Commit:** < 2 hours for new developer
- **CI Pipeline Success Rate:** > 95%
- **Code Review Turnaround:** < 24 hours
- **Architecture Decision Documentation:** 100% of major decisions captured in ADRs
- **Local Dev Environment Success Rate:** > 90% on first attempt

---

## Out of Scope for This Epic

The following will be addressed in their respective epics:

- **EPIC-01:** Authentication implementation, OAuth providers, Auth.js configuration
- **EPIC-02:** Frontend chat UI, message components, typing indicators
- **EPIC-03:** AI provider integration, memory extraction, persona engine
- **EPIC-04:** Correction generation, progress cards, learning analytics
- **EPIC-05:** Production deployment, observability dashboards, scaling configuration

---

## References

- [PRD-v1.md](../../PRD-v1.md) - Product requirements
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - Canonical architecture
- [TECHSTACK.md](../../TECHSTACK.md) - Technology choices and rationale
- [PRINCIPLES.md](../../PRINCIPLES.md) - Core design principles
- [ONBOARDING.md](../../ONBOARDING.md) - Team onboarding guide

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-26 | System | Initial version based on project documentation analysis |
