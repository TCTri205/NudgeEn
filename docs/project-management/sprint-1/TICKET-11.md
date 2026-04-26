# TICKET-11: Password Reset & Email Verification

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 1
- **Assignee:** Lead Developer
- **Domain:** Authentication / Security
- **Priority:** P1 - High
- **Assumptions:**
  - SMTP or Email API (e.g., Resend, SendGrid) credentials are available.
  - Credentials provider (TICKET-08) is implemented.
- **Affected areas:** `web/auth.ts`, Email Service, User model, Database.

## Current State / Existing System

- **Implemented:** Basic credentials-based login (TICKET-08).
- **Missing:** Any way to recover a lost password or verify that a user owns the email they registered with.

## Context / Problem

For security and account integrity, we must verify user emails. Additionally, providing a secure, token-based self-service password reset flow is standard for modern web applications to reduce support overhead and ensure account recovery.

## Why This Is Needed

- **Business Impact:** Reduces user churn due to lost accounts and ensures higher quality user data.
- **Architectural Impact:** Integrates an external email service into the system and introduces time-limited tokens to the database.

## Scope

### In-scope

- Setup a production-ready email service (SMTP/API).
- Create email templates for "Verification" and "Reset Password".
- Implement `VerificationToken` handling in the database via Auth.js.
- Create `/auth/verify-email` and `/auth/reset-password` routes.
- Implement token generation, storage (with expiry), and validation logic.
- Add "Email Not Verified" guard for sensitive features.

### Out-of-scope

- SMS verification.
- Advanced account recovery (identity verification).

## Dependencies / Parallelism

- **Dependencies:** TICKET-08 (Credentials Provider), TICKET-09 (PostgreSQL Adapter).
- **Parallelism:** Can be done after TICKET-08 and TICKET-09 are stable.

## Rules / Constraints

- Tokens must expire (e.g., 1 hour for reset, 24 hours for verification).
- Tokens must be single-use.
- Password reset links must always use HTTPS in production.
- Use Auth.js built-in `VerificationRequest` mechanisms where possible.

## What Needs To Be Built

1. `web/lib/mail.ts`: A utility to send emails.
2. `web/app/auth/verify-email/page.tsx`: Landing page for verification links.
3. `web/app/auth/reset-password/page.tsx`: Form to enter new password with token.
4. Logic to update `emailVerified` field in the `users` table.

## Proposal

Use a lightweight email service like Resend. When a user registers, generate a hash, store it in the `verification_tokens` table, and send the link. For password reset, generate a separate token linked to the user's email.

## Implementation Breakdown

1. **Email Service:** Verify domain and setup credentials.
2. **Verification Flow:** Trigger on registration, handle link click, update DB.
3. **Reset Flow:** Trigger on "Forgot Password" form, send email, handle new password submission.
4. **Validation:** Manually test the full flows with test email accounts.

## Acceptance Criteria

- [ ] User receives a verification email upon registration.
- [ ] Clicking the link in the email marks the user as verified in the DB.
- [ ] User can initiate a password reset and receive an email.
- [ ] Submitting the reset form with a valid token correctly updates the password.
- [ ] Expired tokens return a clear "Link Expired" error.

## Test Cases

### Happy Path

- Register -> Verify -> Log in -> Access app.
- Forgot Password -> Receive link -> Change password -> Login with new password.

### Failure Path

- Click verification link twice -> "Token already used" or "Invalid token".
- Use expired reset token -> Error shown, no password change.

### Regression Tests

- Verify that password reset doesn't invalidate existing OAuth connections.
