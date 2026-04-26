# TICKET-44: Multi-service Deployment (Vercel + Cloud)

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 4
- **Assignee:** DevOps Engineer
- **Domain:** Deployment / Infrastructure
- **Priority:** P1 - High
- **Assumptions:**
  - Domain names are purchased and available.
- **Affected areas:** `Dockerfile`, `docker-compose.yml` (prod), Cloud Infrastructure.

## Current State / Existing System

- **Implemented:** Local development environment (TICKET-01, TICKET-02).
- **Missing:** Final hosted URLs for the web app, API, and workers.

## Context / Problem

A "Modular Monolith" still needs multiple execution contexts in production: the Frontend (Vercel), the API/Backend (Render/Railway), and the Background Workers (Taskiq). Coordinating these disparate services with correct CORS, networking, and SSL is the final hurdle for launch.

## Why This Is Needed

- **Business Impact:** Makes the app available to real users on the public internet.
- **Architectural Impact:** Transitions the project from a "Repository" to a "Live System."

## Scope

### In-scope

- **Frontend:** Deploy to Vercel with automatic Preview Deployments.
- **Backend:** Deploy to a cloud provider (e.g., Railway/Render) using Docker.
- **Workers:** Deploy separate worker instances for `heavy` and `light` queues (TICKET-05).
- **Networking:**
  - Configure CORS to allow `app.nudgen.com` to call `api.nudgen.com`.
  - Secure internal communication between API and Redis/Postgres.
- **SSL:** Ensure all endpoints are `https`.

### Out-of-scope

- Multi-region deployment (single region is fine for MVP).

## Dependencies / Parallelism

- **Dependencies:** TICKET-01, TICKET-05, TICKET-43.
- **Parallelism:** Can be done once the production config (TICKET-43) is ready.

## Rules / Constraints

- Database must NOT be publically accessible (only from internal cloud network).
- Zero-downtime deployment (blue/green or rolling) if supported by the provider.

## What Needs To Be Built

1. Production Dockerfiles optimized for size (multi-stage builds).
2. Deployment manifest/configuration for the selected cloud platform.
3. Health check endpoints (`/health`) for the load balancer.

## Proposal

Use Vercel for the Next.js frontend to leverage their Edge network. Use Render or Railway for the Python backend because of their excellent support for persistent background workers and affordable Postgres/Redis add-ons.

## Implementation Breakdown

1. **Docker Prep:** Refine Dockerfiles for production (remove dev dependencies).
2. **Provisioning:** Create the apps and databases in the cloud UI.
3. **DNS/SSL:** Map custom domains and wait for cert propagation.
4. **Verification:** Live test the full flow: Login -> Chat -> Worker Extraction.

## Acceptance Criteria

- [ ] Web app is live at a public `.com` (or similar) address.
- [ ] API is receiving requests from the frontend correctly (no CORS errors).
- [ ] Workers are successfully processing jobs in the cloud logs.
- [ ] SSL certificates are valid and browser shows "Secure."

## Test Cases

### Happy Path

- User visits site -> Logs in -> Chat streams successfully in prod.

### Failure Path

- One worker goes down -> Deployment platform auto-restarts it.

### Regression Tests

- Check that `api.nudgen.com` returns 401/403 for unauthenticated external crawlers.
