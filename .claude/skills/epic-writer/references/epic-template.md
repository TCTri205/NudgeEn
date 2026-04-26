# Epic Template

Use this template for one feature epic before task breakdown.

```md
# <Epic Title>

- Status:
- Priority:
- Source requirement:
- Impacted domains:

## Summary

One short paragraph that explains the feature, the intended outcome, and the main system or user
impact.

## Current State / Gap

Describe the current product, flow, architecture, or operating model in simple language. Explain
what exists today and what is still missing.

## Problem / Opportunity

Explain what is not good enough in the current state, what pain or risk it creates, or what
opportunity is currently blocked because this feature does not exist yet.

## Desired Outcome

Describe what should become true after this feature is delivered and why that outcome matters.

## Users / Use Cases

- Primary users or systems affected:
- Main use cases:
- Important edge cases:

## Scope

- In scope:
- Out of scope:

## Capability Slices

- Slice 1:
- Slice 2:
- Slice 3:

## Facts / Assumptions / Constraints / Unknowns

- Facts:
- Assumptions:
- Constraints:
- Unknowns:

## Proposed Solution

Describe the preferred feature-level solution direction. Name the main modules, domains, flows,
libraries, or integrations involved, and explain the key tradeoffs.

## Dependencies / Rollout / Risks

- Dependencies:
- Rollout notes:
- Risks:

## Epic Done Criteria

- Observable feature outcome 1
- Observable feature outcome 2
- Observable feature outcome 3

## Task Writer Handoff

- Epic slug:
- Epic file path:
- Original requirement:
- Epic summary:
- Impacted domains:
- Desired outcome:
- In-scope outcomes:
- Non-goals:
- Capability slices:
- Facts:
- Assumptions:
- Constraints:
- Unknowns:
- Proposed solution summary:
- Dependencies:
- Rollout notes:
- Risks:
- Task splitting hints:
- Validation expectations:
```

## Notes

- Keep the metadata compact.
- Use `Status` on every epic. Start with `none` unless there is a clear reason to set another
  state.
- Persist the epic at `project/epics/<epic-slug>/<epic-slug>.md`.
- Use plain language in `Current State / Gap` and `Problem / Opportunity`.
- `Capability Slices` should describe major feature slices or user flows, not domain-specific task
  buckets.
- `Epic Done Criteria` should describe the final feature state, not implementation activity.
- `Task Writer Handoff` should be short and structured so `task-writer` can reuse it directly.
