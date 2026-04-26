# TICKET-12: Chat Bubble & Message List UI

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 1
- **Assignee:** Frontend Lead
- **Domain:** Web UI
- **Priority:** P0 - Critical
- **Assumptions:**
  - Tailwind CSS is configured (TICKET-02).
  - Message data model includes `id`, `text`, `sender` (user/ai), and `timestamp`.
- **Affected areas:** `web/components/chat/`, Message Rendering.

## Current State / Existing System

- **Implemented:** Next.js skeleton (TICKET-02).
- **Missing:** Any UI components to display a conversation history or individual messages.

## Context / Problem

NudgeEn's heart is the conversation. We need a fluid, high-quality, and mobile-first chat interface that supports long threads of text, handles different message origins (User vs AI), and provides a premium feel.

## Why This Is Needed

- **Business Impact:** Directly affects user engagement and perceived quality of the AI friend.
- **Architectural Impact:** Establishes the reusable component library for all chat-related views.

## Scope

### In-scope

- Create `MessageBubble` component with tailwind-based styling.
- Create `MessageList` container that scrolls to the bottom automatically.
- Implement differentiation:
  - User: Right-aligned, primary color, trailing tail.
  - AI: Left-aligned, secondary/gray color, leading tail.
- Basic markdown rendering support (bold, italics, lists).
- Loading/Skeleton states for initial message fetch.

### Out-of-scope

- Image/File attachments (future enhancement).
- Context menus for messages (copy, delete).

## Dependencies / Parallelism

- **Dependencies:** TICKET-02 (Next.js Skeleton).
- **Parallelism:** Can be done in parallel with Backend development (TICKET-14, 16).

## Rules / Constraints

- Must be responsive and accessible (ARIA roles for chat).
- Animations should be subtle (e.g., messages sliding in).
- Avoid excessive re-renders in `MessageList`.

## What Needs To Be Built

1. `web/components/chat/message-bubble.tsx`.
2. `web/components/chat/message-list.tsx`.
3. `web/lib/utils/scroll.ts`: Helpers for bottom-scrolling.

## Proposal

Use a mapping approach for message sender colors. User messages should use the brand's primary gradient. AI messages should use a soft, neutral glassmorphic background to emphasize the "non-human" but friendly nature of the AI.

## Implementation Breakdown

1. **Atoms:** Build the `MessageBubble` with variants for "user" and "ai".
2. **Molecule:** Build `MessageList` using `MessageBubble` and a simple `map()` on message data.
3. **Behavior:** Implement the `useEffect` hook to scroll to bottom when the message array length changes.
4. **Validation:** Manually verify layout on mobile (375px) vs desktop (1440px).

## Acceptance Criteria

- [ ] User and AI messages are visually distinct and correctly aligned.
- [ ] The conversation automatically scrolls to the bottom when a new message is added.
- [ ] Long messages wrap correctly without breaking the layout.
- [ ] Links and simple markdown items are clickable/rendered.
- [ ] Performance remains fluid with 100+ messages in the list.

## Test Cases

### Happy Path

- Add message -> Appears at bottom -> Scroll happens.
- Switch to mobile view -> Bubbles resize appropriately.

### Failure Path

- Empty message list -> "Start a conversation" empty state shown.
- Message with 2000+ words -> Scroll performance remains stable.

### Regression Tests

- Ensure clicking a button doesn't reset the scroll position.
