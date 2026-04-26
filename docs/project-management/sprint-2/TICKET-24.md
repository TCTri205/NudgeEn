# TICKET-24: Interactive 3-turn Onboarding Calibration

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 2
- **Assignee:** Fullstack Developer
- **Domain:** User Experience / AI
- **Priority:** P0 - Critical
- **Assumptions:**
  - Auth.js is functional (Sprint 1).
  - `useChat` hook (TICKET-15) can be reused or adapted for onboarding.
- **Affected areas:** `web/app/onboarding/`, `api/app/modules/user/`, Onboarding State.

## Current State / Existing System

- **Implemented:** Users can log in (Sprint 1).
- **Missing:** Any structured onboarding; users are dropped directly into a blank chat.

## Context / Problem

To provide a personalized experience, the AI needs to know the user's name, interests, and current English proficiency. A structured, interactive 3-turn "Vibe Check" collects this data naturally while demonstrating the AI's personality immediately.

## Why This Is Needed

- **Business Impact:** Increases personalization and user "buy-in" during the critical first 5 minutes of use.
- **Architectural Impact:** Establishes the workflow for specialized "Agent Missions" (one-off tasks with specific goals).

## Scope

### In-scope

- Implement a 3-turn state machine logic:
  - **Turn 1:** AI introduces itself and asks for user's name.
  - **Turn 2:** AI asks about hobbies or goals.
  - **Turn 3:** A short roleplay activity to determine English level.
- Save progress in the `user_profiles` table.
- Frontend: Specialized "Onboarding" UI that feels distinct from the main chat (bubbles-only, full-screen).
- Finalize onboarding and mark `onboarding_completed: true`.

### Out-of-scope

- Complex skill testing (multiple choice, etc.).

## Dependencies / Parallelism

- **Dependencies:** TICKET-23 (Persona Prompts), TICKET-26 (Profile Projection).
- **Parallelism:** Can be done after the basic chat pipe (Sprint 1) is stable.

## Rules / Constraints

- Onboarding cannot be skipped by new users.
- Messages sent during onboarding should trigger memory extraction immediately.
- The UI must be highly focused (no sidebar, no distractions).

## What Needs To Be Built

1. `web/app/onboarding/page.tsx`: Interactive multi-step form or chat view.
2. `api/app/modules/user/onboarding_service.py`: Logic to handle onboarding turns and level assessment.
3. Database update to track `onboarding_step_id`.

## Proposal

Implement onboarding as a specialized conversation with its own system prompt that forces the LLM to follow the 3-step script. The "Level Assessment" should be done by asking the user to describe a picture or situation and having the LLM rank it A1-C2.

## Implementation Breakdown

1. **Frontend UI:** Build the focused landing page for onboarding.
2. **Step Logic:** Create the state machine (Step 1 -> 2 -> 3 -> Done).
3. **Analysis:** Implement the level assessment logic in the final turn.
4. **Finalization:** Update the user record and redirect to the home chat.

## Acceptance Criteria

- [ ] New users are automatically redirected to `/onboarding`.
- [ ] The full 3-turn flow completes without errors.
- [ ] User's name, vibe, and assessed level are saved correctly in the DB.
- [ ] Completing onboarding redirects the user to the main chat.

## Test Cases

### Happy Path

- Complete all 3 steps -> Redirected -> Persona references name in first real chat.

### Failure Path

- Refresh page mid-onboarding -> State is preserved, user continues from where they left off.

### Regression Tests

- Ensure `onboarding_completed` flag prevents returning to the flow once done.
