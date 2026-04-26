# TICKET-02: Next.js Frontend Skeleton

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 0
- **Assignee:** Frontend Lead
- **Domain:** Web Application
- **Priority:** P0 - Critical
- **Assumptions:**
  - Node.js 18+ is available.
  - Standard Next.js App Router pattern is preferred.
- **Affected areas:** `web/`, Frontend Infrastructure.

## Current State / Existing System

- **Implemented:** Tech stack choice (Next.js, Tailwind, Auth.js) documented in TECHSTACK.md.
- **Missing:** Any physical code or directory structure for the web frontend.

## Context / Problem

We need a modern, responsive, and type-safe frontend foundation. Next.js with App Router is the chosen framework to ensure high performance and seamless integration with Auth.js for user session management.

## Why This Is Needed

- **Business Impact:** Provides the user interface for the AI chatbot.
- **Architectural Impact:** Establishes the frontend architecture, component patterns, and authentication shell.

## Scope

### In-scope

- Create `web/` directory with Next.js 14+ initialization.
- Configure TypeScript, Tailwind CSS, and PostCSS.
- Setup basic directory structure: `app/`, `components/`, `lib/`, `hooks/`.
- Initialize Auth.js (NextAuth.v5) configuration shell.
- Create a basic homepage and layout.
- Setup `middleware.ts` for routing and auth logic.

### Out-of-scope

- Actual login/logout flows (EPIC-01).
- Chat UI components (TICKET-20+).
- Backend API integration (beyond health check).

## Dependencies / Parallelism

- **Dependencies:** None.
- **Parallelism:** Can be done in parallel with TICKET-01 (FastAPI Setup).

## Rules / Constraints

- Must use TypeScript strict mode.
- Must follow the Next.js App Router conventions.
- Must use Tailwind CSS for all styling (no global CSS unless necessary).
- Component organization must follow the principles in TECHSTACK.md.

## What Needs To Be Built

1. Initialize `web/` project using `npx create-next-app@latest`.
2. Configure `tailwind.config.ts` and `next.config.mjs`.
3. Create `web/src/app` (if src is used) or `web/app`.
4. Initialize `web/auth.ts` (NextAuth.v5 file).
5. Create a simple `layout.tsx` with a placeholder navigation.
6. Create `page.tsx` with a "Welcome to NudgeEn" message.

## Proposal

Use `create-next-app` to scaffold the project with default settings for App Router, TypeScript, and Tailwind. Move `auth.ts` to the root of the project as per NextAuth.v5 best practices.

## Implementation Breakdown

1. **Bootstrap:** Run `npx create-next-app@latest web --typescript --tailwind --eslint`.
2. **Setup Structure:** Create `components/`, `lib/`, `hooks/` folders.
3. **Auth Shell:** Install `@auth/core` and initialize the configuration file.
4. **Middleware:** Create `middleware.ts` to handle session checks (placeholder).
5. **UI Basic:** Implement a simple, premium-looking splash page.

## Acceptance Criteria

- [ ] `web/` directory exists with Next.js project files.
- [ ] `npm run dev` starts without errors.
- [ ] Homepage is accessible at `http://localhost:3000`.
- [ ] Tailwind CSS classes are applied correctly.
- [ ] Auth.js configuration file is present and exports required handlers.

## Test Cases

### Happy Path

- `npm run build` -> Success.
- Visual check: Layout is consistent across viewport sizes.

### Failure Path

- Missing environment variables (.env) -> Build or runtime failure.
- Incompatible Node.js version -> Installation error.

### Regression Tests

- Check that `next dev` doesn't crash after adding `middleware.ts`.
