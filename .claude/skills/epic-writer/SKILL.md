---
name: epic-writer
description: >
  Turn a feature request, PRD, RFC, or product idea into a clear engineering epic before task
  breakdown. Use when the user wants one feature framed as an epic with problem, scope, goals,
  constraints, risks, and a clean handoff to `task-writer` for domain-separated implementation
  tasks.
---

# Epic Writer

This skill sits one level above `task-writer`.

Its job is to turn one feature into one clear epic, then hand that epic to `task-writer` so the
work can be split into implementation-ready tasks by domain.

The epic is not the task list. The epic explains the feature. `task-writer` explains the work.
Keep this skill thin: define feature intent, scope, capability slices, and success boundaries
without collapsing into task-level planning.

## Mandatory workflow

1. Start with `workflow-orchestration`.
2. Read the feature requirement and restate it in one short paragraph.
3. Read `project/codebase.md` to understand the project architecture, stack, existing boundaries,
   and current libraries.
4. If the requirement is still too ambiguous, write down the explicit facts, assumptions,
   constraints, and open questions before drafting the epic.
5. Decide whether the request is really one feature or several unrelated features:
    - if it is one feature with multiple workstreams, keep one epic
    - if it is multiple unrelated features, split them into separate epics
6. Detect the impacted domains at a high level: frontend, backend, infra/devops, AI/data, or mixed.
7. If the feature has independent discovery workstreams, use subagents in parallel to analyze them.
   This is required when the work can be split safely.
8. Write the epic using `references/epic-template.md`.
9. Save the epic as its own folder and file:
    - folder: `project/epics/<epic-slug>/`
    - file: `project/epics/<epic-slug>/<epic-slug>.md`
    - default status for a newly created epic: `none`
10. After the epic is coherent, prepare a structured handoff for `task-writer` using
    `references/task-writer-handoff.md`.
11. Use `task-writer` to turn the epic into independent tasks grouped by domain.
12. Compare the resulting tasks against the epic:
    - every major in-scope outcome should map to at least one task
    - out-of-scope items must not leak into the task list
    - dependencies should remain explicit instead of merging unrelated work
13. If task generation exposes missing epic clarity, update the epic first and then rerun the
    handoff.

## What the epic must do

The epic must explain the feature clearly enough that another engineer can understand:

- what problem exists today
- who or what part of the system is affected
- what outcome should become true after the feature is delivered
- what is in scope and out of scope
- what constraints cannot be violated
- what solution direction is preferred at feature level
- what success looks like at epic level
- what risks or unknowns still exist

## Required epic sections

Every epic must follow `references/epic-template.md`.

The epic should include:

- compact epic metadata
- `Summary`
- `Current State / Gap`
- `Problem / Opportunity`
- `Desired Outcome`
- `Users / Use Cases`
- `Scope`
- `Capability Slices`
- `Facts / Assumptions / Constraints / Unknowns`
- `Proposed Solution`
- `Dependencies / Rollout / Risks`
- `Epic Done Criteria`
- `Task Writer Handoff`

## Detail rules

- Keep the epic easy to scan. Use compact metadata and put explanation in the main sections.
- `Current State / Gap` must describe the situation today in plain language and clearly state what
  is still missing.
- `Problem / Opportunity` must explain what is painful, risky, missing, or strategically useful in
  the current state.
- `Desired Outcome` must explain what should become true after the feature exists and why that end
  state matters.
- `Users / Use Cases` must explain who uses the feature or which internal flow depends on it.
- `Scope` must make boundaries explicit. The reader should quickly see what this epic will not
  change.
- `Capability Slices` must group the feature by user flow or system capability, not by engineering
  domain. `task-writer` will do the domain split later.
- `Facts / Assumptions / Constraints / Unknowns` must separate what is known from what is inferred.
- `Proposed Solution` must describe the chosen direction clearly enough that `task-writer` can
  break it into tasks without guessing the core design.
- `Dependencies / Rollout / Risks` must make sequencing pressure and delivery risk visible without
  becoming a task plan.
- `Epic Done Criteria` must describe observable feature-level outcomes, not engineering subtasks.
- `Task Writer Handoff` must be short, structured, and optimized for reuse by `task-writer`.
- `Status` must always exist in epic metadata and should usually start as `none`.

## Handoff rules for task-writer

- `task-writer` should receive the epic as the source requirement.
- Pass the original user requirement through unchanged alongside the epic so `task-writer` can
  re-check facts against `project/codebase.md`.
- Pass the epic slug or epic file path so `task-writer` knows where to persist related task files.
- The handoff must include the feature summary, domain impact, scope, non-goals, constraints,
  proposed solution, capability slices, epic done criteria, and unresolved questions.
- Do not ask `task-writer` to rediscover the high-level feature strategy from scratch if the epic
  already defines it.
- Do ask `task-writer` to split the work into implementation-ready tasks by domain and dependency.
- Preserve the same scope boundaries in both the epic and the generated tasks.
- If the epic already identifies capability slices, pass them as hints, not as a forced final task
  structure.
- If the feature spans multiple independent domains, require `task-writer` to use subagents in
  parallel where safe.

## What epic-writer must not do

- Do not generate the final implementation task list directly.
- Do not split the feature into frontend, backend, infra, or AI tasks yourself.
- Do not write task-level `Proposal`, `Implementation Breakdown`, `Acceptance Criteria`, or
  `Test Cases`.
- Do not let capability slices turn into low-level tickets inside the epic.
- If the request is already a small, single-domain change, skip `epic-writer` and call
  `task-writer` directly.

## Subagent strategy

Use subagents when the feature has parallelizable analysis such as:

- frontend UX and state management analysis
- backend data model and API analysis
- infra rollout, observability, or migration analysis
- AI behavior, prompting, evaluation, or safety analysis

Give each subagent:

- the original feature request
- the relevant architecture context from `project/codebase.md`
- the domain or workstream scope
- the requirement to return epic inputs, not full mixed-domain tasks

The main agent remains responsible for:

- choosing the epic shape
- resolving scope boundaries
- writing the final epic
- handing the epic to `task-writer`
- verifying that epic and tasks stay aligned

## Read these references

- `references/epic-template.md` for the required epic structure
- `references/task-writer-handoff.md` for the handoff format

## Quality bar

- The epic must stand on its own without reopening the original requirement.
- The epic must explain both problem and direction, not only summarize the request.
- The epic must stay at feature level and not collapse into an implementation checklist.
- The epic must be detailed enough that `task-writer` can produce strong tasks with minimal
  ambiguity.
- Scope and non-goals must be explicit.
- Capability slices must stay user-flow or system-capability oriented.
- Epic done criteria must be concrete.
- Epic storage and status must follow the shared workflow convention.
- The task handoff must preserve intent, boundaries, and constraints from the epic.
