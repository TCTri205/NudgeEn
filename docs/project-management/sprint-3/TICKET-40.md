# TICKET-40: New Vocabulary Detection & Tracking

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 3
- **Assignee:** AI Engineer / Backend
- **Domain:** Data Extraction / Pedagogy
- **Priority:** P2 - Medium
- **Assumptions:**
  - A baseline "Common Words" list is available.
- **Affected areas:** `api/app/modules/pedagogy/vocabulary.py`, User Profile Stats.

## Current State / Existing System

- **Implemented:** Memory extraction of facts (TICKET-25).
- **Missing:** Any ability to track the *linguistic* growth of the user, specifically new words they are using for the first time.

## Context / Problem

An "English Learning" app should show you your growing vocabulary. By tracking unique lemmas (base word forms) and comparing them against the user's history and CEFR difficulty lists, we can highlight "Sophisticated words" the user has used effectively.

## Why This Is Needed

- **Business Impact:** Provides positive reinforcement and a sense of growing "fluency."
- **Architectural Impact:** Adds a linguistic processing step (NLP) to the message ingest pipeline.

## Scope

### In-scope

- Implement basic lemmatization (using `spaCy` or `NLTK` or LLM-based detection).
- Logic to track "Active Vocabulary" in a `user_vocabulary` table.
- Filter out top 1000 common English words to focus on "Learning Words."
- Categorize words by CEFR level (A1-C2).
- Update the `weekly_progress_card` with "3 New Sophisticated Words You Used."

### Out-of-scope

- Spaced Repetition (SRS) system.

## Dependencies / Parallelism

- **Dependencies:** TICKET-16 (Message Persistence), TICKET-38 (Metrics).
- **Parallelism:** Can be done after basic metrics are working.

## Rules / Constraints

- Must be efficient (don't re-scan old messages).
- Only track words used in valid, full sentences.

## What Needs To Be Built

1. `api/app/modules/pedagogy/vocab_service.py`: Linguistic extraction logic.
2. `user_vocabulary` table implementation.

## Proposal

Use an LLM pass (during memory extraction) to list "Interesting/Advanced vocabulary used by the user in this session." This is more robust than simple list-matching and can detect usage in context.

## Implementation Breakdown

1. **Extraction:** Add vocabulary extraction to the `memory_extraction` worker.
2. **Storage:** Save new words to the DB with the `first_seen_at` timestamp.
3. **Level-check:** Tag words with their CEFR level using a lookup table.
4. **Validation:** Verify that "Sublime" is tracked as a new word but "Good" is ignored.

## Acceptance Criteria

- [ ] New, non-common words used by the user are successfully logged.
- [ ] Vocab intensity (level of words used) is tracked over time.
- [ ] Weekly cards display accurate list of "New words."

## Test Cases

### Happy Path

- User says "This view is absolutely spectacular" -> `spectacular` (B2) added to vocab list.

### Failure Path

- User repeats a word they've used before -> Count increases but no "New Word" event triggered.

### Regression Tests

- Ensure typos are not tracked as "Sophisticated new words."
