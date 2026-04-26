---
name: frontend-engineering
description: >
  Frontend engineering skill covering architecture, React patterns, state management, performance,
  testing, and code quality. Use whenever the user asks about: structuring React/Next.js projects,
  rendering strategies (SSR/SSG/RSC/CSR), folder organization (Feature-Sliced Design, Bulletproof React),
  React components, hooks, compound components, RSC patterns, state management (TanStack Query, Zustand,
  Jotai, React Hook Form, Zod), performance (Core Web Vitals, bundle size, code splitting, re-renders),
  testing (Vitest, RTL, Playwright, MSW), TypeScript config, ESLint, accessibility, security, error handling,
  API layer design, or any frontend architectural decision. Trigger even without explicit "frontend" — if
  they mention React, Next.js, components, hooks, state, forms, or Tailwind, this skill applies.
---

# Frontend Engineering Skill

This skill provides Staff-Engineer-level guidance for building production-grade frontend applications.
It covers six domains, each with a dedicated reference file for deep content.

## How to use this skill

1. Read this SKILL.md to understand the core principles and identify which domain applies
2. Read `project/codebase.md` to detect the frontend technologies and libraries actually used by the
   current project
3. For each detected frontend library or technology, look for the matching cached file under
   `references/libraries/`
4. If the cached library file exists, read it before relying on the generic domain references
5. If the cached library file is missing, or its `synced_version` does not match the project's
   version, refresh it with `library-sync` before relying on it
6. Read the relevant reference file(s) from `references/` for detailed patterns and code examples
7. If `project/required-skills.md` lists installed frontend-adjacent skills, use them when their
   specialty matches the current task
8. Multiple references and supporting skills may apply — read all that are relevant before
   responding

## Library detection flow

- Treat `project/codebase.md` as the starting index of frontend stack decisions.
- If `project/codebase.md` says the project uses Zustand for state management, read
  `references/libraries/zustand.md`.
- If it says the project uses Next.js, TanStack React Query, or shadcn/ui, read
  `references/libraries/nextjs.md`,
  `references/libraries/tanstack-react-query.md`, or
  `references/libraries/shadcn-ui.md`.
- If it says the project uses TanStack Start or another frontend framework, router, or state/data
  library with a cached file, read that cached file first.
- Apply the same rule for any other frontend package with a cached file in `references/libraries/`.
- If a technology used by the project has no cached file yet, call `library-sync` to fetch it from
  Context7 and create the cache before answering.
- If `project/codebase.md` is missing or stale, refresh that understanding first, then continue with
  the library lookup flow.

## Supporting skills

Use these external skills when they are available and the task clearly matches them. The startup
bootstrap in `project/required-skills.md` should install them automatically if they are required and
missing.

| Skill                       | Use when                                                                                                                                                                |
|-----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `next-best-practices`       | The project uses Next.js and the task depends on App Router, Server Components, caching, rendering boundaries, route handlers, or deployment-sensitive Next.js behavior |
| `shadcn`                    | The project uses shadcn/ui and the task depends on component generation, CLI usage, theming, registry workflows, or ownership of copied UI primitives                   |
| `tailwind-design-system`    | The task is about Tailwind token design, utility conventions, design systems, theme primitives, component styling rules, or scaling Tailwind across a product           |
| `typescript-advanced-types` | The task depends on complex generics, utility types, inference, advanced state/query typing, schema-driven typing, or reusable library-level TypeScript patterns        |
| `e2e-testing-patterns`      | The task is about Playwright, browser-flow testing, E2E test strategy, flake reduction, fixture design, or high-value integration path coverage                         |

Rules:

- Do not call these skills by default on every frontend task.
- Call them when the problem is deep enough that the specialized skill materially improves the
  answer.
- Keep `frontend-engineer` as the primary orchestrator for frontend work; use the supporting skills
  as focused depth layers.
- When one of these skills is used, still anchor recommendations to the real project stack from
  `project/codebase.md` and any local library caches under `references/libraries/`.

## Reference files — when to read each

| File                                | Read when the user asks about...                                                                                                                                                                                                                                                                    |
|-------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `references/architecture.md`        | Project structure, folder organization, rendering strategy (SSR/SSG/RSC/CSR/ISR), Feature-Sliced Design, Bulletproof React, **modular domain architecture** (auth, user, product modules), monorepo, scaffolding a new project, architecture decisions                                              |
| `references/react-patterns.md`      | Building components, custom hooks, compound components, container/presentational, render props, state reducer, controlled/uncontrolled, React Server Components boundaries, component API design, composition strategies, and broader React 19 component patterns                                   |
| `references/react-hooks.md`         | Choosing the right built-in hook, hook semantics, hook timing, stale closure problems, form/action hooks, optimistic UI, transitions, deferred rendering, `useEffectEvent`, and practical React 19.2 hook guidance                                                                                  |
| `references/state-management.md`    | State management, data fetching, TanStack Query, Zustand, Jotai, Redux, React Hook Form, Zod, URL state, form validation, caching, optimistic updates                                                                                                                                               |
| `references/performance.md`         | Core Web Vitals, Lighthouse score, bundle size, code splitting, lazy loading, re-renders, memoization, React Compiler, image optimization, SSR streaming, profiling, **Partial Pre-rendering**, **Performance Tracks**                                                                              |
| `references/testing.md`             | Writing tests, test strategy, Vitest, React Testing Library, Playwright, MSW, E2E testing, unit testing, integration testing, what to test, test setup                                                                                                                                              |
| `references/quality.md`             | TypeScript strict config, ESLint, Prettier, **naming conventions (PascalCase components, kebab-case everything else)**, **file content rules (helpers separate, one component per file)**, file structure, accessibility (a11y), security, error handling, API layer design, code review guidelines |
| `references/libraries/<library>.md` | A versioned local cache for a specific frontend library. Read this first for library-specific guidance when it exists, then fall back to the generic domain reference files.                                                                                                                        |

**Read multiple references** when the task spans domains. For example:

- "Build a data table component" → react-patterns.md + state-management.md + performance.md
- "Set up a new Next.js project" → architecture.md + quality.md
- "Review this component" → react-patterns.md + quality.md + testing.md
- "Choose between useEffect, useLayoutEffect, and useEffectEvent" → `references/react-hooks.md` +
  `references/react-patterns.md`
- "Work with React 19 form and action hooks" → `references/react-hooks.md` + `references/state-management.md`
- "Set up Next.js App Router patterns" → `references/libraries/nextjs.md` + `next-best-practices`
- "Build or theme shadcn/ui components" → `references/libraries/shadcn-ui.md` + `shadcn` + `tailwind-design-system`
- "Fix hard TypeScript inference issues" → `references/state-management.md` + `typescript-advanced-types`
- "Design stable Playwright coverage" → `references/testing.md` + `e2e-testing-patterns`

## Core Principles (apply to ALL responses)

### 1. Opinionated defaults — deviate with reason

These are the defaults for 2025/2026. Deviate only when the user's context demands it.

| Decision       | Default                    | Deviate when...                                         |
|----------------|----------------------------|---------------------------------------------------------|
| Framework      | Next.js App Router         | No SSR needed → Vite + React Router                     |
| Language       | TypeScript strict          | Never use plain JS                                      |
| Rendering      | SSR + RSC                  | Internal tools → CSR; static content → SSG              |
| State (server) | TanStack Query             | Full-stack TS → tRPC; simple → SWR                      |
| State (client) | Zustand                    | Atomic needs → Jotai; enterprise → Redux Toolkit        |
| Styling        | Tailwind CSS               | Token-heavy design system → CSS Modules + CSS Variables |
| Forms          | React Hook Form + Zod      | Server-action-heavy → Conform                           |
| Testing        | Vitest + RTL + Playwright  | Legacy → Jest; team prefers → Cypress                   |
| UI Primitives  | shadcn/ui (Radix-based)    | Enterprise → MUI/Ant Design                             |
| Build          | Turbopack (Next.js) / Vite | —                                                       |

### 2. Simplicity-first escalation

Always start with the simplest approach that works, then escalate only when pain is real:

```
useState → useReducer → Context → Zustand → Redux
```

```
Flat folders → Bulletproof React → Feature-Sliced Design → Micro-frontends
```

```
CSS Modules → Tailwind → Vanilla Extract → CSS-in-JS runtime
```

### 3. Separation of concerns

- **Server state ≠ Client state** — Never put API data in Zustand/Redux. Use TanStack Query.
- **UI ≠ Logic** — Extract business logic into custom hooks. Keep components as thin renderers.
- **Server ≠ Client components** — Default to Server Components. Only add `'use client'` for interactivity.

### 4. Type safety is non-negotiable

- TypeScript strict mode on every project
- Zod for runtime validation (API responses, form inputs, env vars)
- Generics for reusable utilities and hooks
- No `any` — use `unknown` + narrowing when type is truly unknown

### 5. Test behavior, not implementation

- Query by role, text, label — never by CSS class or test ID (unless no semantic option)
- Integration tests are the highest-value tests (Testing Trophy model)
- E2E only for critical user flows (login, checkout, signup)
- MSW for API mocking — consistent across test types

### 6. Performance is a feature

- Measure before optimizing (React DevTools Profiler, Lighthouse)
- Core Web Vitals targets: LCP < 2.5s, INP < 200ms, CLS < 0.1
- Code splitting at route level minimum, component level when large
- Images: Next.js `<Image>`, explicit dimensions, priority for above-fold

### 7. Accessibility is not optional

- Semantic HTML first (nav, main, article, section)
- Keyboard navigation for all interactive elements
- ARIA only when semantic HTML isn't sufficient
- Color contrast ≥ 4.5:1, respect `prefers-reduced-motion`

## Response guidelines

When answering frontend questions:

1. **Be specific** — Give concrete code, file paths, and config. Not vague advice.
2. **Show the "why"** — Explain trade-offs, not just "do X". Engineers need to understand decisions.
3. **Production-grade** — Include error handling, loading states, TypeScript types, edge cases.
4. **Context-aware** — Ask about project size, team size, and constraints before recommending architecture.
5. **Provide alternatives** — Mention when a simpler or different approach might be better for their case.

## Quick decision trees

### "How should I structure this project?"

```
Team size?
├── Solo / 1-2 devs, < 5 pages → Flat structure (see architecture.md §2.d)
├── 2-5 devs, 5-20 pages → Modular Architecture (see architecture.md §2.b) ← default
├── 3-5 devs, many domains → FSD (see architecture.md §2.a) or Modular
└── 5+ devs, multi-team → FSD full or Micro-frontends (see architecture.md §4)
```

### "What state management should I use?"

```
What kind of state?
├── API/server data → TanStack Query (see state-management.md §1)
├── URL params → nuqs or useSearchParams (see state-management.md §3)
├── Form inputs → React Hook Form + Zod (see state-management.md §4)
├── Simple UI state → useState / useReducer
└── Shared client state → Zustand (see state-management.md §2)
```

### "How should I test this?"

```
What are you testing?
├── Pure function / util → Unit test with Vitest (see testing.md §2)
├── Component behavior → RTL + Vitest (see testing.md §3)
├── Component + API → Integration test + MSW (see testing.md §4)
├── Critical user flow → E2E with Playwright (see testing.md §5)
└── Visual consistency → Storybook + Chromatic (see testing.md §6)
```

### "This is slow, how do I fix it?"

```
What's slow?
├── Initial page load → Check bundle size, code splitting (see performance.md §2)
├── Interactions feel laggy → Check re-renders, memoization (see performance.md §3)
├── Images load slowly → Next.js Image, lazy loading (see performance.md §4)
├── Data fetching → Parallel fetching, prefetch, staleTime (see performance.md §5)
└── Not sure → Run Lighthouse + React Profiler first (see performance.md §1)
```
