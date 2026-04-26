# TICKET-17: Typing Indicator UX

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 1
- **Assignee:** Frontend Lead
- **Domain:** UX / UI
- **Priority:** P1 - High
- **Assumptions:**
  - `useChat` hook (TICKET-15) is in place.
- **Affected areas:** `web/components/chat/`, User Experience flow.

## Current State / Existing System

- **Implemented:** Basic chat bubbles (TICKET-12).
- **Missing:** Any visual sign that the AI is "thinking" or processing before the stream starts.

## Context / Problem

There's often a 200ms-1s delay between a user sending a message and the first token arriving. An immediate "Typing..." state or animation makes the AI feel more human-like and responsive, reducing user anxiety about whether the message was sent.

## Why This Is Needed

- **Business Impact:** Higher perceived responsiveness and "personality" for the AI character.
- **Architectural Impact:** Lightweight UI state addition.

## Scope

### In-scope

- Create a `TypingIndicator` component (3 animated dots).
- Logic to show the indicator the moment a user hits "Send".
- Logic to hide the indicator once the first chunk of data arrives in the stream.
- Add subtle, randomized "latency" to the indicator appearance for a more organic feel.

### Out-of-scope

- "User is typing" indicator for other users (this is a single-user app).

## Dependencies / Parallelism

- **Dependencies:** TICKET-12 (Chat Bubbles), TICKET-15 (Streaming).
- **Parallelism:** Can be done once the basic chat flow is functional.

## Rules / Constraints

- The animation must be buttery smooth (60fps).
- Must not appear if the message processing is near-instant (<50ms).

## What Needs To Be Built

1. `web/components/chat/typing-indicator.tsx`.
2. Logic update in `MessageList` to conditionally render the indicator at the end of the array.

## Proposal

Use a framer-motion or CSS keyframe animation for three dots with staggered delays. Mount the component at the bottom of the message list whenever the `isAiThinking` state is true.

## Implementation Breakdown

1. **Component:** Build the dots with a subtle bounce or pulse.
2. **State Hook:** Add `isThinking` to the `useChat` hook state.
3. **Orchestration:** Trigger `isThinking=true` on emit, `isThinking=false` on first stream chunk.
4. **Validation:** Visually confirm the transition from dots to words is seamless.

## Acceptance Criteria

- [ ] Three dots appear at the bottom of the chat immediately after user input.
- [ ] Dots disappear and are replaced by the first word of the AI response.
- [ ] Animation is clean and visually fits the NudgeEn theme.

## Test Cases

### Happy Path

- Send message -> Dots appear for 500ms -> Tokens start.

### Failure Path

- API error -> Dots disappear and an error message is shown instead.

### Regression Tests

- Ensure dots aren't "stuck" if the stream fails to start.
