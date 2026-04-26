# TICKET-21: PII Scrubbing Pipeline (Initial)

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 1
- **Assignee:** AI Engineer
- **Domain:** Data Privacy / Safety
- **Priority:** P1 - High
- **Assumptions:**
  - PII scrubbing occurs before data hits long-term persistent storage (Memories).
  - Regex is sufficient for phase 1 (MVP).
- **Affected areas:** `api/app/modules/memory/`, Data ingestion pipeline.

## Current State / Existing System

- **Implemented:** General architecture for memory extraction (planned for EPIC-03).
- **Missing:** Any filter to prevent sensitive personal information (SSN, Phone, Email) from being stored in the AI's permanent memory.

## Context / Problem

Users may share sensitive personal data in casual conversation. To protect user privacy and comply with best practices, we must ensure that highly sensitive identifiers (like SSNs or financial details) are scrubbed from text before they are processed by the memory extraction agent.

## Why This Is Needed

- **Business Impact:** Mitigates the risk of sensitive data leaks and builds long-term user trust.
- **Architectural Impact:** Establishes a "Privacy-First" middleware in the message processing chain.

## Scope

### In-scope

- Implement a `ScrubberService` using robust regex patterns for:
  - Emails.
  - Phone numbers (various formats).
  - Social Security Numbers (SSNs).
- Create a unit test suite with common PII examples.
- Integrate the service into the memory extraction pipeline (hook only for now).

### Out-of-scope

- Advanced NLP-based PII detection (e.g., detecting names or complex addresses).
- Scrubbing of the primary message history (messages are immutable).

## Dependencies / Parallelism

- **Dependencies:** TICKET-01 (FastAPI Skeleton).
- **Parallelism:** Can be done in parallel with TICKET-20 (Safety Gatekeeper).

## Rules / Constraints

- Handled as a non-destructive transformation for memory only.
- Redaction should replace PII with generic tokens (e.g., `[EMAIL_REDACTED]`).
- The scrubbing logic must be fast enough to run in background worker threads without significant delay.

## What Needs To Be Built

1. `api/app/core/privacy/scrubber.py`: The utility containing regex patterns and the `scrub()` function.
2. `api/app/tests/core/test_scrubber.py`: Comprehensive test suite for redaction.
3. Hook in the memory task pipeline to call `scrubber.scrub(text)`.

## Proposal

Use a collection of standard Python regex patterns. The `scrub` function will iterate through these patterns and apply `re.sub()` to the input string.

## Implementation Breakdown

1. **Research:** Identify standard, tested regex patterns for PII.
2. **Library Development:** Build the `ScrubberService`.
3. **Testing:** Create a "PII Jailbreak" test set to ensure patterns are effective.
4. **Integration:** Add the scrubbing step to the `Taskiq` worker responsible for memory extraction.

## Acceptance Criteria

- [ ] Email addresses in test strings are correctly replaced with `[EMAIL_REDACTED]`.
- [ ] Phone numbers in various international formats are redacted.
- [ ] SSNs are redacted.
- [ ] Non-sensitive text (like names or hobbies) remains intact.
- [ ] Scrubber passes all unit tests.

## Test Cases

### Happy Path

- "My email is john@example.com" -> "My email is [EMAIL_REDACTED]".
- "Call me at +1-555-0199" -> "Call me at [PHONE_REDACTED]".

### Failure Path

- Complex edge case (e.g., email written as "john at example dot com") -> Likely fails (document as known limitation).

### Regression Tests

- Ensure no excessive "False Positive" redaction (e.g., redacting a product ID that looks like a phone number).
