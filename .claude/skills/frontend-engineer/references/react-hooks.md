# React Hooks Reference

## Scope

This reference covers the commonly used built-in hooks a frontend engineer should know in React
19.2, with practical guidance for modern product code. It focuses on:

- basic concept
- when to use the hook
- common mistakes or caveats
- a concrete example

Notes:

- `useFormStatus` is from `react-dom`, not `react`
- `useFormState` should be treated as the old canary name for `useActionState`, not as a separate
  current stable hook
- React 19.2 and the React Compiler reduce some manual `useMemo` and `useCallback` usage, but they
  do not make those hooks irrelevant

## Quick selection guide

| Need                                                       | Prefer               |
|------------------------------------------------------------|----------------------|
| Local interactive state                                    | `useState`           |
| Complex local transitions                                  | `useReducer`         |
| Shared read-mostly tree state                              | `useContext`         |
| Mutable value that should not re-render                    | `useRef`             |
| Sync with external system                                  | `useEffect`          |
| Measure layout before paint                                | `useLayoutEffect`    |
| Inject runtime CSS in a library                            | `useInsertionEffect` |
| Stabilize expensive calculation                            | `useMemo`            |
| Stabilize callback identity                                | `useCallback`        |
| Generate accessible IDs                                    | `useId`              |
| Mark non-urgent UI work                                    | `useTransition`      |
| Keep slow UI lagging behind urgent input                   | `useDeferredValue`   |
| Handle form action state                                   | `useActionState`     |
| Read nearest form submission status                        | `useFormStatus`      |
| Show optimistic UI during async work                       | `useOptimistic`      |
| Read latest values inside an Effect without re-subscribing | `useEffectEvent`     |
| Label a custom hook in DevTools                            | `useDebugValue`      |

## `useState`

**Concept**

`useState` stores local component state and triggers a re-render when that state changes.

**Use when**

- the state is local to one component or a very small subtree
- transitions are simple and event-driven
- a boolean, string, number, selected item, or small object is enough

**Notes**

- use functional updates when the next value depends on the previous one
- do not split tightly related state too aggressively if it makes transitions harder to follow
- if state transitions become branch-heavy, move to `useReducer`

```tsx
import { useState } from 'react';

export function LikeButton() {
  const [liked, setLiked] = useState(false);
  const [count, setCount] = useState(12);

  function handleClick() {
    setLiked((value) => !value);
    setCount((value) => (liked ? value - 1 : value + 1));
  }

  return (
    <button type="button" onClick={handleClick}>
      {liked ? 'Unlike' : 'Like'} ({count})
    </button>
  );
}
```

## `useEffect`

**Concept**

`useEffect` synchronizes React with an external system such as a DOM API, timer, subscription,
network side effect, or third-party widget.

**Use when**

- connecting and disconnecting from a socket
- subscribing to browser APIs
- syncing imperative libraries
- reacting to URL, room ID, or auth token changes in an external system

**Notes**

- if there is no external system, you often do not need an Effect
- declare all reactive dependencies honestly
- in development with Strict Mode, React runs setup and cleanup an extra time
- if the Effect is only reading the latest value inside a subscription callback, consider
  `useEffectEvent`

```tsx
import { useEffect } from 'react';

function ChatRoom({ roomId }: { roomId: string }) {
  useEffect(() => {
    const connection = createConnection(roomId);
    connection.connect();

    return () => {
      connection.disconnect();
    };
  }, [roomId]);

  return null;
}
```

## `useContext`

**Concept**

`useContext` reads a value from the nearest matching provider and subscribes the component to that
context.

**Use when**

- sharing theme, locale, auth session, feature flags, or design-system state
- the value is needed across a subtree without prop drilling

**Notes**

- context is not a replacement for all state management
- every consumer re-renders when the provided value changes
- keep provider values stable and small; split contexts if unrelated values change at different
  rates

```tsx
import { createContext, useContext } from 'react';

const ThemeContext = createContext<'light' | 'dark'>('light');

export function ThemeBadge() {
  const theme = useContext(ThemeContext);
  return <span data-theme={theme}>Theme: {theme}</span>;
}
```

## `useReducer`

**Concept**

`useReducer` manages local state transitions with a reducer function and explicit actions.

**Use when**

- state transitions are complex
- several events affect the same state object
- you need predictable branch-based updates

**Notes**

- prefer meaningful action names over generic patch actions
- keep reducers pure
- if the reducer grows into cross-component shared state, that is a sign to consider Zustand or
  another state layer

```tsx
import { useReducer } from 'react';

type ComposerState = {
  text: string;
  status: 'idle' | 'submitting' | 'error';
};

type ComposerAction =
  | { type: 'text-changed'; value: string }
  | { type: 'submit-started' }
  | { type: 'submit-failed' }
  | { type: 'submit-succeeded' };

function reducer(state: ComposerState, action: ComposerAction): ComposerState {
  switch (action.type) {
    case 'text-changed':
      return { ...state, text: action.value };
    case 'submit-started':
      return { ...state, status: 'submitting' };
    case 'submit-failed':
      return { ...state, status: 'error' };
    case 'submit-succeeded':
      return { text: '', status: 'idle' };
    default:
      return state;
  }
}
```

## `useRef`

**Concept**

`useRef` stores a mutable value that survives re-renders without causing a re-render.

**Use when**

- holding a DOM node
- keeping an interval ID, timeout ID, previous value, or imperative instance
- avoiding stale access to mutable values across renders

**Notes**

- changing `ref.current` does not re-render
- do not use refs as hidden state for rendered output
- do not read or write refs during render except for predictable initialization

```tsx
import { useEffect, useRef } from 'react';

export function SearchInput() {
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return <input ref={inputRef} placeholder="Search feed" />;
}
```

## `useMemo`

**Concept**

`useMemo` caches the result of a calculation between renders.

**Use when**

- a calculation is measurably expensive
- the memoized value is passed to a memoized child
- a derived object would otherwise change on every render and break another hook dependency

**Notes**

- do not add `useMemo` everywhere by default
- first fix data flow and component structure; then memoize hot paths
- React Compiler can reduce some manual memoization needs, but you still need `useMemo` when a
  stable cached value matters in the current codebase

```tsx
import { useMemo, useState } from 'react';

export function FeedFilter({ posts }: { posts: Post[] }) {
  const [tab, setTab] = useState<'all' | 'following'>('all');

  const visiblePosts = useMemo(() => {
    return posts.filter((post) => (tab === 'all' ? true : post.isFollowing));
  }, [posts, tab]);

  return <FeedList posts={visiblePosts} onTabChange={setTab} />;
}
```

## `useCallback`

**Concept**

`useCallback` caches a function identity between renders.

**Use when**

- passing callbacks into memoized children
- a callback is used as a dependency of another hook and would otherwise change every render
- a third-party hook or widget depends on stable callback identity

**Notes**

- do not use it just to “optimize” every event handler
- if no memoized child or dependency sensitivity exists, `useCallback` often adds noise
- prefer simpler code unless profiling shows value

```tsx
import { memo, useCallback, useState } from 'react';

const FeedItem = memo(function FeedItem({
  title,
  onSave,
}: {
  title: string;
  onSave: () => void;
}) {
  return <button onClick={onSave}>{title}</button>;
});

export function SavedFeed() {
  const [savedIds, setSavedIds] = useState<string[]>([]);

  const handleSave = useCallback(() => {
    setSavedIds((ids) => [...ids, crypto.randomUUID()]);
  }, []);

  return <FeedItem title="Save post" onSave={handleSave} />;
}
```

## `useLayoutEffect`

**Concept**

`useLayoutEffect` runs after React commits DOM updates but before the browser repaints.

**Use when**

- measuring layout
- positioning a tooltip, popover, or floating element before paint
- synchronizing scroll or size-sensitive DOM logic that would visibly flicker in `useEffect`

**Notes**

- prefer `useEffect` unless you truly need pre-paint work
- this hook can hurt performance because it blocks paint
- it does nothing during server rendering, so keep it in client-only UI

```tsx
import { useLayoutEffect, useRef, useState, type ReactNode } from 'react';

export function Tooltip({ children }: { children: ReactNode }) {
  const ref = useRef<HTMLDivElement | null>(null);
  const [height, setHeight] = useState(0);

  useLayoutEffect(() => {
    setHeight(ref.current?.getBoundingClientRect().height ?? 0);
  }, []);

  return (
    <div ref={ref} style={{ transform: `translateY(-${height}px)` }}>
      {children}
    </div>
  );
}
```

## `useInsertionEffect`

**Concept**

`useInsertionEffect` is a specialized hook for injecting styles before layout Effects run.

**Use when**

- writing a CSS-in-JS library or styling runtime

**Notes**

- most app code should not use this hook
- React docs explicitly position it for CSS-in-JS library authors
- you cannot update state here, and refs are not attached yet

```tsx
import { useInsertionEffect } from 'react';

function useRuntimeCss(rule: string) {
  useInsertionEffect(() => {
    const style = document.createElement('style');
    style.textContent = rule;
    document.head.appendChild(style);

    return () => {
      document.head.removeChild(style);
    };
  }, [rule]);
}
```

## `useDebugValue`

**Concept**

`useDebugValue` adds a readable label to a custom hook in React DevTools.

**Use when**

- building reusable hooks that are hard to inspect
- you want DevTools to show a meaningful state label instead of raw internals

**Notes**

- only useful for custom hook authoring and debugging
- skip it for ordinary app components unless the hook is reused enough to justify it

```tsx
import { useDebugValue, useEffect, useState } from 'react';

function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    function handleOnline() {
      setIsOnline(true);
    }

    function handleOffline() {
      setIsOnline(false);
    }

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  useDebugValue(isOnline ? 'Online' : 'Offline');
  return isOnline;
}
```

## `useId`

**Concept**

`useId` generates a unique stable ID for accessibility relationships.

**Use when**

- linking labels, hints, and error messages
- generating multiple related IDs for a form field

**Notes**

- prefer `useId` over `Math.random()` for SSR-safe markup
- it is for DOM relationships, not list keys

```tsx
import { useId } from 'react';

export function EmailField() {
  const inputId = useId();
  const hintId = useId();

  return (
    <div>
      <label htmlFor={inputId}>Email</label>
      <input id={inputId} aria-describedby={hintId} type="email" />
      <p id={hintId}>We only use this for account notifications.</p>
    </div>
  );
}
```

## `useTransition`

**Concept**

`useTransition` marks updates as non-urgent so urgent interactions can stay responsive.

**Use when**

- switching tabs, routes, or filters where some heavy UI can update in the background
- running async actions where the UI should stay interactive
- pairing with `useOptimistic` for immediate feedback plus background confirmation

**Notes**

- transitions do not replace all loading states
- do not wrap controlled text input state itself in a transition
- React 19 docs describe the function passed to `startTransition` as an Action

```tsx
import { useState, useTransition } from 'react';

export function FeedTabs() {
  const [tab, setTab] = useState<'for-you' | 'following'>('for-you');
  const [isPending, startTransition] = useTransition();

  function handleTabChange(nextTab: 'for-you' | 'following') {
    startTransition(() => {
      setTab(nextTab);
    });
  }

  return (
    <>
      <button onClick={() => handleTabChange('for-you')}>For you</button>
      <button onClick={() => handleTabChange('following')}>Following</button>
      {isPending ? <p>Updating feed...</p> : <FeedContent tab={tab} />}
    </>
  );
}
```

## `useDeferredValue`

**Concept**

`useDeferredValue` lets a slow part of the UI lag behind a fast-changing value.

**Use when**

- an input should stay responsive while a slow list, chart, or preview catches up
- the expensive work happens during rendering

**Notes**

- this is different from debouncing network requests
- the slow subtree often needs `memo` to benefit
- use it when urgent typing or pointer input should win over non-urgent rendering

```tsx
import { memo, useDeferredValue, useState } from 'react';

const SlowList = memo(function SlowList({ query }: { query: string }) {
  return <ExpensiveSearchResults query={query} />;
});

export function SearchPanel() {
  const [query, setQuery] = useState('');
  const deferredQuery = useDeferredValue(query);

  return (
    <>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <SlowList query={deferredQuery} />
    </>
  );
}
```

## `useFormStatus`

**Concept**

`useFormStatus` reads the submission status of the nearest parent `<form>`.

**Use when**

- a nested button, status badge, or hint inside a form needs pending state
- you want access to submitted `FormData`, method, or action without prop drilling

**Notes**

- import it from `react-dom`
- it only works inside a descendant of the form it tracks
- it does not manage the form result state; it only reports status

```tsx
'use client';

import { useFormStatus } from 'react-dom';

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Saving...' : 'Save profile'}
    </button>
  );
}

export function ProfileForm({
  action,
}: {
  action: (formData: FormData) => Promise<void>;
}) {
  return (
    <form action={action}>
      <input name="displayName" />
      <SubmitButton />
    </form>
  );
}
```

## `useFormState`

**Concept**

Treat `useFormState` as historical context, not as a current stable React 19.2 hook.

**Use when**

- reading older examples, canary-era articles, or code written before the rename to
  `useActionState`

**Notes**

- React 19 renamed `ReactDOM.useFormState` to `React.useActionState`
- new code should use `useActionState`
- if a repo still uses `useFormState`, plan a cleanup toward the current API and verify framework
  compatibility first

```tsx
// Old examples may show:
// const [state, formAction] = useFormState(action, initialState);

// Current React 19.2 code should use:
const [state, formAction, isPending] = useActionState(action, initialState);
```

## `useActionState`

**Concept**

`useActionState` ties a piece of UI state to an Action, commonly a form submission or async update.

**Use when**

- handling server actions or async form actions
- keeping result state, error state, and pending state close to the action
- building mutation flows without manual `loading/error/result` wiring everywhere

**Notes**

- it returns `[state, dispatchAction, isPending]`
- known errors can be returned as state; unknown errors should throw and be handled by an Error
  Boundary
- React docs show it combining naturally with `useOptimistic`

```tsx
'use client';

import { useActionState } from 'react';

type SignupState = {
  message: string;
  fieldError?: string;
};

const initialState: SignupState = { message: '' };

async function signupAction(
  previousState: SignupState,
  formData: FormData,
): Promise<SignupState> {
  const email = String(formData.get('email') ?? '');

  if (!email.includes('@')) {
    return { message: '', fieldError: 'Email is invalid' };
  }

  await saveSignup(email);
  return { message: 'Signup completed' };
}

export function SignupForm() {
  const [state, formAction, isPending] = useActionState(signupAction, initialState);

  return (
    <form action={formAction}>
      <input name="email" type="email" />
      {state.fieldError ? <p>{state.fieldError}</p> : null}
      {state.message ? <p>{state.message}</p> : null}
      <button disabled={isPending} type="submit">
        {isPending ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
```

## `useOptimistic`

**Concept**

`useOptimistic` lets the UI show a temporary success-looking state while an Action is still in
flight.

**Use when**

- liking a post
- adding a comment
- reordering a list
- toggling a setting where the UI should feel instant

**Notes**

- optimistic updates should be reversible
- use it for UI feedback, not as a replacement for canonical server state ownership
- in React Query or Zustand projects, keep one clear owner of confirmed data

```tsx
'use client';

import { startTransition, useOptimistic } from 'react';

export function LikeButton({
  likes,
  onLike,
}: {
  likes: number;
  onLike: () => Promise<number>;
}) {
  const [optimisticLikes, addOptimisticLike] = useOptimistic(
    likes,
    (currentLikes, delta: number) => currentLikes + delta,
  );

  async function handleLike() {
    startTransition(async () => {
      addOptimisticLike(1);
      await onLike();
    });
  }

  return <button onClick={handleLike}>Like ({optimisticLikes})</button>;
}
```

## `useEffectEvent`

**Concept**

`useEffectEvent` lets an Effect call logic that reads the latest props or state without making the
surrounding Effect re-subscribe to those values.

**Use when**

- an external subscription should stay stable, but the callback should use the latest theme,
  analytics data, or derived state
- extracting custom hooks with subscriptions, intervals, or sockets

**Notes**

- this is not a dependency-array escape hatch for ordinary logic
- use it only for logic that is conceptually an event fired from an Effect
- React 19.2 docs and the 19.2 release note position this as the right fix for many “stale closure
  inside Effect callback” cases

```tsx
import { useEffect, useEffectEvent } from 'react';

function ChatRoom({ roomId, theme }: { roomId: string; theme: 'light' | 'dark' }) {
  const onConnected = useEffectEvent(() => {
    showToast('Connected', { theme });
  });

  useEffect(() => {
    const connection = createConnection(roomId);

    connection.on('connected', () => {
      onConnected();
    });

    connection.connect();

    return () => {
      connection.disconnect();
    };
  }, [roomId]);

  return null;
}
```

## Basic patterns to prefer in product code

- Start with `useState`; move to `useReducer` only when transition logic becomes hard to reason
  about
- Use `useEffect` for external systems, not as a generic data-flow tool
- Reach for `useRef` before state when the value should not re-render the UI
- Add `useMemo` and `useCallback` only when they solve a measured render problem or a real identity
  problem
- Use `useTransition`, `useDeferredValue`, `useActionState`, and `useOptimistic` to improve
  perceived responsiveness instead of inventing ad-hoc pending logic everywhere
- Prefer `useEffectEvent` over linter suppression when an Effect callback needs the latest values
  without re-subscribing

## Related React 19 API worth knowing

The user-provided article also covers `use(resource)`. It is a real React 19 API, but it is not in
the main hook list requested above. Use it to read a Promise or context during render, typically
with Suspense and Error Boundaries. In Server Components, prefer `async` / `await` over `use` when
you can, because the official docs call that the better default for server-side data reads.

## Sources

- React hooks reference: https://react.dev/reference/react
- React DOM hooks reference: https://react.dev/reference/react-dom/hooks
- React 19 release note for the `useFormState` to `useActionState` rename:
  https://react.dev/blog/2024/12/05/react-19
- Supporting article from the user prompt:
  https://medium.com/@rohitkuwar/deep-dive-into-react-19s-latest-hooks-use-useactionstate-useoptimistic-and-useformstatus-849395af9c11
