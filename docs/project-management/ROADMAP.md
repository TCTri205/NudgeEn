# NudgeEn Project Roadmap

## Product Vision

Build an AI chatbot that feels like a real messaging friend and helps users improve daily English reading and writing through natural conversation.

---

## Epics (High-Level Goals)

| ID | Title | Focus | Status |
| --- | --- | --- | --- |
| **EPIC-00** | Infrastructure & Project Setup | CI/CD, architecture baseline, documentation, environments | [/] In Progress |
| **EPIC-01** | Security, Auth & Guardrails | Auth.js, credentials, OAuth, safety controls | [ ] Pending |
| **EPIC-02** | Core Messaging Interface | Chat UI, streaming, conversation persistence | [ ] Pending |
| **EPIC-03** | AI Persona & Memory Engine | Vibe, memory extraction, user profile | [ ] Pending |
| **EPIC-04** | Pedagogical Layer | Subtle corrections, progress cards, learning metrics | [ ] Pending |
| **EPIC-05** | Production Readiness | Deployment, observability, reliability, scaling | [ ] Pending |

---

## Active Sprint

- **Sprint 0: Core Foundation** ([sprint-0/README.md](./sprint-0/README.md))
  - *Fulfills: EPIC-00*

## Future Sprints (Backlog)

- [ ] **Sprint 1: Scalable Gateway** ([sprint-1/README.md](./sprint-1/README.md))
  - *Fulfills: EPIC-01, EPIC-02*
  - Initialize Auth.js with PostgreSQL adapter.
  - Provision Redis and bootstrap **Taskiq Workers** skeleton.
  - Deliver initial chat UI and API connectivity.
- [ ] **Sprint 2: The Brain**
  - *Fulfills: EPIC-03*
  - Implement onboarding vibe check.
  - Build memory extraction pipeline in workers.
  - Add gatekeeper and profile projection update flow.
- [ ] **Sprint 3: The Teacher**
  - *Fulfills: EPIC-04*
  - Deliver structured corrections and Sparkle Icon UX.
  - Generate weekly progress cards.
- [ ] **Sprint 4: Production Readiness**
  - *Fulfills: EPIC-05*
  - Deploy web, API, worker, Postgres, and Redis environments.
  - Add observability, retry policies, and failure dashboards.
- [ ] **Sprint 5: Hardening & Beta**
  - *Fulfills: EPIC-01, EPIC-02, EPIC-05*
  - LLM-as-a-Judge regression testing.
  - Load testing, security review, and final UX polish.
