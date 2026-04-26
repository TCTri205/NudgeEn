---
name: task-writer
description: >
  Turn a requirement, epic, PRD, RFC, or bug report into implementation-ready engineering tasks
  and file them into the DevPath sprint kanban (`docs/project-management/ticket/`). Use when the
  user asks to break work into tasks, split scope by frontend/backend/infra/AI, route analysis to
  domain skills or subagents, and produce clear task documents with goals, proposals, acceptance
  criteria, and test checklists. **Sprint is auto-derived from the epic number**: epic
  `NN-<slug>` always maps to `sprint-N`. Non-epic inputs go to `backlog/`. The skill refuses to
  write across this mapping.
---

# Task Writer

This skill is the lead orchestration layer for turning one requirement or epic into many clear,
independent tasks, then filing each task as a kanban card under `docs/project-management/ticket/`.

The output should read like a mini-spec per task, not like short planning notes.

## Domain vocabulary

The canonical domain tokens used across this skill, the team, and every task are:
`frontend`, `backend`, `infra`, `ai`. Treat `devops`, `ci/cd`, `sre`, and `ops` as aliases that
collapse to `infra`. Always emit the canonical token in the task's `Domain:` field and when
matching team eligibility.

## Task storage (DevPath kanban)

All tasks created by this skill live under `docs/project-management/ticket/`.

```
docs/project-management/
├── epics/<epic-slug>/
│   ├── epic.md               # PRD — input to this skill, NOT touched by this skill
│   └── implementation-plan.md
└── ticket/
    ├── backlog/              # epic 00-* and non-epic inputs land here
    └── sprint-<N>/           # epic NN-* (N>0) lands here, derived from epic number
        ├── todo/             # initial status for new tickets
        ├── in-progress/
        ├── in-review/
        └── done/
```

**Rules:**

- One task = one file. Filename is `<task-slug>.md` (kebab-case, stable, e.g.
  `be-001-idp-jwt-middleware.md`). No per-task subfolder.
- **Status is encoded by the folder**, per `CLAUDE.md`. Moving the file IS the status update
  (`backlog → todo → in-progress → in-review → done`). The `Status:` metadata field is a snapshot
  and must match the folder name.
- **Where new tasks land — driven by the PRD-to-sprint mapping (see next section).** Never accept
  a sprint number from the user that contradicts the epic's number.
- **Never write into `done/`, `in-progress/`, or `in-review/`** — those are downstream states owned
  by the engineer working the ticket.
- **Do not modify or move existing tickets** unless the user explicitly asks for a status change.
- The `epics/<epic-slug>/` tree is read-only for this skill — read `epic.md` for context, never
  write tasks there.

## PRD-to-sprint mapping (enforced)

DevPath enforces **one PRD per sprint** via the epic numbering convention. The skill derives the
target sprint from the epic slug — the user does not choose it.

**Rule:** for an epic at `docs/project-management/epics/<NN>-<slug>/epic.md`, all generated tasks
go to `docs/project-management/ticket/sprint-<N>/todo/`, where `<N>` is the integer parsed from
`<NN>` (leading zero stripped — `01` → `1`, `02` → `2`).

**Examples:**

| Epic slug                               | Target folder                    |
|-----------------------------------------|----------------------------------|
| `01-foundation-onboarding-subscription` | `ticket/sprint-1/todo/`          |
| `02-job-search`                         | `ticket/sprint-2/todo/`          |
| `07-community`                          | `ticket/sprint-7/todo/`          |

**Edge cases — handle in this exact order:**

1. **Epic `00-*` (pre-sprint setup):** treated as backlog. Write to `ticket/backlog/`. There is no
   `sprint-0/`. Sprint planning has not started for these tasks.
2. **Epic number > highest existing sprint** (e.g. `08-*` or `09-*` when sprints only run 1–7):
   **stop and surface an error** to the user. Do NOT auto-create the sprint folder. Sprint
   creation is a planning decision, not a side effect of task generation. Suggested message:
   `Epic 08-... maps to sprint-8, which does not exist. Create docs/project-management/ticket/sprint-8/{todo,in-progress,in-review,done}/ first, or move work into an existing sprint by renumbering the epic.`
3. **Epic with no leading `NN-` prefix** (e.g. `hotfix-search-ranking`): treated as a non-epic
   input → write to `ticket/backlog/`.
4. **Non-epic input** (bug report, RFC, ad-hoc requirement not under `epics/`): write to
   `ticket/backlog/`.
5. **User supplies a sprint number that contradicts the derived sprint** (e.g. user says "put
   epic 02 tasks into sprint 4"): **refuse**. Surface the conflict and ask the user to either
   re-number the epic or move the epic folder. Do not silently honour either side.
6. **Target `sprint-<N>/` exists but `sprint-<N>/todo/` does not:** create the missing `todo/`
   subfolder (this is a normal kanban state, not a planning decision).

**One-PRD-per-sprint guarantee:** because the mapping is 1:1 and derived, two epics cannot land
in the same sprint folder. If you ever observe tickets from two different epics in one
`sprint-<N>/`, that is a hand-edited drift and out of scope for this skill to repair.

## Architecture context sources

This skill needs codebase awareness before splitting work. Read these in order and stop at the
first that answers the question:

1. `CLAUDE.md` (repository root) — DevPath stack, paths, and conventions.
2. `repo/web/CLAUDE.md` — frontend-specific conventions.
3. `docs/PRD-v1.md` — product requirements.
4. `docs/BACKEND-ARCHITECTURE.md` — FastAPI hex layers, Alembic rules.
5. Any `docs/ADR-*.md` relevant to the requirement.
6. The relevant `repo/web/` or `repo/api/` source directories for module-level detail.

Note any unresolved gaps in the resulting task's `Assumptions` field.

## Mandatory workflow

1. Read `references/task-template.md`, `references/team.md`, `references/domain-detection.md`,
   and this workflow before writing tasks.
2. Read the requirement and restate the problem in one short paragraph before splitting work.
3. **Resolve the target folder.** Apply the *PRD-to-sprint mapping*:
   a. If the input is an epic at `docs/project-management/epics/<NN>-<slug>/epic.md`, parse `<NN>`
      to derive `sprint-<N>` (strip leading zero).
   b. If `<NN>` is `00`, target = `ticket/backlog/`.
   c. If `sprint-<N>/` does not exist as a directory, **stop and report the error** — do not
      auto-create it.
   d. If `sprint-<N>/` exists but `sprint-<N>/todo/` does not, create `todo/`.
   e. If the input has no epic prefix or is not under `epics/`, target = `ticket/backlog/`.
   f. If the user supplies a sprint number that contradicts the derived sprint, **stop and report
      the conflict**. Do not proceed.
4. Read the architecture context sources above. Note gaps.
5. Detect the impacted domains using `references/domain-detection.md`.
6. Extract explicit facts, assumptions, constraints, and unknowns from the requirement.
7. For each detected domain, choose the best available domain skill or specialist:
    - `frontend` → `frontend-engineer` skill
    - `backend` → `backend-engineer` skill
    - `infra` → no dedicated skill installed; analyze directly per *Missing skill fallback*
    - `ai` → no dedicated skill installed; analyze directly per *Missing skill fallback*
8. If the requirement can be split into independent domains or parallel workstreams, use subagents.
   This is required, not optional, when parallel decomposition is possible and safe.
9. Split analysis into one subagent per domain or per independently parallelizable workstream. Give
   each subagent:
    - the original requirement
    - the relevant architecture context
    - the domain scope (canonical token)
    - the task template from `references/task-template.md`
10. Ask each domain worker to analyze only its own domain and return implementation-ready tasks,
    not generic advice.
11. Merge the domain outputs into independent tasks grouped by domain. If a task spans two
    domains, split it before continuing.
12. **Determine `Assignee` per finalized task** using `references/team.md`:
    a. Read the task's canonical `Domain` token.
    b. Filter eligible team members from `team.md`.
    c. Run `python .claude/skills/task-writer/scripts/count_open_tasks.py` from the repo root to
       get current `{assignee: open_count}` across `backlog/` plus every `sprint-*/todo/`,
       `in-progress/`, and `in-review/`. The script counts open tickets only — `done/` is
       excluded.
    d. Assign the eligible member with the lowest open count. Break ties by Lead > Engineer.
13. **Persist each task** to the target folder resolved in step 3:
    - `docs/project-management/ticket/sprint-<N>/todo/<task-slug>.md` (epic-driven), or
    - `docs/project-management/ticket/backlog/<task-slug>.md` (backlog).
    Set the `Status:` metadata to match the folder (`todo` or `backlog`). Set `Sprint:` to the
    integer `<N>` or to `backlog`.
14. **Update the sprint index** at `docs/project-management/ticket/sprint-<N>/README.md` (create if
    missing) with a row per new task: `| <task-slug> | <domain> | <assignee> | todo | <link> |`.
    For backlog tasks, update `docs/project-management/ticket/backlog/README.md` the same way.

## Required output shape

Every task must follow `references/task-template.md` and include:

- Metadata: `Status`, `Assignee`, `Domain`, `Priority`, `Sprint`, `Assumptions`, `Affected areas`
- `Current State / Existing System`
- `Context / Problem`
- `Why This Is Needed`
- `Scope` (with `In scope:` and `Out of scope:`)
- `Dependencies / Parallelism`
- `Rules / Constraints`
- `What Needs To Be Built`
- `Proposal`
- `Implementation Breakdown`
- `Goal`
- `Acceptance Criteria`
- `Test Cases`
- `Risks / Open Questions`

Include only when relevant: rollout/migration notes, feature-flag wiring, additional impacted
modules beyond `Affected areas`.

## Detail rules

- Keep the task header compact. Do not dump long prose into metadata fields.
- `Status` is mandatory and must equal the parent folder name (`backlog`, `todo`, `in-progress`,
  `in-review`, `done`). For new tasks this skill writes, it is `todo` (sprint case) or `backlog`.
- `Sprint` is mandatory. Use the integer (`3`) when the task lives under `sprint-3/`, or
  `backlog` when it lives in `backlog/`.
- `Assignee` is mandatory. Use `—` only when the user explicitly requested no auto-assignment.
- `Domain` must be one of the canonical tokens (`frontend`, `backend`, `infra`, `ai`).
- `Depends on task(s)` (under `Dependencies / Parallelism`) should be task slugs only,
  e.g. `be-001-idp-jwt-middleware`.
- Put explanations in the main sections, not in the metadata lines.
- `Current State / Existing System` must explain in plain language what exists today and what is
  still missing.
- `Context / Problem` must explain the pain or risk the current state creates. Do not repeat
  `Current State`.
- `Why This Is Needed` must explain business, product, delivery, or architectural impact.
- `Scope` must make boundaries explicit.
- `Rules / Constraints` must capture non-negotiables: architecture boundaries, ownership rules,
  performance budgets, compatibility rules, operational limits.
- `What Needs To Be Built` must enumerate concrete implementation scope, not vague aspirations.
- `Proposal` must name the chosen approach, affected layers/modules/libraries, and the important
  tradeoffs.
- `Implementation Breakdown` must give an engineer a practical starting sequence.
- `Goal` must describe a measurable or clearly observable end state.
- `Acceptance Criteria` must be binary outcome statements.
- `Test Cases` must cover happy path, failure path, regression path, and domain-specific checks
  (accessibility, performance, contracts, migrations, ops behavior) when relevant.
- Prefer short, clear paragraphs or 2–4 bullets over dense blocks of text.

## Orchestration rules

- Split by domain first, then by independently shippable units.
- If two or more parts can be analyzed independently, dispatch them to separate subagents in
  parallel.
- Frontend tasks stay frontend-only unless cross-domain coupling is unavoidable.
- Backend tasks stay backend-only unless cross-domain coupling is unavoidable.
- Infra tasks stay infra-only unless cross-domain coupling is unavoidable.
- AI tasks stay AI-only unless cross-domain coupling is unavoidable. See
  `references/domain-detection.md` for the AI-vs-backend boundary.
- If one task depends on another, keep them separate and record the dependency by task slug.
- Prefer smaller, implementation-ready tasks over large umbrella tasks.
- Every task should be understandable on its own by an engineer who has not read the original PRD.
- Prefer concrete implementation direction over abstract commentary.

## Domain worker instructions

Each domain worker should:

1. Restate the requirement from its own domain perspective.
2. Ignore unrelated domains unless there is a hard dependency.
3. Identify what is already present in the codebase for that domain.
4. Produce one or more tasks using the shared template.
5. Make scope boundaries explicit: in scope, out of scope, dependent on another task.
6. State the implementation rules, constraints, and architectural boundaries that must be
   respected.
7. Describe the proposal concretely enough that an engineer could start implementation from the
   task alone.
8. Break the solution into implementation slices when helpful.
9. Keep acceptance criteria testable and specific.
10. Keep test cases concrete: unit, integration, e2e, migration, performance, or ops checks as
    appropriate.
11. Mention affected modules, layers, or libraries when known.
12. Write `Current State` and `Context / Problem` so a reader can understand them quickly without
    decoding dense architecture language.

## Missing skill fallback

If a domain skill is missing (currently `infra` and `ai`):

- do not block task generation
- analyze the domain directly using the architecture context sources and the requirement
- record lower confidence in `Risks / Open Questions` only when the missing specialist materially
  affects quality

## Read these references

- `references/domain-detection.md` for routing work to domains
- `references/task-template.md` for the required task structure
- `references/team.md` for team member eligibility and workload-based assignment

## Use these scripts

- `scripts/count_open_tasks.py` — scans `ticket/backlog/` and every `ticket/sprint-*/{todo,
  in-progress,in-review}/` and prints `{assignee: open_count}` JSON. `done/` is excluded. Run
  with `python .claude/skills/task-writer/scripts/count_open_tasks.py` from the repo root.

## Quality bar

- Tasks must be implementation-ready, not brainstorming notes.
- Each task should feel like a small design brief for one shippable unit of work.
- The task header stays easy to scan; detail lives in the main sections.
- Acceptance criteria must be checkable.
- Test cases must map to real verification work.
- Tasks must be independently understandable without rereading the whole PRD.
- Avoid domain mixing unless required by the architecture.
- Goals must describe the end state clearly, not just repeat the task title.
- Rules and constraints must be explicit when they affect design or implementation choices.
- Storage and status must follow the kanban folder convention.
- Create as many tasks as needed. There is no fixed task limit.
