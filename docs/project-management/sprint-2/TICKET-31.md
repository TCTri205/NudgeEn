# TICKET-31: Groq Fallback Implementation

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 2
- **Assignee:** AI Engineer
- **Domain:** AI / Reliability
- **Priority:** P1 - High
- **Assumptions:**
  - Groq API Key is available.
  - Groq supports Llama 3 or similar compatible models.
- **Affected areas:** `api/app/core/llm/groq.py`, Failover Logic.

## Current State / Existing System

- **Implemented:** Abstract LLM base class (TICKET-01).
- **Missing:** Support for Groq, which is intended as our high-speed failover or alternative for specific tasks.

## Context / Problem

LLM providers occasionally experience downtime or latency spikes. To ensure NudgeEn is always available for our users, we need a "multi-provider" strategy where Groq (known for extreme speed) can take over if Gemini is struggling.

## Why This Is Needed

- **Business Impact:** Guarantees uptime and provides a baseline for "instant" responses.
- **Architectural Impact:** Standardizes the multi-provider failover pattern in the AI layer.

## Scope

### In-scope

- Implement `GroqProvider` using the `groq` Python SDK (OpenAI-compatible).
- Support streaming tokens via SSE.
- Implement the "Circuit Breaker" pattern in the Chat Service:
  - Try Gemini.
  - If Gemini fails 3 times, switch to Groq for 10 minutes.
- Ensure system prompts are 100% compatible with Llama-based models on Groq.

### Out-of-scope

- Running Groq as the primary engine (Flash remains primary for token context reasons).

## Dependencies / Parallelism

- **Dependencies:** TICKET-30 (Gemini Integration).
- **Parallelism:** Can be done concurrently with TICKET-30.

## Rules / Constraints

- Must match the `StructuredOutput` schema defined for Gemini.
- Latency for Groq should be <100ms for TTFT (Time To First Token).
- Failover should be invisible to the user (no error message, just a different provider).

## What Needs To Be Built

1. `api/app/core/llm/groq.py`: The provider implementation.
2. `api/app/modules/chat/failover.py`: Generic failover/retry logic.

## Proposal

Use a "Provider Registry" in the LLM module. The Chat Service will request the `Primary` provider, and if it catches a `ProviderException`, it will automatically request the `Secondary` provider and retry the specific turn.

## Implementation Breakdown

1. **SDK Integration:** Setup the Groq client.
2. **Streaming:** Map Groq's token format to the internal SSE stream.
3. **Failover Logic:** Implement the retry-on-failure wrapper in the service layer.
4. **Validation:** Force a Gemini failure in dev and verify the chat continues using Groq.

## Acceptance Criteria

- [ ] Groq successfully generates responses when called directly.
- [ ] Failover happens automatically within 2 seconds of a Gemini failure.
- [ ] Resulting JSON structure from Groq matches Gemini's exactly.

## Test Cases

### Happy Path

- Gemini fails -> Groq takes over -> User gets a message -> User doesn't notice.

### Failure Path

- Both providers are down -> System returns a "System Maintenance" message to user.

### Regression Tests

- Verify that Groq handles the same prompt templates correctly (no hallucinations due to different model instructions).
