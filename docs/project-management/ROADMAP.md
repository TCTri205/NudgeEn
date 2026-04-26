# NudgeEn Project Roadmap

## Product Vision

Build an AI chatbot that feels like a real messaging friend and helps users improve daily English reading and writing through natural conversation.

---

## Epics (High-Level Goals)

| ID | Title | Focus | Status |
| --- | --- | --- | --- |
| **EPIC-00** | Infrastructure & Project Setup | CI/CD, architecture baseline, documentation, environments | [x] Completed |
| **EPIC-01** | Security, Auth & Guardrails | Auth.js, credentials, OAuth, safety controls | [ ] Pending |
| **EPIC-02** | Core Messaging Interface | Chat UI, streaming, conversation persistence | [ ] Pending |
| **EPIC-03** | AI Persona & Memory Engine | Vibe, memory extraction, user profile | [ ] Pending |
| **EPIC-04** | Pedagogical Layer | Subtle corrections, progress cards, learning metrics | [ ] Pending |
| **EPIC-05** | Production Readiness | Deployment, observability, reliability, scaling | [ ] Pending |

---

## Active Sprint

- **Sprint 0: Core Foundation** ([sprint-0/README.md](./sprint-0/README.md))
  - *Fulfills: EPIC-00*
  - Tickets: [TICKET-01](./sprint-0/TICKET-01.md), [TICKET-02](./sprint-0/TICKET-02.md), [TICKET-03](./sprint-0/TICKET-03.md), [TICKET-04](./sprint-0/TICKET-04.md), [TICKET-05](./sprint-0/TICKET-05.md), [TICKET-06](./sprint-0/TICKET-06.md)

## Future Sprints (Backlog)

- [ ] **Sprint 1: Scalable Gateway** ([sprint-1/README.md](./sprint-1/README.md))
  - *Fulfills: EPIC-01, EPIC-02*
  - Tickets: [TICKET-07](./sprint-1/TICKET-07.md) - [TICKET-22](./sprint-1/TICKET-22.md)
  - Initialize Auth.js with PostgreSQL adapter.
  - Provision Redis and bootstrap **Taskiq Workers** skeleton.
  - Deliver initial chat UI and API connectivity.
- [ ] **Sprint 2: The Brain** ([sprint-2/README.md](./sprint-2/README.md))
  - *Fulfills: EPIC-03*
  - Tickets: [TICKET-23](./sprint-2/TICKET-23.md) - [TICKET-33](./sprint-2/TICKET-33.md)
  - Implement onboarding vibe check.
  - Build memory extraction pipeline in workers.
  - Add gatekeeper and profile projection update flow.
- [ ] **Sprint 3: The Teacher** ([sprint-3/README.md](./sprint-3/README.md))
  - *Fulfills: EPIC-04*
  - Tickets: [TICKET-34](./sprint-3/TICKET-34.md) - [TICKET-42](./sprint-3/TICKET-42.md)
  - Deliver structured corrections and Sparkle Icon UX.
  - Generate weekly progress cards.
- [ ] **Sprint 4: Production Readiness** ([sprint-4/README.md](./sprint-4/README.md))
  - *Fulfills: EPIC-05*
  - Tickets: [TICKET-43](./sprint-4/TICKET-43.md) - [TICKET-52](./sprint-4/TICKET-52.md)
  - Deploy web, API, worker, Postgres, and Redis environments.
  - Add observability, retry policies, and failure dashboards.
- [ ] **Sprint 5: Hardening & Beta** ([sprint-5/README.md](./sprint-5/README.md))
  - *Fulfills: EPIC-01, EPIC-02, EPIC-05*
  - Tickets: [TICKET-53](./sprint-5/TICKET-53.md) - [TICKET-56](./sprint-5/TICKET-56.md)
  - LLM-as-a-Judge regression testing.
  - Load testing, security review, and final UX polish.
