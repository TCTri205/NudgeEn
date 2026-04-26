# State Management Reference

## Table of contents

- §1 Server State — TanStack Query
- §2 Client State — Zustand
- §3 URL State — nuqs / searchParams
- §4 Form State — React Hook Form + Zod
- §5 State Co-location Principle
- §6 Decision Framework

---

## §1 Server State — TanStack Query

TanStack Query (formerly React Query) handles all data from APIs. Never put API data in Zustand or Redux.

### Setup

```tsx
// lib/query-client.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,        // 1 minute before refetch
      gcTime: 5 * 60 * 1000,       // 5 minutes cache retention
      retry: 3,                     // Retry failed requests 3x
      refetchOnWindowFocus: false,  // Disable for most apps
    },
  },
});
```

```tsx
// app/providers.tsx
'use client';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from '@/lib/query-client';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

### Query patterns

```tsx
// Basic query
function useProducts(categoryId: string) {
  return useQuery({
    queryKey: ['products', { categoryId }],
    queryFn: () => api.products.list({ categoryId }),
    staleTime: 5 * 60 * 1000, // Override default for this query
  });
}

// Dependent query (waits for userId before fetching)
function useUserOrders(userId: string | undefined) {
  return useQuery({
    queryKey: ['orders', userId],
    queryFn: () => api.orders.listByUser(userId!),
    enabled: !!userId, // Only fetch when userId exists
  });
}

// Paginated query
function useProductsPaginated(page: number) {
  return useQuery({
    queryKey: ['products', 'list', page],
    queryFn: () => api.products.list({ page, limit: 20 }),
    placeholderData: keepPreviousData, // Keep old data while fetching new page
  });
}

// Infinite scroll
function useInfiniteProducts() {
  return useInfiniteQuery({
    queryKey: ['products', 'infinite'],
    queryFn: ({ pageParam }) => api.products.list({ cursor: pageParam }),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  });
}
```

### Mutation patterns

```tsx
function useCreateProduct() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateProductInput) => api.products.create(data),

    // Optimistic update
    onMutate: async (newProduct) => {
      await queryClient.cancelQueries({ queryKey: ['products'] });
      const previous = queryClient.getQueryData(['products']);

      queryClient.setQueryData(['products'], (old: Product[]) => [
        ...old,
        { ...newProduct, id: 'temp-id', createdAt: new Date() },
      ]);

      return { previous };
    },

    // Rollback on error
    onError: (_err, _variables, context) => {
      queryClient.setQueryData(['products'], context?.previous);
    },

    // Refetch on success
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
  });
}
```

### Prefetching

```tsx
// Prefetch on hover (for anticipated navigation)
function ProductLink({ product }: { product: Product }) {
  const queryClient = useQueryClient();

  const prefetch = () => {
    queryClient.prefetchQuery({
      queryKey: ['product', product.id],
      queryFn: () => api.products.getById(product.id),
      staleTime: 60 * 1000,
    });
  };

  return (
    <Link href={`/products/${product.id}`} onMouseEnter={prefetch}>
      {product.name}
    </Link>
  );
}
```

---

## §2 Client State — Zustand

Zustand manages client-only state: UI state, user preferences, app-specific data not from an API.

### Basic store

```tsx
// stores/useAppStore.ts
import { create } from 'zustand';

interface AppState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark' | 'system';
  toggleSidebar: () => void;
  setTheme: (theme: AppState['theme']) => void;
}

export const useAppStore = create<AppState>((set) => ({
  sidebarOpen: true,
  theme: 'system',
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setTheme: (theme) => set({ theme }),
}));
```

### Slices pattern (for larger stores)

```tsx
// stores/slices/cartSlice.ts
import type { StateCreator } from 'zustand';

export interface CartSlice {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  clearCart: () => void;
  totalItems: () => number;
}

export const createCartSlice: StateCreator<CartSlice> = (set, get) => ({
  items: [],
  addItem: (item) => set((s) => ({ items: [...s.items, item] })),
  removeItem: (id) => set((s) => ({ items: s.items.filter((i) => i.id !== id) })),
  clearCart: () => set({ items: [] }),
  totalItems: () => get().items.reduce((sum, i) => sum + i.quantity, 0),
});

// stores/useStore.ts — compose slices
import { create } from 'zustand';
import { createCartSlice, type CartSlice } from './slices/cartSlice';
import { createUISlice, type UISlice } from './slices/uiSlice';

type StoreState = CartSlice & UISlice;

export const useStore = create<StoreState>()((...args) => ({
  ...createCartSlice(...args),
  ...createUISlice(...args),
}));
```

### Zustand with persistence

```tsx
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      language: 'en',
      notifications: true,
      setLanguage: (lang: string) => set({ language: lang }),
      toggleNotifications: () => set((s) => ({ notifications: !s.notifications })),
    }),
    {
      name: 'user-settings', // localStorage key
      partialize: (state) => ({ language: state.language }), // Only persist specific fields
    }
  )
);
```

### Selector pattern (prevent unnecessary re-renders)

```tsx
// Bad — subscribes to entire store, re-renders on any change
const { sidebarOpen, theme } = useAppStore();

// Good — subscribes only to what you need
const sidebarOpen = useAppStore((s) => s.sidebarOpen);
const theme = useAppStore((s) => s.theme);
```

---

## §3 URL State — nuqs / searchParams

URL is a state manager. Filters, pagination, sorting, search queries belong in the URL.

### With nuqs (type-safe, Next.js optimized)

```tsx
import { useQueryState, parseAsInteger, parseAsString } from 'nuqs';

function ProductListPage() {
  const [search, setSearch] = useQueryState('q', parseAsString.withDefault(''));
  const [page, setPage] = useQueryState('page', parseAsInteger.withDefault(1));
  const [sort, setSort] = useQueryState('sort', parseAsString.withDefault('newest'));

  // URL: /products?q=shoes&page=2&sort=price
  // These are the source of truth — no separate useState needed

  const { data } = useQuery({
    queryKey: ['products', { search, page, sort }],
    queryFn: () => api.products.list({ search, page, sort }),
  });

  return (
    <div>
      <SearchInput value={search} onChange={setSearch} />
      <SortSelect value={sort} onChange={setSort} />
      <ProductGrid products={data?.products} />
      <Pagination page={page} total={data?.totalPages} onChange={setPage} />
    </div>
  );
}
```

### Without nuqs (native Next.js)

```tsx
import { useSearchParams, useRouter, usePathname } from 'next/navigation';

function ProductFilters() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const updateParam = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set(key, value);
    router.push(`${pathname}?${params.toString()}`);
  };

  const category = searchParams.get('category') ?? 'all';
  // ...
}
```

---

## §4 Form State — React Hook Form + Zod

### Setup

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

// 1. Define schema (single source of truth for validation)
const createUserSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  role: z.enum(['admin', 'user', 'editor']),
  age: z.number().min(18, 'Must be 18+').optional(),
});

type CreateUserInput = z.infer<typeof createUserSchema>; // Auto-derive TypeScript type

// 2. Use in component
function CreateUserForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<CreateUserInput>({
    resolver: zodResolver(createUserSchema),
    defaultValues: { name: '', email: '', role: 'user' },
  });

  const onSubmit = async (data: CreateUserInput) => {
    await api.users.create(data);
    reset();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div>
        <label htmlFor="name">Name</label>
        <input id="name" {...register('name')} aria-invalid={!!errors.name} />
        {errors.name && <p role="alert">{errors.name.message}</p>}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" {...register('email')} />
        {errors.email && <p role="alert">{errors.email.message}</p>}
      </div>

      <div>
        <label htmlFor="role">Role</label>
        <select id="role" {...register('role')}>
          <option value="user">User</option>
          <option value="admin">Admin</option>
          <option value="editor">Editor</option>
        </select>
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Creating...' : 'Create User'}
      </button>
    </form>
  );
}
```

### Reusable form pattern with mutation

```tsx
function useCreateUserForm() {
  const mutation = useMutation({ mutationFn: api.users.create });

  const form = useForm<CreateUserInput>({
    resolver: zodResolver(createUserSchema),
  });

  const onSubmit = form.handleSubmit(async (data) => {
    await mutation.mutateAsync(data);
    form.reset();
  });

  return { form, onSubmit, mutation };
}
```

---

## §5 State Co-location Principle

> Place state as close as possible to where it's used. Only lift when you must share.

### Escalation path

```
1. Component state (useState)           → Default. Keep it local.
2. Shared between siblings              → Lift to nearest common parent
3. Shared across distant components     → Context (if rarely updates) or Zustand
4. Server/API data                      → TanStack Query (NEVER in Zustand/Redux)
5. URL-visible state (filters, pages)   → URL params (nuqs / searchParams)
6. Persistent state (preferences)       → Zustand + persist middleware
```

### Anti-patterns

- **Putting API data in Zustand/Redux** → Use TanStack Query. It handles caching, dedup, background refetch.
- **Giant global store for everything** → Split by domain. Use selectors.
- **Context for frequently updating state** → Every consumer re-renders. Use Zustand instead.
- **Duplicating URL state in useState** → URL IS the state. Read from searchParams.

---

## §6 Decision Framework

```
What kind of state?
├── From an API/database?
│   └── TanStack Query
│       - Caching, dedup, background refetch, optimistic updates built-in
│       - queryKey for cache identity, staleTime for freshness control
│
├── In the URL? (filters, pagination, search, tabs)
│   └── nuqs (Next.js) or useSearchParams
│       - Shareable, bookmarkable, browser back/forward works
│
├── Form inputs + validation?
│   └── React Hook Form + Zod
│       - Minimal re-renders, schema-based validation
│       - Share Zod schemas between frontend and API
│
├── Simple local UI state? (open/close, toggle, counter)
│   └── useState or useReducer
│       - No library needed for local concerns
│
├── Shared UI state across components? (sidebar, theme, modal stack)
│   └── Few updates → Context API
│   └── Frequent updates → Zustand
│
└── Complex state machines? (multi-step wizard, workflow)
    └── XState or useReducer with explicit states
```
