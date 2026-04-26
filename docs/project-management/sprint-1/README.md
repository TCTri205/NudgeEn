# Sprint 1: Scalable Gateway (Auth + UI + Basic API)

## Overview

Status: **Pending**

Focus:

- establish authentication
- establish the initial chat path
- lay down PostgreSQL, Redis, queue, and worker foundations

## Tasks

- [ ] **Infrastructure**
  - [ ] **[TICKET-07](TICKET-07.md)** Configure Google/GitHub OAuth providers.
  - [ ] **[TICKET-08](TICKET-08.md)** Implement Credentials provider.
  - [ ] **[TICKET-09](TICKET-09.md)** Configure PostgreSQL adapter for Auth.js.
  - [ ] **[TICKET-10](TICKET-10.md)** Implementation Multi-provider Account Linking.
  - [ ] **[TICKET-11](TICKET-11.md)** Password Reset & Email Verification.
  - [ ] **[TICKET-19](TICKET-19.md)** Redis Sliding Window Rate Limiter.
  - [ ] **[TICKET-20](TICKET-20.md)** Safety Gatekeeper Agent (Basic).
  - [ ] **[TICKET-21](TICKET-21.md)** PII Scrubbing Pipeline.
  - [ ] **[TICKET-22](TICKET-22.md)** "Wipe My Memory" Endpoint.
- [ ] **Frontend**
  - [ ] **[TICKET-12](TICKET-12.md)** Build basic chat window UI (bubbles).
  - [ ] **[TICKET-13](TICKET-13.md)** Build Conversation List & Sidebar.
  - [ ] **[TICKET-15](TICKET-15.md)** SSE Client-side consumption hook.
  - [ ] **[TICKET-17](TICKET-17.md)** Add typing indicator UX.
- [ ] **Backend**
  - [ ] **[TICKET-14](TICKET-14.md)** Implement SSE Streaming (Back-end).
  - [ ] **[TICKET-16](TICKET-16.md)** Persist conversations and messages in PostgreSQL.
  - [ ] **[TICKET-18](TICKET-18.md)** Message Idempotency & Deduplication.
