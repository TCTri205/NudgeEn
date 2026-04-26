# TICKET-14: SSE Streaming Implementation (Back-end)

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 1
- **Assignee:** Backend Lead
- **Domain:** API / Streaming
- **Priority:** P0 - Critical
- **Assumptions:**
  - FastAPI skeleton is ready (TICKET-01).
  - LLM provider supports streaming responses (async).
- **Affected areas:** `api/app/modules/chat/router.py`, Streaming Service.

## Current State / Existing System

- **Implemented:** FastAPI base with health checks (TICKET-01).
- **Missing:** Any support for long-running HTTP connections or streaming token responses.

## Context / Problem

For an AI friend to feel responsive, the user should see characters as they are generated. Standard JSON responses wait for the entire text to be complete, which can take several seconds. Server-Sent Events (SSE) provide a lightweight, unidirectional stream for real-time token delivery.

## Why This Is Needed

- **Business Impact:** Drastically reduces Time-To-First-Token (TTFT), leading to a much smoother user experience.
- **Architectural Impact:** Shifts from a request-response model to an event-stream model for chat endpoints.

## Scope

### In-scope

- Implement `POST /api/chat/stream` using FastAPI's `StreamingResponse`.
- Implement a generator function that yields tokens in the `data: token \n\n` format.
- Handle metadata events (e.g., `event: metadata` for message IDs).
- Detect client-side disconnects to stop LLM generation and save resources.
- Support CORS for streaming headers.

### Out-of-scope

- WebSockets (SSE only).

## Dependencies / Parallelism

- **Dependencies:** TICKET-01 (FastAPI Skeleton).
- **Parallelism:** Can be done in parallel with TICKET-15 (Frontend Consumption).

## Rules / Constraints

- Must use `application/x-ndjson` or `text/event-stream` content types.
- Ensure proper error handling within the generator so connection isn't dropped silently.
- Logging should capture the completion status of the stream.

## What Needs To Be Built

1. `api/app/modules/chat/router.py`: Endpoint for streaming.
2. `api/app/modules/chat/service.py`: Generator logic that interfaces with the AI provider.
3. Utility for formatting SSE messages.

## Proposal

Use an `AsyncGenerator` to yield objects. Wrap the generator in a `StreamingResponse`. Use a specialized separator string or JSON format for chunks to ensure the frontend can parse them easily even if multiple chunks arrive in a single packet.

## Implementation Breakdown

1. **Generator Pattern:** Implement the async generator that calls the LLM.
2. **Endpoint Hookup:** Create the FastAPI route that returns the generator.
3. **Middleware/Headers:** Ensure the response headers prevent proxy buffering.
4. **Validation:** Use `curl -N` to verify that tokens appear line-by-line in the terminal.

## Acceptance Criteria

- [ ] Endpoint successfully streams data to a client without waiting for completion.
- [ ] Tokens are correctly formatted according to the SSE protocol.
- [ ] Stopping the request from the client stops the LLM generation on the server.
- [ ] Final "DONE" signal is sent once the LLM finishes.

## Test Cases

### Happy Path

- Call endpoint -> Tokens arrive instantly -> "DONE" received.

### Failure Path

- LLM provider error -> Stream sends an error event and closes.
- Network interruption -> Server cleans up the generator resource.

### Regression Tests

- Verify that streaming doesn't block other concurrent API requests.
