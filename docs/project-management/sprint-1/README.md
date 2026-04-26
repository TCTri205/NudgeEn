# Sprint 1: Scalable Gateway (Auth + UI + Basic API)

## Overview

Status: **Pending**

Focus:

- establish authentication
- establish the initial chat path
- lay down PostgreSQL, Redis, queue, and worker foundations

## Tasks

- [ ] **Infrastructure**
  - [ ] Initialize Auth.js
  - [ ] Configure Google and GitHub OAuth providers
  - [ ] Implement Credentials provider
  - [ ] Configure PostgreSQL adapter for Auth.js
  - [ ] Provision Redis for queue and rate limiting
  - [ ] Bootstrap Taskiq worker process
- [ ] **Frontend**
  - [ ] Create login/register pages
  - [ ] Build basic chat window UI
  - [ ] Build message bubble components
  - [ ] Add typing indicator UX
- [ ] **Backend**
  - [ ] Connect to Gemini 2.5 Flash
  - [ ] Integrate Groq fallback
  - [ ] Implement basic message exchange flow
  - [ ] Persist conversations and messages in PostgreSQL
  - [ ] Enqueue post-response background jobs
