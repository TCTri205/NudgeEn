---
library: tanstack router
package: "@tanstack/react-router"
context7_library_id: /tanstack/router
synced_version: v1.114.3
project_version: latest
declared_range: latest
benchmark_score: 86.83
source_reputation: High
last_synced: 2026-03-21
coverage: file-based routing, createFileRoute, loaders, search params, Link, useNavigate, route context, nested routes, error boundaries
---

# TanStack Router

Type-safe, file-based router for React. Route tree is auto-generated into `routeTree.gen.ts` — never edit that file
manually.

## File-Based Route Convention

```
src/routes/
  __root.tsx          → root layout (all routes)
  index.tsx           → /
  about.tsx           → /about
  posts.tsx           → /posts (layout)
  posts/
    index.tsx         → /posts
    $postId.tsx       → /posts/:postId (dynamic)
  _authed.tsx         → pathless layout route (no URL segment)
  _authed/
    dashboard.tsx     → /dashboard (wrapped by _authed)
  (group)/
    settings.tsx      → /settings (grouped, no URL impact)
```

## Basic Route Definition

```tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/posts')({
  loader: () => fetchPosts(),           // runs before component renders
  component: PostsPage,
  pendingComponent: () => <Spinner />,
  errorComponent: ({ error }) => <div>{error.message}</div>,
})

function PostsPage() {
  const posts = Route.useLoaderData()
  return <ul>{posts.map(p => <li key={p.id}>{p.title}</li>)}</ul>
}
```

## Dynamic Routes + Params

```tsx
// src/routes/posts.$postId.tsx
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params }) => fetchPost(params.postId),
  component: function PostPage() {
    const post = Route.useLoaderData()
    const { postId } = Route.useParams()
    return <h1>{post.title}</h1>
  },
})
```

## Search Params with Validation

```tsx
export const Route = createFileRoute('/posts/$postId')({
  validateSearch: (search) => ({
    page: Number(search?.page ?? 1),
    filter: String(search?.filter ?? ''),
  }),
  loaderDeps: ({ search }) => ({ page: search.page }),
  loader: async ({ params, deps }) => {
    return fetchPost(params.postId, { page: deps.page })
  },
  component: function PostPage() {
    const { page, filter } = Route.useSearch()
    const { postId } = Route.useParams()
    return <div>Post {postId}, page {page}</div>
  },
})
```

## Route Context (passes data down to child routes)

```tsx
// Parent route (e.g., _authed.tsx)
export const Route = createFileRoute('/_authed')({
  beforeLoad: async () => {
    const user = await getUser()
    if (!user) throw redirect({ to: '/login' })
    return { user }
  },
})

// Child route
export const Route = createFileRoute('/_authed/dashboard')({
  component: function Dashboard() {
    const { user } = Route.useRouteContext()
    return <div>Welcome {user.name}</div>
  },
})
```

## Type-Safe Link Component

```tsx
import { Link } from '@tanstack/react-router'

// Basic link
<Link to="/">Home</Link>

// With path params
<Link to="/posts/$postId" params={{ postId: '123' }}>View Post</Link>

// With search params
<Link to="/posts" search={{ page: 2, sort: 'newest' }}>Next Page</Link>

// Functional search param update (preserves existing params)
<Link to="." search={(prev) => ({ ...prev, page: prev.page + 1 })}>
  Next Page
</Link>

// Preload on hover, active styling
<Link
  to="/posts/$postId"
  params={{ postId: '456' }}
  preload="intent"
  activeProps={{ className: 'font-bold' }}
  inactiveProps={{ className: 'text-gray-600' }}
>
  Featured Post
</Link>
```

## Programmatic Navigation

```tsx
import { useNavigate } from '@tanstack/react-router'

function SearchForm() {
  const navigate = useNavigate()

  const handleSearch = (query: string) => {
    navigate({
      to: '/search',
      search: (prev) => ({ ...prev, query, page: 1 }),
    })
  }

  // Navigate to dynamic route
  const goToPost = (postId: string) => {
    navigate({ to: '/posts/$postId', params: { postId } })
  }
}
```

## Router Context with QueryClient

```tsx
// src/router.tsx
import { createRouter } from '@tanstack/react-router'
import { routeTree } from './routeTree.gen'
import type { QueryClient } from '@tanstack/react-query'

export const router = createRouter({
  routeTree,
  context: { queryClient: undefined! },
  defaultPreload: 'intent',         // preload on hover
  scrollRestoration: true,
})

// src/routes/__root.tsx
import { createRootRouteWithContext } from '@tanstack/react-router'

interface RouterContext {
  queryClient: QueryClient
}

export const Route = createRootRouteWithContext<RouterContext>()({ ... })
```

## Redirect

```tsx
import { createFileRoute, redirect } from '@tanstack/react-router'

export const Route = createFileRoute('/admin')({
  beforeLoad: async () => {
    const user = await getUser()
    if (!user?.isAdmin) {
      throw redirect({ to: '/', search: { message: 'Unauthorized' } })
    }
  },
})
```

## Testing Routes with Vitest

```tsx
import { useNavigate } from '@tanstack/react-router'

it('navigates to post', () => {
  function TestComponent() {
    const navigate = useNavigate()
    return (
      <button onClick={() => navigate({ to: '/posts/$postId', params: { postId: '123' } })}>
        Go
      </button>
    )
  }

  const { router } = renderWithFileRoutes(<TestComponent />, { initialLocation: '/' })
  fireEvent.click(screen.getByText('Go'))
  expect(router.state.location.pathname).toBe('/posts/123')
})
```
