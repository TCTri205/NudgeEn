# TICKET-37: Weekly Progress Card Generator & UI

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 3
- **Assignee:** Fullstack Developer
- **Domain:** Web UI / AI
- **Priority:** P2 - Medium
- **Assumptions:**
  - Learning metrics (TICKET-38) are available.
  - Redis Taskiq scheduler is active.
- **Affected areas:** `web/components/chat/cards/`, `api/app/modules/pedagogy/summary.py`.

## Current State / Existing System

- **Implemented:** Chat history (TICKET-16).
- **Missing:** Any high-level "feedback loop" that shows the user their progress over a longer duration (1 week).

## Context / Problem

Learning a language is a marathon. To keep users motivated, we need to periodically "zoom out" and show them their wins—new words learned, most common mistakes fixed, and total activity. This should be delivered as a beautiful, rich "Progress Card" right in the chat stream.

## Why This Is Needed

- **Business Impact:** Drives "Learning Efficacy" perception and provides shareable moments of achievement.
- **Architectural Impact:** Integrates background aggregation jobs with the real-time chat UI.

## Scope

### In-scope

- Create `WeeklyProgressCard` UI component (Tile/Card style).
- Background job `generate_weekly_card(user_id)`:
  - Aggregate message counts.
  - Fetch and rank top 3 "Corrected Grammar Rules."
  - Identify 3 "New Words" used.
  - Use LLM to write a 1-sentence personalized encouragement.
- Persistence: Store the card data as a special message type `system_card`.
- Frontend: Distinct styling for the card (shadows, icons, possibly a mini-chart).

### Out-of-scope

- Social sharing to Twitter/FB.

## Dependencies / Parallelism

- **Dependencies:** TICKET-36 (Corrections Persistence), TICKET-38 (Metrics).
- **Parallelism:** Can be done after the metrics engine is ready.

## Rules / Constraints

- Cards should only be generated once every 7 days per user.
- The card must be readable on mobile in portrait mode.

## What Needs To Be Built

1. `web/components/chat/cards/weekly-progress.tsx`.
2. `workers/app/tasks/pedagogy.py`: The cron task.
3. API endpoint to retrieve card details if needed.

## Proposal

Implement the card as a "System Message" in the database. When the frontend encounters a message with `type="progress_card"`, it renders the specialized `WeeklyProgress` component instead of a chat bubble. Use `recharts` for a simple accuracy sparkline.

## Implementation Breakdown

1. **Frontend Components:** Build the card layout.
2. **Aggregation Logic:** Write the service that queries the last 7 days of DB data.
3. **Card Generation:** Hook the service into a Taskiq background task.
4. **Validation:** Manually trigger the card for a test user and verify the UI aesthetics.

## Acceptance Criteria

- [ ] A progress card appears in the chat for active users every 7 days.
- [ ] Card contains correct numbers for messages and corrections.
- [ ] The personalized summary tone matches the user's chosen persona.
- [ ] UI is "Premium" with icons and clear highlights.

## Test Cases

### Happy Path

- Week of chats -> Cron runs -> Card appears -> Shows "Articles (5), Tenses (2)" as top errors.

### Failure Path

- No activity during the week -> No card is generated (silent skip).

### Regression Tests

- Ensure the card doesn't count "System messages" in the total message tally.
