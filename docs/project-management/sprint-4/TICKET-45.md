# TICKET-45: Production CI/CD Pipeline Hardening

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 4
- **Assignee:** DevOps Engineer
- **Domain:** Automation / DevOps
- **Priority:** P1 - High
- **Assumptions:**
  - GitHub Actions is the chosen orchestrator.
- **Affected areas:** `.github/workflows/deploy.yml`, Deployment automation.

## Current State / Existing System

- **Implemented:** Basic Linting/Testing CI (TICKET-06).
- **Missing:** Automated deployment logic that handles migrations, environment-specific builds, and rollbacks.

## Context / Problem

Manual deployments are slow and dangerous. We need a "push-to-deploy" workflow where merging to `main` automatically runs tests, builds production assets, migrates the database, and rolls out the new version to users without downtime.

## Why This Is Needed

- **Business Impact:** Faster feature delivery and reduced human-error risk during releases.
- **Architectural Impact:** Finalizes the "Development Lifecycle" of the NudgeEn platform.

## Scope

### In-scope

- Enhance the GitHub Actions pipeline:
  - **Phase 1:** Build & Test.
  - **Phase 2:** Deployment to Staging (on PR).
  - **Phase 3:** Automated DB Migrations (`alembic upgrade head`).
  - **Phase 4:** Production rollout (on Merge to main).
- Implementation of "Migration Safety" (check if a migration is destructive).
- Slack/Discord notification on build success/failure.
- Rollback logic: Manual or automated way to revert to the last stable commit.

### Out-of-scope

- Canary deployments (too complex for MVP).

## Dependencies / Parallelism

- **Dependencies:** TICKET-06 (Initial CI), TICKET-44 (Production Hosting).
- **Parallelism:** Can be done once the hosting platform (TICKET-44) exposes its CD hooks.

## Rules / Constraints

- Production deployments must never happen if tests fail.
- Database migrations MUST run before the new code is live to avoid breaking old schema.

## What Needs To Be Built

1. `.github/workflows/production-deploy.yml`.
2. Scripts for automated migration execution in the CI context.

## Proposal

Use platform-provided CLI tools (e.g., `vercel-cli`, `railway-cli`) within GitHub Actions. For database migrations, run a "pre-deploy" task that connects to the production Postgres instance.

## Implementation Breakdown

1. **Pipeline Script:** Write the YAML workflow.
2. **Secrets:** Add deployment tokens to GitHub Repository Secrets.
3. **Migration Logic:** Integrate `alembic` commands into the build step.
4. **Validation:** Perform a test PR and merge to verify the full flow.

## Acceptance Criteria

- [ ] A developer can deploy a change to production simply by merging a PR.
- [ ] Database schema updates naturally alongside code updates.
- [ ] CI pipeline takes < 10 minutes to complete from push to live.
- [ ] Failed builds send an immediate notification to the team.

## Test Cases

### Happy Path

- Add a new field -> PR -> Merge -> DB migrates + App updates -> New field visible in Prod.

### Failure Path

- Code has syntax error -> CI fails -> No deployment happens (Safety).

### Regression Tests

- Verify that a failed migration blocks the code deployment step.
