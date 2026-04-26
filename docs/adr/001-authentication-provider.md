# ADR-001: Selection of Authentication Provider

## Status

Accepted

## Context

NudgeEn requires a secure authentication system to manage user profiles and chat history. The team wants strong control over user data and wants to avoid per-user pricing from an external IAM SaaS when possible.

## Decision

Use **Auth.js** for authentication, supporting:

- OAuth2 with Google and GitHub
- Credentials provider for Email/Password

## Rationale

- **Cost:** Runs as part of the web application without separate per-user IAM pricing.
- **Control:** User identity data stays in our own **PostgreSQL** database.
- **Integration:** Strong fit with Next.js.
- **Flexibility:** Supports both OAuth and credentials-based login.

## Consequences

Positive:

- lower long-term IAM cost
- stronger data ownership
- clean integration with the web application

Negative:

- more implementation responsibility than a fully managed auth SaaS
- password hashing, session hardening, and recovery flows must be implemented carefully
- email recovery and verification require additional infrastructure
