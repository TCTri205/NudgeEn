# TICKET-23: Persona Engine Prompt Templates

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 2
- **Assignee:** AI Engineer
- **Domain:** AI / Persona
- **Priority:** P0 - Critical
- **Assumptions:**
  - Base prompt structure supports Jinja2 or similar templating.
  - Persona identifiers match the DB `vibe_preference`.
- **Affected areas:** `api/app/modules/persona/prompts.py`, LLM Context.

## Current State / Existing System

- **Implemented:** Modular monolith skeleton and basic chat routing (TICKET-01).
- **Missing:** Any logic to differentiate AI behavior based on selected vibe/persona.

## Context / Problem

Users expect the AI to have a distinct personality that resonates with them. We need to formalize how "Sarcastic", "Gentle", and "Tech-savvy" personas are represented in the LLM's system instructions to ensure consistent "vibe" and effectiveness as an English learning friend.

## Why This Is Needed

- **Business Impact:** High emotional engagement leads to more frequent use.
- **Architectural Impact:** Establishes the prompt engineering layer and the "Persona-as-a-Service" pattern.

## Scope

### In-scope

- Implement three core system prompt templates:
  - **Gentle/Empathetic:** Warm, encouraging, simple English.
  - **Sarcastic/Banter:** Playful, witty, conversational.
  - **Tech-savvy:** Precise, analytical, modern.
- Define a standard context structure for:
  - User name.
  - English level (A1-C2).
  - Recent memories (formatted).
- Implement "Correction" instructions within the prompt to ensure consistent structured output.

### Out-of-scope

- User-created custom personas.

## Dependencies / Parallelism

- **Dependencies:** TICKET-01 (FastAPI Skeleton).
- **Parallelism:** Can be done in parallel with TICKET-30 (Gemini Integration).

## Rules / Constraints

- Persona prompts must not exceed 500 tokens.
- All prompts must strictly request JSON output with `reply` and `correction` fields.
- Tone must be consistently maintained throughout long conversations.

## What Needs To Be Built

1. `api/app/modules/persona/config.py`: Hardcoded prompt strings.
2. `api/app/modules/persona/builder.py`: Logic to inject user data into templates.
3. Unit tests to verify correct placeholder replacement.

## Proposal

Use a dictionary mapping in Python to store the system prompts. Utilize a helper function `build_system_message(user_profile, memories)` that selects the template and interpolates the current user context.

## Implementation Breakdown

1. **Prompt Design:** Write and refine the three system prompts in a markdown-friendly configuration file.
2. **Templating Logic:** Implement the `PersonaBuilder` class.
3. **Validation:** Test prompts against Gemini/Groq using a script to ensure they generate the expected "vibe" and JSON format.

## Acceptance Criteria

- [ ] Each of the three personas exhibits a distinct and consistent tone in chat tests.
- [ ] System prompt correctly includes the user's name and English level.
- [ ] LLM output matches the required `{reply, correction}` JSON structure 100% of the time.
- [ ] Prompt remains effective even when memories are injected.

## Test Cases

### Happy Path

- Vibe set to "Sarcastic" -> AI uses "Banter" and witty remarks.
- Vibe set to "Gentle" -> AI uses "Sweet/Supportive" language.

### Failure Path

- Unknown vibe ID passed -> Reverts to "Gentle" (safe default).

### Regression Tests

- Ensure updates to the prompt don't break the JSON parsing logic.
