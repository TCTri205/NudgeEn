# TICKET-56: Final UX Polish & Beta Feedback Loop

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 5
- **Assignee:** Frontend Lead
- **Domain:** UX / UI
- **Priority:** P2 - Medium
- **Assumptions:**
  - Fundamental UI components are in place (EPIC-02).
- **Affected areas:** All frontend pages, Global styles.

## Current State / Existing System

- **Implemented:** Functional UI (TICKET-12, TICKET-13).
- **Missing:** The "Premium" feel. Sharp edges, lack of transitions, and missing feedback mechanisms make the app feel like a prototype rather than a product.

## Context / Problem

In the final stretch before Beta, we need to focus on "Micro-interactions" (hover effects, loading states) and a way for beta testers to voice their opinions. This is the difference between a "good" app and a "lovable" app.

## Why This Is Needed

- **Business Impact:** Increases user retention and better qualitative data from beta testers.
- **Architectural Impact:** Final polish of the UI design system.

## Scope

### In-scope

- **UI Polish:**
  - Harmonize spacing (padding/margins) using a strict 8px grid.
  - Refine typography (Inter/Outfit fonts) across all views.
  - Add Framer Motion transitions between chat messages.
  - Dark mode refinement (ensure all colors are accessible).
- **Feedback Loop:**
  - "Bug / Feedback" persistent button in the Sidebar.
  - Simple modal to capture text feedback + user screenshot (optional).
  - Store feedback in a `user_feedback` table.

### Out-of-scope

- Major layout changes or new features.

## Dependencies / Parallelism

- **Dependencies:** EPIC-02 (Frontend).
- **Parallelism:** Can be done while the Backend team is hardening infrastructure.

## Rules / Constraints

- No more than 3 distinct primary colors in the UI.
- All interactive elements must have a visual "Active/Pressed" state.

## What Needs To Be Built

1. `web/components/layout/feedback-trigger.tsx`.
2. `web/components/animations/message-entry.tsx`.
3. `api/app/modules/user/feedback_router.py`.

## Proposal

Use "Glassmorphism" for the sidebar to give a modern feel. Use `lucide-react` for consistent, thin-line icons. For the feedback loop, integrate a simple form that sends the data to a Discord Webhook *and* the DB for easy visibility.

## Implementation Breakdown

1. **Design Sweep:** Check every component against the `task-template.md` premium design rules.
2. **Animations:** Subtle "slide up" entry for new messages.
3. **Feedback UI:** Build the simple submission form.
4. **Validation:** Ask a non-developer to use the app and rate the "Feel" out of 10.

## Acceptance Criteria

- [ ] UI is visually consistent across all screens.
- [ ] Feedback button is visible but non-intrusive.
- [ ] Success feedback (Toast) after submitting feedback.
- [ ] No layout shifts during message streaming.

## Test Cases

### Happy Path

- Open app -> Everything looks sleek -> Send feedback -> Toast confirms.

### Failure Path

- Feedback submission fails -> User is informed and text is preserved (not lost).

### Regression Tests

- Check mobile responsiveness one final time (no horizontal scrolling).
