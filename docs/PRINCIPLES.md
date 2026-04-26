# NudgeEn Core Principles

## 1. Optimized Scaling & Robustness

- **Principle:** Prefer architectures that preserve data delivery and concurrency safety over short-term simplicity.
- **Goal:** Build a system that remains stable as traffic and background processing grow.
- **Implementation:** Use **PostgreSQL** for durable data and **Redis + workers** for asynchronous workloads.

## 2. Pedagogy as a Sidekick

- **Principle:** Learning should be non-intrusive.
- **Goal:** Preserve the "friendship vibe" instead of making the experience feel like a test.
- **Implementation:** Use the **Sparkle Icon** for subtle feedback.

## 3. Privacy by Design

- **Principle:** User data is valuable and must be minimized and scrubbed.
- **Goal:** Support memory without storing unnecessary sensitive PII.
- **Implementation:** The memory pipeline must scrub PII before persistence.

## 4. Physical Separation of Concerns

- **Principle:** Decouple the user-facing response path from heavy background processing.
- **Goal:** Ensure typing indicators and streamed replies are never blocked by memory extraction or analytics jobs.
- **Implementation:** Use **Taskiq Workers + Redis** to move heavy tasks to dedicated background processes.

## 5. Single Source of Truth

- **Principle:** Architectural intent must be consistent across product, platform, and delivery documentation.
- **Goal:** Eliminate drift such as conflicting database or deployment choices.
- **Implementation:** Treat `docs/ARCHITECTURE.md` as the canonical runtime architecture document.

## 6. Logical Mapping

- **Principle:** Planning artifacts should be easy to navigate and align with implementation boundaries.
- **Goal:** Reduce delivery confusion for a small team.
- **Implementation:** Keep epics, sprints, ADRs, and architecture docs mutually consistent.
