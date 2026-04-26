# TICKET-15: SSE Client-side Consumption

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 1
- **Assignee:** Frontend Lead
- **Domain:** Web Application / Streaming
- **Priority:** P0 - Critical
- **Assumptions:**
  - Frontend TICKET-02 and Backend TICKET-14 (SSE) are functional or specified.
- **Affected areas:** `web/hooks/use-chat.ts`, UI streaming state.

## Current State / Existing System

- **Implemented:** Basic Next.js setup (TICKET-02).
- **Missing:** Any logic to handle Server-Sent Events (SSE) or update the UI iteratively as AI tokens arrive.

## Context / Problem

Standard HTTP request-response patterns feel slow for AI chat. Users expect the "streaming" experience where words appear as they are generated. We need a robust client-side implementation to handle these streams reliably.

## Why This Is Needed

- **Business Impact:** Provides the "Wow" factor of real-time AI and significantly reduces perceived latency.
- **Architectural Impact:** Introduces event-driven state management to the frontend.

## Scope

### In-scope

- Implement a `useChat` custom hook.
- Logic to connect to `/api/chat/stream` using `fetch` + `ReadableStream`.
- Internal state management to collect and append tokens to the active message.
- Error handling for network drops or backend timeouts.
- "Stop Generation" functionality to abort the stream.

### Out-of-scope

- WebSocket support (SSE only for MVP).

## Dependencies / Parallelism

- **Dependencies:** TICKET-12 (Message List UI), TICKET-14 (Backend SSE).
- **Parallelism:** Can be implemented concurrently with Backend SSE logic.

## Rules / Constraints

- Must handle UTF-8 partial token chunks correctly.
- Must not crash the browser tab on long streams.
- State updates must be batched to avoid excessive UI flickers.

## What Needs To Be Built

1. `web/hooks/use-chat.ts`: The core hook.
2. `web/lib/streaming/parser.ts`: Utility for parsing SSE data chunks.
3. UI Update logic in `MessageList`.

## Proposal

Use the `fetch` API directly rather than `EventSource` to allow for POST requests and custom headers (e.g., Authorization). Process the response body using a reader that pushes chunks into a reactive state array.

## Implementation Breakdown

1. **Hook Structure:** Define `isLoading`, `messages`, and `sendMessage`.
2. **Streaming Logic:** Implement the `while(true)` reader loop for the response body.
3. **Abortion:** Setup `AbortController` to handle manual user stops.
4. **Validation:** Stream a long text (e.g., a poem) and verify it appears word-by-word.

## Acceptance Criteria

- [ ] AI tokens appear in the `MessageBubble` in real-time as they are received.
- [ ] The "Stop" button successfully kills the incoming stream.
- [ ] Network errors are caught and show a "Retry" or "Error" state in the chat.
- [ ] Final message state is properly finalized once the "DONE" signal is received.

## Test Cases

### Happy Path

- Send message -> AI starts typing -> Full message completes.
- Click Stop mid-stream -> Stream stops instantly.

### Failure Path

- Browser loses internet mid-stream -> UI shows disconnection error.
- Server returns 500 mid-stream -> Hook catches error and notifies user.

### Regression Tests

- Ensure multiple streams don't overlap if triggered rapidly.
