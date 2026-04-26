---
library: zustand
package: zustand
context7_library_id: /pmndrs/zustand
synced_version: v5.0.12
project_version: unknown
declared_range: unknown
benchmark_score: 80.77
source_reputation: High
last_synced: 2026-03-21
coverage: core-api, typescript, selectors, equality, migration, middleware, slices, vanilla
project_version_notes: Seeded without a local project manifest. Refresh before using in a real repo.
---

# Zustand

## Version Match Rule

- This cache is currently synced to official Zustand docs version `v5.0.12`.
- Match it against the real project version before using it as authoritative local guidance.
- If the project resolves to a different version, rerun `library-sync` with Context7 and replace
  this file before relying on it.
- If Context7 does not expose the exact project version, sync to the nearest official version and
  record the gap in frontmatter and `Known Gaps`.

## What This Cache Covers

- core store creation with `create` and `createStore`
- TypeScript store typing with state and actions
- narrow selectors for React components
- `useShallow`, `shallow`, and v4 -> v5 migration behavior
- middleware patterns: `persist`, `devtools`, `immer`, `redux`
- combined stores with the slices pattern

## Recommended Patterns

- Prefer the curried TypeScript form `create<State>()((set) => ({ ... }))`.
- Model stores as explicit `state + actions` interfaces.
- Use separate stores for independent domains instead of merging unrelated state by default.
- In React components, select the smallest slice possible, for example
  `useStore((state) => state.bears)`.
- External module-level actions using `useStore.setState(...)` are supported and useful for code
  splitting, but they trade away colocated action encapsulation.
- Use `createStore` from `zustand/vanilla` when the store must exist outside React.

## Selectors And Equality

- Zustand v5 expects stable selector outputs. Returning a fresh object or array from a selector can
  cause rerender problems and, in some migration cases, infinite loops.
- For selectors that return objects or arrays, prefer `useShallow(...)` so shallow-equal outputs do
  not trigger unnecessary rerenders.
- The v5 default `create` API does not accept custom equality functions the same way many v4
  examples did.
- If you truly need custom equality at the hook level, use `createWithEqualityFn` from
  `zustand/traditional`.
- The docs show both object-pick and array-pick patterns with `useShallow`.

## Middleware And Organization

- Wrap `persist(...)` around the combined store so persistence happens at the full-store boundary.
- `devtools(...)` works with the slices pattern and benefits from explicit action names.
- `immer(...)` is the documented shortcut for mutable-style nested updates while preserving
  immutable state semantics.
- `redux(...)` is available when reducer-style action dispatch is a better fit than store-local
  actions.
- The slices pattern combines multiple `StateCreator` functions into one store; middleware should be
  applied at the combined store rather than inside individual slices.

## Migration Notes

- A common v4 pattern passed `shallow` as a custom equality function directly to store hooks.
- In v5, the easiest migration paths are:
    - switch to `createWithEqualityFn` from `zustand/traditional`
    - or keep the default `create` API and use `useShallow(...)` for array/object selectors
- The migration docs note that `createWithEqualityFn` requires `use-sync-external-store` as a peer
  dependency.
- The migration guide explicitly calls out stable selector outputs as a behavioral change in v5.
- If a selector returns a fresh reference every render, fix that before assuming the issue is in
  React.

## Known Gaps

- This cached pass did not capture a dedicated SSR or hydration-specific snippet from Context7.
- If the project depends on SSR persistence, React Server Components boundaries, or framework-specific
  hydration behavior, refresh this cache with an SSR-focused Context7 query before making strong
  recommendations.

## Source Index

- Context7 library: `/pmndrs/zustand` version `v5.0.12`
- Beginner TypeScript guide:
  [docs/learn/guides/beginner-typescript.md](https://github.com/pmndrs/zustand/blob/v5.0.12/docs/learn/guides/beginner-typescript.md)
- Practice with no store actions:
  [docs/learn/guides/practice-with-no-store-actions.md](https://github.com/pmndrs/zustand/blob/v5.0.12/docs/learn/guides/practice-with-no-store-actions.md)
- `createStore` API:
  [docs/reference/apis/create-store.md](https://github.com/pmndrs/zustand/blob/v5.0.12/docs/reference/apis/create-store.md)
- Migration guide:
  [docs/reference/migrations/migrating-to-v5.md](https://github.com/pmndrs/zustand/blob/v5.0.12/docs/reference/migrations/migrating-to-v5.md)
- Slices pattern:
  [docs/learn/guides/slices-pattern.md](https://github.com/pmndrs/zustand/blob/v5.0.12/docs/learn/guides/slices-pattern.md)
- Devtools middleware:
  [docs/reference/middlewares/devtools.md](https://github.com/pmndrs/zustand/blob/v5.0.12/docs/reference/middlewares/devtools.md)
- Redux middleware:
  [docs/reference/middlewares/redux.md](https://github.com/pmndrs/zustand/blob/v5.0.12/docs/reference/middlewares/redux.md)
- README:
  [README.md](https://github.com/pmndrs/zustand/blob/v5.0.12/README.md)
