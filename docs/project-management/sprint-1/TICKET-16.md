# TICKET-16: Message Persistence Logic (PostgreSQL)

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 1
- **Assignee:** Backend Lead
- **Domain:** Data Layer
- **Priority:** P0 - Critical
- **Assumptions:**
  - Database migrations for conversations/messages are ready (TICKET-04).
  - Database session dependency is functional (TICKET-03).
- **Affected areas:** `api/app/modules/chat/repository.py`, PostgreSQL Schema.

## Current State / Existing System

- **Implemented:** Database connection and Alembic setup (TICKET-03, TICKET-04).
- **Missing:** Any logic to actually save or load chat messages from the persistence layer.

## Context / Problem

A stateless chat is forgetful. To build a long-term AI friend, we must store every message sent by the user and every response from the AI in a permanent, searchable, and paginated store.

## Why This Is Needed

- **Business Impact:** Enables users to pick up conversations where they left off, creating a sense of continuity.
- **Architectural Impact:** Implements the core of the Chat module's data access layer.

## Scope

### In-scope

- Implement `MessageRepository` with methods for `create`, `get_by_conversation`, and `get_recent`.
- Implement `ConversationRepository` for thread management.
- Handle automatic timestamping (`created_at`).
- Implement pagination using `cursor-based` or `offset-based` limits.
- Ensure messages are linked to the correct `user_id`.

### Out-of-scope

- Full-text search (future enhancement).

## Dependencies / Parallelism

- **Dependencies:** TICKET-03 (PostgreSQL), TICKET-04 (Alembic).
- **Parallelism:** Can be done while Frontend UI (TICKET-12) is being built.

## Rules / Constraints

- Messages should be treated as **immutable** (once written, they are never updated).
- Database queries must be async to prevent blocking the main event loop.
- Use composite indexes on `(conversation_id, created_at)` for fast retrieval.

## What Needs To Be Built

1. `api/app/modules/chat/models.py`: SQLAlchemy models for `Conversation` and `Message`.
2. `api/app/modules/chat/repository.py`: CRUD operations.
3. Service logic to trigger "Save" during or after the streaming process.

## Proposal

Save the user's message immediately upon receipt. For the AI's response, buffer the chunks in memory (or a temporary store) and save the full message to the database once the stream completes successfully.

## Implementation Breakdown

1. **Model Definition:** Finalize the fields in the `Message` and `Conversation` models.
2. **Repository Logic:** Write the async functions for DB operations.
3. **Integration:** Hook the repository into the chat service.
4. **Validation:** Verify that messages persist after a page refresh in the frontend.

## Acceptance Criteria

- [ ] New messages are successfully written to the `messages` table.
- [ ] GET `/conversations/{id}/messages` returns a chronological list of messages.
- [ ] Conversations are correctly associated with the authenticated user.
- [ ] Database supports 100k+ messages without significant latency degradation.

## Test Cases

### Happy Path

- Send message -> Refresh -> Message is still there.
- Load history -> Returns 50 messages -> Load more -> Returns next 50.

### Failure Path

- Database error -> Message fails to save but user is notified (or retry strategy).

### Regression Tests

- Ensure User A cannot read messages from User B's conversation.
