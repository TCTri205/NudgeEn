# TICKET-32: Structured Output Parsing (Reply + Correction)

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 2
- **Assignee:** Backend Lead
- **Domain:** AI / Data Processing
- **Priority:** P0 - Critical
- **Assumptions:**
  - The LLM prompt (TICKET-23) instructs the model to return JSON.
- **Affected areas:** `api/app/modules/chat/parser.py`, Response Handling.

## Current State / Existing System

- **Implemented:** Basic API routes (TICKET-01).
- **Missing:** Logic to parse a "dual-payload" from the AI (The friendly reply AND the pedagogical correction).

## Context / Problem

NudgeEn's unique feature is correcting the user *while* responding as a friend. This requires the LLM to return a structured JSON object. However, LLMs sometimes add markdown backticks, prefix text, or return invalid JSON. We need a "bulletproof" parser to extract these fields reliably.

## Why This Is Needed

- **Business Impact:** Crucial for the Pedagogical Engine (Sprint 3/4). If parsing fails, the user gets no corrections.
- **Architectural Impact:** Centralizes output validation and cleaning.

## Scope

### In-scope

- Create Pydantic models for the response:
  - `reply`: The conversational text.
  - `correction`: `Optional[CorrectionObject]`.
- Implement a "Robust Parser" that:
  - Strips markdown (```json ...```).
  - Repair simple JSON syntax errors.
  - Fallback to treating the entire response as a "Reply" if JSON cannot be found.
- Integration: Trigger database persistence for both parts separately (TICKET-16).

### Out-of-scope

- Multi-language corrections (English only for MVP).

## Dependencies / Parallelism

- **Dependencies:** TICKET-23 (Prompts), TICKET-30 (Gemini).
- **Parallelism:** Can be done while LLM adapters are being built.

## Rules / Constraints

- Parsing must not block the SSE stream (tokens should stream raw, but the FINAL object should be parsed for storage).
- Must handle the case where `has_correction` is false.

## What Needs To Be Built

1. `api/app/modules/chat/schemas.py`: Pydantic models.
2. `api/app/modules/chat/parser.py`: JSON extraction logic.

## Proposal

Since we are streaming, we will collect all chunks into a buffer. Once the stream ends, the buffer text is passed to the parser. If it's valid JSON, we extract fields. If not, we use regex to find `{...}` blocks or fallback to raw text.

## Implementation Breakdown

1. **Schema Definition:** Define the `ChatResponse` Pydantic model.
2. **Parser Logic:** Write the regex-based "Cleaning" step before `json.loads`.
3. **Integration:** Hook into the chat service's post-completion logic.
4. **Validation:** Feed the parser 20 malformed examples and ensure it extracts correctly from all.

## Acceptance Criteria

- [ ] Conversational reply is correctly separated from grammar corrections.
- [ ] Corrections are not showed to the user "raw" in the chat bubble (handled by UI later).
- [ ] Malformed JSON from the LLM doesn't crash the server.
- [ ] Database stores the correction and reply in their respective tables.

## Test Cases

### Happy Path

- LLM returns valid JSON -> Reply and Correction stored correctly.

### Failure Path

- LLM returns raw text (No JSON) -> Parser extracts everything as "Reply", correction is null.
- LLM returns JSON with markdown "```json ..." -> Parser strips markdown and parses successfully.

### Regression Tests

- Verify that large replies (500+ words) don't break the regex parser.
