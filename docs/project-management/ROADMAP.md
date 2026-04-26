# NudgeEn Project Roadmap

## 🎯 Product Vision

Build an AI chatbot that acts as a real friend in a messaging interface to improve daily English reading and writing skills for non-native speakers.

---

## 🏛 Epics (High-Level Goals)

| ID | Title | Focus | Status |
| :--- | :--- | :--- | :--- |
| **EPIC-00** | Infrastructure & Project Setup | CI/CD, Documentation, Env | [/] In Progress |
| **EPIC-01** | Security, Auth & Guardrails | Auth.js (Social & Credentials), PII scrubbing | [ ] Pending |
| **EPIC-02** | Core Messaging Interface | Chat UI, Bubble System, Latency | [ ] Pending |
| **EPIC-03** | AI Persona & Memory Engine | Profile extraction, Vibe maintenance | [ ] Pending |
| **EPIC-04** | Pedagogical Layer (Corrections) | Subtle JSON-based feedback | [ ] Pending |
| **EPIC-05** | Cloud Deployment | Vercel & Backend Hosting | [ ] Pending |

---

## 🏃 Active Sprint

- **[Sprint 0: Core Foundation](file:///d:/Persional_Projects/NudgeEn/docs/project-management/sprint-0/README.md)** (Infrastructure & PRD Setup)
  - *Fulfills: EPIC-00*

## 📋 Future Sprints (Backlog)

- [ ] **[Sprint 1: The Gateway](file:///d:/Persional_Projects/NudgeEn/docs/project-management/sprint-1/README.md)** (Auth + UI + Basic API)
  - *Fulfills: EPIC-01, EPIC-02*
  - Initialize **Auth.js** with Social (Google/GitHub) + **Credentials (Email/Password)**.
  - Basic Chat UI & **Gemini 2.5 Flash** + **Groq API (Fallback)** connectivity.
- [ ] **Sprint 2: The Brain (Memory + Calibration)**
  - *Fulfills: EPIC-01, EPIC-03*
  - 3-turn Calibration flow & SQLite Memory storage.
  - **Gatekeeper Agent** safety prompt.
- [ ] **Sprint 3: The Teacher (Pedagogical Layer)**
  - *Fulfills: EPIC-04*
  - Structured JSON corrections & ✨ Sparkle Icon UI.
- [ ] **Sprint 4: The Launch (Deployment & Stats)**
  - *Fulfills: EPIC-04, EPIC-05*
  - Weekly progress cards.
  - Production deployment to **Vercel & Railway**.
- [ ] **Sprint 5: The Fortress (Hardening & Beta)**
  - *Fulfills: EPIC-01, EPIC-02*
  - LLM-as-a-Judge regression testing.
  - Pen-testing & final UX polish.
