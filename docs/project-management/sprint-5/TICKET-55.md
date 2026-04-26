# TICKET-55: LLM-as-a-Judge Regression Suite

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 5
- **Assignee:** AI Engineer
- **Domain:** AI Quality / QA
- **Priority:** P2 - Medium
- **Assumptions:**
  - Access to a high-tier model (e.g., Gemini 2.5 Pro) for judging.
- **Affected areas:** CI Pipeline, Persona Engine.

## Current State / Existing System

- **Implemented:** Manual testing of persona responses (TICKET-23).
- **Missing:** Automated way to ensure that a prompt update in TICKET-23 doesn't accidentally make the "Sarcastic" persona too mean or the "Gentle" persona too boring.

## Context / Problem

AI behavior is "fuzzy." We need a scientific way to measure response quality. By using a "Judge" LLM to grade our chatbot's responses against a rubric, we can detect quality regressions before they reach users.

## Why This Is Needed

- **Business Impact:** Maintains consistent product "vibe" and pedagogical accuracy.
- **Architectural Impact:** Implements a state-of-the-art "Eval" pipeline.

## Scope

### In-scope

- Build the `EvaluationSuite`:
  - **Dataset:** 30 prompt pairs (User Input + Expected Vibe).
  - **The Judge:** An LLM with a detailed grading rubric (1-10 on Vibe, 1-10 on Grammar correctness).
- Integration into GitHub Actions: Run the suite on any change to `prompts/persona.py`.
- Reporting: Generate a markdown comment on the PR with the "Vibe Score."

### Out-of-scope

- Human-in-the-loop validation (automated only for now).

## Dependencies / Parallelism

- **Dependencies:** TICKET-23 (Persona Prompts), TICKET-32 (Structured Output).

## Rules / Constraints

- Evals should take < 5 minutes to run.
- Use a diverse set of user levels (A1 to C1) in the test cases.

## What Needs To Be Built

1. `api/tests/evals/judge_logic.py`.
2. `api/tests/evals/gold_standard.json`.

## Proposal

Use a "Single-Turn" evaluation. For every PR, the CI sends 30 inputs to the current code, then sends the outputs to Gemini 2.5 Pro with the prompt: "Is this correction helpful? Is the persona tone correct? Grade 1-10."

## Implementation Breakdown

1. **Rubric Definition:** Write the grading prompt for the Judge.
2. **Tooling:** Use `promptfoo` or a custom script to manage the harness.
3. **Baseline:** Run against the current "Good" version to establish the target score (e.g., 8.5).
4. **Validation:** Purposefully break a prompt and ensure the score drops in the CI.

## Acceptance Criteria

- [ ] Regression suite runs automatically on PRs.
- [ ] PR is blocked if the Vibe Score drops below 8.0.
- [ ] Every "Gold Standard" case has a documented reasoning for its score.

## Test Cases

### Happy Path

- Refactor prompt -> Evals run -> Score: 8.7 -> PR marked safe.

### Failure Path

- Break the persona (make it rude) -> Evals run -> Score: 4.2 -> PR fails.

### Regression Tests

- Ensure "Gentle" persona always provides corrections politely.
