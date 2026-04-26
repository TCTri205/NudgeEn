# TICKET-13: Conversation List & Sidebar

## Metadata

- **Status:** Todo
- **Sprint:** Sprint 1
- **Assignee:** Frontend Lead
- **Domain:** Web UI
- **Priority:** P1 - High
- **Assumptions:**
  - Database is populated with dummy conversations for testing.
- **Affected areas:** `web/components/layout/`, Sidebar Navigation.

## Current State / Existing System

- **Implemented:** Basic Next.js layout (TICKET-02).
- **Missing:** Any way for users to browse high-level chat history or start new conversations.

## Context / Problem

Users will have dozens of ongoing conversations over time. They need a clear way to see their recent chats, the most recent message snippet, and a way to quickly start a "New Chat" with their AI friend.

## Why This Is Needed

- **Business Impact:** Encourages repeat usage and long-term retention.
- **Architectural Impact:** Defines the multi-thread navigation structure of the web app.

## Scope

### In-scope

- Create a `Sidebar` component.
- Implement `ConversationItem` with:
  - Persona name.
  - Last message snippet.
  - Relative time (e.g., "5m ago").
  - Active state highlighting.
- "New Chat" button at the top.
- Responsive design: Sidebar becomes a Drawer on mobile.
- Infinite scroll or "Load More" for historical conversations.

### Out-of-scope

- Search through conversations (future enhancement).
- Deleting conversations from the sidebar (TICKET-22).

## Dependencies / Parallelism

- **Dependencies:** TICKET-02 (Next.js Skeleton).
- **Parallelism:** Can be done in parallel with TICKET-12.

## Rules / Constraints

- Sidebar must be collapsible to maximize chat real estate on small screens.
- Must show unread indicators (if applicable in future).

## What Needs To Be Built

1. `web/components/layout/sidebar.tsx`.
2. `web/components/layout/conversation-item.tsx`.
3. `web/hooks/use-conversations.ts`: Hook for fetching and state management.

## Proposal

Implement a fixed-width sidebar on desktop that persists between pages. Use a shared layout to prevent re-mounting the sidebar when switching conversations, ensuring smooth transitions and no layout shift.

## Implementation Breakdown

1. **Structure:** Define the `Sidebar` layout with a scrollable area for chat history.
2. **Item Design:** Create the `ConversationItem` tile with hover effects.
3. **State:** Track the `activeConversationId` via URL params or global state (Zustand/Context).
4. **Mobile Polish:** Implement the drawer using a portal or `shadcn/ui` sheet component.

## Acceptance Criteria

- [ ] Sidebar displays a list of recent conversations.
- [ ] Clicking a conversation updates the central chat view.
- [ ] "New Chat" button creates a fresh, empty conversation state.
- [ ] Sidebar is correctly hidden on mobile and toggleable via a burger menu.
- [ ] Last message snippet is truncated with an ellipsis.

## Test Cases

### Happy Path

- Select chat 1 -> View content -> Select chat 2 -> View content.
- Click Burger Icon (Mobile) -> Sidebar slides in.

### Failure Path

- No conversations -> Sidebar shows "No chats yet. Start one!" message.

### Regression Tests

- Check that navigating between conversations doesn't reload the entire page.
