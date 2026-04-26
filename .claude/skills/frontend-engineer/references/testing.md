# Testing Reference

## Table of contents

- §1 Testing Strategy — Testing Trophy
- §2 Unit Tests — Vitest
- §3 Component Tests — React Testing Library
- §4 Integration Tests — RTL + MSW
- §5 E2E Tests — Playwright
- §6 Visual Tests — Storybook
- §7 What to Test (and What Not To)

---

## §1 Testing Strategy — Testing Trophy

Based on Kent C. Dodds' Testing Trophy — invest most effort in integration tests.

```
        ┌─────────┐
        │   E2E   │  ← Few: critical user flows only
       ┌┴─────────┴┐
       │Integration │  ← Most tests: components + API interactions
      ┌┴───────────┴┐
      │    Unit     │  ← Focused: utils, hooks, pure functions
     ┌┴─────────────┴┐
     │    Static     │  ← Always: TypeScript strict + ESLint
     └───────────────┘
```

### Tool stack

| Layer       | Tool                           | Purpose                                          |
|-------------|--------------------------------|--------------------------------------------------|
| Static      | TypeScript (strict) + ESLint   | Catch type errors and bad patterns at build time |
| Unit        | Vitest                         | Pure functions, utility helpers, custom hooks    |
| Component   | Vitest + React Testing Library | Component rendering and behavior                 |
| Integration | Vitest + RTL + MSW             | Component + API interaction with mocked server   |
| E2E         | Playwright                     | Full browser, critical user flows                |
| Visual      | Storybook + Chromatic          | Visual regression detection                      |

### Distribution guideline

- **Static**: 100% coverage (TypeScript strict mode on)
- **Integration**: 60-70% of your test effort (highest ROI)
- **Unit**: 20-25% (focused on complex logic)
- **E2E**: 5-10% (critical paths only — login, checkout, signup)

---

## §2 Unit Tests — Vitest

### Setup

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: ['node_modules/', 'src/test/'],
    },
  },
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
});
```

```ts
// src/test/setup.ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => cleanup());
```

### Unit test examples

```ts
// utils/formatCurrency.test.ts
import { describe, it, expect } from 'vitest';
import { formatCurrency } from './formatCurrency';

describe('formatCurrency', () => {
  it('formats USD correctly', () => {
    expect(formatCurrency(1234.56, 'USD')).toBe('$1,234.56');
  });

  it('handles zero', () => {
    expect(formatCurrency(0, 'USD')).toBe('$0.00');
  });

  it('handles negative values', () => {
    expect(formatCurrency(-50, 'USD')).toBe('-$50.00');
  });
});
```

### Testing custom hooks

```ts
// hooks/useDebounce.test.ts
import { renderHook, act } from '@testing-library/react';
import { vi } from 'vitest';
import { useDebounce } from './useDebounce';

describe('useDebounce', () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it('returns initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('hello', 500));
    expect(result.current).toBe('hello');
  });

  it('debounces value changes', () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 500),
      { initialProps: { value: 'hello' } }
    );

    rerender({ value: 'world' });
    expect(result.current).toBe('hello'); // Not yet updated

    act(() => vi.advanceTimersByTime(500));
    expect(result.current).toBe('world'); // Now updated
  });
});
```

---

## §3 Component Tests — React Testing Library

### Core philosophy

Test what the user sees and does, not how the component is implemented internally.

### Query priority (use in this order)

1. `getByRole` — accessible role (button, heading, textbox) ← **Prefer this**
2. `getByLabelText` — form fields by label
3. `getByPlaceholderText` — inputs by placeholder
4. `getByText` — visible text content
5. `getByDisplayValue` — current input value
6. `getByTestId` — **Last resort** when no semantic option exists

### Component test example

```tsx
// components/UserCard.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserCard } from './UserCard';

const mockUser = { id: '1', name: 'John Doe', email: 'john@example.com', role: 'admin' };

describe('UserCard', () => {
  it('renders user information', () => {
    render(<UserCard user={mockUser} />);

    expect(screen.getByRole('heading', { name: 'John Doe' })).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
    expect(screen.getByText('admin')).toBeInTheDocument();
  });

  it('calls onEdit when edit button is clicked', async () => {
    const user = userEvent.setup();
    const onEdit = vi.fn();

    render(<UserCard user={mockUser} onEdit={onEdit} />);

    await user.click(screen.getByRole('button', { name: /edit/i }));
    expect(onEdit).toHaveBeenCalledWith('1');
  });

  it('shows loading state', () => {
    render(<UserCard user={mockUser} loading />);
    expect(screen.getByRole('status')).toBeInTheDocument(); // Skeleton/spinner
  });
});
```

---

## §4 Integration Tests — RTL + MSW

Integration tests verify components work with their data dependencies. MSW mocks the API at the network level.

### MSW setup

```ts
// src/test/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users', () => {
    return HttpResponse.json([
      { id: '1', name: 'John', email: 'john@example.com' },
      { id: '2', name: 'Jane', email: 'jane@example.com' },
    ]);
  }),

  http.post('/api/users', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: '3', ...body }, { status: 201 });
  }),

  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({ id: params.id, name: 'John', email: 'john@example.com' });
  }),
];
```

```ts
// src/test/mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

```ts
// src/test/setup.ts — add MSW lifecycle
import { server } from './mocks/server';

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### Integration test example

```tsx
// features/users/UserList.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { http, HttpResponse } from 'msw';
import { server } from '@/test/mocks/server';
import { UserList } from './UserList';

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }, // No retries in tests
  });
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  );
}

describe('UserList', () => {
  it('renders users from API', async () => {
    renderWithProviders(<UserList />);

    // Shows loading state
    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    // Waits for data to load
    await waitFor(() => {
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText('Jane')).toBeInTheDocument();
    });
  });

  it('handles API error gracefully', async () => {
    // Override handler for this test
    server.use(
      http.get('/api/users', () => HttpResponse.json(null, { status: 500 }))
    );

    renderWithProviders(<UserList />);

    await waitFor(() => {
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    });
  });

  it('creates a new user', async () => {
    const user = userEvent.setup();
    renderWithProviders(<UserList />);

    await waitFor(() => expect(screen.getByText('John')).toBeInTheDocument());

    await user.click(screen.getByRole('button', { name: /add user/i }));
    await user.type(screen.getByLabelText(/name/i), 'New User');
    await user.type(screen.getByLabelText(/email/i), 'new@example.com');
    await user.click(screen.getByRole('button', { name: /save/i }));

    await waitFor(() => {
      expect(screen.getByText('New User')).toBeInTheDocument();
    });
  });
});
```

---

## §5 E2E Tests — Playwright

### Setup

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'mobile', use: { ...devices['iPhone 14'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### E2E test example — critical user flow

```ts
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication flow', () => {
  test('user can sign up, log in, and access dashboard', async ({ page }) => {
    // Sign up
    await page.goto('/signup');
    await page.getByLabel('Name').fill('Test User');
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('SecurePass123!');
    await page.getByRole('button', { name: /create account/i }).click();

    // Redirected to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByRole('heading', { name: /welcome/i })).toBeVisible();

    // Log out
    await page.getByRole('button', { name: /log out/i }).click();
    await expect(page).toHaveURL('/');

    // Log in
    await page.goto('/login');
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('SecurePass123!');
    await page.getByRole('button', { name: /sign in/i }).click();

    await expect(page).toHaveURL('/dashboard');
  });
});
```

### Playwright best practices

- Use `getByRole`, `getByLabel`, `getByText` — same philosophy as RTL
- Use `await expect(locator).toBeVisible()` not `waitForSelector`
- Use Page Object or Feature Object pattern for reusable actions
- Keep E2E tests focused on critical paths — login, checkout, core workflows
- Run in CI with retries (flaky tests are expected at this level)

---

## §6 Visual Tests — Storybook

```tsx
// components/Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'UI/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: { control: 'select', options: ['primary', 'secondary', 'ghost'] },
    size: { control: 'select', options: ['sm', 'md', 'lg'] },
  },
};
export default meta;

type Story = StoryObj<typeof Button>;

export const Primary: Story = { args: { variant: 'primary', children: 'Click me' } };
export const Secondary: Story = { args: { variant: 'secondary', children: 'Click me' } };
export const Loading: Story = { args: { variant: 'primary', loading: true, children: 'Loading' } };
export const Disabled: Story = { args: { variant: 'primary', disabled: true, children: 'Disabled' } };
```

Pair with Chromatic for automated visual regression testing in CI.

---

## §7 What to Test (and What Not To)

### DO test

- **User interactions**: clicks, typing, form submission
- **Data rendering**: correct data displayed from API
- **Error states**: API failure, validation errors, empty states
- **Loading states**: skeletons, spinners shown during fetch
- **Conditional rendering**: show/hide based on permissions, flags
- **Accessibility**: ARIA roles, keyboard navigation, focus management
- **Edge cases**: empty lists, very long text, special characters

### DON'T test

- **Implementation details**: internal state shape, method names, hook call count
- **CSS/styling**: unless visual regression testing with Chromatic
- **Third-party library internals**: if TanStack Query caches correctly
- **Snapshot tests**: fragile, low signal, high maintenance (avoid or minimize)
- **Console.log statements**: not user-facing behavior
- **Static content**: if it's just rendering a string, TypeScript already covers it

### AAA Pattern for every test

```ts
it('shows error when form is submitted with invalid email', async () => {
  // Arrange — set up component and dependencies
  const user = userEvent.setup();
  render(<LoginForm />);

  // Act — perform the user action
  await user.type(screen.getByLabelText(/email/i), 'invalid-email');
  await user.click(screen.getByRole('button', { name: /sign in/i }));

  // Assert — verify the expected outcome
  expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
});
```
