# TICKET-29: Weekly Vibe Check / Progress Summary

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 2
- **Assignee:** Backend Lead / AI
- **Domain:** Engagement / Automation
- **Priority:** P2 - Medium
- **Assumptions:**
  - Database contains enough message history for a 7-day period.
  - User has not opted out of "Vibe Checks."
- **Affected areas:** `workers/app/tasks/maintenance.py`, Chat system messages.

## Current State / Existing System

- **Implemented:** Chat history persistence (TICKET-16).
- **Missing:** Any proactive automation to re-engage users who have gone "quiet" for several days.

## Context / Problem

Users often forget to check their English learning apps. A "Weekly Vibe Check" serves as a warm, character-driven summary of what they talked about last week and an invitation to return, making the AI feel proactive and caring.

## Why This Is Needed

- **Business Impact:** Drastically improves Day-7 and Day-30 retention.
- **Architectural Impact:** Introduces "System-Initiated" messages into the conversation stream.

## Scope

### In-scope

- Implement a cron-like task (Taskiq) that runs daily.
- Logic to query users who:
  - Have `onboarding_completed: true`.
  - Have not sent a message in >= 7 days.
  - Have not received a "Vibe Check" in the last 14 days.
- Generate a 2-3 sentence "Miss You / Summary" message using the user's memories and persona.
- Inject this as an "AI Message" into the user's most recent conversation.

### Out-of-scope

- Email/Push notifications (chat-only for now).

## Dependencies / Parallelism

- **Dependencies:** TICKET-05 (Taskiq), TICKET-16 (Persistence), TICKET-23 (Personas).
- **Parallelism:** Can be done at the end of Sprint 2.

## Rules / Constraints

- Do not spam the user; the check-in should feel rare and special.
- The tone MUST match the user's selected persona (e.g., Sarcastic Sam might say "Finally giving up on English, are we?").

## What Needs To Be Built

1. `workers/app/tasks/retention.py`: The daily inactivity scan.
2. `api/app/modules/chat/system_service.py`: Logic to "force-inject" an AI message into a thread.

## Proposal

Use Taskiq's scheduler to run `generate_vibe_checks` at 10:00 AM daily. For each eligible user, use a "Summary Prompt" that looks at their profile JSON and generates a greeting.

## Implementation Breakdown

1. **Inactivity Query:** Write the SQL/ORM query to find target users.
2. **Generation:** Create the "Vibe Check" prompt for the LLM.
3. **Delivery:** Insert the message into the `messages` table.
4. **Validation:** Manually backdate a message timestamp in DB and verify the worker triggers a check-in.

## Acceptance Criteria

- [ ] Users who are inactive for 7 days receive a personalized check-in message.
- [ ] The message reflects the user's selected persona tone.
- [ ] The system doesn't send duplicate check-ins within the same week.

## Test Cases

### Happy Path

- Last message: 8 days ago -> Worker runs -> "Miss you!" message appears in chat.

### Failure Path

- User has no memories yet -> AI sends a generic "Hope you're having a good week" instead of a deep summary.

### Regression Tests

- Verify that a system-initiated message doesn't break the `conversation.last_message` pointer in the UI.
