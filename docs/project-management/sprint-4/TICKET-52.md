# TICKET-52: SSL/TLS & Security Headers Hardening

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 4
- **Assignee:** Security Engineer / DevOps
- **Domain:** Web Security
- **Priority:** P2 - Medium
- **Assumptions:**
  - SSL certs are managed by the platform (e.g., Vercel, Render).
- **Affected areas:** `web/next.config.js`, `api/app/main.py` CORS.

## Current State / Existing System

- **Implemented:** Default framework settings (TICKET-02).
- **Missing:** Hardened headers that prevent common web attacks like Clickjacking, XSS, or MIME-sniffing.

## Context / Problem

Even if our code is secure, our browser-level headers might leave users vulnerable to cross-site scripting or iframing. We need to explicitly instruct the browser on how to handle our content.

## Why This Is Needed

- **Business Impact:** Increases user trust and ensures compliance with basic security standards.
- **Architectural Impact:** Finalizes the "Hardened Interface" of the application.

## Scope

### In-scope

- Configure the following headers:
  - **HSTS (Strict-Transport-Security):** Force HTTPS for 1 year.
  - **Content-Security-Policy (CSP):** Restrict script sources to self + Gemini/Auth domains.
  - **X-Frame-Options:** DENY (prevent iframing).
  - **X-Content-Type-Options:** nosniff.
  - **Referrer-Policy:** strict-origin-when-cross-origin.
  - **Permissions-Policy:** Disable unused features (camera, microphone, geolocation).
- CORS setup: Only allow `app.nudgen.com` to call the API.

### Out-of-scope

- Penetration testing (third-party).

## Dependencies / Parallelism

- **Dependencies:** TICKET-44 (Production Deployment).
- **Parallelism:** Can be done as the final polish of Sprint 4.

## Rules / Constraints

- CSP must be tested in "Report-Only" mode first to avoid breaking the frontend.
- SSL must be TLS 1.2 or higher.

## What Needs To Be Built

1. Middleware in FastAPI to inject security headers.
2. `next.config.js` update to include a `headers()` block.

## Proposal

Use `fastapi.middleware.httpsredirect.HTTPSRedirectMiddleware` and a custom response header middleware. For Next.js, use the built-in `headers` array in `next.config.js`.

## Implementation Breakdown

1. **Header Config:** Define the strict policies.
2. **Deployment:** Apply headers and verify them using `curl -I`.
3. **External Audit:** Use **Mozilla Observatory** or **SecurityHeaders.com** to run a public scan.
4. **Validation:** Fix any "B" or "C" ratings until "A+" is achieved.

## Acceptance Criteria

- [ ] A+ rating on SecurityHeaders.com.
- [ ] No mixed content or "Insecure" warnings in Chrome DevTools.
- [ ] `X-Frame-Options` successfully prevents the app from being loaded in an `<iframe>`.
- [ ] HSTS is active and verified.

## Test Cases

### Happy Path

- Visit site -> Check headers in Network tab -> All standard security headers are present.

### Failure Path

- CSP too strict -> Image/Script from Gemini fails to load -> Fix policy to whitelist necessary domains.

### Regression Tests

- Ensure "Sign in with Google" still works after CSP hardening (OAuth redirects).
