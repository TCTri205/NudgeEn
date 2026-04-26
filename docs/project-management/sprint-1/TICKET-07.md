# TICKET-07: Auth.js OAuth Configuration (Google/GitHub)

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 1
- **Assignee:** Lead Developer
- **Domain:** Authentication
- **Priority:** P0 - Critical
- **Assumptions:**
  - Google and GitHub OAuth applications are created in their respective developer consoles.
  - `web/` skeleton (TICKET-02) is functional.
- **Affected areas:** `web/auth.ts`, Frontend Login UI, `.env.local`.

## Current State / Existing System

- **Implemented:** Next.js skeleton and Auth.js shell (Sprint 0).
- **Missing:** Real OAuth provider configuration and secrets.

## Context / Problem

Users need a frictionless way to sign up and log in. OAuth via trusted providers like Google and GitHub is the primary mechanism for user onboarding and identity verification in NudgeEn.

## Why This Is Needed

- **Business Impact:** High conversion rate for new users.
- **Architectural Impact:** Establishes the delegated identity pattern, reducing the burden of managing user credentials directly.

## Scope

### In-scope

- Configure `Google` and `GitHub` providers in `auth.ts`.
- Securely map `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GITHUB_ID`, and `GITHUB_SECRET`.
- Implement `signIn` and `signOut` helper functions.
- Create a reusable `SignInButton` component.
- Handle standard OAuth callback routes.

### Out-of-scope

- Multi-provider linking (TICKET-10).
- Custom user profile enrichment (beyond standard OAuth fields).

## Dependencies / Parallelism

- **Dependencies:** TICKET-02 (Next.js Skeleton).
- **Parallelism:** Can be done in parallel with TICKET-08 (Credentials Provider).

## Rules / Constraints

- Secrets must NEVER be committed to version control.
- Must use Auth.js v5 (beta) latest patterns.
- User data must be synchronized with the database only after successful OAuth verification.

## What Needs To Be Built

1. Update `web/auth.ts` to include Google and GitHub providers.
2. Add environment variables to `.env.local`.
3. Create `web/components/auth/login-button.tsx`.
4. Implement a basic login page at `web/app/login/page.tsx`.

## Proposal

Use the official Auth.js provider packages. Map the provider's `id` and `email` to the internal `User` model. Utilize Auth.js's built-in `session` callback to expose the user ID to the client.

## Implementation Breakdown

1. **Provider Setup:** Add Google and GitHub to the `providers` array in `auth.ts`.
2. **Env Config:** Populate `.env.local` with real/test credentials.
3. **UI Implementation:** Create a simple login view with "Sign in with Google" and "Sign in with GitHub" buttons.
4. **Validation:** Test the full redirect flow and verify session creation.

## Acceptance Criteria

- [ ] User can successfully sign in using a Google account.
- [ ] User can successfully sign in using a GitHub account.
- [ ] User is redirected back to the app after successful authentication.
- [ ] Session cookie is correctly set in the browser.
- [ ] `auth()` function returns the correct user object on the server side.

## Test Cases

### Happy Path

- Click Google Login -> Authenticate on Google -> Redirected to NudgeEn -> Session active.
- Same flow for GitHub.

### Failure Path

- User cancels OAuth prompt -> Redirected back to login with error message.
- Invalid Client Secret -> 500 error handled gracefully on the login page.

### Regression Tests

- Ensure session survives a page refresh.
