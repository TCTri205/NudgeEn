# TICKET-39: Adaptive Correction Frequency by User Level

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 3
- **Assignee:** AI Engineer
- **Domain:** AI / Pedagogy
- **Priority:** P2 - Medium
- **Assumptions:**
  - `english_level` is stored in the User Profile (TICKET-24).
- **Affected areas:** `api/app/modules/pedagogy/logic.py`, Prompt Context.

## Current State / Existing System

- **Implemented:** Generic correction generation rules (TICKET-32).
- **Missing:** Any ability to tone down or amp up the number of corrections based on whether the user is a Beginner or an Advanced speaker.

## Context / Problem

A beginner (A1/A2) needs guidance on basic tenses and articles. An advanced speaker (C1/C2) will find basic corrections annoying and needs focus on nuanced word choice or natural phrasing. We must adapt our LLM instructions and severity filters to match the user's assessed level.

## Why This Is Needed

- **Business Impact:** Prevents user frustration (over-correcting advanced users) and maximizes learning value (guiding beginners).
- **Architectural Impact:** Adds a "Sensitivity" layer to the pedagogical engine.

## Scope

### In-scope

- Implement "Correction Tiers" based on CEFR levels:
  - **A1-A2:** Correct everything (major and minor). High frequency.
  - **B1-B2:** Correct moderate and major errors only.
  - **C1-C2:** Only correct "Unnatural phrasing" or "Major meaning errors".
- Inject the user's level and the corresponding "Strictness" instructions into the correction prompt.
- Settings implementation: Allow user manual override ("Strict", "Gentle", "Off").

### Out-of-scope

- Multi-dimensional skill levels (e.g., A1 in grammar, C1 in vocab).

## Dependencies / Parallelism

- **Dependencies:** TICKET-24 (Onboarding assessment), TICKET-30 (Gemini).
- **Parallelism:** Can be done once the basic correction service is stable.

## Rules / Constraints

- Never exceed 2 corrections per message, regardless of level.
- Higher level users should receive more complex "Explanations."

## What Needs To Be Built

1. `api/app/modules/pedagogy/adaptive_config.py`: Level-to-sensitivity mapping.
2. Logic update in `CorrectionService` to filter results before returning to AI.

## Proposal

Add a `threshold` parameter to the correction service. For A1 users, `threshold=0.3`. For C1 users, `threshold=0.8`. Compare this against the LLM's returned `severity_score` or `confidence`.

## Implementation Breakdown

1. **Tier Definition:** Formalize the rules for each CEFR level.
2. **Prompt Injection:** Update the system prompt for corrections to include the level-specific style.
3. **Filtering Logic:** Code the logic to discard "Minor" corrections for high-level users.
4. **Validation:** Perform a "Battle of the Levels" test—verify same error is corrected for A1 but ignored for C1.

## Acceptance Criteria

- [ ] Users at A1 level get more corrections than users at C1 level.
- [ ] Explanations for C1 users use more sophisticated pedagogical terms.
- [ ] User settings (frequency) successfully override the auto-assessed level logic.

## Test Cases

### Happy Path

- User at A2 says "I go school" -> Correction appears.
- User at C1 says "I go school" -> Correction appears (Major error).
- User at C1 says "I'm looking for the information" -> No correction (Small article error ignored for high level).

### Failure Path

- No level data found -> Defaults to "B1" (Moderate) frequency.

### Regression Tests

- Ensure changing level in settings instantly updates the next message's corrections.
