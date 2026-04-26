# TICKET-08: Credentials Provider Implementation

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 1
- **Assignee:** Lead Developer
- **Domain:** Authentication
- **Priority:** P0 - Critical
- **Assumptions:**
  - Database adapter (TICKET-09) is set up or can be mocked for testing.
  - Password hashing standards are agreed upon (bcrypt).
- **Affected areas:** `web/auth.ts`, `api/`, `users` table, Registration Form.

## Current State / Existing System

- **Implemented:** Documentation for password-based login in TECHSTACK.md.
- **Missing:** Implementation of the credentials provider, hashing logic, and registration/login forms.

## Context / Problem

Not all users wish to use OAuth. Providing a traditional email/password option is essential for accessibility and user choice, but it requires careful implementation to avoid security pitfalls.

## Why This Is Needed

- **Business Impact:** Accommodates users who prefer direct accounts or use non-supported OAuth providers.
- **Architectural Impact:** Requires specialized security logic (hashing, validation) in both frontend and backend layers.

## Scope

### In-scope

- Implement `Credentials` provider in `auth.ts`.
- Define `authorize` callback to validate user against the PostgreSQL database.
- Use `bcryptjs` for secure password hashing and comparison.
- Create Registration and Login forms using React Server Actions.
- Client-side and server-side validation for email and password strength.

### Out-of-scope

- Password reset (TICKET-11).
- Email verification (TICKET-11).

## Dependencies / Parallelism

- **Dependencies:** TICKET-02 (Next.js Skeleton), TICKET-03 (PostgreSQL Setup).
- **Parallelism:** Can be done in parallel with TICKET-07 (OAuth Setup).

## Rules / Constraints

- **Passwords must NEVER be stored in plain text.**
- Minimum password length: 8 characters.
- Use Auth.js standard error handling for invalid credentials.
- All credential-based requests must be over HTTPS (assumed for production).

## What Needs To Be Built

1. Define a `credentials` object in the Auth.js config.
2. Implement robust validation logic in the `authorize` function.
3. Create `/register` and `/login` routes in the Next.js app.
4. Implement a `User` model update to store hashed passwords.

## Proposal

Implement a "Credentials" sign-in flow that queries the `users` table by email. If the user exists and the password matches (checked via `bcrypt.compare`), return a user object to initiate the session.

## Implementation Breakdown

1. **Hashing Utility:** Create a secure utility for hashing and comparing passwords.
2. **Auth Config:** Setup the `CredentialsProvider` with `email` and `password` fields.
3. **Registration Flow:** Implement a form that hashes the password before saving the new user to the DB.
4. **Login Flow:** Implement a form that calls `signIn("credentials", ...)` and handles success/error.

## Acceptance Criteria

- [ ] User can successfully register with a valid email and password.
- [ ] User can successfully log in with registered credentials.
- [ ] Attempting to log in with an incorrect password returns a "Invalid credentials" error.
- [ ] Hashed passwords in the database start with `$2b$` (bcrypt).
- [ ] Frontend displays validation errors for weak passwords or malformed emails.

## Test Cases

### Happy Path

- Register -> Login -> Session created.
- Login with correct email/password -> Success.

### Failure Path

- Login with non-existent email -> "Invalid credentials".
- Register with existing email -> "User already exists".

### Regression Tests

- Check that logging in with credentials doesn't affect existing OAuth sessions.
