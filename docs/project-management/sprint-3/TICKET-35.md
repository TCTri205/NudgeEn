# TICKET-35: Correction Details Modal (Original/Improved/Explanation)

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 3
- **Assignee:** Frontend Lead
- **Domain:** Web UI / Pedagogy
- **Priority:** P1 - High
- **Assumptions:**
  - Correction data (obj) is passed to the component.
- **Affected areas:** `web/components/chat/modals/`, Correction Flow.

## Current State / Existing System

- **Implemented:** None.
- **Missing:** The interactive UI to actually teach the user the grammar rule they broke.

## Context / Problem

Once a user clicks the ✨ icon, they need a clear, educational side-by-side comparison of their mistake and the corrected version, along with a "why". This information should be presented as a focused "moment of learning" that is easy to digest.

## Why This Is Needed

- **Business Impact:** Directly responsible for the "English Learning" value.
- **Architectural Impact:** Defines the standard modal/overlay pattern for all future learning widgets.

## Scope

### In-scope

- Implement `CorrectionModal` using `shadcn/ui` Dialog.
- Three specific sections:
  - **Original:** Styled with red background/strikethrough.
  - **Improved:** Styled with green highlight/bold.
  - **Explanation:** 1-2 sentences of friendly context.
- "Copy Improved" button for quick usage.
- "Helpful / Not Helpful" feedback buttons (TICKET-41 placeholder).
- Close on backdrop click or ESC.

### Out-of-scope

- Interactive grammar exercises inside the modal.

## Dependencies / Parallelism

- **Dependencies:** TICKET-32 (Structured Output), TICKET-34 (Sparkle Icon).
- **Parallelism:** Can be done after the Sparkle Icon is positioned.

## Rules / Constraints

- Must be mobile-friendly (Drawer on mobile, Dialog on desktop).
- No more than 300 words of text total to avoid overwhelming the user.

## What Needs To Be Built

1. `web/components/chat/modals/correction-modal.tsx`.
2. `web/hooks/use-correction-modal.ts`: Hook to manage modal state and active correction data.

## Proposal

Use a "Compare" card layout where the original and improved versions are clearly labeled. Use a soft color palette (amber/gold) for the header to maintain the "Sidekick" vibe rather than a "Strict Teacher" vibe.

## Implementation Breakdown

1. **Structure:** Setup the shadcn/ui Dialog wrapper.
2. **Content:** Map the `Correction` object fields to the UI sections.
3. **Behavior:** Connect the "Copy" button to `navigator.clipboard`.
4. **Validation:** Sanity check the reading level of dummy explanations (A2-B1 levels).

## Acceptance Criteria

- [ ] Modal displays the correct data for the specific message clicked.
- [ ] "Original" and "Improved" text are easily distinguishable at a glance.
- [ ] "Copy Improved" successfully puts text in the user's clipboard.
- [ ] Modal animations are smooth and don't lag.

## Test Cases

### Happy Path

- Click ✨ -> Modal opens -> See error -> Click Copy -> Close.

### Failure Path

- Data is missing for one field (e.g., no explanation) -> UI renders a placeholder or omits the section gracefully.

### Regression Tests

- Verify modal doesn't open "underneath" the chat sidebar.
