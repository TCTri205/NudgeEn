# ADR-001: Selection of Authentication Provider

## Status

Accepted

## Context

NudgeEn requires a secure authentication system to manage user profiles and chat history. The initial recommendation was Clerk (a managed IAM service). However, the project goal is to optimize for cost ("the cheaper the better") and avoid per-user scaling fees where possible.

## Decision

We will use **NextAuth.js (Auth.js)** for authentication, supporting both **OAuth2 (Google/GitHub)** and **Email/Password (Credentials provider)**.

## Rationale

- **Cost**: $0. It runs as part of the Next.js application without separate licensing or per-user "active user" fees.
- **Vendor Lock-in**: NextAuth.js is open-source and allows us to own the user data directly in our own database (SQLite/PostgreSQL).
- **Integration**: Native integration with Next.js, which is the frontend framework for NudgeEn.
- **Cheaper at Scale**: Avoids the "SaaS tax" associated with managed providers like Clerk or Auth0 as the user base grows.
- **Flexibility**: Including Email/Password allows users without OAuth accounts to register, broadening the potential user base.

## Consequences

- **Development Overhead**: Requires more manual setup of UI (Login/Register pages) compared to Clerk's pre-built components.
- **Security Responsibility**: We are responsible for managing session security and database encryption for user credentials. **Password hashing (Argon2/bcrypt)** must be implemented correctly.
- **Maintenance**: Requires keeping NextAuth package and its adapters up to date. We also need to manage account recovery (Forgot Password) which requires an email SMTP setup.
