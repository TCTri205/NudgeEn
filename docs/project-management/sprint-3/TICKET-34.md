# TICKET-34: Sparkle Icon (✨) UX Overlay

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 3
- **Assignee:** Frontend Lead
- **Domain:** Web UI / UX
- **Priority:** P1 - High
- **Assumptions:**
  - Message data structure includes a `has_correction` boolean or `correction_id` link.
- **Affected areas:** `web/components/chat/message-bubble.tsx`, UI components.

## Current State / Existing System

- **Implemented:** Basic chat bubbles for User and AI (TICKET-12).
- **Missing:** Any visual indicator that the AI has detected an English error in the user's previous message.

## Context / Problem

NudgeEn's philosophy is "Sidekick Pedagogy"—corrections should be persistent but non-intrusive. A small "Sparkle" icon (✨) attached to a user's message bubble is the perfect signal: it's visible if the user wants to see it, but doesn't interrupt the conversation flow.

## Why This Is Needed

- **Business Impact:** The core pedagogical hook. It transforms a simple chat into a learning session.
- **Architectural Impact:** Adds conditional overlays and meta-data icons to the message rendering pipeline.

## Scope

### In-scope

- Create `CorrectionBadge` or `SparkleIcon` component using Tailwind.
- Logic in `MessageList` to detect if a message has an associated correction.
- Positioning: Place the icon at the top-left or top-right of the User's message bubble.
- Add a subtle "pulse" animation when a new correction first appears.
- Tooltip integration: Show "View correction" on hover.

### Out-of-scope

- Inline highlighting of specific words (icon-based only for now).

## Dependencies / Parallelism

- **Dependencies:** TICKET-12 (Chat Bubbles), TICKET-32 (Structured Output Parser).
- **Parallelism:** Can be done in parallel with TICKET-35 (Modal).

## Rules / Constraints

- The icon must be small (e.g., 16x16px) and high-contrast (amber-500).
- Must not shift the message bubble's layout when appearing (use absolute positioning).

## What Needs To Be Built

1. `web/components/chat/correction-badge.tsx`.
2. Update `web/components/chat/message-bubble.tsx` to include the badge.

## Proposal

Use `lucide-react` Sparkles icon. Wrap the badge in a button that, when clicked, triggers the `onOpenCorrection(id)` callback. Use a Framer Motion `AnimatePresence` for the pulse effect.

## Implementation Breakdown

1. **Atoms:** Build the badge component with hover states.
2. **Integration:** Update the `Message` type and bubble component to render the badge conditionally.
3. **Behavior:** Link the click event to a dummy console log (until TICKET-35 is ready).
4. **Validation:** Check that the icon looks good on both light and dark backgrounds.

## Acceptance Criteria

- [ ] Sparkle icon appears ONLY on user messages where the AI generated a correction.
- [ ] Clicking the icon triggers a specific action (e.g., opening a future modal).
- [ ] The icon is correctly positioned and responsive on mobile devices.
- [ ] Tooltip appears on desktop hover.

## Test Cases

### Happy Path

- Message with correction -> ✨ appears instantly.
- Message without correction -> No icon appears.

### Failure Path

- Correction data is null -> Component handles it gracefully without rendering a broken icon.

### Regression Tests

- Ensure clicking the icon doesn't trigger the bubble's own "Copy Text" logic (if any).
