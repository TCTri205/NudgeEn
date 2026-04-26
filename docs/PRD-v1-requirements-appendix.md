# PRD-v1 Requirements Appendix

This document lists specific requirements derived from `docs/PRD-v1.md`.

| ID | Category | Requirement Description | Priority |
| --- | --- | --- | --- |
| **REQ-001** | Core UI | Messenger-like interface with chat bubbles, emojis, and reactions. | P0 |
| **REQ-001.1** | Core UI | Real-time typing indicators to simulate human activity. | P1 |
| **REQ-002** | AI Intelligence | Contextual memory of user name, interests, and history. | P0 |
| **REQ-002.1** | AI Intelligence | Proactive engagement based on past conversation context. | P1 |
| **REQ-003** | Pedagogy | Subtle, non-intrusive grammar/vocabulary corrections. | P0 |
| **REQ-004** | Persona | Configurable vibe: Sarcastic, Empathetic, Tech-savvy. | P1 |
| **REQ-005** | Infrastructure | Text-based only MVP to optimize operational costs. | P0 |
| **REQ-005.1** | Infrastructure | PostgreSQL is the primary system of record from the first production release. | P0 |
| **REQ-005.2** | Infrastructure | Redis is required for queue transport, caching, and rate limiting. | P0 |
| **REQ-005.3** | Infrastructure | Background jobs must run in dedicated workers and be retry-safe. | P0 |
| **REQ-006** | Security | Prevention of prompt injection and rogue AI behavior. | P0 |
| **REQ-006.1** | Security | NSFW and sensitive topic filtering. | P0 |
| **REQ-007** | Quality | Automated test suite for memory, persona, and guardrails. | P1 |
