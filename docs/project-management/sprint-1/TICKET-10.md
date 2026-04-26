# TICKET-10: Multi-provider Account Linking

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 1
- **Assignee:** Lead Developer
- **Domain:** Authentication
- **Priority:** P1 - High
- **Assumptions:**
  - Database adapter (TICKET-09) is functional.
  - User email addresses are unique and verified.
- **Affected areas:** `web/auth.ts`, Auth.js Callbacks, Settings UI.

## Current State / Existing System

- **Implemented:** Basic Sign-in for Google, GitHub, and Credentials independently.
- **Missing:** Logic to link multiple providers to the same user profile based on a shared email.

## Context / Problem

Users may sign in with Google today and GitHub tomorrow. If they use the same email, they should see the same data (conversations, persona). Without account linking, they would have two fragmented accounts.

## Why This Is Needed

- **Business Impact:** Provides a unified user experience and prevents data fragmentation.
- **Architectural Impact:** Hardens the identity layer by ensuring a 1:N relationship between User and Accounts.

## Scope

### In-scope

- Configure `allowDangerousEmailAccountLinking: true` for trusted providers.
- Implement specialized logic in the `signIn` callback to check for existing email matches.
- Handle edge cases where a user tries to link an account already linked to another user.
- Add a basic "Link Account" section in the user settings UI.

### Out-of-scope

- Unlinking accounts (future enhancement).
- Merging two existing users with different emails.

## Dependencies / Parallelism

- **Dependencies:** TICKET-07 (OAuth), TICKET-09 (PostgreSQL Adapter).
- **Parallelism:** Can be done after TICKET-07 and TICKET-09 are stable.

## Rules / Constraints

- Account linking must only occur if the email matches exactly.
- Credentials-based accounts can be linked to OAuth, but OAuth-to-OAuth linking requires manual verification or trusted provider status.

## What Needs To Be Built

1. Configuration update in `auth.ts`.
2. Logic in `events` or `callbacks` to handle account linking.
3. Simple UI in `web/app/settings/page.tsx` to display currently linked providers.

## Proposal

Configure Auth.js to allow email-based linking. When a new provider sign-in occurs with an existing email, the adapter will automatically link the new `Account` to the existing `User` record.

## Implementation Breakdown

1. **Config:** Set `allowDangerousEmailAccountLinking` to true for Google and GitHub.
2. **Callbacks:** Implement `signIn` callback to log linking events.
3. **UI:** Create a "Security" or "Settings" page showing "Connected Accounts".
4. **Validation:** Test signing in with Google, then logging out and signing in with GitHub using the same email.

## Acceptance Criteria

- [ ] User can sign in with Google, then later sign in with GitHub (same email) and access the same profile.
- [ ] Database shows one row in `users` but two rows in `accounts` for the same `userId`.
- [ ] User is notified when a new account is successfully linked.

## Test Cases

### Happy Path

- OAuth Google -> OAuth GitHub (same email) -> Both work for the same user.

### Failure Path

- OAuth Google -> OAuth GitHub (different email) -> Two separate users created (correct behavior).

### Regression Tests

- Ensure linking doesn't overwrite existing user traits (like persona settings).
