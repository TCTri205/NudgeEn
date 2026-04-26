# TICKET-28: Proactive Engagement Triggers

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 2
- **Assignee:** AI Engineer
- **Domain:** AI / UX
- **Priority:** P2 - Medium
- **Assumptions:**
  - AI has access to historical memories (TICKET-27).
- **Affected areas:** `api/app/modules/persona/builder.py`, Engagement Logic.

## Current State / Existing System

- **Implemented:** Passive response generation (AI only speaks when spoken to) (TICKET-23).
- **Missing:** Any logic for the AI to "take the lead" or reference a previous conversation topic to deepen the connection.

## Context / Problem

A true friend doesn't just answer questions; they bring up things you talked about before. We need to instruct the AI to occasionally (e.g., 20% of the time) use a "Proactive Trigger" from its memory to ask a follow-up question about the user's life.

## Why This Is Needed

- **Business Impact:** Significantly increases user satisfaction and the feeling of a "genuine connection," driving long-term retention.
- **Architectural Impact:** Adds a "Proactive Instruction" layer to the prompt builder.

## Scope

### In-scope

- Implement a "Proactive Instruction" block in the system prompt.
- Logic to pick a "Topic of the Day" from the user's memories.
- Instructions for the AI to:
  - "Ask how the [Hobby/Goal] from last week is going."
  - "Reference a past fact naturally in the reply."
- Implement a "Nudge Probability" to ensure it's not annoying or repetitive.

### Out-of-scope

- Push notifications (frontend only displays this in-chat).

## Dependencies / Parallelism

- **Dependencies:** TICKET-25 (Memory Extraction), TICKET-27 (Retrieval).
- **Parallelism:** Can be done once memory extraction is producing reliable facts.

## Rules / Constraints

- Proactive comments must be relevant to the *current* conversation flow if possible.
- If the user is asking a specific question, the AI should prioritize answering before being proactive.

## What Needs To Be Built

1. `api/app/modules/persona/engagement.py`: Logic to choose a "Memory Nudge."
2. Integration into the `PersonaBuilder`.

## Proposal

Add a section to the system prompt: `PROACTIVE CHALLENGE: Reference the user's interest in {interest} and ask a brief follow-up question.` Select a random interest from the profile JSON that hasn't been mentioned in the current session.

## Implementation Breakdown

1. **Topic Selection:** Logic to find an "under-referenced" memory fact.
2. **Prompt Update:** Dynamically inject the proactive goal into the prompt.
3. **Validation:** Chat with the AI and ensure it mentions a fact from "yesterday" (test data).

## Acceptance Criteria

- [ ] AI naturally asks a follow-up question about a stored user fact.
- [ ] Engagement doesn't feel generic (e.g., "Tell me more about your hobby").
- [ ] AI doesn't bring up the same fact in every single message.

## Test Cases

### Happy Path

- DB contains "User is preparing for an exam" -> AI asks "How's the test prep going?" during a casual chat.

### Failure Path

- No memories found -> No proactive goals are set; AI remains passive (safe).

### Regression Tests

- Ensure proactive comments don't break the English correction logic (TICKET-32).
