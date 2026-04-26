# Code Quality Reference

## Table of contents

- §1 TypeScript Configuration
- §2 Linting & Formatting
- §3 Naming Conventions & File Structure
- §4 Accessibility (a11y)
- §5 Security Best Practices
- §6 Error Handling Patterns
- §7 API Layer Design

---

## §1 TypeScript Configuration

### Strict config (non-negotiable)

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true,
    "isolatedModules": true,
    "moduleResolution": "bundler",
    "module": "ESNext",
    "target": "ES2022",
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    },
    "types": ["vitest/globals"]
  },
  "include": ["src/**/*", "*.config.ts"],
  "exclude": ["node_modules", "dist"]
}
```

### TypeScript patterns

```tsx
// Discriminated unions for variants
type ButtonVariant =
  | { variant: 'link'; href: string }
  | { variant: 'button'; onClick: () => void }
  | { variant: 'submit'; formId: string };

// Generic components
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
  keyExtractor: (item: T) => string;
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return <ul>{items.map((item) => <li key={keyExtractor(item)}>{renderItem(item)}</li>)}</ul>;
}

// Utility types
type WithRequired<T, K extends keyof T> = T & Required<Pick<T, K>>;
type Prettify<T> = { [K in keyof T]: T[K] } & {};

// Zod for runtime validation
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().min(1),
  role: z.enum(['admin', 'user', 'editor']),
  createdAt: z.string().datetime(),
});

type User = z.infer<typeof UserSchema>; // Single source of truth

// Validate API response
const response = await fetch('/api/user');
const data = UserSchema.parse(await response.json()); // Throws if invalid
```

### Rules

- **No `any`** — Use `unknown` + type narrowing when type is genuinely unknown
- **No type assertions (`as`)** — Use type guards or Zod parsing instead
- **No non-null assertions (`!`)** — Handle null/undefined explicitly
- **Export types from index.ts** — Same public API pattern as components

---

## §2 Linting & Formatting

### ESLint config (flat config, ESLint 9+)

```ts
// eslint.config.js
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import importPlugin from 'eslint-plugin-import';

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  {
    plugins: {
      react,
      'react-hooks': reactHooks,
      'jsx-a11y': jsxA11y,
      import: importPlugin,
    },
    rules: {
      // React
      'react/jsx-no-leaked-render': 'error',
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',

      // TypeScript
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/consistent-type-imports': 'error',
      '@typescript-eslint/no-explicit-any': 'error',

      // Import
      'import/order': ['error', {
        groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
        'newlines-between': 'always',
        alphabetize: { order: 'asc' },
      }],
      'import/no-cycle': 'error',

      // Accessibility
      'jsx-a11y/alt-text': 'error',
      'jsx-a11y/anchor-is-valid': 'error',
      'jsx-a11y/click-events-have-key-events': 'error',
      'jsx-a11y/no-static-element-interactions': 'error',
    },
  },
);
```

### Prettier config

```json
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2,
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

### FSD boundary enforcement (optional, for FSD projects)

```ts
// eslint-plugin-boundaries config
{
  'boundaries/element-types': ['error', {
    default: { allow: [] },
    rules: [
      { from: 'app', allow: ['pages', 'widgets', 'features', 'entities', 'shared'] },
      { from: 'pages', allow: ['widgets', 'features', 'entities', 'shared'] },
      { from: 'widgets', allow: ['features', 'entities', 'shared'] },
      { from: 'features', allow: ['entities', 'shared'] },
      { from: 'entities', allow: ['shared'] },
      { from: 'shared', allow: ['shared'] },
    ],
  }],
}
```

---

## §3 Naming Conventions & File Structure

### Naming rules

| Thing                      | Convention                               | Example                                       |
|----------------------------|------------------------------------------|-----------------------------------------------|
| Components (files)         | **PascalCase**                           | `UserCard.tsx`, `SearchInput.tsx`             |
| Components (exports)       | **PascalCase**                           | `export function UserCard()`                  |
| Hooks (files)              | **kebab-case** with `use-`               | `use-auth.ts`, `use-debounce.ts`              |
| Hooks (exports)            | **camelCase** with `use`                 | `export function useAuth()`                   |
| Utils/helpers (files)      | **kebab-case**                           | `format-date.ts`, `validate-email.ts`         |
| Services/API (files)       | **kebab-case**                           | `user-api.ts`, `auth-service.ts`              |
| Types (files)              | **kebab-case**                           | `user-types.ts`, `api-types.ts`               |
| Store files                | **kebab-case**                           | `cart-store.ts`, `app-store.ts`               |
| Types/interfaces (exports) | PascalCase                               | `User`, `ApiResponse<T>`                      |
| Constants (values)         | UPPER_SNAKE_CASE                         | `MAX_RETRY_COUNT`, `API_BASE_URL`             |
| Folders                    | **kebab-case**                           | `add-to-cart/`, `product-detail/`             |
| Test files                 | Same name + `.test.`                     | `UserCard.test.tsx`, `use-auth.test.ts`       |
| Story files                | Same name + `.stories.`                  | `Button.stories.tsx`                          |
| CSS Modules                | **kebab-case** file, camelCase selectors | `user-card.module.css` → `styles.cardWrapper` |

**Summary rule: Components = PascalCase. Everything else = kebab-case.**

### Component file structure

```
ComponentName/                 # Folder kebab-case is OK too, but component file is PascalCase
├── ComponentName.tsx          # Main component — ONE component per file
├── ComponentName.test.tsx     # Tests
├── ComponentName.stories.tsx  # Storybook stories (if design system)
├── component-name.module.css  # Styles (kebab-case for non-component files)
├── use-component-name.ts      # Component-specific hook (kebab-case)
├── component-name-types.ts    # Component-specific types (kebab-case)
└── index.ts                   # Public API barrel export
```

### File content rules (STRICT — prevent code misplacement)

These rules ensure code is always in the right place. Violations make code hard to find and maintain.

**1. Helpers/utils NEVER live inside component files:**

```tsx
// ❌ WRONG — helper defined inside component file
// components/ProductCard.tsx
function formatPrice(price: number) { return `$${price.toFixed(2)}`; }
export function ProductCard({ product }) { /* uses formatPrice */ }

// ✅ CORRECT — helper in its own file
// utils/format-price.ts
export function formatPrice(price: number): string { return `$${price.toFixed(2)}`; }

// components/ProductCard.tsx
import { formatPrice } from '../utils/format-price';
export function ProductCard({ product }) { /* uses formatPrice */ }
```

**2. One primary component per file.**
Small, unexported sub-components are OK if tightly coupled:

```tsx
// ✅ OK — ItemRow is only used inside DataTable, not exported
function ItemRow({ item }: { item: Item }) { return <tr>...</tr>; }
export function DataTable({ items }: { items: Item[] }) { ... }
```

**3. API calls → services/ directory, never inside hooks or components:**

```tsx
// ❌ WRONG
function useUser(id: string) {
  return useQuery({ queryFn: () => fetch(`/api/users/${id}`).then(r => r.json()) });
}

// ✅ CORRECT
// services/user-api.ts
export const userApi = {
  getById: (id: string): Promise<User> => client.get(`/users/${id}`).then(r => r.data),
};

// hooks/use-user.ts
import { userApi } from '../services/user-api';
export function useUser(id: string) {
  return useQuery({ queryKey: ['user', id], queryFn: () => userApi.getById(id) });
}
```

**4. Zod schemas** → `types/` or `services/` (near validation), not in components

**5. Store definitions** → `store/` directory, never inline

**6. File name MUST match its primary export:**

- `UserCard.tsx` → exports `UserCard`
- `use-auth.ts` → exports `useAuth`
- `format-date.ts` → exports `formatDate`
- `user-types.ts` → exports `User`, `UserProfile`, etc.

**7. Props design:**

- Simple/component-specific → define in component file
- Shared across modules → define in `types/` file
- Always use `interface` (not `type`) for props — better extensibility
- Name: `{ComponentName}Props` (e.g., `UserCardProps`)

### Import order

```tsx
// 1. React/framework imports
import { useState, useEffect } from 'react';
import Link from 'next/link';

// 2. External libraries
import { useQuery } from '@tanstack/react-query';
import { z } from 'zod';

// 3. Internal absolute imports (@/ alias) — modules and shared
import { Button } from '@/shared/components';
import { useAuth } from '@/modules/auth';

// 4. Relative imports (parent, sibling)
import { useProductData } from '../hooks/use-product-data';
import { ProductCard } from './ProductCard';

// 5. Type imports (always last, with `type` keyword)
import type { Product } from '@/modules/product';
```

---

## §4 Accessibility (a11y)

### Non-negotiable requirements

**Semantic HTML first:**

```tsx
// Bad — div soup
<div onClick={handleClick}>Click me</div>
<div class="nav">...</div>

// Good — semantic elements
<button onClick={handleClick}>Click me</button>
<nav aria-label="Main navigation">...</nav>
```

**Landmarks:** `<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>`, `<article>`, `<section>`

**Forms:**

```tsx
// Every input needs a label
<label htmlFor="email">Email address</label>
<input id="email" type="email" aria-describedby="email-error" />
{error && <p id="email-error" role="alert">{error}</p>}

// Group related fields
<fieldset>
  <legend>Shipping address</legend>
  {/* fields */}
</fieldset>
```

**Keyboard navigation:**

- All interactive elements focusable and operable via keyboard
- Logical tab order (follow DOM order)
- Visible focus indicators (never `outline: none` without replacement)
- Trap focus inside modals, restore on close
- Skip-to-content link for screen reader users

**Color and motion:**

```css
/* Color contrast: ≥ 4.5:1 for text, ≥ 3:1 for large text */

/* Respect motion preferences */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Images and icons:**

```tsx
// Informative image — describe content
<img src="chart.png" alt="Revenue grew 40% from Q1 to Q2 2025" />

// Decorative image — empty alt
<img src="decoration.svg" alt="" />

// Icon button — aria-label required
<button aria-label="Close dialog"><XIcon /></button>
```

### a11y testing tools

- `eslint-plugin-jsx-a11y` — Catch issues at build time
- `@axe-core/react` — Runtime auditing in development
- Lighthouse Accessibility audit — Score and actionable suggestions
- VoiceOver (macOS) / NVDA (Windows) — Manual screen reader testing

---

## §5 Security Best Practices

### XSS Prevention

```tsx
// React auto-escapes JSX — safe by default
<p>{userInput}</p> // ✅ Escaped

// DANGER — only use when absolutely necessary
<div dangerouslySetInnerHTML={{ __html: sanitizedHtml }} /> // ⚠️ Must sanitize first

// Use DOMPurify for sanitization
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(dirtyHtml);
```

- Set Content-Security-Policy headers
- Never interpolate user input into URLs without encoding

### Authentication

- Store tokens in httpOnly cookies (not localStorage — XSS vulnerable)
- Use CSRF tokens for state-changing requests
- Implement proper token refresh flow
- Role-based access control (RBAC) on both server and client

### API Security

- HTTPS everywhere
- Validate all inputs (Zod on both frontend and backend)
- Rate limiting on API routes
- Never expose API keys or secrets in client code — use server actions or API routes

### Dependencies

```bash
# Regular audit
npm audit
npm audit fix

# Automate with Dependabot / Renovate
# Lock files committed (package-lock.json or pnpm-lock.yaml)
```

### Security headers (Next.js)

```ts
// next.config.js
const securityHeaders = [
  { key: 'X-DNS-Prefetch-Control', value: 'on' },
  { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' },
  { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'origin-when-cross-origin' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
];
```

---

## §6 Error Handling Patterns

### Error Boundary (React)

```tsx
// Next.js — error.tsx per route segment (automatic Error Boundary)
// app/dashboard/error.tsx
'use client';

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log to error tracking (Sentry)
    captureException(error);
  }, [error]);

  return (
    <div role="alert">
      <h2>Something went wrong</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

### API error handling strategy

```tsx
// Centralized in API client
const apiClient = axios.create({ baseURL: '/api' });

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error.response?.status;

    switch (status) {
      case 401:
        // Try token refresh, then redirect to login
        await refreshToken();
        return apiClient.request(error.config);
      case 403:
        // Redirect to access denied page
        window.location.href = '/access-denied';
        break;
      case 429:
        // Rate limited — exponential backoff handled by TanStack Query retry
        break;
      default:
        // Report to Sentry
        captureException(error);
    }

    return Promise.reject(error);
  }
);
```

### Toast notification for user-facing errors

```tsx
// Use a toast library (sonner, react-hot-toast)
import { toast } from 'sonner';

const mutation = useMutation({
  mutationFn: createProduct,
  onSuccess: () => toast.success('Product created'),
  onError: (error) => {
    if (error instanceof ValidationError) {
      // Show field-level errors in form
      return;
    }
    toast.error('Failed to create product. Please try again.');
  },
});
```

### Graceful degradation

- Error Boundaries catch render errors — app stays usable
- TanStack Query retries failed requests (3x default)
- Fallback UI for each Suspense boundary
- Feature flags to disable broken features without redeploying
- Offline detection + queue for critical actions

---

## §7 API Layer Design

### Structure

```
src/shared/api/
├── client.ts          # Axios/fetch instance with interceptors
├── types.ts           # Generic API types
└── endpoints/
    ├── users.ts       # User CRUD
    ├── products.ts    # Product CRUD
    └── index.ts       # Re-export
```

### Type-safe API client

```tsx
// shared/api/client.ts
import axios from 'axios';
import { z } from 'zod';

const client = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Type-safe request wrapper with Zod validation
async function apiGet<T>(url: string, schema: z.ZodType<T>): Promise<T> {
  const { data } = await client.get(url);
  return schema.parse(data); // Runtime validation
}

async function apiPost<TInput, TOutput>(
  url: string,
  body: TInput,
  schema: z.ZodType<TOutput>
): Promise<TOutput> {
  const { data } = await client.post(url, body);
  return schema.parse(data);
}

export { client, apiGet, apiPost };
```

```tsx
// shared/api/endpoints/users.ts
import { z } from 'zod';
import { apiGet, apiPost } from '../client';

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
  role: z.enum(['admin', 'user']),
});

const UsersListSchema = z.array(UserSchema);

export type User = z.infer<typeof UserSchema>;

export const usersApi = {
  list: () => apiGet('/users', UsersListSchema),
  getById: (id: string) => apiGet(`/users/${id}`, UserSchema),
  create: (input: CreateUserInput) => apiPost('/users', input, UserSchema),
};
```

### Generic API response types

```tsx
// shared/api/types.ts
export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

export interface ApiError {
  message: string;
  code: string;
  details?: Record<string, string[]>; // Field-level validation errors
}
```

### Integration with TanStack Query

```tsx
// Keep query hooks close to the feature that uses them
// features/users/model/useUsers.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersApi } from '@/shared/api';

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: usersApi.list,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: usersApi.create,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
  });
}
```
