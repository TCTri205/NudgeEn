# TICKET-25: Memory Extraction Taskiq Worker

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 2
- **Assignee:** AI Engineer
- **Domain:** AI / Memory
- **Priority:** P0 - Critical
- **Assumptions:**
  - Taskiq worker infrastructure is functional (TICKET-05).
  - LLM (Gemini/Groq) can output structured JSON for fact extraction.
- **Affected areas:** `workers/app/tasks/memory.py`, `user_memories` table.

## Current State / Existing System

- **Implemented:** Message persistence and Redis task queue (TICKET-05, TICKET-16).
- **Missing:** Any logic to "read back" conversations and extract key facts like hobbies, names, or goals for long-term storage.

## Context / Problem

A "friend" remembers things. To simulate this, we need a background process that analyzes recent conversation turns, identifies important user facts, and stores them in a normalized format. This happens out-of-band to ensure the chat remains fast.

## Why This Is Needed

- **Business Impact:** Forms the basis of the "Persistent AI Friend" value proposition.
- **Architectural Impact:** Implements the asynchronous intelligence layer, separating chat response generation from long-term knowledge extraction.

## Scope

### In-scope

- Create a Taskiq job `extract_memories_task(conversation_id, message_ids)`.
- Implement a specialized LLM prompt for "Fact Extraction" that outputs:
  - `topic` (e.g., "hobby", "goal", "family").
  - `detail` (e.g., "loves hiking in the Alps").
  - `confidence` (0.0 - 1.0).
- Save extracted facts into the `user_memories` table.
- Logic to prevent redocking/duplicate extraction of the same message.
- Basic PII scrubbing before storage (TICKET-21 integration).

### Out-of-scope

- Real-time memory extraction (must be background).

## Dependencies / Parallelism

- **Dependencies:** TICKET-05 (Taskiq Setup), TICKET-16 (Message Persistence), TICKET-21 (PII Scrubber).
- **Parallelism:** Can be done in parallel with Frontend UI work.

## Rules / Constraints

- Extraction should run at most once per 5 minutes or after a conversation "ends" (inactivity).
- LLM response must be strictly valid JSON.
- Extraction must not impact the primary database's write performance significantly.

## What Needs To Be Built

1. `workers/app/tasks/memory.py`: Task definition.
2. `api/app/modules/memory/service.py`: LLM orchestration for extraction.
3. Database triggers or manual enqueuing logic in the chat router.

## Proposal

When a chat turn completes, the API finishes the SSE stream and then enqueues a `memory_extraction` task. The worker fetches the recent context, asks a small LLM (like Gemini Flash) to "Identify 3-5 new facts about [User]", and saves the results.

## Implementation Breakdown

1. **Prompt Engineering:** Define the extraction prompt and schema.
2. **Worker Logic:** Implement the Taskiq task to fetch text and call the LLM.
3. **Storage:** Implement the write logic to `user_memories`.
4. **Validation:** Manually trigger the task on a test conversation and check the DB for data.

## Acceptance Criteria

- [ ] New facts about the user appear in the `user_memories` table after a chat.
- [ ] Facts include correct `topic` and `detail` descriptions.
- [ ] Extraction job completes without errors in the worker logs.
- [ ] Duplicate messages in a single job are handled correctly.

## Test Cases

### Happy Path

- "I really love playing tennis on weekends" -> `topic: hobby, detail: loves playing tennis`.

### Failure Path

- LLM returned invalid JSON -> Worker logs error and retries.
- Connection to Postgres lost -> Job is re-queued by Taskiq.

### Regression Tests

- Ensure User A facts are never mistaken for User B facts.
