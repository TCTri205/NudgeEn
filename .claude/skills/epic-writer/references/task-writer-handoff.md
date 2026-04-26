# Task Writer Handoff

Use this structure when handing an epic to `task-writer`.

The goal is to preserve feature intent and boundaries without forcing `task-writer` to rediscover
the entire epic from scratch.

```md
Use `task-writer` on the following epic.

Epic slug:
Epic file path:
Original requirement:
Epic title:
Epic summary:
Impacted domains:
Current state / gap:
Problem / opportunity:
Desired outcome:
In scope:
Out of scope:
Capability slices:
Facts:
Assumptions:
Constraints / rules:
Proposed solution:
Dependencies:
Rollout notes:
Risks:
Open questions:
Epic done criteria:

Task generation instructions:
- Split tasks by domain first.
- Keep frontend, backend, infra, and AI tasks separate unless coupling is unavoidable.
- Use subagents when the work can be analyzed in parallel safely.
- Produce implementation-ready tasks, not brainstorming notes.
- Preserve epic scope and non-goals.
- Make dependencies explicit.
```

## Notes

- Keep the handoff short enough that `task-writer` can process it quickly.
- Keep the handoff faithful to the epic. Do not add scope that the epic does not support.
- Keep capability slices as feature hints only. `task-writer` still owns domain decomposition.
- Include epic storage information so related tasks can be written under the same epic folder.
