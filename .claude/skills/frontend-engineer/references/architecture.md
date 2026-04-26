# Architecture Reference

## Table of contents

- §1 Rendering Strategy Decision
- §2 Project Structure Patterns
- §3 Architecture Decision Framework
- §4 Monorepo Strategy
- §5 Modular Domain Architecture (Alternative to FSD)

---

## §1 Rendering Strategy Decision

### Decision matrix

| Strategy                | Best for                                            | Trade-offs                                         |
|-------------------------|-----------------------------------------------------|----------------------------------------------------|
| **CSR**                 | SPA, dashboard, internal tools, heavy interactivity | Large bundle, poor SEO, slow TTFB                  |
| **SSR**                 | E-commerce, content + SEO, social sharing           | Server load, hydration gap, TTFB depends on server |
| **SSG**                 | Blog, docs, marketing, portfolio                    | Slow builds at scale, stale data without ISR       |
| **ISR**                 | Product catalogs, news sites                        | Stale window during revalidation                   |
| **RSC**                 | Content-heavy + interactive mix, data colocation    | Ecosystem still maturing, learning curve           |
| **Island Architecture** | Content sites with minimal JS (Astro)               | Not suited for complex SPA                         |
| **Streaming SSR**       | Large apps, progressive loading                     | Requires thoughtful Suspense boundary design       |

### Decision rule

Default to **SSR + RSC** via Next.js App Router for most production apps. This gives you:

- SEO out of the box
- Server-side data fetching (no API routes needed for reads)
- Streaming with Suspense for progressive loading
- Client components only where interactivity is needed

Deviate when:

- **Pure internal tool / dashboard** → CSR is fine (Vite + React Router)
- **Content-heavy, minimal JS** → Astro with Islands or Next.js SSG
- **Hybrid** → Modern frameworks let you mix strategies per route. Use SSG for marketing pages, SSR for dynamic pages,
  CSR for dashboard sections — all in the same app.

### Next.js App Router conventions

```
app/
├── layout.tsx          # Root layout (Server Component by default)
├── page.tsx            # Home page
├── loading.tsx         # Suspense fallback for this route segment
├── error.tsx           # Error boundary for this route segment
├── not-found.tsx       # 404 page
├── (marketing)/        # Route group (no URL impact)
│   ├── about/page.tsx
│   └── pricing/page.tsx
├── dashboard/
│   ├── layout.tsx      # Nested layout with sidebar
│   ├── page.tsx
│   └── settings/page.tsx
└── api/                # API routes (when needed)
    └── webhooks/route.ts
```

Key rules:

- `layout.tsx` = persistent UI across child routes (does NOT re-render on navigation)
- `loading.tsx` = auto-wrapped in `<Suspense>` — free streaming
- `error.tsx` = auto-wrapped in Error Boundary — granular error recovery
- Route groups `(name)` organize code without affecting URL
- `page.tsx` files are the only files that make a route publicly accessible

---

## §2 Project Structure Patterns

### §2.a Feature-Sliced Design (FSD) — for medium-to-large projects

```
src/
├── app/              # App initialization, providers, routing, global config
│   ├── providers/    # QueryClientProvider, ThemeProvider, etc.
│   ├── styles/       # Global styles, Tailwind config
│   └── index.tsx     # App entry
│
├── pages/            # Page compositions — compose widgets + features
│   ├── home/
│   │   ├── ui/
│   │   │   └── HomePage.tsx
│   │   ├── model/
│   │   │   └── useHomeData.ts
│   │   └── index.ts  # Public API
│   └── product-detail/
│       ├── ui/
│       └── index.ts
│
├── widgets/          # Complex reusable UI blocks (composed from features + entities)
│   ├── header/
│   │   ├── ui/
│   │   │   └── Header.tsx
│   │   └── index.ts
│   └── product-reviews/
│
├── features/         # User interaction slices (one action = one feature)
│   ├── add-to-cart/
│   │   ├── ui/
│   │   │   └── AddToCartButton.tsx
│   │   ├── model/
│   │   │   └── useAddToCart.ts
│   │   ├── api/
│   │   │   └── cartApi.ts
│   │   └── index.ts
│   ├── auth-login/
│   └── search-products/
│
├── entities/         # Business domain models
│   ├── user/
│   │   ├── ui/
│   │   │   └── UserAvatar.tsx
│   │   ├── model/
│   │   │   ├── types.ts
│   │   │   └── useUser.ts
│   │   ├── api/
│   │   │   └── userApi.ts
│   │   └── index.ts
│   ├── product/
│   └── order/
│
└── shared/           # Reusable infrastructure (NO business logic)
    ├── ui/           # Design system components (Button, Input, Modal)
    ├── api/          # API client, interceptors, base config
    ├── lib/          # Utility functions (formatDate, cn, debounce)
    ├── config/       # Environment variables, constants
    └── types/        # Global TypeScript types
```

**FSD dependency rule (strict, one-directional):**

```
app → pages → widgets → features → entities → shared
```

- A layer can import from any layer BELOW it, never from above or same level
- Enforce with `eslint-plugin-boundaries`
- Each slice exposes only its public API via `index.ts`

**Segments within each slice:**

- `ui/` — React components
- `model/` — State, hooks, business logic, TypeScript types
- `api/` — API calls for this slice
- `lib/` — Helper functions specific to this slice
- `config/` — Constants, feature flags

**When NOT to use FSD:**

- Project < 5 pages or team < 3 developers — overhead not worth it
- MVP / prototype that needs to ship in days — use flat structure
- Adopt gradually: start with `shared/` + `features/`, add layers as complexity grows

### §2.b Modular Architecture — for medium projects (recommended default)

Organize by domain/module. Each module is self-contained with its own components, hooks, API, types.
This is simpler than FSD while still domain-driven.

```
src/
├── app/                   # Next.js app directory (routing, layouts)
│   ├── (auth)/            # Route group: login, register, forgot-password
│   ├── (dashboard)/       # Route group: dashboard pages
│   ├── layout.tsx
│   └── providers.tsx
│
├── modules/               # Domain modules (the heart of the app)
│   ├── auth/
│   │   ├── components/    # Auth-specific components
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── AuthGuard.tsx
│   │   ├── hooks/
│   │   │   ├── use-auth.ts
│   │   │   └── use-session.ts
│   │   ├── services/
│   │   │   └── auth-api.ts
│   │   ├── types/
│   │   │   └── auth.types.ts
│   │   ├── helpers/
│   │   │   └── token-utils.ts
│   │   └── index.ts       # Public API — only export what other modules need
│   │
│   ├── user/
│   │   ├── components/
│   │   │   ├── UserAvatar.tsx
│   │   │   ├── UserCard.tsx
│   │   │   └── UserProfileForm.tsx
│   │   ├── hooks/
│   │   │   └── use-user.ts
│   │   ├── services/
│   │   │   └── user-api.ts
│   │   ├── types/
│   │   │   └── user.types.ts
│   │   └── index.ts
│   │
│   ├── product/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── helpers/
│   │   ├── types/
│   │   └── index.ts
│   │
│   └── order/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       ├── types/
│       └── index.ts
│
├── shared/                # Cross-module shared code (NO business logic)
│   ├── components/        # Design system: Button, Input, Modal, Card, Badge
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   └── Input.tsx
│   │   └── layout/
│   │       ├── PageLayout.tsx
│   │       └── Sidebar.tsx
│   ├── hooks/             # Generic hooks (use-debounce, use-media-query)
│   ├── lib/               # Library configs (query-client, axios, cn utility)
│   ├── helpers/           # Pure utility functions (format-date, format-currency)
│   ├── types/             # Global types (api-response, pagination)
│   └── config/            # Constants, env vars
│
└── styles/                # Global styles, Tailwind config
```

**Module rules:**

- Each module has an `index.ts` that exports ONLY its public API
- Modules can import from `shared/` freely
- Cross-module imports go through `index.ts` (never reach into another module's internals)
- If two modules need the same code → move it to `shared/`
- Pages (in `app/`) compose modules — they are thin orchestration layers

**File naming rules (strict):**

- Components: **PascalCase** → `LoginForm.tsx`, `UserAvatar.tsx`
- Everything else: **kebab-case** → `use-auth.ts`, `auth-api.ts`, `token-utils.ts`, `user.types.ts`
- Folders: **kebab-case** → `modules/`, `shared/`, `components/`
- Test files: same name + `.test` → `LoginForm.test.tsx`, `use-auth.test.ts`
- No `index.tsx` for components — use explicit names for findability

**Separation rules (strict):**

- Helper/utility functions → `helpers/` folder, NEVER define in a component file
- API calls → `services/` folder, NEVER inline `fetch` in components
- Types → `types/` folder or co-located `.types.ts`, NEVER in component files
- Constants → `config/` or module-level `constants.ts`
- Hooks → `hooks/` folder, one hook per file
- A file's content must match its name — `UserCard.tsx` only contains UserCard component

### §2.c Bulletproof React — alternative for medium projects

```
src/
├── assets/            # Images, fonts, static files
├── components/        # Shared, reusable UI components
│   ├── ui/            # Primitives (Button, Input, Badge)
│   └── layout/        # Layout components (PageLayout, Sidebar)
├── features/          # Feature-based modules
│   ├── auth/
│   │   ├── components/ # Feature-specific components
│   │   ├── hooks/      # Feature-specific hooks
│   │   ├── api/        # Feature-specific API calls
│   │   ├── types/      # Feature-specific types
│   │   └── index.ts    # Public API
│   ├── products/
│   └── orders/
├── hooks/             # Global shared hooks
├── lib/               # Library configs (queryClient, axios instance)
├── pages/             # Route pages (thin — just compose features)
├── providers/         # App-level context providers
├── routes/            # Route definitions
├── stores/            # Global state stores (Zustand)
├── types/             # Global TypeScript types
└── utils/             # Pure utility functions
```

Simpler than FSD but still feature-organized. Good middle ground.

### §2.c Flat structure — for small projects / MVP

```
src/
├── components/        # All components
├── hooks/             # All custom hooks
├── pages/             # Route pages
├── services/          # API calls
├── utils/             # Utilities
├── types/             # TypeScript types
└── styles/            # Global styles
```

No ceremony. Ship fast. Refactor to Bulletproof/FSD when pain appears.

---

## §3 Architecture Decision Framework

### By project characteristics

| Signal                                  | Recommendation                         |
|-----------------------------------------|----------------------------------------|
| Solo dev, < 5 pages, ship in days       | Flat structure, CSR or SSG             |
| Small team (2-3), product growing       | **Modular architecture**, SSR          |
| Team 3-5, 10+ pages, multiple domains   | Modular or FSD (simplified), SSR + RSC |
| 5+ devs, multi-team, enterprise         | FSD full or Micro-frontends, SSR + RSC |
| Content site with minimal interactivity | Astro or Next.js SSG                   |
| Internal dashboard / admin panel        | CSR (Vite), Flat or Modular            |

### When to adopt micro-frontends

Only when ALL of these are true:

- Multiple teams (3+) working on the same frontend
- Teams need independent deployment cycles
- App is large enough that build times are a bottleneck
- You have platform engineering support for the infrastructure

Tools: Module Federation (webpack/rspack), Single-SPA, or Turborepo with separate apps.

**Do NOT adopt micro-frontends because:**

- Your app is "large" (FSD handles scale fine for single-team)
- You want to use different frameworks (this is almost never worth the complexity)
- Someone read an article about it

---

## §4 Monorepo Strategy

### When to use monorepo

- Shared design system across multiple apps (web, admin, mobile-web)
- Shared TypeScript types between frontend and backend
- Team wants atomic commits across packages

### Turborepo structure

```
my-monorepo/
├── apps/
│   ├── web/           # Main Next.js app
│   ├── admin/         # Admin dashboard
│   └── docs/          # Documentation site
├── packages/
│   ├── ui/            # Shared design system components
│   ├── utils/         # Shared utility functions
│   ├── config-eslint/ # Shared ESLint config
│   ├── config-ts/     # Shared TypeScript config
│   └── types/         # Shared TypeScript types
├── turbo.json         # Pipeline definitions
├── package.json       # Workspace root
└── pnpm-workspace.yaml
```

### turbo.json pipeline

```json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {},
    "test": {
      "dependsOn": ["^build"]
    }
  }
}
```

Key benefits: remote caching (only rebuild what changed), parallel tasks, dependency-aware builds.

---

## §5 Modular Domain Architecture (Alternative to FSD)

A more flexible approach than FSD — organize by domain modules without strict layering.
Each module is a self-contained domain (auth, user, product, order) with clear internal structure.

### Structure

```
src/
├── app/                      # App shell — routing, providers, global config
│   ├── providers.tsx
│   ├── layout.tsx
│   └── routes.tsx
│
├── modules/                  # Domain modules — each is a mini-app
│   ├── auth/
│   │   ├── components/       # PascalCase files: LoginForm.tsx, AuthGuard.tsx
│   │   ├── hooks/            # kebab-case files: use-auth.ts, use-session.ts
│   │   ├── services/         # kebab-case files: auth-api.ts, token-storage.ts
│   │   ├── utils/            # kebab-case files: validate-token.ts
│   │   ├── types/            # kebab-case files: auth-types.ts
│   │   └── index.ts          # Public API — only exported items are accessible
│   │
│   ├── user/
│   │   ├── components/       # UserAvatar.tsx, UserCard.tsx, UserList.tsx
│   │   ├── hooks/            # use-user.ts, use-user-profile.ts
│   │   ├── services/         # user-api.ts
│   │   ├── types/            # user-types.ts
│   │   └── index.ts
│   │
│   ├── product/
│   │   ├── components/       # ProductCard.tsx, ProductGrid.tsx
│   │   ├── hooks/            # use-products.ts, use-product-detail.ts
│   │   ├── services/         # product-api.ts
│   │   ├── utils/            # format-price.ts, calculate-discount.ts
│   │   ├── types/            # product-types.ts
│   │   └── index.ts
│   │
│   ├── cart/
│   │   ├── components/       # CartDrawer.tsx, CartItem.tsx
│   │   ├── hooks/            # use-cart.ts
│   │   ├── store/            # cart-store.ts (Zustand)
│   │   ├── services/         # cart-api.ts
│   │   ├── types/            # cart-types.ts
│   │   └── index.ts
│   │
│   └── notification/
│       ├── components/       # NotificationBell.tsx, NotificationList.tsx
│       ├── hooks/            # use-notifications.ts
│       └── index.ts
│
├── shared/                   # Shared code — NO business logic
│   ├── components/           # Design system: Button.tsx, Input.tsx, Modal.tsx
│   ├── hooks/                # Generic hooks: use-debounce.ts, use-media-query.ts
│   ├── lib/                  # Library configs: query-client.ts, axios-instance.ts
│   ├── utils/                # Pure helpers: format-date.ts, cn.ts
│   ├── types/                # Global types: api-types.ts, common-types.ts
│   └── config/               # Env vars, constants: env.ts, constants.ts
│
├── pages/                    # Route pages — thin compositions of modules
│   ├── home/
│   │   └── HomePage.tsx      # Composes modules/product + modules/notification
│   ├── product-detail/
│   │   └── ProductDetailPage.tsx
│   └── checkout/
│       └── CheckoutPage.tsx  # Composes modules/cart + modules/auth
│
└── layouts/                  # Shared layouts
    ├── MainLayout.tsx
    ├── AuthLayout.tsx
    └── DashboardLayout.tsx
```

### Module rules

1. **Public API via `index.ts`** — Every module exports only what others may use:

```ts
// modules/auth/index.ts
export { LoginForm } from './components/LoginForm';
export { AuthGuard } from './components/AuthGuard';
export { useAuth } from './hooks/use-auth';
export type { User, AuthState } from './types/auth-types';
// Internal files like token-storage.ts are NOT exported
```

2. **Modules import from other modules' public API only**:

```ts
// modules/cart/hooks/use-cart.ts
import { useAuth } from '@/modules/auth';     // ✅ via public API
import { useAuth } from '@/modules/auth/hooks/use-auth'; // ❌ reaching into internals
```

3. **shared/ has NO business logic** — only generic, reusable code
4. **pages/ are thin** — they compose modules, handle routing, and little else
5. **Each module owns its own types, services, hooks, utils** — no cross-module util dumping

### File naming rules (strict)

| What                  | Naming                                        | Example                                  |
|-----------------------|-----------------------------------------------|------------------------------------------|
| Components (files)    | **PascalCase**                                | `LoginForm.tsx`, `UserCard.tsx`          |
| Component exports     | **PascalCase**                                | `export function LoginForm()`            |
| Hooks (files)         | **kebab-case** with `use-` prefix             | `use-auth.ts`, `use-debounce.ts`         |
| Hook exports          | **camelCase** with `use` prefix               | `export function useAuth()`              |
| Services/API (files)  | **kebab-case**                                | `auth-api.ts`, `user-service.ts`         |
| Utils/helpers (files) | **kebab-case**                                | `format-date.ts`, `validate-email.ts`    |
| Types (files)         | **kebab-case**                                | `auth-types.ts`, `api-types.ts`          |
| Store files           | **kebab-case**                                | `cart-store.ts`, `app-store.ts`          |
| Constants             | **kebab-case** files, UPPER_SNAKE_CASE values | `constants.ts` → `MAX_RETRY`             |
| Folders               | **kebab-case**                                | `product-detail/`, `add-to-cart/`        |
| Test files            | Same name + `.test.`                          | `LoginForm.test.tsx`, `use-auth.test.ts` |
| Story files           | Same name + `.stories.`                       | `Button.stories.tsx`                     |

### File content rules (strict — prevent code misplacement)

1. **Helpers NEVER live inside component files**:

```tsx
// ❌ BAD — helper defined inside component file
// components/ProductCard.tsx
function formatPrice(price: number) { return `$${price.toFixed(2)}`; }
export function ProductCard({ product }) { ... }

// ✅ GOOD — helper in its own file
// utils/format-price.ts
export function formatPrice(price: number) { return `$${price.toFixed(2)}`; }

// components/ProductCard.tsx
import { formatPrice } from '../utils/format-price';
export function ProductCard({ product }) { ... }
```

2. **One component per file** (colocated small sub-components are OK only if unexported)
3. **API call functions** → `services/` directory, never inside hooks or components
4. **Zod schemas** → `types/` or `services/` (near where validation happens), not in components
5. **Store definitions** → `store/` directory, never inline in components
6. **Props types** → either in the same component file (if simple) or in `types/` (if shared)
7. **File name must match its primary export**: `UserCard.tsx` exports `UserCard`, `use-auth.ts` exports `useAuth`

### When to use Modular vs FSD

| Modular Domain Architecture                | Feature-Sliced Design                    |
|--------------------------------------------|------------------------------------------|
| Team prefers flexibility over strict rules | Team wants rigid, enforceable boundaries |
| Domains map cleanly to business areas      | Need strict layer dependency rules       |
| 2-5 devs, growing product                  | 5+ devs, need lint-enforced boundaries   |
| Next.js App Router (pages map to routes)   | Framework-agnostic, any SPA              |
| Faster to adopt, lower learning curve      | More structured, better for large orgs   |
