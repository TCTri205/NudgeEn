---
library: tanstack start
package: "@tanstack/react-start"
context7_library_id: /websites/tanstack_start_framework_react
synced_version: latest
project_version: latest
declared_range: latest
benchmark_score: 84.67
source_reputation: High
last_synced: 2026-03-21
coverage: server-functions, createServerFn, route loaders, SSR, middleware, auth, API routes, server-only functions
---

# TanStack Start

Full-stack React framework built on Vite + TanStack Router. Enables server functions callable from client, SSR by
default.

## Bootstrap (vite.config.ts)

```ts
import { tanstackStart } from '@tanstack/react-start/plugin/vite'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [tanstackStart()],
})
```

## Server Functions — `createServerFn`

```tsx
import { createServerFn } from '@tanstack/react-start'

// Basic GET server function
export const getServerTime = createServerFn().handler(async () => {
  return new Date().toISOString() // runs only on server
})

// POST with input validator
export const updateCount = createServerFn({ method: 'POST' })
  .inputValidator((d: number) => d)
  .handler(async ({ data }) => {
    await db.update({ count: data })
  })

// Call from anywhere (component, loader, hook)
const time = await getServerTime()
```

## Route with Loader + Server Function

```tsx
// src/routes/movies.tsx
import { createFileRoute } from '@tanstack/react-router'
import { createServerFn } from '@tanstack/react-start'

const fetchMovies = createServerFn().handler(async () => {
  const res = await fetch('https://api.example.com/movies', {
    headers: { Authorization: `Bearer ${process.env.API_KEY}` },
  })
  return res.json()
})

export const Route = createFileRoute('/movies')({
  loader: async () => {
    try {
      return { movies: await fetchMovies(), error: null }
    } catch {
      return { movies: [], error: 'Failed to load' }
    }
  },
  component: MoviesPage,
})

function MoviesPage() {
  const { movies } = Route.useLoaderData()
  return <ul>{movies.map(m => <li key={m.id}>{m.title}</li>)}</ul>
}
```

## Server-Only Functions

```tsx
import { createServerFn, createServerOnlyFn } from '@tanstack/react-start'

// RPC — callable from client (network request)
const fetchUser = createServerFn().handler(async () => await db.users.find())

// Server-only — crashes if called from client
const getSecret = createServerOnlyFn(() => process.env.SECRET)
```

## Protected Routes with `beforeLoad`

```tsx
// src/routes/_authed.tsx — layout route for protected pages
import { createFileRoute, redirect } from '@tanstack/react-router'
import { createServerFn } from '@tanstack/react-start'

const getCurrentUser = createServerFn().handler(async () => {
  const session = await getSession()
  return session?.user ?? null
})

export const Route = createFileRoute('/_authed')({
  beforeLoad: async ({ location }) => {
    const user = await getCurrentUser()
    if (!user) {
      throw redirect({ to: '/login', search: { redirect: location.href } })
    }
    return { user } // available via Route.useRouteContext() in child routes
  },
})

// src/routes/_authed/dashboard.tsx
export const Route = createFileRoute('/_authed/dashboard')({
  component: () => {
    const { user } = Route.useRouteContext()
    return <div>Hello {user.email}</div>
  },
})
```

## Server Route Handlers (API Routes)

```tsx
// src/routes/api/hello.tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/api/hello')({
  server: {
    middleware: [authMiddleware],
    handlers: {
      GET: async ({ request }) => new Response('Hello!'),
      POST: async ({ request }) => {
        const body = await request.json()
        return Response.json({ message: `Hello ${body.name}` })
      },
    },
  },
})
```

## Middleware for Server Functions

```tsx
import { createMiddleware } from '@tanstack/react-start'

const authMiddleware = createMiddleware({ type: 'function' })
  .client(async ({ next }) => {
    return next({ headers: { Authorization: `Bearer ${getToken()}` } })
  })
  .server(async ({ next }) => {
    return next({ context: { user: await getUser() } })
  })

const protectedFn = createServerFn()
  .middleware([authMiddleware])
  .handler(async ({ context }) => {
    return `Hello ${context.user.name}`
  })
```

## Root Route Setup

```tsx
// src/routes/__root.tsx
import { createRootRouteWithContext, HeadContent, Scripts } from '@tanstack/react-router'
import type { QueryClient } from '@tanstack/react-query'

interface RouterContext {
  queryClient: QueryClient
}

export const Route = createRootRouteWithContext<RouterContext>()({
  head: () => ({
    meta: [{ charSet: 'utf-8' }, { name: 'viewport', content: 'width=device-width, initial-scale=1' }],
    links: [{ rel: 'stylesheet', href: appCss }],
  }),
  shellComponent: RootDocument,
})
```

## Sentry Instrumentation of Server Functions

```tsx
import * as Sentry from '@sentry/tanstackstart-react'

const myFn = createServerFn().handler(async () => {
  return Sentry.startSpan({ name: 'My operation' }, async () => {
    return await expensiveOperation()
  })
})
```

## Router Initialization

```tsx
// src/router.tsx
import { createRouter } from '@tanstack/react-router'
import { routeTree } from './routeTree.gen' // auto-generated

export const router = createRouter({
  routeTree,
  context: { queryClient: undefined! },
  defaultPreload: 'intent',
  scrollRestoration: true,
})
```
