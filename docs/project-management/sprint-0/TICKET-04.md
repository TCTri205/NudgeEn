# TICKET-04: Alembic Database Migration Setup

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 0
- **Assignee:** Backend Lead
- **Domain:** Data Layer / Infrastructure
- **Priority:** P0 - Critical
- **Assumptions:**
  - PostgreSQL connection is functional (TICKET-03).
  - SQLAlchemy models will be defined in a way that is accessible to `env.py`.
- **Affected areas:** `api/alembic/`, `api/app/models/`, PostgreSQL Schema.

## Current State / Existing System

- **Implemented:** Database connection logic (TICKET-03).
- **Missing:** Migration framework to manage schema changes over time.

## Context / Problem

As the project grows, the database schema will change frequently. We need a reliable way to version these changes, allow for rollbacks, and ensure consistency across development and production environments.

## Why This Is Needed

- **Business Impact:** Prevents data loss and downtime during schema updates.
- **Architectural Impact:** Ensures that the database schema is always in sync with the source code's data models.

## Scope

### In-scope

- Initialize Alembic in the `api/` directory.
- Configure `alembic.ini` and `env.py`.
- Auto-discovery of SQLAlchemy models for migration generation.
- Implement the initial migration for core tables: `users`, `accounts`, `sessions`.
- Documentation of common Alembic commands.

### Out-of-scope

- Complex migrations for feature modules (Auth, Chat, etc.) beyond core identity tables.
- Data seeding/migrations for static content.

## Dependencies / Parallelism

- **Dependencies:** TICKET-03 (Database Connection Setup).
- **Parallelism:** Can be done while TICKET-02 (Next.js) is in progress.

## Rules / Constraints

- Must use `async` mode in `env.py` to match the async nature of the application.
- All migrations must have a clear description and unique ID.
- Schema auto-generation should ignore internal PostgreSQL tables.

## What Needs To Be Built

1. Run `alembic init -t async migrations` in `api/`.
2. Modify `migrations/env.py` to import `Base` from model definitions.
3. Update `alembic.ini` to use environment variables for `sqlalchemy.url`.
4. Generate the first migration: `alembic revision --autogenerate -m "initial_schema"`.

## Proposal

Use a centralized `Base` model class in `api/app/core/database.py` that all other models inherit from. This allows Alembic's `env.py` to easily discover all models by importing this single base class.

## Implementation Breakdown

1. **Initialize:** Install `alembic` and run basic initialization.
2. **Configuration:** Tailor `env.py` to support async engines and model discovery.
3. **Core Models:** Define initial Pydantic/SQLAlchemy models for identity (from EPIC-01 scope but needed for schema foundation).
4. **First Migration:** Run autogenerate and verify the generated Python script.
5. **Applied:** Run `alembic upgrade head` and verify tables in Postgres.

## Acceptance Criteria

- [ ] `alembic upgrade head` runs successfully against a local Postgres instance.
- [ ] Core tables (`users`, `accounts`, `sessions`) are created with correct columns and constraints.
- [ ] `alembic_version` table exists and tracks the current schema state.
- [ ] Auto-generation identifies new models without manual configuration changes in `env.py`.

## Test Cases

### Happy Path

- `alembic revision --autogenerate` -> Creates a valid migration file.
- `alembic upgrade head` -> Tables appear in DB.

### Failure Path

- Database is unreachable -> Migration fails with connection error.
- Invalid model definition -> Autogenerate fails or creates invalid SQL.

### Regression Tests

- Ensure `alembic downgrade -1` successfully reverts the last migration.
