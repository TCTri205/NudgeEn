# EPIC-01: Security, Auth & Guardrails

- **Status:** Pending (Planned for Sprint 1)
- **Priority:** P0 - Critical Path
- **Source requirement:** PRD-v1.md (REQ-007, REQ-008, REQ-010)
- **Impacted domains:** Authentication, Security, Platform

---

## Summary

Implement comprehensive authentication, authorization, and safety control infrastructure. This epic establishes the identity boundary for the application, ensuring secure user access while protecting against malicious inputs and unsafe AI behavior. It creates the trust foundation that allows users to interact with their AI friend safely. This epic builds directly on the infrastructure foundation from EPIC-00 and enables the user-facing features in EPIC-02 and beyond.

---

## Current State / Gap

- **Implemented:** Infrastructure foundation from EPIC-00 (FastAPI skeleton, Next.js skeleton, PostgreSQL/Redis connections, project structure).
- **Missing:** Auth.js integration, OAuth providers (Google, GitHub), credentials provider, session management, safety gatekeeper, rate limiting, PII scrubbing, abuse tracking.

---

## Problem / Opportunity

Without authentication and safety controls, the platform cannot:
- Distinguish between users or personalize their experience
- Protect against abuse, spam, or malicious usage
- Ensure user data privacy and conversation security
- Prevent unsafe AI outputs or prompt injection attacks

Building these controls after user-facing features would require costly refactoring and expose security vulnerabilities.

---

## Desired Outcome

After this epic is complete:
- Users can securely sign in via OAuth (Google, GitHub) or email/password
- Sessions persist across server restarts and devices
- Every chat message passes through a safety gatekeeper before AI processing
- Rate limiting prevents abuse (50 messages/24hrs per user)
- PII is scrubbed before memory storage
- Users can reset passwords and verify emails
- Abuse events are logged for monitoring

This outcome matters because security and safety are foundational to user trust and cannot be retrofitted easily.

---

## Users / Use Cases

- **Primary users:** End users (authentication), Development team (security infrastructure)
- **Main use cases:**
  - User signs in with Google/GitHub account
  - User registers with email/password
  - User resets forgotten password
  - User verifies email address
  - System validates every message for safety risks
  - System rate limits excessive usage
- **Important edge cases:**
  - OAuth account linking (same email, different providers)
  - Session expiration and refresh
  - Rate limit bypass attempts
  - Prompt injection attacks

---

## Scope

### In scope

- ✅ Auth.js integration with Next.js (web boundary)
- ✅ Google and GitHub OAuth providers
- ✅ Credentials provider (email/password)
- ✅ PostgreSQL adapter for Auth.js persistence
- ✅ JWT/session token management
- ✅ User role and permission system
- ✅ Safety gatekeeper agent (pre-chat validation)
- ✅ NSFW and sensitive topic filtering
- ✅ Prompt injection detection and prevention
- ✅ Rate limiting (50 messages/24hrs per user, MVP)
- ✅ Redis-based sliding window rate limiter
- ✅ Abuse event tracking and logging
- ✅ IP-based and account-based rate limiting
- ✅ Content safety classification
- ✅ PII scrubbing pipeline for memory extraction
- ✅ User data export and deletion (GDPR compliance)
- ✅ Session management and refresh
- ✅ Password reset flow
- ✅ Email verification (for credentials provider)

### Out of scope

- ❌ Multi-factor authentication (MFA) (future enhancement)
- ❌ Social login beyond Google and GitHub (future enhancement)
- ❌ Enterprise SSO (SAML, OIDC) (future enhancement)
- ❌ Advanced CAPTCHA or bot detection (initial MVP)
- ❌ Real-time abuse response (automated account suspension)

---

## Capability Slices

- **Slice 1: OAuth Integration** — Google and GitHub providers, callback handling, account linking
- **Slice 2: Credentials Provider** — Email/password registration, login, password hashing
- **Slice 3: Session Management** — PostgreSQL adapter, JWT tokens, session persistence
- **Slice 4: Safety Gatekeeper** — Pre-chat validation, NSFW filtering, prompt injection detection
- **Slice 5: Rate Limiting & Abuse Prevention** — Redis rate limiter, abuse logging, IP-based limits
- **Slice 6: Account Recovery** — Password reset, email verification, PII scrubbing

---

## Facts / Assumptions / Constraints / Unknowns

- **Facts:**
  - Auth.js v5 (next-auth) is the chosen authentication framework
  - PostgreSQL is the session store (via @auth/pg-adapter)
  - Redis is used for rate limiting
  - bcrypt/scrypt for password hashing
- **Assumptions:**
  - OAuth applications will be created in Google and GitHub developer consoles
  - SMTP or email API (Resend, SendGrid) credentials are available
  - Production will enforce HTTPS for all auth flows
- **Constraints:**
  - Passwords must NEVER be stored in plain text
  - Minimum password length: 8 characters
  - Rate limit: 50 messages/24hrs per user (MVP)
  - Tokens must expire (1 hour for reset, 24 hours for verification)
  - Tokens must be single-use
- **Unknowns:**
  - Exact OAuth client secrets (to be configured per environment)
  - Email provider choice (Resend vs SendGrid vs SMTP)

---

## Proposed Solution

**Authentication Architecture:**
- Use Auth.js v5 with Next.js App Router
- PostgreSQL adapter for session persistence (next-auth/prisma or custom)
- OAuth providers: Google, GitHub
- Credentials provider with bcrypt password hashing

**Safety Gatekeeper Chain:**
```
User Message → Rate Limit Check → Injection Detection → NSFW Filter → Sensitive Topic Check → Persona Agent
```

**Rate Limiting:**
- Redis-based sliding window using sorted sets
- Key pattern: `rate_limit:{user_id}`
- Window: 86400 seconds (24 hours), Limit: 50 requests

**PII Scrubbing:**
- Regex-based pattern matching for phone numbers, emails, SSN
- Configurable patterns via environment variables
- Audit logging of scrubbed content (metadata only)

**Key tradeoffs:**
- Chose PostgreSQL adapter over JWT-only for better session management and revocation capability
- Chose sequential gatekeeper (simpler debugging) over parallel checks
- Chose Redis sorted sets for rate limiting (atomic operations) over counter-based approach

---

## Dependencies / Rollout / Risks

### Dependencies

- **External:**
  - Auth.js (next-auth) — Authentication framework
  - Google OAuth — OAuth provider
  - GitHub OAuth — OAuth provider
  - bcrypt — Password hashing
  - @auth/pg-adapter — PostgreSQL adapter for Auth.js
  - Redis — Rate limiting store

- **Internal:**
  - **EPIC-00: Infrastructure & Project Setup** — Must be completed first
    - FastAPI project skeleton
    - Next.js project skeleton
    - PostgreSQL connection
    - Redis connection

### Rollout notes

- OAuth credentials must be configured per environment (dev, staging, prod)
- Email templates need to be tested with real email accounts
- Rate limiting should start in logging mode before enforcement

### Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| OAuth configuration errors | High | Medium | Use official libraries, test thoroughly in dev |
| Session security vulnerabilities | Critical | Low | HttpOnly cookies, secure flags, short expiry |
| Rate limit bypass | Medium | Low | Multiple layers (IP + account), Redis atomic ops |
| False positives in content filtering | Medium | Medium | Adjustable thresholds, human review option |
| PII scrubbing misses data | High | Medium | Multiple pattern types, audit sampling |
| Password reset token leakage | High | Low | Short expiry, single-use tokens |

---

## Epic Done Criteria

- [ ] Google OAuth provider configured and working
- [ ] GitHub OAuth provider configured and working
- [ ] Credentials provider (email/password) working
- [ ] PostgreSQL adapter storing sessions correctly
- [ ] Session persistence across server restarts
- [ ] Rate limiting active (50 msgs/24hr default)
- [ ] Safety gatekeeper runs before every chat message
- [ ] NSFW/content filtering blocks unsafe content
- [ ] Prompt injection detection in place
- [ ] PII scrubbing function implemented and tested
- [ ] "Wipe My Memory" endpoint working
- [ ] Password reset flow functional
- [ ] Email verification for new accounts
- [ ] Abuse events logged to database
- [ ] Clear error messages for auth failures

---

## Task Writer Handoff

- **Epic slug:** EPIC-01
- **Epic file path:** `docs/project-management/epics/EPIC-01.md`
- **Original requirement:** PRD-v1.md (REQ-007, REQ-008, REQ-010)
- **Epic summary:** Authentication, authorization, and safety control infrastructure
- **Impacted domains:** Authentication, Security, Platform
- **Desired outcome:** Users can securely authenticate; all messages pass safety checks
- **In-scope outcomes:** OAuth, credentials, sessions, gatekeeper, rate limiting, PII scrubbing
- **Non-goals:** MFA, enterprise SSO, advanced bot detection
- **Capability slices:** 6 slices (OAuth, credentials, sessions, gatekeeper, rate limiting, recovery)
- **Facts:** Auth.js v5, PostgreSQL adapter, Redis rate limiting, bcrypt hashing
- **Assumptions:** OAuth apps created, email API available, HTTPS in production
- **Constraints:** Passwords never plain text, 8+ chars, 50 msgs/24hr, tokens expire
- **Unknowns:** OAuth secrets per environment, email provider choice
- **Proposed solution summary:** Auth.js + PostgreSQL + Redis gatekeeper chain with rate limiting
- **Dependencies:** EPIC-00 (infrastructure skeletons, database, Redis)
- **Rollout notes:** Configure OAuth per environment, test email templates
- **Risks:** OAuth errors, session vulnerabilities, rate limit bypass, PII leakage
- **Task splitting hints:** Split by capability slice (OAuth → credentials → sessions → gatekeeper → rate limiting → recovery)
- **Validation expectations:** All auth flows must be testable end-to-end with clear pass/fail

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-26 | System | Initial version based on project documentation |
| 2.0 | 2026-04-27 | Assistant | Standardized to epic-template.md format |
