---
library: next.js
package: next
context7_library_id: /vercel/next.js
synced_version: v16.1.6
project_version: unknown
declared_range: unknown
benchmark_score: 84.6
source_reputation: High
last_synced: 2026-03-21
coverage: app-router, server-components, client-components, fetch, caching, revalidation, route-handlers, server-actions, deployment
project_version_notes: Seeded without a local project manifest. Refresh before using in a real repo.
---

# Next.js

## Version Match Rule

- This cache is synced to official Next.js docs version `v16.1.6`.
- Match it against the real `next` version in the project before treating it as authoritative.
- If the project uses a different major or minor version, rerun `library-sync` and replace this
  file.

## What This Cache Covers

- App Router architecture
- Server Component and Client Component boundaries
- `fetch`-based data fetching in route segments
- caching, `no-store`, and `revalidate`
- Route Handlers and caching behavior
- Server Actions and form-driven redirects
- runtime and deployment-sensitive choices

## Recommended Patterns

- Default to the App Router for new work.
- Keep data fetching in Server Components whenever interactivity is not required.
- Move only interactive islands to Client Components instead of marking large trees with
  `'use client'`.
- Use the built-in `fetch` semantics first before introducing an extra client-side data layer.
- Treat Route Handlers, Server Actions, and page/layout components as different boundaries with
  different caching and runtime behavior.

## App Router And Boundaries

- In App Router, `page.tsx` files are Server Components by default.
- A common pattern is:
    - fetch data in a Server Component
    - pass the result into a smaller Client Component when interaction is needed
- This keeps data access on the server while preserving client-side interactivity only where needed.
- Use Client Components deliberately, because they move code and state to the browser.

## Data Fetching And Caching

- Next.js App Router uses standard `fetch()` with cache semantics instead of the old
  `getStaticProps` / `getServerSideProps` mental model.
- The docs highlight three core modes:
    - `cache: 'force-cache'` for static caching
    - `cache: 'no-store'` for per-request fetching
    - `next: { revalidate: <seconds> }` for timed revalidation
- `force-cache` is documented as the default for the static case.
- Revalidation should be chosen intentionally per fetch instead of treated as a global default.

## Runtime And Deployment

- Route Handler `GET` functions are not cached by default in the cited upgrade guidance.
- If you need a cached static `GET` handler, export `const dynamic = 'force-static'`.
- Server Actions are a first-class path for form submissions and server-side redirects.
- Deployment decisions should respect whether a route needs static output, per-request work, or a
  bounded revalidation window.

## Migration Notes

- App Router guidance replaces the older split between `getStaticProps` and `getServerSideProps`
  with `fetch` caching semantics inside Server Components.
- If you are migrating older code, do not mechanically port everything into Client Components.
- Re-check Route Handler caching expectations because recent Next.js versions changed defaults.

## Known Gaps

- This cached pass did not capture a dedicated SSR streaming, Partial Prerendering, or edge-runtime
  deep dive from Context7.
- If the project relies heavily on middleware, edge execution, image optimization, or RSC cache
  invalidation APIs, refresh this cache with narrower Next.js queries first.

## Source Index

- Context7 library: `/vercel/next.js` version `v16.1.6`
- App Router migration guide:
  [docs/01-app/02-guides/migrating/app-router-migration.mdx](https://github.com/vercel/next.js/blob/v16.1.6/docs/01-app/02-guides/migrating/app-router-migration.mdx)
- `redirect` function and Server Actions:
  [docs/01-app/03-api-reference/04-functions/redirect.mdx](https://github.com/vercel/next.js/blob/v16.1.6/docs/01-app/03-api-reference/04-functions/redirect.mdx)
- Upgrading to version 15, Route Handler caching note:
  [docs/01-app/02-guides/upgrading/version-15.mdx](https://github.com/vercel/next.js/blob/v16.1.6/docs/01-app/02-guides/upgrading/version-15.mdx)
