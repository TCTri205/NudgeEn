---
library: shadcn/ui
package: shadcn
context7_library_id: /shadcn-ui/ui
synced_version: shadcn_3.5.0
project_version: unknown
declared_range: unknown
benchmark_score: 78.63
source_reputation: High
last_synced: 2026-03-21
coverage: cli, init, add-components, ownership-model, theming, tailwind, radix, accessibility, nextjs, maintenance
project_version_notes: Seeded without a local project manifest. Refresh before using in a real repo.
---

# shadcn/ui

## Version Match Rule

- This cache is synced to official shadcn/ui docs version `shadcn_3.5.0`.
- Match it against the real shadcn CLI or registry version in the project before relying on it.
- If the project uses a different generation of shadcn/ui config or component registry, rerun
  `library-sync` and replace this file.

## What This Cache Covers

- project initialization with the CLI
- adding components with the CLI
- code ownership model
- theming configuration and CSS variable choices
- Tailwind and Radix expectations
- Next.js dark mode integration pattern

## Recommended Patterns

- Treat shadcn/ui as source code you own, not as a black-box dependency.
- Add only the components the project actually needs instead of dumping the full registry.
- Keep generated component code aligned with the project’s aliases, Tailwind config, and theme
  strategy.
- Use the CLI as the canonical path for init and component sync unless the project has a deliberate
  custom registry workflow.

## CLI, Ownership, And Theming

- `npx shadcn init` is the base initialization flow.
- The CLI supports:
    - interactive init
    - `--defaults`
    - template and base-color flags
    - adding components during init
- `npx shadcn add <component>` is the base flow for importing components.
- The docs emphasize that components are copied into your codebase, which means the team owns the
  code and can modify it freely.
- The theming docs show a `components.json` structure that controls aliases, base color, CSS
  variables, and icon library selection.
- If `tailwind.cssVariables` is disabled, theming falls back to direct utility-class styling.

## Composition And Maintenance

- shadcn/ui expects Tailwind CSS and Radix-based composition patterns.
- Because the code lives in-repo, maintenance is a source-management problem rather than a pure
  package-upgrade problem.
- Updating components should be handled carefully when the team has already customized local copies.
- In Next.js layouts, the documented dark-mode pattern wraps the tree in a `ThemeProvider` and uses
  `suppressHydrationWarning` on the root `html` tag.

## Migration Notes

- The biggest migration risk is not an API import break; it is drift between your local copied
  components and newer registry output.
- Before refreshing components, diff local customizations and theme primitives so the CLI does not
  silently overwrite deliberate design-system changes.

## Known Gaps

- This cached pass did not capture a full registry authoring workflow, advanced form composition, or
  RSC-specific component boundary guidance.
- If the project uses custom registries, monorepo component sharing, or heavy design-token
  customization, refresh this cache with narrower shadcn/ui queries first.

## Source Index

- Context7 library: `/shadcn-ui/ui` version `shadcn_3.5.0`
- CLI init and add commands:
  [Context7 llms.txt summary](https://context7.com/shadcn-ui/ui/llms.txt)
- Theming docs:
  [apps/www/content/docs/theming.mdx](https://github.com/shadcn-ui/ui/blob/shadcn@3.5.0/apps/www/content/docs/theming.mdx)
- Next.js dark mode integration:
  [apps/v4/content/docs/dark-mode/next.mdx](https://github.com/shadcn-ui/ui/blob/shadcn@3.5.0/apps/v4/content/docs/dark-mode/next.mdx)
