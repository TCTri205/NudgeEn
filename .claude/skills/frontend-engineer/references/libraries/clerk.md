---
library: clerk
package: "@clerk/clerk-react"
context7_library_id: /clerk/clerk-docs
synced_version: v5.61.3
project_version: v5.61.3
declared_range: ^5.61.3
benchmark_score: 89.5
source_reputation: High
last_synced: 2026-03-21
coverage: ClerkProvider, useAuth, useUser, useClerk, SignIn, SignUp, UserButton, route protection, getToken, server auth
---

# Clerk

Authentication and user management. This project uses `@clerk/clerk-react` with TanStack Start.

## Setup

```tsx
// src/integrations/clerk/provider.tsx
import { ClerkProvider as BaseClerkProvider } from '@clerk/clerk-react'

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

export default function ClerkProvider({ children }: { children: React.ReactNode }) {
  return (
    <BaseClerkProvider publishableKey={PUBLISHABLE_KEY}>
      {children}
    </BaseClerkProvider>
  )
}
```

## `useAuth` — Authentication State + Token

```tsx
import { useAuth } from '@clerk/clerk-react'

export default function Page() {
  const { isLoaded, isSignedIn, userId, sessionId, getToken } = useAuth()

  // Always handle loading state first
  if (!isLoaded) return <div>Loading...</div>
  if (!isSignedIn) return <div>Please sign in</div>

  // Get token for API requests
  const fetchData = async () => {
    const token = await getToken()
    const res = await fetch('/api/data', {
      headers: { Authorization: `Bearer ${token}` },
    })
    return res.json()
  }

  return <div>User ID: {userId}</div>
}
```

## `useUser` — User Profile Data

```tsx
import { useUser } from '@clerk/clerk-react'

export default function Profile() {
  const { isLoaded, isSignedIn, user } = useUser()

  if (!isLoaded) return <div>Loading...</div>
  if (!isSignedIn) return <div>Sign in</div>

  return (
    <div>
      <img src={user.imageUrl} alt={user.fullName ?? ''} />
      <p>{user.firstName} {user.lastName}</p>
      <p>{user.primaryEmailAddress?.emailAddress}</p>
    </div>
  )
}
```

## `useClerk` — Client Actions

```tsx
import { useClerk } from '@clerk/clerk-react'

function Nav() {
  const { signOut, openSignIn, openUserProfile } = useClerk()

  return (
    <nav>
      <button onClick={() => signOut()}>Sign Out</button>
      <button onClick={() => openSignIn()}>Sign In</button>
      <button onClick={() => openUserProfile()}>Profile</button>
    </nav>
  )
}
```

## Prebuilt UI Components

```tsx
import { SignIn, SignUp, UserButton, SignInButton, SignUpButton } from '@clerk/clerk-react'

// Embeds full sign-in form
<SignIn />
<SignUp />

// Floating user menu button (shows avatar, sign-out, profile)
<UserButton />

// Simple buttons to trigger sign-in/sign-up modals
<SignInButton mode="modal">Sign In</SignInButton>
<SignUpButton mode="modal">Get Started</SignUpButton>
```

## Conditional Rendering Based on Auth

```tsx
import { SignedIn, SignedOut } from '@clerk/clerk-react'

function Header() {
  return (
    <header>
      <SignedOut>
        <SignInButton />
        <SignUpButton />
      </SignedOut>
      <SignedIn>
        <UserButton />
      </SignedIn>
    </header>
  )
}
```

## Route Protection with TanStack Router (beforeLoad)

```tsx
// src/routes/_authed.tsx
import { createFileRoute, redirect } from '@tanstack/react-router'
import { createServerFn } from '@tanstack/react-start'

// Server-side auth check (works with Clerk session cookies)
const getCurrentUser = createServerFn().handler(async () => {
  // Use getAuth from @clerk/tanstackstart-react if available
  // Or check session via Clerk backend API
  return session?.userId ? { id: session.userId } : null
})

export const Route = createFileRoute('/_authed')({
  beforeLoad: async ({ location }) => {
    const user = await getCurrentUser()
    if (!user) {
      throw redirect({ to: '/sign-in', search: { redirect: location.href } })
    }
    return { user }
  },
})
```

## Feature Authorization with `has()`

```tsx
import { useAuth } from '@clerk/clerk-react'

function PremiumContent() {
  const { isLoaded, has } = useAuth()

  if (!isLoaded) return null

  const hasPremium = has({ feature: 'premium_access' })
  if (!hasPremium) return <div>Upgrade to access this</div>

  return <div>Premium content here</div>
}
```

## Environment Variables

```
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...   # client-side (exposed)
CLERK_SECRET_KEY=sk_test_...             # server-side only (never expose)
```

## User Object Properties

```ts
user.id                              // Clerk user ID
user.firstName                       // string | null
user.lastName                        // string | null
user.fullName                        // string | null
user.username                        // string | null
user.imageUrl                        // string
user.primaryEmailAddress?.emailAddress  // string
user.primaryPhoneNumber?.phoneNumber    // string
user.createdAt                       // Date
user.publicMetadata                  // Record<string, unknown>
```
