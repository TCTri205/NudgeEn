# React Patterns Reference

## Table of contents

- §1 Component Design Patterns
- §2 Custom Hooks Best Practices
- §3 React Server Components (RSC) Patterns
- §4 Component API Design
- §5 Composition Strategies
- §6 React 19 Hooks — Actions, Forms, Optimistic UI
- §7 React 19.2 — Activity, useEffectEvent, cacheSignal

---

## §1 Component Design Patterns

### Compound Components

Use when building a group of components that share implicit state. Think `<select>` + `<option>` in HTML.

```tsx
// Usage — clean, declarative API
<Tabs defaultValue="general">
  <Tabs.List>
    <Tabs.Trigger value="general">General</Tabs.Trigger>
    <Tabs.Trigger value="security">Security</Tabs.Trigger>
  </Tabs.List>
  <Tabs.Content value="general">General settings...</Tabs.Content>
  <Tabs.Content value="security">Security settings...</Tabs.Content>
</Tabs>
```

```tsx
// Implementation — Context + composition
import { createContext, useContext, useState, type ReactNode } from 'react';

interface TabsContextValue {
  activeTab: string;
  setActiveTab: (value: string) => void;
}

const TabsContext = createContext<TabsContextValue | null>(null);

function useTabsContext() {
  const ctx = useContext(TabsContext);
  if (!ctx) throw new Error('Tabs components must be used within <Tabs>');
  return ctx;
}

function Tabs({ defaultValue, children }: { defaultValue: string; children: ReactNode }) {
  const [activeTab, setActiveTab] = useState(defaultValue);
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div role="tablist">{children}</div>
    </TabsContext.Provider>
  );
}

function TabsList({ children }: { children: ReactNode }) {
  return <div className="flex gap-1">{children}</div>;
}

function TabsTrigger({ value, children }: { value: string; children: ReactNode }) {
  const { activeTab, setActiveTab } = useTabsContext();
  return (
    <button
      role="tab"
      aria-selected={activeTab === value}
      onClick={() => setActiveTab(value)}
      className={activeTab === value ? 'font-medium border-b-2' : 'text-muted'}
    >
      {children}
    </button>
  );
}

function TabsContent({ value, children }: { value: string; children: ReactNode }) {
  const { activeTab } = useTabsContext();
  if (activeTab !== value) return null;
  return <div role="tabpanel">{children}</div>;
}

Tabs.List = TabsList;
Tabs.Trigger = TabsTrigger;
Tabs.Content = TabsContent;

export { Tabs };
```

**When to use:** Tabs, Accordion, Select, Dialog, Menu, Toast, Popover — any multi-part component with shared state.
Libraries like Radix UI and Headless UI are built on this pattern.

### Container/Presentational (Modern Hook Version)

Separate data-fetching logic from rendering. In 2025, the "container" is a custom hook, not a wrapper component.

```tsx
// Hook = Container (logic + data)
function useUserProfile(userId: string) {
  const { data: user, isLoading, error } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => api.users.getById(userId),
  });
  return { user, isLoading, error };
}

// Component = Presentational (pure rendering)
interface UserCardProps {
  user: User;
}

function UserCard({ user }: UserCardProps) {
  return (
    <div className="rounded-lg border p-4">
      <img src={user.avatar} alt="" className="h-12 w-12 rounded-full" />
      <h3 className="font-medium">{user.name}</h3>
      <p className="text-sm text-muted-foreground">{user.email}</p>
    </div>
  );
}

// Page = Composition
function UserProfilePage({ userId }: { userId: string }) {
  const { user, isLoading, error } = useUserProfile(userId);

  if (isLoading) return <UserCardSkeleton />;
  if (error) return <ErrorMessage error={error} />;
  if (!user) return <NotFound />;

  return <UserCard user={user} />;
}
```

**Benefits:** Presentational components are trivially testable (pass props, assert output), reusable across data
sources, and easy to preview in Storybook.

### State Reducer Pattern

Give consumers control over state transitions. Essential for flexible design system components.

```tsx
type ToggleState = { on: boolean };
type ToggleAction = { type: 'toggle' } | { type: 'reset' };

function defaultReducer(state: ToggleState, action: ToggleAction): ToggleState {
  switch (action.type) {
    case 'toggle': return { on: !state.on };
    case 'reset': return { on: false };
    default: return state;
  }
}

function useToggle({
  initialOn = false,
  reducer = defaultReducer,
}: {
  initialOn?: boolean;
  reducer?: typeof defaultReducer;
} = {}) {
  const [state, dispatch] = useReducer(reducer, { on: initialOn });
  const toggle = () => dispatch({ type: 'toggle' });
  const reset = () => dispatch({ type: 'reset' });
  return { on: state.on, toggle, reset, dispatch };
}

// Consumer can override behavior:
function App() {
  const { on, toggle } = useToggle({
    reducer(state, action) {
      // Prevent turning off after 3pm
      if (action.type === 'toggle' && state.on && new Date().getHours() >= 15) {
        return state; // no-op
      }
      return defaultReducer(state, action);
    },
  });
  return <Switch checked={on} onChange={toggle} />;
}
```

### Render Props (still useful for JSX-coupled behavior)

```tsx
// Useful when behavior is tightly coupled to JSX structure
<MouseTracker>
  {({ x, y }) => (
    <div style={{ position: 'absolute', left: x, top: y }}>
      Cursor here
    </div>
  )}
</MouseTracker>
```

Prefer custom hooks for most cases. Use render props when the behavior directly determines what JSX to render (
animations, layout delegation, third-party library integration).

### Controlled vs Uncontrolled

Every form-like component should support both modes:

```tsx
interface InputProps {
  value?: string;          // Controlled
  defaultValue?: string;   // Uncontrolled
  onChange?: (value: string) => void;
}

function Input({ value, defaultValue, onChange }: InputProps) {
  const [internalValue, setInternalValue] = useState(defaultValue ?? '');
  const isControlled = value !== undefined;
  const currentValue = isControlled ? value : internalValue;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!isControlled) setInternalValue(e.target.value);
    onChange?.(e.target.value);
  };

  return <input value={currentValue} onChange={handleChange} />;
}
```

---

## §2 Custom Hooks Best Practices

### Naming: `use` + action/resource

```
useAuth          — authentication state + actions
useFetch         — generic data fetching (prefer TanStack Query though)
useDebounce      — debounce a value
useMediaQuery    — responsive breakpoint detection
useLocalStorage  — sync state with localStorage
useEventListener — safe DOM event listener with cleanup
usePrevious      — track previous render's value
useLatestRef     — avoid stale closures in callbacks
useOnClickOutside — detect clicks outside a ref
useIntersection  — IntersectionObserver hook
```

### Composition rule

Hooks compose hooks. Each hook has a single responsibility.

```tsx
// Bad — one hook doing everything
function useProductPage(productId: string) {
  // fetches product, manages cart, tracks analytics, handles reviews...
}

// Good — composed from focused hooks
function useProductPage(productId: string) {
  const product = useProduct(productId);
  const { addToCart } = useCart();
  const reviews = useProductReviews(productId);
  usePageView('product', productId);

  return { product, addToCart, reviews };
}
```

### Essential hook implementations

```tsx
// useDebounce — debounce any value
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// useLocalStorage — persist state in localStorage
function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    const valueToStore = value instanceof Function ? value(storedValue) : value;
    setStoredValue(valueToStore);
    window.localStorage.setItem(key, JSON.stringify(valueToStore));
  };

  return [storedValue, setValue] as const;
}

// useMediaQuery — responsive breakpoint
function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    setMatches(media.matches);
    const listener = (e: MediaQueryListEvent) => setMatches(e.matches);
    media.addEventListener('change', listener);
    return () => media.removeEventListener('change', listener);
  }, [query]);

  return matches;
}
```

---

## §3 React Server Components (RSC) Patterns

### Server vs Client decision

| Use Server Component when...       | Use Client Component when...              |
|------------------------------------|-------------------------------------------|
| Fetching data (DB, API)            | Handling user events (onClick, onChange)  |
| Rendering static/read-only UI      | Using React hooks (useState, useEffect)   |
| Accessing backend resources        | Using browser APIs (localStorage, window) |
| Keeping sensitive data server-side | Needing real-time interactivity           |
| Reducing client bundle size        | Using third-party client-only libraries   |

**Default to Server Components.** Only add `'use client'` when you need interactivity.

### Boundary pattern — Server wraps Client

```tsx
// app/products/[id]/page.tsx — Server Component (default)
import { AddToCartButton } from '@/features/add-to-cart';
import { ProductReviews } from '@/widgets/product-reviews';

export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await db.product.findUnique({ where: { id: params.id } }); // Direct DB access

  return (
    <main>
      <h1>{product.name}</h1>           {/* Static — stays on server */}
      <p>{product.description}</p>       {/* Static — stays on server */}
      <span>${product.price}</span>      {/* Static — stays on server */}
      <AddToCartButton productId={product.id} /> {/* Client — ships JS */}
      <Suspense fallback={<ReviewsSkeleton />}>
        <ProductReviews productId={product.id} /> {/* Server — async + streamed */}
      </Suspense>
    </main>
  );
}
```

```tsx
// features/add-to-cart/ui/AddToCartButton.tsx
'use client'; // Only this component ships to browser

import { useCart } from '../model/useCart';

export function AddToCartButton({ productId }: { productId: string }) {
  const { addItem, isPending } = useCart();
  return (
    <button onClick={() => addItem(productId)} disabled={isPending}>
      {isPending ? 'Adding...' : 'Add to cart'}
    </button>
  );
}
```

### Rules

1. Server Components CAN import Client Components ✅
2. Client Components CANNOT import Server Components ❌
3. Pass data Server → Client via props (must be serializable — no functions, Dates, Maps)
4. Wrap async Server Components in `<Suspense>` for streaming
5. Keep `'use client'` boundary as low as possible in the component tree

### Data fetching in Server Components

```tsx
// Parallel fetching — avoid waterfalls
async function DashboardPage() {
  // Launch all fetches simultaneously
  const [user, stats, notifications] = await Promise.all([
    getUser(),
    getDashboardStats(),
    getNotifications(),
  ]);

  return (
    <div>
      <UserHeader user={user} />
      <StatsGrid stats={stats} />
      <NotificationList notifications={notifications} />
    </div>
  );
}
```

```tsx
// Streaming with Suspense — don't block the whole page
async function DashboardPage() {
  const user = await getUser(); // Fast — render immediately

  return (
    <div>
      <UserHeader user={user} />
      <Suspense fallback={<StatsSkeleton />}>
        <StatsGrid /> {/* Slow — streams in when ready */}
      </Suspense>
      <Suspense fallback={<NotificationSkeleton />}>
        <NotificationList /> {/* Slow — streams independently */}
      </Suspense>
    </div>
  );
}
```

---

## §4 React 19+ New Hooks & APIs

### `use()` — Read promises and context during render

Replaces `useEffect` + `useState` pattern for data fetching. Works with Suspense.

```tsx
import { use, Suspense } from 'react';

// Create promise OUTSIDE the component (or cache it)
const userPromise = fetchUser();

function UserProfile() {
  const user = use(userPromise); // Suspends until resolved
  return <h1>{user.name}</h1>;
}

// Wrap in Suspense
<Suspense fallback={<Skeleton />}>
  <UserProfile />
</Suspense>
```

**Also reads Context conditionally** (unlike useContext):

```tsx
function Component({ isAdmin }) {
  if (isAdmin) {
    const adminData = use(AdminContext); // Allowed in conditionals!
  }
}
```

**When to use:** Server Components data fetching, replacing useEffect-based fetch patterns, conditional context reading.
Pair with TanStack Query for client-side (Query handles caching/dedup that `use` doesn't).

### `useActionState()` — Form action state management

Manages async action state (pending, result, error) — replaces manual useState + try/catch patterns.

```tsx
import { useActionState } from 'react';

async function createUser(prevState: State, formData: FormData) {
  const email = formData.get('email') as string;
  if (!email) return { error: 'Email required' };
  
  const user = await api.users.create({ email });
  return { success: true, user };
}

function SignUpForm() {
  const [state, action, isPending] = useActionState(createUser, { error: null });

  return (
    <form action={action}>
      <input name="email" type="email" />
      <button disabled={isPending}>{isPending ? 'Creating...' : 'Sign Up'}</button>
      {state.error && <p role="alert">{state.error}</p>}
      {state.success && <p>Welcome!</p>}
    </form>
  );
}
```

**Key:** No `e.preventDefault()`, no manual `setLoading`. Works with Server Actions and client actions.

### `useOptimistic()` — Instant UI updates while async runs

```tsx
import { useOptimistic } from 'react';

function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, addOptimistic] = useOptimistic(
    todos,
    (current, newTodo: Todo) => [...current, newTodo]
  );

  async function addTodo(formData: FormData) {
    const text = formData.get('text') as string;
    addOptimistic({ id: 'temp', text, completed: false }); // Instant UI
    await api.todos.create({ text }); // Server confirms
  }

  return (
    <form action={addTodo}>
      <input name="text" />
      <button type="submit">Add</button>
      <ul>{optimisticTodos.map(t => <li key={t.id}>{t.text}</li>)}</ul>
    </form>
  );
}
```

**When to use:** Like buttons, chat messages, todo lists, any action where waiting for server feels slow.

### `useFormStatus()` — Read parent form state (no prop drilling)

```tsx
import { useFormStatus } from 'react-dom';

// Reusable submit button — auto-detects parent form state
function SubmitButton({ children }: { children: React.ReactNode }) {
  const { pending } = useFormStatus(); // Reads from nearest <form> ancestor
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : children}
    </button>
  );
}

// Use anywhere inside a <form> — no props needed
<form action={serverAction}>
  <input name="email" />
  <SubmitButton>Save</SubmitButton>
</form>
```

**Must be a child component** of `<form>`, not in the same component that renders the form.

### React 19.2: `<Activity />` — Pre-render and preserve hidden UI

```tsx
import { Activity } from 'react';

function App() {
  const [tab, setTab] = useState('home');

  return (
    <div>
      <TabBar active={tab} onChange={setTab} />
      
      {/* Both tabs stay mounted — hidden tab preserves state */}
      <Activity mode={tab === 'home' ? 'visible' : 'hidden'}>
        <HomePage />
      </Activity>
      <Activity mode={tab === 'settings' ? 'visible' : 'hidden'}>
        <SettingsPage /> {/* Form inputs preserved when switching back */}
      </Activity>
    </div>
  );
}
```

**`hidden` mode:** Hides children, unmounts effects, defers updates. State (useState, form inputs) is preserved.
**Use for:** Tab navigation (preserve form state), pre-rendering anticipated routes, offscreen content.

### React 19.2: `useEffectEvent()` — Stable event callbacks in Effects

Solves the "stale closure" problem: read latest props/state without re-triggering the effect.

```tsx
import { useEffect, useEffectEvent } from 'react';

function ChatRoom({ roomId, theme }: { roomId: string; theme: string }) {
  // This always sees latest `theme` but is NOT a dependency
  const onConnected = useEffectEvent(() => {
    showNotification('Connected!', theme);
  });

  useEffect(() => {
    const conn = createConnection(roomId);
    conn.on('connected', () => onConnected());
    conn.connect();
    return () => conn.disconnect();
  }, [roomId]); // ✅ Only re-runs when roomId changes, not theme
}
```

**Rules:**

- Only call from within effects (not JSX event handlers)
- Don't include in dependency arrays
- Must be in same component/hook as the effect
- Use for: analytics logging, notifications, WebSocket event callbacks

### React 19.2: `cacheSignal()` — Abort cached server work (RSC only)

```tsx
import { cache, cacheSignal } from 'react';

const cachedFetch = cache(async (url: string) => {
  const res = await fetch(url, { signal: cacheSignal() });
  return res.json();
});
```

Aborts fetch when cache lifetime ends (render completes, aborts, or fails). Prevents wasted server work.

### React 19.2: Partial Pre-rendering (PPR)

Pre-render static shell at build time, resume with dynamic content at request time:

```tsx
// Build time: pre-render static parts
const { prelude, postponed } = await prerender(<App />, { signal: controller.signal });

// Request time: resume with dynamic content
const stream = await resume(<App />, postponed);
```

Framework-level feature (Next.js handles this). Understand the concept for architecture decisions.

---

## §5 Component API Design

### Props design principles

```tsx
// Use interface (extends better than type intersections)
interface ButtonProps {
  // Required props first
  children: React.ReactNode;

  // Variant using discriminated union
  variant: 'primary' | 'secondary' | 'ghost' | 'destructive';

  // Optional with sensible defaults
  size?: 'sm' | 'md' | 'lg';        // default: 'md'
  disabled?: boolean;                 // default: false
  loading?: boolean;                  // default: false

  // Event handlers
  onClick?: (event: React.MouseEvent) => void;

  // Spread native attributes
  className?: string;
}
```

### Polymorphic `as` prop

```tsx
interface BoxProps<C extends React.ElementType = 'div'> {
  as?: C;
  children: React.ReactNode;
}

type BoxPropsWithRef<C extends React.ElementType> = BoxProps<C> &
  Omit<React.ComponentPropsWithoutRef<C>, keyof BoxProps>;

function Box<C extends React.ElementType = 'div'>({
  as,
  children,
  ...props
}: BoxPropsWithRef<C>) {
  const Component = as || 'div';
  return <Component {...props}>{children}</Component>;
}

// Usage
<Box as="section" className="p-4">Content</Box>
<Box as="a" href="/about">Link</Box>
```

---

## §5 Composition Strategies

### Children composition (simplest)

```tsx
<Card>
  <CardHeader>Title</CardHeader>
  <CardBody>Content</CardBody>
</Card>
```

### Slot pattern (explicit named areas)

```tsx
<PageLayout
  header={<Header />}
  sidebar={<Sidebar />}
  footer={<Footer />}
>
  Main content
</PageLayout>
```

### When to choose what

| Pattern             | Use when                                       |
|---------------------|------------------------------------------------|
| `children`          | Single content area, flexible                  |
| Named slots (props) | Multiple distinct content areas                |
| Compound components | Group of related components sharing state      |
| Custom hooks        | Sharing logic without UI coupling              |
| Render props        | Behavior tightly coupled to JSX structure      |
| HOC                 | Cross-cutting concerns (rarely needed in 2025) |

---

## §6 React 19 Hooks — Actions, Forms, Optimistic UI

React 19 introduced first-class primitives for async workflows, form handling, and optimistic updates.
These hooks reduce boilerplate that previously required external libraries or manual state machines.

### `use()` — Read promises and context in render

```tsx
import { use, Suspense } from 'react';

// Read a promise directly in render — React will Suspend until resolved
function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise); // Suspends until resolved
  return <h1>{user.name}</h1>;
}

// Read context conditionally (unlike useContext, can be called after early returns)
function Dashboard({ isAdmin }: { isAdmin: boolean }) {
  if (!isAdmin) return <p>Access denied</p>;
  const theme = use(ThemeContext); // OK — after early return
  return <div className={theme}>Admin Panel</div>;
}

// Usage: pass the promise from a parent/server, wrap in Suspense
<Suspense fallback={<Skeleton />}>
  <UserProfile userPromise={fetchUser(userId)} />
</Suspense>
```

**Rules:** `use()` can only be called in render (like hooks), but CAN be called conditionally.
The promise must come from a Suspense-compatible source (server component, framework, cached).

### `useActionState()` — Form + server action state

Replaces manual `useState` + `isLoading` + `error` juggling for form actions.

```tsx
import { useActionState } from 'react';

async function createUser(prevState: FormState, formData: FormData): Promise<FormState> {
  const name = formData.get('name') as string;
  if (!name) return { error: 'Name is required', success: false };

  await api.users.create({ name });
  return { error: null, success: true };
}

type FormState = { error: string | null; success: boolean };

function CreateUserForm() {
  const [state, formAction, isPending] = useActionState(createUser, {
    error: null,
    success: false,
  });

  return (
    <form action={formAction}>
      <input name="name" placeholder="User name" />
      {state.error && <p role="alert">{state.error}</p>}
      <button disabled={isPending}>
        {isPending ? 'Creating...' : 'Create User'}
      </button>
      {state.success && <p>User created!</p>}
    </form>
  );
}
```

**Key points:**

- Works with `<form action={...}>` — no `onSubmit` + `preventDefault` needed
- Supports Server Actions (Next.js) with progressive enhancement
- Returns `[state, dispatchAction, isPending]`
- Think of it as `useReducer` for side effects

### `useOptimistic()` — Instant UI feedback

```tsx
import { useOptimistic } from 'react';

function CommentList({ comments }: { comments: Comment[] }) {
  const [optimisticComments, addOptimistic] = useOptimistic(
    comments,
    (current, newComment: string) => [...current, { id: 'temp', text: newComment, pending: true }]
  );

  async function handleAdd(text: string) {
    addOptimistic(text);                    // Instant UI update
    await api.comments.create({ text });    // Server confirmation
    // React auto-reconciles optimistic → real state
  }

  return (
    <ul>
      {optimisticComments.map((c) => (
        <li key={c.id} style={{ opacity: c.pending ? 0.6 : 1 }}>{c.text}</li>
      ))}
    </ul>
  );
}
```

**When to use:** Like buttons, add-to-cart, comments, toggles — any action where
instant feedback matters. Pairs well with `useActionState`.

### `useFormStatus()` — Form status without prop drilling

```tsx
import { useFormStatus } from 'react-dom';

// Must be a CHILD of a <form> — cannot be in the same component as the form
function SubmitButton() {
  const { pending, data } = useFormStatus();
  return (
    <button disabled={pending} type="submit">
      {pending ? `Submitting ${data?.get('name')}...` : 'Submit'}
    </button>
  );
}

// Usage
<form action={serverAction}>
  <input name="name" />
  <SubmitButton /> {/* Reads parent form status automatically */}
</form>
```

**Key constraint:** `useFormStatus` reads the *parent* `<form>`, not a `<form>` in the same component.
Design system `SubmitButton` components benefit most — reusable across all forms.

### Summary table

| Hook               | Purpose                                         | Replaces                                            |
|--------------------|-------------------------------------------------|-----------------------------------------------------|
| `use()`            | Read promises/context in render                 | useEffect+useState for data, conditional useContext |
| `useActionState()` | Form action lifecycle (state + pending + error) | Multiple useState + loading + error booleans        |
| `useOptimistic()`  | Instant UI updates before async completes       | Manual optimistic logic + rollback                  |
| `useFormStatus()`  | Access parent form's pending/data               | Prop drilling isPending to submit buttons           |

---

## §7 React 19.2 — Activity, useEffectEvent, cacheSignal

Released October 2025. These are production-stable features (not experimental).

### `<Activity />` — Hide UI while preserving state

```tsx
import { Activity } from 'react';

function App() {
  const [activeTab, setActiveTab] = useState<'feed' | 'settings'>('feed');

  return (
    <div>
      <nav>
        <button onClick={() => setActiveTab('feed')}>Feed</button>
        <button onClick={() => setActiveTab('settings')}>Settings</button>
      </nav>

      {/* Both tabs stay mounted — hidden tab preserves state, form inputs, scroll */}
      <Activity mode={activeTab === 'feed' ? 'visible' : 'hidden'}>
        <FeedPage />
      </Activity>
      <Activity mode={activeTab === 'settings' ? 'visible' : 'hidden'}>
        <SettingsPage />
      </Activity>
    </div>
  );
}
```

**What `hidden` mode does:**

- Hides children visually (display: none equivalent)
- Unmounts effects (cleanup runs, but state is preserved)
- Defers updates until React has nothing else to do (low priority rendering)
- Form inputs, scroll positions, component state all survive

**Use cases:**

- Tab panels — preserve state across tab switches
- Prefetching — `<Activity mode="hidden">` pre-renders the next screen in background
- Back navigation — keep previous page alive for instant back
- Wizard steps — preserve form state while navigating steps

**Caveat with TanStack Query:** Since effects unmount in hidden mode, `useQuery` (which uses useEffect) won't fetch. For
prefetching with hidden Activity, use `queryClient.prefetchQuery` instead.

### `useEffectEvent()` — Stable callbacks in Effects

Solves the stale closure problem without suppressing lint rules.

```tsx
import { useEffect, useEffectEvent } from 'react';

function ChatRoom({ roomId, theme }: { roomId: string; theme: string }) {
  // Effect Event: always sees latest `theme`, not a dependency
  const onConnected = useEffectEvent(() => {
    showNotification('Connected!', theme);  // Always reads current theme
  });

  useEffect(() => {
    const connection = createConnection(roomId);
    connection.on('connected', () => onConnected());
    connection.connect();
    return () => connection.disconnect();
  }, [roomId]); // ✅ Only roomId — theme changes don't reconnect
}
```

**When to use:**

- Analytics/logging that reads current state but shouldn't re-trigger effects
- WebSocket/subscription callbacks needing fresh props
- Timer callbacks (setInterval) reading latest values
- Any Effect where some values are "reactive" and others are "event-like"

**Rules:**

- Must be declared in the same component/hook as the Effect that calls it
- CANNOT be in the dependency array
- Requires `eslint-plugin-react-hooks` v6+
- Only call from inside Effects — not from event handlers or render

### `cacheSignal()` — Abort cached server work (RSC only)

```tsx
import { cache, cacheSignal } from 'react';

const cachedFetch = cache(async (url: string) => {
  const response = await fetch(url, { signal: cacheSignal() });
  return response.json();
});
```

Automatically cancels fetch when the cache entry expires, render is aborted, or render fails.
Only relevant in React Server Components.

### React Compiler (19+)

The React Compiler automatically memoizes at build time. Impact on your code:

- **Remove most manual** `useMemo`, `useCallback`, `React.memo` — compiler handles it
- **Still useful manually for**: very expensive computations, referential identity for external libs
- **Requires**: eslint-plugin-react-hooks v6+ for compiler-aware lint rules
- **Prep your code**: ensure pure components, no side effects in render, proper dependency arrays

### Performance Tracks (Chrome DevTools)

React 19.2 adds custom tracks to Chrome DevTools Performance profiler:

- **Scheduler track**: shows priorities (blocking vs transition), event timing, render phases
- **Components track**: shows component tree rendering, mount/unmount timing, effect execution

Use these to identify slow components and unnecessary re-renders in production profiling.
