---
library: tanstack store
package: "@tanstack/react-store"
context7_library_id: /tanstack/store
synced_version: latest
project_version: latest
declared_range: latest
benchmark_score: 87.85
source_reputation: High
last_synced: 2026-03-21
coverage: Store, useStore, setState, derived state, shallow comparison, React integration
---

# TanStack Store

Lightweight, framework-agnostic reactive state. This project uses it instead of Zustand.

## Create a Store

```tsx
import { Store } from '@tanstack/store'

// Define outside React — store is a singleton
export const counterStore = new Store({
  count: 0,
  step: 1,
})
```

## Use in React Components

```tsx
import { useStore } from '@tanstack/react-store'
import { counterStore } from '../lib/store'

// Selective subscription — only re-renders when count changes
function Counter() {
  const count = useStore(counterStore, (state) => state.count)
  return <div>Count: {count}</div>
}

// Subscribe to whole state
function Debug() {
  const state = useStore(counterStore)
  return <pre>{JSON.stringify(state, null, 2)}</pre>
}
```

## Update State

```tsx
// Immutable update via setState
counterStore.setState((state) => ({
  ...state,
  count: state.count + state.step,
}))

// Direct state mutation (spread required)
counterStore.setState((prev) => ({ ...prev, step: 5 }))
```

## Full Example

```tsx
import { Store, useStore } from '@tanstack/react-store'

export const store = new Store({ dogs: 0, cats: 0 })

function Display({ animal }: { animal: 'dogs' | 'cats' }) {
  const count = useStore(store, (state) => state[animal])
  return <div>{animal}: {count}</div>
}

function Increment({ animal }: { animal: 'dogs' | 'cats' }) {
  return (
    <button onClick={() => store.setState((s) => ({ ...s, [animal]: s[animal] + 1 }))}>
      Add {animal}
    </button>
  )
}
```

## Shallow Comparison (prevent unnecessary re-renders for objects/arrays)

```tsx
import { useStore, shallow } from '@tanstack/react-store'

const userStore = new Store({ user: { name: 'Alice', age: 30 } })

function UserProfile() {
  // shallow comparison — won't re-render if new object has same values
  const user = useStore(userStore, (state) => state.user, { equal: shallow })
  return <div>{user.name} — {user.age}</div>
}
```

## useStore Signature

```tsx
function useStore<TState, TSelected>(
  store: Store<TState>,
  selector?: (state: TState) => TSelected,
  options?: { equal?: (a: TSelected, b: TSelected) => boolean }
): TSelected
```

## Derived State

```tsx
import { Derived } from '@tanstack/store'

const derived = new Derived({
  deps: [counterStore],
  fn: () => counterStore.state.count * 2,
})

// In component
const doubled = useStore(derived)
```

## Organize Stores (project pattern)

```ts
// src/lib/app-store.ts
import { Store } from '@tanstack/store'

export const uiStore = new Store({
  sidebarOpen: false,
  theme: 'auto' as 'light' | 'dark' | 'auto',
})

export const uiActions = {
  toggleSidebar: () =>
    uiStore.setState((s) => ({ ...s, sidebarOpen: !s.sidebarOpen })),
  setTheme: (theme: 'light' | 'dark' | 'auto') =>
    uiStore.setState((s) => ({ ...s, theme })),
}
```
