# TICKET-54: Security Audit & Vulnerability Scanning

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 5
- **Assignee:** Security Engineer
- **Domain:** Security / Compliance
- **Priority:** P1 - High
- **Assumptions:**
  - No high-risk PII leak currently known.
- **Affected areas:** Auth, Data Access, PII Scrubbing logic.

## Current State / Existing System

- **Implemented:** Security headers and basic PII scrubbing (TICKET-52, TICKET-21).
- **Missing:** A formal "Red Team" style audit to ensure no edge cases (e.g., IDOR, SQL Injection, or Token hijacking) are possible.

## Context / Problem

Before opening to beta users, we need to be 100% sure that User A cannot see User B's memories or messages. A security breach at launch would be fatal to the project's reputation.

## Why This Is Needed

- **Business Impact:** Protects user privacy and prevents legal/reputational damage.
- **Architectural Impact:** Validates the "Tenant Isolation" and "API Hardening" layers.

## Scope

### In-scope

- Automated Scan: Use `OWASP ZAP` or `Snyk` to find common vulnerabilities.
- Manual Audit:
  - **IDOR (Insecure Direct Object Reference):** Verify `/messages/{id}` cannot be accessed by other users.
  - **XSS/CSRF:** Check all user inputs and the Chat UI.
  - **Token Security:** Verify JWT expiration and invalidation logic.
  - **PII Leakage:** Review logs (structlog) and Sentry to ensure no messages are leaked.
- Remediate all "High" and "Critical" findings.

### Out-of-scope

- Social engineering testing.

## Dependencies / Parallelism

- **Dependencies:** TICKET-46 (Sentry), TICKET-52 (Headers).
- **Parallelism:** Can be done alongside load testing.

## Rules / Constraints

- No "Critical" vulnerabilities can go into production.
- Audit must cover both the Web frontend and the API.

## What Needs To Be Built

1. Security Audit Report (Internal).
2. Fixes for any discovered loopholes in the `AuthMiddleware`.

## Proposal

Perform a day of focused "Breaking" testing. Use a tool like `Burp Suite` to intercept requests and attempt to change `user_id` parameters to access unauthorized data.

## Implementation Breakdown

1. **Automated Run:** Trigger Snyk scan.
2. **Auth Review:** Audit the `get_current_user` dependency in FastAPI for any loopholes.
3. **Scrubbing Check:** Verify PII gatekeeper logic in `memory_extraction`.
4. **Validation:** Re-scan until the tools return "0 Critical Findings."

## Acceptance Criteria

- [ ] ZAP/Snyk report shows 0 Critical and 0 High vulnerabilities.
- [ ] Manual test confirms that `/api/conversations/{id}` returns 404/403 for unauthorized users.
- [ ] JWT tokens are verified to be short-lived and securely signed.

## Test Cases

### Happy Path

- Standard user uses app as intended -> Logs show only authorized requests.

### Failure Path

- Attacker tries to GET a message ID they don't own -> System returns 403.

### Regression Tests

- Verify that adding a new API endpoint requires the `current_active_user` dependency.
