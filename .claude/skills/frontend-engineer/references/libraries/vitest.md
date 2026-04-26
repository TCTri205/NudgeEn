---
library: vitest
package: "vitest"
context7_library_id: /vitest-dev/vitest
synced_version: v3.2.4
project_version: v3.0.5
declared_range: ^3.0.5
benchmark_score: 88.18
source_reputation: High
last_synced: 2026-03-21
coverage: describe/test/expect, vi.fn/mock/spyOn, jsdom setup, React Testing Library, async tests, coverage
---

# Vitest

Vite-native testing framework. Jest-compatible API. This project uses jsdom + React Testing Library.

## Basic Test

```ts
import { describe, expect, it, test } from 'vitest'

describe('math utils', () => {
  it('adds numbers', () => {
    expect(1 + 1).toBe(2)
  })

  test('object equality', () => {
    expect({ a: 1 }).toEqual({ a: 1 })
  })
})
```

## Configuration (vite.config.ts)

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  test: {
    environment: 'jsdom',   // or 'happy-dom'
    globals: true,          // no need to import describe/it/expect
    setupFiles: './src/test/setup.ts',
  },
})
```

## Setup File

```ts
// src/test/setup.ts
import '@testing-library/jest-dom'  // extends expect with DOM matchers
```

## React Component Testing (with @testing-library/react)

```tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, expect, test } from 'vitest'
import Counter from './Counter'

describe('Counter', () => {
  test('increments on click', () => {
    render(<Counter initialCount={0} />)

    expect(screen.getByText('Count: 0')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /increment/i }))

    expect(screen.getByText('Count: 1')).toBeInTheDocument()
  })

  test('renders with initial value', () => {
    render(<Counter initialCount={5} />)
    expect(screen.getByText('Count: 5')).toBeInTheDocument()
  })
})
```

## Async Tests

```ts
test('fetches data', async () => {
  const data = await fetchUser('123')
  expect(data.name).toBe('Alice')
})

// With userEvent (async interactions)
import userEvent from '@testing-library/user-event'

test('fills form', async () => {
  const user = userEvent.setup()
  render(<LoginForm />)

  await user.type(screen.getByLabelText(/email/i), 'alice@example.com')
  await user.click(screen.getByRole('button', { name: /submit/i }))

  expect(screen.getByText('Welcome!')).toBeInTheDocument()
})
```

## Mocking

```ts
import { vi, describe, test, expect } from 'vitest'

// Mock a function
const fn = vi.fn()
fn.mockReturnValue(42)
fn.mockResolvedValue({ data: 'hello' })  // async

// Mock a module
vi.mock('./api', () => ({
  fetchUser: vi.fn().mockResolvedValue({ id: '1', name: 'Alice' }),
}))

// Mock with partial module (spy + override)
vi.mock('./api', async (importOriginal) => {
  const mod = await importOriginal()
  return {
    ...mod,
    fetchUser: vi.fn().mockResolvedValue({ id: '1', name: 'Alice' }),
  }
})

// Spy on existing method
const spy = vi.spyOn(console, 'error').mockImplementation(() => {})
```

## Mock Assertions

```ts
expect(fn).toHaveBeenCalled()
expect(fn).toHaveBeenCalledTimes(2)
expect(fn).toHaveBeenCalledWith('arg1', 'arg2')
expect(fn).toHaveBeenLastCalledWith('last-arg')
expect(fn).toHaveReturnedWith(42)
```

## Hooks Testing with renderHook

```tsx
import { renderHook, act } from '@testing-library/react'
import { useCounter } from './useCounter'

test('useCounter increments', () => {
  const { result } = renderHook(() => useCounter(0))

  act(() => {
    result.current.increment()
  })

  expect(result.current.count).toBe(1)
})
```

## Timer Mocks

```ts
import { vi, beforeEach, afterEach } from 'vitest'

beforeEach(() => vi.useFakeTimers())
afterEach(() => vi.useRealTimers())

test('delays work', async () => {
  const callback = vi.fn()
  setTimeout(callback, 1000)

  vi.advanceTimersByTime(1000)

  expect(callback).toHaveBeenCalled()
})
```

## Environment Override per File

```ts
/**
 * @vitest-environment jsdom
 */
test('uses DOM', () => {
  const el = document.createElement('div')
  expect(el).not.toBeNull()
})
```

## Common DOM Matchers (from @testing-library/jest-dom)

```ts
expect(element).toBeInTheDocument()
expect(element).toBeVisible()
expect(element).toBeDisabled()
expect(element).toHaveValue('text')
expect(element).toHaveTextContent('hello')
expect(element).toHaveAttribute('aria-label', 'close')
expect(element).toHaveClass('active')
expect(element).toHaveFocus()
```

## Run Commands

```bash
bun --bun run test           # run once
bun --bun run test --watch   # watch mode
bun --bun run test --coverage # coverage report
vitest run path/to/file.test.tsx  # single file
vitest run -t "test name"    # by test name
```
