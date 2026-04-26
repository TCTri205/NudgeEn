# TICKET-38: Learning Metrics Aggregation (Vocab/Grammar)

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 3
- **Assignee:** Backend Lead / Data
- **Domain:** Data Analysis / Pedagogy
- **Priority:** P2 - Medium
- **Assumptions:**
  - `message_corrections` table is populated (TICKET-36).
- **Affected areas:** `api/app/modules/pedagogy/metrics.py`, Analytics.

## Current State / Existing System

- **Implemented:** Raw storage of corrections (TICKET-36).
- **Missing:** Any analytics layer to compute "User Accuracy" or "Common Pitfalls."

## Context / Problem

Raw corrections are too granular for high-level insight. We need to aggregate them into metrics like "Accuracy Rate" (Corrections / Messages) and "Growth Trends" (Error rate in Week 2 vs Week 1) to power the progress cards and a future user dashboard.

## Why This Is Needed

- **Business Impact:** Provides the "Proof of Progress" that users need to justify long-term engagement.
- **Architectural Impact:** Implements the pedagogical reporting layer.

## Scope

### In-scope

- Implement aggregation queries in SQLAlchemy:
  - Count corrections by `grammar_rule`.
  - Total messages per user per day/week.
  - "Accuracy Rate": `(1 - (total_corrections / total_messages)) * 100`.
- Implement `VocabularyTracker` (TICKET-40 pre-requisite):
  - Identify unique words in user messages.
- Expose an internal Service `PedagogyAnalyticsService`.

### Out-of-scope

- Real-time dashboard (data can be cached/pre-computed).

## Dependencies / Parallelism

- **Dependencies:** TICKET-36 (Persistence).
- **Parallelism:** Can be done in parallel with TICKET-37.

## Rules / Constraints

- Queries must be optimized to avoid table scans on millions of messages.
- Use materialized views or Redis caching for frequent user dashboard lookups.

## What Needs To Be Built

1. `api/app/modules/pedagogy/metrics_service.py`.
2. Optimized SQL queries for rule-based aggregation.

## Proposal

Pre-calculate stats at the end of each day and store them in a `user_daily_stats` table. This allows the "Weekly Card" to be a simple sum of 7 rows rather than a complex join over thousands of messages.

## Implementation Breakdown

1. **Aggregator Logic:** Implement the "Score" calculation formulas.
2. **Persistence:** Create the `user_stats` table for cached metrics.
3. **Task Hook:** Trigger an update after each message or daily.
4. **Validation:** Verify metrics against a manual count of a test user's corrections.

## Acceptance Criteria

- [ ] Accuracy Rate is correctly calculated.
- [ ] Top 3 grammar error categories can be identified for any user.
- [ ] Vocab count (unique words) matches the actual user message content.
- [ ] Query performance is stable under load.

## Test Cases

### Happy Path

- Send 10 messages, 2 corrections -> Accuracy shown as 80%.

### Failure Path

- No messages sent -> Accuracy shown as 0% or N/A (handle division by zero).

### Regression Tests

- Ensure stats for User A never include data from User B.
