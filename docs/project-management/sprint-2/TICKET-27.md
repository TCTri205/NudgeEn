# TICKET-27: Memory-to-Context Retrieval Logic

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 2
- **Assignee:** AI Engineer
- **Domain:** AI / Context
- **Priority:** P1 - High
- **Assumptions:**
  - User Profile JSON projection (TICKET-26) is functional.
  - Token budget for memory is ~500-1000 tokens.
- **Affected areas:** `api/app/modules/persona/builder.py`, Chat prompt assembly.

## Current State / Existing System

- **Implemented:** Persona prompts with dummy context (TICKET-23).
- **Missing:** Logic to actually fetch and inject stored user facts into the prompt.

## Context / Problem

Even if we have memories in the DB, the AI won't "know" them unless they are injected into the prompt context for every message. We need a performant way to select the *most relevant* or *most recent* memories to give the AI its "long-term memory" during a conversation.

## Why This Is Needed

- **Business Impact:** Enables the AI to say things like "How was that hike you mentioned?" instead of "Tell me about yourself."
- **Architectural Impact:** Integrates the "Read" side of our Memory engine into the primary chat flow.

## Scope

### In-scope

- Implement a retrieval strategy:
  - **Primary:** Load from the `user_profiles.profile` JSON (fast).
  - **Fallback:** Query `user_memories` for the top 10 most recent facts if the JSON is stale.
- Design the "Memory Block" in the system prompt.
- Logic to format these facts into a clean, human-readable string for the LLM.
- Token counting and truncation to prevent context window overflow.

### Out-of-scope

- Vector search / Semantic retrieval (RAG) - out of scope for MVP.

## Dependencies / Parallelism

- **Dependencies:** TICKET-23 (Persona Prompts), TICKET-26 (Profile Projection).
- **Parallelism:** Can be done once the first set of memories is successfully saved.

## Rules / Constraints

- Retrieval must add < 50ms to the total request latency.
- Do not repeat information that is already in the recent conversation windows.
- Prioritize facts mentioned by the user over AI assumptions.

## What Needs To Be Built

1. `api/app/modules/persona/retrieval.py`: Logic to fetch and format memories.
2. Integration in `api/app/modules/persona/builder.py` (the prompt builder).

## Proposal

For the MVP, use a simple chronological retrieval of the 10 most recent memories from the `user_profiles` JSON projection. This ensures consistency and extreme speed.

## Implementation Breakdown

1. **Fetch Logic:** Implement the profile read and memory sorting.
2. **Formatting:** Create a template: `User Facts: [Fact 1], [Fact 2]...`.
3. **Prompt Injection:** Append the memory string to the base system prompt.
4. **Validation:** Use "Simulated Conversation" to see if the AI acknowledges the injected facts.

## Acceptance Criteria

- [ ] AI correctly references the user's name (from memory) during chat.
- [ ] AI can recall facts from previous sessions (e.g., "Last time we talked about hiking...").
- [ ] Memory block in the final LLM prompt is correctly formatted and non-redundant.
- [ ] Performance of retrieval is within the <50ms budget.

## Test Cases

### Happy Path

- DB has memory "loves coffee" -> AI says "Maybe you should grab a coffee."

### Failure Path

- No memories found -> Memory block is omitted from the prompt seamlessly.

### Regression Tests

- Ensure memory injection doesn't push the prompt over the model's token limit (safety truncation).
