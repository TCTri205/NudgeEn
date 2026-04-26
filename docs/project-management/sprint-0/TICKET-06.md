# TICKET-06: CI/CD & Linting Baseline

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 0
- **Assignee:** DevOps / Lead Developer
- **Domain:** Platform / CI-CD
- **Priority:** P2 - Medium
- **Assumptions:**
  - GitHub is used as the version control platform.
  - `api/` and `web/` projects are initialized.
- **Affected areas:** `.github/workflows/`, Pre-commit hooks, Linter configs.

## Current State / Existing System

- **Implemented:** Tech stack and principles documented in TECHSTACK.md and PRINCIPLES.md.
- **Missing:** Automated checks, CI pipelines, or local linting enforcement.

## Context / Problem

To maintain a high standard of code quality and prevent regressions, we need automated checks that run both locally (via pre-commit) and in the cloud (via GitHub Actions).

## Why This Is Needed

- **Business Impact:** Reduces bugs reaching production and lowers code review effort.
- **Architectural Impact:** Enforces consistent coding standards and architectural patterns automatically.

## Scope

### In-scope

- Create GitHub Actions workflow for Backend (Ruff, Pytest).
- Create GitHub Actions workflow for Frontend (ESLint, Prettier, Build).
- Setup `pre-commit` configuration for the repository.
- Configure `pyproject.toml` (Ruff) and `package.json` (ESLint) with project-specific rules.

### Out-of-scope

- Automated deployment to staging/production (EPIC-05).
- Security scanning (SonarCloud, etc.).

## Dependencies / Parallelism

- **Dependencies:** TICKET-01 (Backend Skeleton), TICKET-02 (Frontend Skeleton).
- **Parallelism:** Can be done once both skeletons are in place.

## Rules / Constraints

- CI must fail if linting or tests fail.
- Use the fastest available tools (e.g., Ruff instead of Flake8/Black).
- Keep CI execution time under 5 minutes for the initial phase.

## What Needs To Be Built

1. `.github/workflows/backend-ci.yml`: Ruff + Pytest.
2. `.github/workflows/frontend-ci.yml`: ESLint + Next.js build check.
3. `.pre-commit-config.yaml`: Hooks for formatting and simple checks.
4. Update `ARCHITECTURE.md` or `PRINCIPLES.md` with CI/CD standards.

## Proposal

Leverage GitHub Actions' native caching for Python (pip/uv) and Node.js (npm/yarn) to minimize runtimes. Use composite actions if duplication between workflows becomes significant.

## Implementation Breakdown

1. **Config:** Define Ruff and ESLint rules.
2. **Local Hooks:** Setup `pre-commit` and verify it blocks bad commits.
3. **GitHub Workflows:** Implement `.yml` files in `.github/workflows/`.
4. **Validation:** Push a test commit and verify the CI run status.

## Acceptance Criteria

- [ ] GitHub Actions pipeline triggers correctly on PRs to `main`.
- [ ] Backend pipeline runs Ruff and returns success/failure correctly.
- [ ] Frontend pipeline runs ESLint and returns success/failure correctly.
- [ ] Pre-commit hooks run locally and format code on save/commit.

## Test Cases

### Happy Path

- Committing clean code -> CI passes green.
- `pre-commit run --all-files` -> Success.

### Failure Path

- Committing code with lint errors -> CI fails and blocks merge.
- `pre-commit` finds errors -> Commit is blocked until fixed.

### Regression Tests

- Ensure CI doesn't pass if a critical test fails.
