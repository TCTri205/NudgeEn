---
library: tanstack react query
package: "@tanstack/react-query"
context7_library_id: /tanstack/query
synced_version: v5.90.3
project_version: unknown
declared_range: unknown
benchmark_score: 85.07
source_reputation: High
last_synced: 2026-03-21
coverage: queryclient, provider, usequery, usemutation, query-keys, invalidation, optimistic-updates, staleTime, gcTime, ssr, hydration, typescript
project_version_notes: Seeded without a local project manifest. Refresh before using in a real repo.
---

# TanStack React Query

## Version Match Rule

- This cache is synced to official TanStack Query docs version `v5.90.3`.
- Match it against the real `@tanstack/react-query` version in the project before using it as the
  local source of truth.
- If the project version differs, rerun `library-sync` and replace this file.

## What This Cache Covers

- `QueryClient` creation and provider setup
- `useQuery` and `useMutation` basics
- query invalidation and optimistic updates
- `staleTime` and `gcTime`
- SSR and hydration-oriented configuration guidance
- key migration note from `cacheTime` to `gcTime`

## Recommended Patterns

- Create one stable `QueryClient` at the app root and provide it through `QueryClientProvider`.
- Use structured query keys consistently so invalidation stays predictable.
- Keep server state in React Query instead of duplicating it into Zustand or other client state.
- For SSR-capable apps, set a non-zero default `staleTime` to avoid immediate client refetch after
  hydration.
- Treat optimistic updates as a controlled workflow: cancel, snapshot, patch, rollback, invalidate.

## Queries And Mutations

- `useQuery` is the standard read path and should handle pending and error states explicitly.
- `useMutation` plus `onSettled` is the standard write path when the UI should refetch affected
  queries after completion.
- For optimistic writes, the docs show this order:
    - cancel in-flight queries for the target key
    - snapshot previous cached data
    - patch the cache optimistically
    - rollback in `onError`
    - invalidate in `onSettled`
- When invalidating inside mutation lifecycle callbacks, return the invalidation Promise so the
  mutation can remain pending until refetch completes.

## Caching, SSR, And Hydration

- `staleTime` controls freshness; with SSR, docs recommend setting it above `0` so the client does
  not refetch immediately after hydration.
- `gcTime` is the v5 name for the old `cacheTime` option and controls garbage collection for unused
  query data.
- SSR setup still centers on a stable root `QueryClientProvider`, with defaults tuned to avoid noisy
  refetch behavior.
- Query behavior should be tuned per data volatility rather than by one global number for every key.

## Organization And Integration

- Keep query keys colocated with the feature or API module that owns the data contract.
- Make invalidation rules explicit near each mutation instead of hiding them in generic helpers.
- React Query should own remote data synchronization; use local state libraries only for UI state or
  draft form state.

## Migration Notes

- v5 renames `cacheTime` to `gcTime`.
- Older mental models around “cache lifetime” should be updated: `gcTime` only matters once a query
  becomes unused.
- If you are migrating from older React Query examples, verify status field names and mutation/query
  options against the current docs before copying code.

## Known Gaps

- This cached pass did not capture a full Next.js-specific hydration example or advanced utilities
  like infinite queries, suspense, or streaming integration.
- If the project depends on server rendering with prefetch/dehydrate flows, refresh this cache with
  a Next.js-focused TanStack Query query first.

## Source Index

- Context7 library: `/tanstack/query` version `v5.90.3`
- React overview:
  [docs/framework/react/overview.md](https://github.com/tanstack/query/blob/v5.90.3/docs/framework/react/overview.md)
- SSR guide:
  [docs/framework/react/guides/ssr.md](https://github.com/tanstack/query/blob/v5.90.3/docs/framework/react/guides/ssr.md)
- Optimistic updates guide:
  [docs/framework/react/guides/optimistic-updates.md](https://github.com/tanstack/query/blob/v5.90.3/docs/framework/react/guides/optimistic-updates.md)
- Migration guide:
  [docs/framework/react/guides/migrating-to-v5.md](https://github.com/tanstack/query/blob/v5.90.3/docs/framework/react/guides/migrating-to-v5.md)
