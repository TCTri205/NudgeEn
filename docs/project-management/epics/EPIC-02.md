# EPIC-02: Core Messaging Interface

- **Status:** Pending (Planned for Sprint 1)
- **Priority:** P0 - Critical Path
- **Source requirement:** PRD-v1.md (REQ-001, REQ-001.1, REQ-005.2)
- **Impacted domains:** Chat, Frontend, Backend API

---

## Summary

Build the core user-facing messaging interface that enables natural conversation between users and their AI friend. This epic delivers the chat bubble UI, real-time typing indicators, message persistence, and SSE streaming that creates the illusion of a responsive, human-like texting experience. It bridges the frontend presentation layer with the backend chat orchestration. This epic directly implements requirements from the PRD and is the primary user interaction surface for the application.

---

## Current State / Gap

- **Implemented:** Infrastructure (EPIC-00) and authentication (EPIC-01) foundations.
- **Missing:** Chat bubble UI components, typing indicators, conversation list, SSE streaming endpoint, message persistence logic, idempotency handling, optimistic updates, responsive design for mobile.

---

## Problem / Opportunity

Without a polished messaging interface, users cannot interact with the AI friend. A poor chat experience (slow, non-responsive, breaks on mobile) will cause immediate user churn. The messaging interface is the primary product interaction — it must feel responsive, reliable, and delightful to use. Building this after AI integration would mean retrofitting the UI around backend constraints rather than designing for optimal user experience.

---

## Desired Outcome

After this epic is complete:
- Users can send and receive messages in a messenger-like chat interface
- AI responses stream in real-time with typing indicators
- Conversation history persists and loads on demand
- The interface works on desktop and mobile browsers
- Messages are deduplicated (idempotency) even on network retries
- The UI feels responsive with optimistic updates

This outcome matters because the chat interface is the product — if it doesn't feel smooth and reliable, users won't engage regardless of AI quality.

---

## Users / Use Cases

- **Primary users:** End users (chatting with AI), Development team (chat infrastructure)
- **Main use cases:**
  - User sends a message and receives streaming AI response
  - User views conversation history
  - User switches between conversations
  - User reacts to messages (emoji)
  - User copies message text
  - User sees typing indicator while AI is "thinking"
- **Important edge cases:**
  - Network disconnection during message send
  - Duplicate message prevention on retry
  - Long conversation history (pagination)
  - Mobile keyboard covering input field

---

## Scope

### In scope

- ✅ Messenger-like chat bubble UI with responsive design
- ✅ Support for emojis in messages
- ✅ Message reactions (like 👍, ❤️, etc.)
- ✅ Real-time typing indicators (simulated human activity)
- ✅ Responsive design: desktop first, mobile browser second
- ✅ Conversation list/sidebar
- ✅ Message persistence in PostgreSQL
- ✅ SSE (Server-Sent Events) streaming for AI responses
- ✅ WebSocket fallback capability (optional)
- ✅ Message idempotency (prevent duplicate sends)
- ✅ Client-side message queue for offline support
- ✅ Message read receipts (delivered/seen status)
- ✅ Auto-scroll to new messages
- ✅ Message history pagination/load more
- ✅ Copy message functionality
- ✅ Timestamp display (relative: "2m ago", absolute on hover)
- ✅ Online/offline status indicators
- ✅ Connection state management (reconnect logic)
- ✅ Optimistic UI updates (show message before server ack)

### Out of scope

- ❌ Voice/audio messaging (text-only MVP)
- ❌ Image/file attachments (future enhancement)
- ❌ Video calls or screen sharing
- ❌ Group chats (1:1 with AI only)
- ❌ Rich text formatting (bold, italic, etc.)
- ❌ Message editing or deletion (future feature)
- ❌ Message translation (future enhancement)
- ❌ Custom themes/skins (future enhancement)

---

## Capability Slices

- **Slice 1: Chat UI Components** — Message bubbles, input field, send button, emoji picker
- **Slice 2: Conversation Management** — Conversation list, sidebar, switching conversations
- **Slice 3: Streaming Infrastructure** — SSE endpoint, token-by-token streaming, backpressure handling
- **Slice 4: Message Persistence** — PostgreSQL schema, repository layer, query optimization
- **Slice 5: Reliability Features** — Idempotency keys, optimistic updates, connection recovery
- **Slice 6: Responsive Design** — Mobile adaptation, keyboard handling, touch interactions

---

## Facts / Assumptions / Constraints / Unknowns

- **Facts:**
  - Next.js 14+ with App Router is the frontend framework
  - FastAPI is the backend framework
  - PostgreSQL stores messages (immutable rows)
  - SSE is the primary streaming protocol
  - Messages are immutable once created
- **Assumptions:**
  - Users have modern browsers (SSE support)
  - Desktop is the primary use case (mobile browser is secondary)
  - Average conversation length: 50-200 messages
- **Constraints:**
  - Time to first message: < 500ms (cached conversation)
  - Stream start latency: < 200ms after API processing
  - 60fps scrolling performance (virtualized list for long chats)
  - Bundle size: < 200KB for chat components
  - Rate limit: 50 messages/24hrs per user (enforced at API layer)
- **Unknowns:**
  - State management library choice (Zustand vs Jotai vs Context)
  - Exact component library (shadcn/ui vs custom)

---

## Proposed Solution

**Frontend Architecture:**
```
web/src/app/
├── (chat)/
│   ├── page.tsx              # Chat page
│   └── layout.tsx
├── conversations/[id]/       # Specific conversation
├── components/chat/
│   ├── ChatContainer.tsx
│   ├── MessageList.tsx
│   ├── MessageBubble.tsx
│   ├── TypingIndicator.tsx
│   └── EmojiPicker.tsx
├── lib/api/                  # API clients
└── hooks/
    ├── useChat.ts
    ├── useTyping.ts
    └── useOptimistic.ts
```

**SSE Streaming Implementation:**
- Backend: FastAPI `StreamingResponse` with `text/event-stream`
- Frontend: EventSource API with automatic reconnection
- Token-by-token streaming for "live typing" feel
- Backpressure handling for slow clients

**Message Data Model:**
```typescript
interface Message {
  id: string              // UUID
  conversationId: string
  role: 'user' | 'assistant'
  content: string
  hasCorrection?: boolean
  correctionId?: string
  reaction?: string[]
  createdAt: string       // ISO-8601
  status: 'sending' | 'sent' | 'delivered' | 'failed'
  idempotencyKey?: string // Client-generated dedupe key
}
```

**Idempotency Pattern:**
- Client generates UUID for each outbound message
- Server deduplicates within time window using `idempotency_keys` table
- Returns existing message if duplicate detected

**Key tradeoffs:**
- Chose SSE over WebSocket (simpler, sufficient for one-way streaming)
- Chose optimistic updates (better UX) with rollback on failure
- Chose immutable messages (simpler concurrency, enables correction tracking)

---

## Dependencies / Rollout / Risks

### Dependencies

- **External:**
  - Next.js 14+ — App Router for chat pages
  - React — UI components
  - TypeScript — Type safety
  - Zustand/Jotai — Client state management (TBD)
  - Tailwind CSS — Styling (via shadcn/ui)
  - shadcn/ui — UI component library

- **Internal:**
  - **EPIC-00: Infrastructure & Project Setup** — Must complete first
    - Next.js project skeleton
    - FastAPI project skeleton
    - Database schema setup
  - **EPIC-01: Security & Auth** — Parallel development
    - Authentication (chat routes protected)
    - User context propagation

### Rollout notes

- Chat UI should be tested with real users for responsiveness perception
- SSE connections need monitoring for resource usage
- Idempotency keys should have TTL (24 hours)

### Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| SSE connection issues on mobile | Medium | Medium | Implement WebSocket fallback |
| Memory leak from unclosed EventSources | Medium | Low | Proper cleanup in useEffect |
| Duplicate messages on retry | High | Low | Idempotency keys, server dedup |
| Slow message history loading | Medium | Medium | Pagination, query optimization |
| Typing indicator feels unnatural | Low | Medium | Tune timing parameters |
| Bundle size too large | Medium | Low | Code splitting, lazy loading |

---

## Epic Done Criteria

- [ ] Chat bubble UI with user/AI differentiation
- [ ] Emoji support (native input/display)
- [ ] Message reactions (at least 3 emoji options)
- [ ] Typing indicator animation
- [ ] SSE streaming from FastAPI to Next.js
- [ ] Message persistence in PostgreSQL
- [ ] Idempotency keys working
- [ ] Optimistic UI updates
- [ ] Auto-scroll to new messages
- [ ] Responsive design (desktop + mobile browser)
- [ ] Copy message button
- [ ] Relative timestamps with hover for absolute
- [ ] Conversation list/sidebar
- [ ] Online/offline status indicator
- [ ] Connection recovery on network loss
- [ ] Message history pagination (50 per page)

---

## Task Writer Handoff

- **Epic slug:** EPIC-02
- **Epic file path:** `docs/project-management/epics/EPIC-02.md`
- **Original requirement:** PRD-v1.md (REQ-001, REQ-001.1, REQ-005.2)
- **Epic summary:** Core messaging interface with chat UI, streaming, and persistence
- **Impacted domains:** Chat, Frontend, Backend API
- **Desired outcome:** Users can chat with AI in a responsive, messenger-like interface
- **In-scope outcomes:** Chat UI, SSE streaming, message persistence, idempotency, responsive design
- **Non-goals:** Voice messages, file attachments, group chats, rich text formatting
- **Capability slices:** 6 slices (UI components, conversations, streaming, persistence, reliability, responsive)
- **Facts:** Next.js 14+, FastAPI, PostgreSQL, SSE streaming, immutable messages
- **Assumptions:** Desktop primary, mobile secondary, modern browsers
- **Constraints:** <500ms first message, <200ms stream start, 60fps scroll, <200KB bundle
- **Unknowns:** State management library, component library choice
- **Proposed solution summary:** Next.js chat UI with SSE streaming, optimistic updates, idempotency keys
- **Dependencies:** EPIC-00 (infrastructure), EPIC-01 (auth — parallel)
- **Rollout notes:** Test with real users, monitor SSE connections, idempotency TTL
- **Risks:** SSE mobile issues, memory leaks, duplicates, slow history loading
- **Task splitting hints:** Split by slice (UI → conversations → streaming → persistence → reliability → responsive)
- **Validation expectations:** All criteria testable with binary pass/fail, performance metrics measurable

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-26 | System | Initial version based on project documentation |
| 2.0 | 2026-04-27 | Assistant | Standardized to epic-template.md format |
