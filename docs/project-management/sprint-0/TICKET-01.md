# TICKET-01: FastAPI Project Skeleton

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 0
- **Assignee:** Backend Lead
- **Domain:** Platform / Infrastructure
- **Priority:** P0 - Critical
- **Assumptions:**
  - Python 3.12+ is available on the development environment.
  - Standard directory structure is acceptable as per ARCHITECTURE.md.
- **Affected areas:** `api/`, Backend Infrastructure.

## Current State / Existing System

- **Implemented:** Documentation structure and architectural guidelines (PRD, ARCHITECTURE.md, TECHSTACK.md).
- **Missing:** Any physical code or directory structure for the FastAPI backend.

## Context / Problem

We need a robust, scalable, and modular base for the NudgeEn backend. A standard FastAPI skeleton is required to begin feature development and ensure all team members follow the same patterns.

## Why This Is Needed

- **Business Impact:** Enables the development of all AI-driven features.
- **Architectural Impact:** Establishes the "Modular Monolith" pattern, preventing spaghetti code and easing future service extraction if needed.

## Scope

### In-scope

- Create `api/` directory with `app/main.py`.
- Define module skeleton for: `auth`, `chat`, `persona`, `guardrails`, `memory`, `pedagogy`, `platform`.
- Implement FastAPI application factory.
- Basic health check endpoint.
- Configure Ruff for linting and formatting.
- `pyproject.toml` initialization.

### Out-of-scope

- Database connection logic (TICKET-03).
- Background worker setup (TICKET-05).
- Actual feature implementation in modules.

## Dependencies / Parallelism

- **Dependencies:** None. This is the first technical ticket.
- **Parallelism:** Can be done in parallel with TICKET-02 (Next.js Setup).

## Rules / Constraints

- Must follow the directory structure defined in EPIC-00 and ARCHITECTURE.md.
- Must use Python 3.12+ type hinting.
- No direct dependencies between modules except through the `platform` layer or service orchestration.

## What Needs To Be Built

1. Create `api/app` directory structure.
2. Initialize `api/pyproject.toml`.
3. Create `api/app/main.py` with FastAPI instance.
4. Add `/health` GET endpoint.
5. Setup `api/app/core` for platform-wide logic.
6. Setup `api/app/modules/` with `__init__.py` files for each planned module.

## Proposal

Initialize a template-based FastAPI project using `uv`. Use `app/main.py` to orchestrate routers from various modules. Each module in `app/modules/` will eventually have its own `router.py`, `models.py`, `schemas.py`, and `service.py`.

## Implementation Breakdown

1. **Initialize Workspace:** Create `api/` folder.
2. **Project Setup:** Initialize `pyproject.toml` with `fastapi`, `uvicorn`, `ruff`, `pydantic-settings`.
3. **Skeleton Creation:** Create the `app/`, `app/core/`, and `app/modules/` subdirectories.
4. **App Factory:** Implement `create_app()` in `main.py`.
5. **Validation:** Run `ruff check .` and start server locally.

## Acceptance Criteria

- [ ] `api/` directory exists with `app/main.py`.
- [ ] FastAPI app starts successfully with `uvicorn`.
- [ ] Health check endpoint `/health` returns `{"status": "ok"}`.
- [ ] Module structure exists: `auth`, `chat`, `persona`, `guardrails`, `memory`, `pedagogy`.
- [ ] `ruff` is configured and passes.

## Test Cases

### Happy Path

- Run `uvicorn app.main:app` -> Server starts.
- `curl http://localhost:8000/health` -> 200 OK.

### Failure Path

- Missing dependencies in `pyproject.toml` -> Startup fail.
- Incorrect Python version (<3.12) -> Runtime error.

### Regression Tests

- Future tickets must not break the basic `/health` endpoint.
