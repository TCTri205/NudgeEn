# Team Structure & Assignment Rules

## Members

| Name | Role | Eligible domains |
|---|---|---|
| **Phuc Pham** | Backend Lead | `backend`, `ai` |
| **Nguyen Dang** | Frontend Lead | `frontend` |
| **Long Nguyen** | DevOps/Backend Engineer | `infra`, `backend` |
| **Tri Truong** | Software Engineer | `backend`, `frontend`, `ai` |

## Domain eligibility

- `frontend` → Nguyen Dang, Tri Truong
- `backend` → Phuc Pham, Long Nguyen, Tri Truong
- `ai` → Phuc Pham, Tri Truong
- `infra` (covers DevOps and CI/CD) → Long Nguyen

## Assignment workflow

When writing a task, follow these steps to set `Assignee`:

1. **Determine the task domain** using `references/domain-detection.md`.
2. **Filter eligible members** using the table above — only consider members whose eligible domains include the task's domain.
3. **Check current workloads** by scanning all existing task files under:
   - `docs/project-management/epics/**/tasks/**/*.md`
   - `docs/project-management/tasks/**/*.md`
   Count how many tasks each eligible member already has where `Assignee` is set to their name and `Status` is not `done` or `cancelled`.
4. **Assign to the eligible member with the lowest open task count.**
5. **Break ties** by role seniority in the domain: Lead > Engineer.
6. If no workload data is available (no existing tasks found), assign to the domain Lead where one exists, otherwise assign to Tri Truong as the most flexible member.

## Rules

- **Never assign outside eligibility.** Phuc does not get frontend tasks. Nguyen does not get backend, AI, or infra tasks. Long does not get frontend or AI tasks.
- **Tri is the overflow member** — assign to Tri when all other eligible members have higher workloads or when the task spans multiple domains that no single specialist covers.
- **Long is the sole owner of all `infra` tasks** (DevOps, CI/CD, deployment, observability) — do not assign these to anyone else.
- **AI tasks** are shared between Phuc and Tri; prefer Phuc when the task is primarily model/prompt/API work, prefer Tri when the task involves integrating AI output into the product UI or pipeline.
- When a task spans two domains (e.g. backend + frontend), split it into two tasks — one per domain — rather than assigning a cross-domain task to one person.
- Use `—` only when a task is explicitly unassigned by the user's request. Auto-assignment is the default.
