# TICKET-43: Environment Separation & Config (.env.production)

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 4
- **Assignee:** DevOps Engineer
- **Domain:** Infrastructure / Configuration
- **Priority:** P1 - High
- **Assumptions:**
  - Separate infrastructure IDs exist for Dev/Staging/Prod.
- **Affected areas:** `api/app/core/config.py`, GitHub Secrets, `.env.production`.

## Current State / Existing System

- **Implemented:** Local `.env` based config (TICKET-03).
- **Missing:** Formal production configuration, secrets management, and validation logic to prevent "leaking" dev settings into production.

## Context / Problem

Production environments require stricter security and different connection strings (e.g., Supavisor for DB, production Redis). Hardcoding or manually copying `.env` files is error-prone. We need a robust "Environment-Aware" configuration system that validates all required secrets at startup.

## Why This Is Needed

- **Business Impact:** Prevents production downtime due to misconfiguration and protects sensitive API keys (Gemini, Auth).
- **Architectural Impact:** Standardizes the configuration lifecycle across all environments.

## Scope

### In-scope

- Implement Pydantic-based configuration with strict types and field validation.
- Create `.env.example` and `.env.production.template` files.
- Setup Secrets Management:
  - **GitHub Actions Secrets** for CI.
  - **Deployment Platform Secrets** (Vercel, Railway/Render).
- Logic to detect `APP_ENV` and load appropriate defaults.
- Block application startup if critical secrets (DATABASE_URL, GEMINI_API_KEY) are missing.

### Out-of-scope

- HashiCorp Vault implementation (too complex for MVP).

## Dependencies / Parallelism

- **Dependencies:** TICKET-03 (Generic Config).
- **Parallelism:** Can be done in parallel with TICKET-44.

## Rules / Constraints

- Never commit `.env.production` to version control.
- Production logging levels must be set to `INFO` or `WARN` by default.
- Fail-fast on startup if a secret is missing.

## What Needs To Be Built

1. Refactor `api/app/core/config.py` using `pydantic-settings`.
2. Documentation on how to rotate secrets.
3. Startup health-check for config integrity.

## Proposal

Use `pydantic-settings` to auto-read environment variables. Define a `Settings` class where fields like `POSTGRES_PASSWORD` have no default, forcing the app to crash if the variable is not set in the environment.

## Implementation Breakdown

1. **Model Update:** Create the strict `ProdSettings` model.
2. **Secrets Setup:** Populate the deployment platform UI with required keys.
3. **Validation:** Write a small script to verify the config object in the CI pipeline.
4. **Validation:** Confirm that removing an ENV var causes the container to fail to start.

## Acceptance Criteria

- [ ] Application crashes if `DATABASE_URL` is missing in production mode.
- [ ] Production secrets are successfully pulled from the platform and into the app.
- [ ] Connection strings are verified to be "Production-Grade" (e.g., using pooling proxies).
- [ ] No dev-only variables (e.g., mock auth) are active in production.

## Test Cases

### Happy Path

- All ENV vars set -> App starts -> Reaches "Ready" state.

### Failure Path

- Missing `ANTHROPIC_API_KEY` (if used) -> Pydantic raises `ValidationError`.

### Regression Tests

- Ensure `docker-compose` for dev still works after these strict changes.
