# Task Template

Use this template for every implementation task. The file is saved as
`<task-slug>.md` directly inside its kanban folder (`backlog/`, `sprint-N/todo/`, etc.).

```md
## <Task Title>

- Status:        # backlog | todo | in-progress | in-review | done — must match parent folder
- Sprint:        # integer (e.g. 3) or `backlog`
- Assignee:
- Domain:        # frontend | backend | infra | ai
- Priority:      # P0 | P1 | P2 | P3
- Assumptions:
- Affected areas:

### Current State / Existing System

Describe the relevant part of the current system, module, flow, or architecture that this task
will change or depend on. Plain language. The reader should quickly understand what already
exists and what is still missing.

### Context / Problem

Describe where the pain or gap appears, what is failing or missing today, and why this task
exists in this domain. Focus on the actual problem caused by the current state.

### Why This Is Needed

Why the task matters for the product, system, users, delivery flow, or architecture.

### Scope

- In scope:
- Out of scope:

### Dependencies / Parallelism

- Depends on task(s):    # task slugs only, e.g. be-001-idp-jwt-middleware
- Can run in parallel with task(s):
- Sequencing notes:

### Rules / Constraints

- Architectural rules that must be respected
- Data ownership or state ownership rules
- UX, performance, security, or operational constraints
- Library, framework, or integration boundaries

### What Needs To Be Built

A concrete description of the expected implementation scope.

### Proposal

The recommended implementation approach for this domain, including the main design choices and
why they are preferred.

### Implementation Breakdown

- Step 1
- Step 2
- Step 3

### Goal

Describe the end state that must be true when this task is complete. Measurable and easy to
verify.

### Acceptance Criteria

- [ ] Outcome statement 1
- [ ] Outcome statement 2
- [ ] Outcome statement 3

### Test Cases

- [ ] Happy path verification
- [ ] Failure path or edge-case verification
- [ ] Regression / integration / domain-specific verification

### Risks / Open Questions

- Risk:
- Open question:
```

## Notes

- Each major prose section should contain enough detail that the task can stand on its own.
- Prefer 2–5 strong bullets or a short dense paragraph per section instead of one vague sentence.
- Keep metadata lines compact. Use them as short references, not as mini-paragraphs.
- **`Status` must match the parent kanban folder name.** New tasks land in `todo/` (sprint case)
  or `backlog/`. To change status, *move the file* — do not just edit `Status:`.
- **Filename = `<task-slug>.md`**, e.g. `be-001-idp-jwt-middleware.md`. No per-task subfolder.
- File location:
    - sprint-scoped: `docs/project-management/ticket/sprint-<N>/todo/<task-slug>.md`
    - unassigned to a sprint: `docs/project-management/ticket/backlog/<task-slug>.md`
- `Depends on task(s)` should be task slugs only, e.g. `be-001-idp-jwt-middleware`.
- Acceptance criteria must be objectively checkable.
- Acceptance criteria should describe observable outcomes, not implementation activity.
- Test cases should match the domain:
    - frontend: UI behavior, accessibility, loading/error states
    - backend: API contracts, persistence, authorization, failure modes
    - infra: deploy health, env config, observability, rollback
    - AI: eval cases, prompt behavior, fallback paths, cost or safety checks
- Test cases should cover happy path, failure path, and regression risk.
- Split tasks whenever one domain can move independently.
- `Goal` should describe the final state, while `Proposal` explains how to get there.
- `Rules / Constraints` captures the non-negotiables an engineer must not violate.
- `Current State` explains what exists today.
- `Context / Problem` explains why the current state is not good enough.
