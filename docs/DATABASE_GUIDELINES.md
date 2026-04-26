# NudgeEn Database Design & Management

## 1. Primary Engine: PostgreSQL

NudgeEn uses **PostgreSQL** as its primary system of record.

Why PostgreSQL:

- strong transactional guarantees
- safe concurrent writes across API and worker processes
- JSONB where flexible profile projections are useful
- mature indexing, backup, and scaling ecosystem

## 2. Redis Role

**Redis** is used for:

- queue transport for **Taskiq Workers**
- rate limiting
- ephemeral cache
- short-lived request idempotency or presence state

Redis is not the durable source of truth for user, conversation, or memory data.

## 3. Core Tables

- `users`
- `accounts`
- `sessions`
- `conversations`
- `messages`
- `message_corrections`
- `user_profiles`
- `user_memories`
- `weekly_progress_cards`
- `job_runs`
- `abuse_events`

## 4. Data Modeling Rules

- store each message as an immutable row
- keep user profile as a current projection
- keep extracted memory facts separately for traceability
- use JSONB selectively, not as the default for everything
- include `created_at`, `updated_at`, and versioning where mutable state exists

## 5. Scalability Principles

- always use connection pooling
- index hot access paths such as `user_id`, `conversation_id`, and `created_at`
- make worker writes idempotent
- prefer append-oriented event or audit tables for traceability

## 6. Repository Pattern - Python Example

```python
class PostgresChatMessageRepository(ChatMessageRepository):
    async def add_message(self, message: ChatMessage) -> None:
        async with self.session_factory() as session:
            session.add(message)
            await session.commit()
```

## 7. Security & PII

- all text is stored as UTF-8
- memory extraction must scrub sensitive PII before persistence
- database access should be restricted to application services only
- backups and storage must be encrypted at rest

## 8. Operational Rules

- every schema change must ship with a migration
- avoid storing oversized raw prompts unless retention and purpose are explicit
- background jobs should write through the same domain/repository rules as the API
