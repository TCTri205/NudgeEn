---
library: tailwind css v4
package: "tailwindcss"
context7_library_id: null
synced_version: v4.1.18
project_version: v4.1.18
declared_range: ^4.1.18
benchmark_score: null
source_reputation: High
last_synced: 2026-03-21
coverage: CSS-first config, @theme, @import, Vite plugin, dark mode, custom utilities, breaking changes from v3
notes: Context7 does not have a Tailwind CSS v4 index. Content from official docs + release notes.
---

# Tailwind CSS v4

**Major rewrite** released Jan 2025. CSS-first configuration replaces `tailwind.config.js`. Up to 5× faster full builds,
100× faster incremental.

## Breaking Changes from v3

| v3                                    | v4                                        |
|---------------------------------------|-------------------------------------------|
| `tailwind.config.js` required         | No config file needed (optional)          |
| `@tailwind base/components/utilities` | `@import "tailwindcss"`                   |
| `theme.extend.colors.brand`           | `@theme { --color-brand: ... }`           |
| `darkMode: 'class'`                   | `@variant dark (&:where(.dark, .dark *))` |
| `content: [...]`                      | Auto-detected (no config needed)          |
| `plugins: [...]`                      | `@plugin` directive                       |
| `screens.sm: '640px'`                 | `@theme { --breakpoint-sm: 640px; }`      |

## Setup with Vite (@tailwindcss/vite)

```ts
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [tailwindcss()],
})
```

```css
/* src/styles.css */
@import "tailwindcss";
```

That's it — no `tailwind.config.js` needed.

## CSS-First Configuration with @theme

```css
/* src/styles.css */
@import "tailwindcss";

@theme {
  /* Custom colors → generates text-brand, bg-brand, etc. */
  --color-brand: #4fb8b2;
  --color-brand-dark: #3a9a95;

  /* Custom fonts → generates font-display, etc. */
  --font-display: "Inter", sans-serif;

  /* Custom spacing → generates p-18, m-18, etc. */
  --spacing-18: 4.5rem;

  /* Custom breakpoints */
  --breakpoint-xs: 480px;

  /* Custom border radius */
  --radius-pill: 9999px;
}
```

Generated utilities:

- `--color-brand` → `text-brand`, `bg-brand`, `border-brand`, `fill-brand`, etc.
- `--font-display` → `font-display`
- `--spacing-18` → `p-18`, `m-18`, `gap-18`, etc.

## Custom CSS Variables as Tailwind Utilities

```css
@theme {
  /* This project's color palette */
  --color-sea-ink: #173a40;
  --color-lagoon: #4fb8b2;
  --color-palm: #2f6a4a;
  --color-sand: #e7f0e8;
  --color-foam: #f3faf5;
}
```

Usage: `text-sea-ink`, `bg-lagoon`, `border-palm`, etc.

## Dark Mode

```css
/* src/styles.css — configure dark variant */
@import "tailwindcss";

@variant dark (&:where(.dark, .dark *));
```

```tsx
// Works same as v3
<div className="bg-white dark:bg-gray-900">
  <p className="text-gray-900 dark:text-white">Content</p>
</div>
```

## Custom Utilities with @utility

```css
@utility container {
  width: 100%;
  max-width: 1280px;
  margin-inline: auto;
  padding-inline: 1rem;
}

@utility truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

## Plugins with @plugin

```css
@import "tailwindcss";
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";
```

## Container Queries (built-in in v4)

```html
<div class="@container">
  <div class="@sm:grid-cols-2 @lg:grid-cols-4 grid grid-cols-1">
    <!-- responsive to container width, not viewport -->
  </div>
</div>
```

## Arbitrary Values (same as v3)

```html
<div class="w-[327px] bg-[#1da1f2] text-[clamp(1rem,2vw,1.5rem)]">
```

## CSS Variables in Utilities

```css
@theme {
  --color-primary: oklch(0.55 0.2 240);
}
```

```html
<!-- Access as CSS variable -->
<div style="color: var(--color-primary)">
<!-- Or as Tailwind utility -->
<div class="text-primary">
```

## Key v4 Utilities Added

```html
<!-- Field sizing -->
<input class="field-sizing-content" />

<!-- Color mix -->
<div class="bg-blue-500/50">  <!-- opacity still works -->

<!-- Logical properties (new) -->
<div class="ms-4 me-4 ps-4 pe-4">  <!-- margin/padding start/end -->

<!-- Not variant -->
<div class="not-[:focus]:opacity-50">

<!-- Starting style (enter animations) -->
<div class="starting:opacity-0 transition-opacity">
```

## Upgrade from v3

```bash
# Install official upgrade tool
pnpm dlx @tailwindcss/upgrade@next
```

Manual steps:

1. Replace `@tailwind base/components/utilities` with `@import "tailwindcss"`
2. Move `tailwind.config.js` `theme.extend` → `@theme {}` in CSS
3. Replace `bg-opacity-*` with `bg-*/50` (or `bg-*/[0.5]`)
4. Remove `content: [...]` (auto-detected now)
