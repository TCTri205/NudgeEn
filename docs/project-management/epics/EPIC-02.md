# EPIC-02: Core Messaging Interface

**Focus:** Chat UI, streaming, conversation persistence  
**Status:** Pending (Planned for Sprint 1)  
**Sprint:** Sprint 1: Scalable Gateway  
**Priority:** P0 - Critical Path

---

## Epic Description

Build the core user-facing messaging interface that enables natural conversation between users and their AI friend. This epic delivers the chat bubble UI, real-time typing indicators, message persistence, and SSE streaming that creates the illusion of a responsive, human-like texting experience. It bridges the frontend presentation layer with the backend chat orchestration.

This epic directly implements requirements from the PRD and is the primary user interaction surface for the application.

---

## Business Value

- **User Engagement:** Messenger-like interface encourages prolonged conversation
- **Perceived Responsiveness:** Streaming and typing indicators make AI feel alive
- **Conversation Continuity:** Persistent chat history enables memory and context
- **Platform Foundation:** Core interaction pattern for all future features

---

## Scope

### In Scope

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

### Out of Scope

- ❌ Voice/audio messaging (text-only MVP)
- ❌ Image/file attachments (future enhancement)
- ❌ Video calls or screen sharing
- ❌ Group chats (1:1 with AI only)
- ❌ Rich text formatting (bold, italic, etc.)
- ❌ Message editing or deletion (future feature)
- ❌ Message translation (future enhancement)
- ❌ Custom themes/skins (future enhancement)

---

## Key Requirements

### REQ-UI-01: Messenger Interface

**From:** PRD-v1.md (REQ-001)

- Chat bubble display with distinct styling for user vs AI messages
- Support for emojis (native emoji picker or keyboard input)
- Message reactions via hover/click (heart, thumbs up, etc.)
- Visual distinction between sent and received messages
- Avatar display for AI character
- Timestamps for all messages

### REQ-UI-02: Real-time Typing Indicators

**From:** PRD-v1.md (REQ-001.1)

- Display "..." animation when AI is "typing"
- Simulated human typing delay (1-3s variation)
- Hide indicator when response starts streaming
- Optional: intermittent typing indicators during long responses

### REQ-UI-03: Responsive Design

- Desktop-first layout (>= 768px)
- Mobile browser adaptation (<= 767px)
- Flexible chat bubble sizing
- Safe area handling for mobile browsers
- Keyboard avoidance (input stays visible)

### REQ-UI-04: Conversation Persistence

**From:** PRD-v1.md (Data Schemas)

- Store each message as immutable row in `messages` table
- Link messages to `conversations` (thread metadata)
- Include `user_id`, `conversation_id`, `content`, `role` (user/assistant), `created_at`
- Support for `correction_id` foreign key (for corrected messages)
- Efficient query for message history (pagination)

### REQ-UI-05: Streaming Architecture

**From:** ARCHITECTURE.md (Chat Flow)

- SSE streaming from FastAPI to Next.js frontend
- Token-by-token streaming for "live typing" feel
- Backpressure handling (slow clients)
- Connection recovery on network interruption
- Stream cancellation (user navigates away)

### REQ-UI-06: Message Idempotency

**From:** ARCHITECTURE.md (Reliability)

- Idempotency key per chat send request
- Prevent duplicate messages on retry
- Client-generated UUID for each outbound message
- Server deduplication within time window

### REQ-UI-07: Optimistic Updates

- Show user message immediately (before server ack)
- Show AI typing indicator immediately after send
- Rollback UI if send fails
- Queue messages when offline, send when reconnected

### REQ-UI-08: Performance Requirements

- Time to first message: < 500ms (cached conversation)
- Stream start latency: < 200ms after API processing
- Typing indicator delay: 300-800ms after send
- 60fps scrolling performance (virtualized list for long chats)
- Bundle size: < 200KB for chat components

---

## Technical Design

### Frontend Architecture

```
web/
├── src/
│   ├── app/
│   │   ├── (chat)/
│   │   │   ├── page.tsx              # Chat page
│   │   │   └── layout.tsx            # Chat layout
│   │   ├── conversations/
│   │   │   └── [id]/                 # Specific conversation
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatContainer.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   ├── TypingIndicator.tsx
│   │   │   │   ├── EmojiPicker.tsx
│   │   │   │   └── Reactions.tsx
│   │   │   ├── input/
│   │   │   │   ├── ChatInput.tsx
│   │   │   │   └── SendButton.tsx
│   │   │   └── sidebar/
│   │   │       ├── ConversationList.tsx
│   │   │       └── ConversationItem.tsx
│   │   ├── lib/
│   │   │   ├── api/                  # API clients
│   │   │   ├── hooks/
│   │   │   │   ├── useChat.ts
│   │   │   │   ├── useTyping.ts
│   │   │   │   └── useOptimistic.ts
│   │   │   └── utils/
│   │   │       ├── idempotency.ts
│   │   │       └── streaming.ts
│   │   └── styles/
│   │       └── globals.css
```

### State Management

**Client-side Store (Zustand/Jotai):**
```typescript
interface ChatState {
  messages: Message[]
  conversations: Conversation[]
  activeConversationId: string | null
  pendingMessages: Map<string, PendingMessage>  // idempotency
  typingStatus: TypingStatus
  connectionStatus: 'online' | 'offline' | 'reconnecting'
  
  // Actions
  addMessage: (msg: Message) => void
  updateMessage: (id: string, updates: Partial<Message>) => void
  setTyping: (isTyping: boolean) => void
  sendMessage: (content: string) => Promise<void>
  reconnect: () => void
}
```

### Message Data Model

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

interface Conversation {
  id: string
  userId: string
  title?: string
  lastMessageAt: string
  messageCount: number
  createdAt: string
  updatedAt: string
}
```

### API Endpoints

#### POST /api/chat/send
```typescript
// Request
{
  "conversationId": "uuid",
  "content": "Hello!",
  "idempotencyKey": "client-uuid-123"
}

// Response (SSE Stream)
data: {"type":"message_start","id":"msg-123"}
data: {"type":"content_delta","delta":"H"}
data: {"type":"content_delta","delta":"i"}
data: {"type":"content_delta","delta":"!"}
data: {"type":"message_end","id":"msg-123"}
```

#### GET /api/chat/history?conversationId=uuid&page=1&limit=50
```typescript
// Response
{
  "messages": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 1234,
    "hasNext": true
  }
}
```

### SSE Streaming Implementation

**Backend (FastAPI):**
```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
import json

@app.post("/api/chat/send")
async def send_message(request: Request):
    body = await request.json()
    conversation_id = body["conversationId"]
    content = body["content"]
    idempotency_key = body.get("idempotencyKey")
    
    async def event_stream():
        # Check idempotency
        if await is_duplicate(idempotency_key):
            yield f"data: {json.dumps({'type': 'error', 'message': 'duplicate'})}\n\n"
            return
        
        # Persist user message
        user_msg = await save_user_message(conversation_id, content)
        
        # Run gatekeeper
        if not await gatekeeper.check(content):
            yield f"data: {json.dumps({'type': 'error', 'reason': 'blocked'})}\n\n"
            return
        
        # Stream AI response
        yield f"data: {json.dumps({'type': 'message_start', 'id': 'ai-123'})}\n\n"
        
        async for token in persona_agent.generate(content):
            yield f"data: {json.dumps({'type': 'content_delta', 'delta': token})}\n\n"
        
        yield f"data: {json.dumps({'type': 'message_end', 'id': 'ai-123'})}\n\n"
        
        # Enqueue background jobs
        await enqueue_memory_extraction(user_msg, ai_msg)
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
```

**Frontend (Next.js):**
```typescript
// hooks/useChat.ts
import { useEffect, useRef } from 'react'

export function useChat(conversationId: string) {
  const eventSourceRef = useRef<EventSource | null>(null)
  
  const sendMessage = async (content: string) => {
    const idempotencyKey = crypto.randomUUID()
    
    // Optimistic update
    addMessageOptimistic({
      id: idempotencyKey,
      role: 'user',
      content,
      status: 'sending'
    })
    
    // Create SSE connection
    const es = new EventSource(
      `/api/chat/send?conversationId=${conversationId}`,
      {
        method: 'POST',
        body: JSON.stringify({ content, idempotencyKey }),
        headers: { 'Content-Type': 'application/json' }
      }
    )
    
    es.onmessage = (event) => {
      const data = JSON.parse(event.data)
      switch (data.type) {
        case 'message_start':
          setTyping(true)
          break
        case 'content_delta':
          appendAIMessageContent(data.delta)
          break
        case 'message_end':
          setTyping(false)
          markUserMessageAsSent(idempotencyKey)
          es.close()
          break
      }
    }
    
    es.onerror = () => {
      es.close()
      setTyping(false)
      markUserMessageAsFailed(idempotencyKey)
    }
    
    eventSourceRef.current = es
  }
  
  useEffect(() => {
    return () => eventSourceRef.current?.close()
  }, [])
  
  return { sendMessage }
}
```

### Typing Indicator

**Simulated Human Behavior:**
```typescript
// Simulate realistic typing delays
function simulateTypingDelay(wordCount: number): number {
  const avgWordTime = 200 // ms per word
  const variance = 0.3    // ±30% randomness
  const delay = wordCount * avgWordTime
  return delay * (1 + (Math.random() - 0.5) * 2 * variance)
}

// Show indicator before stream starts
setTimeout(() => setTyping(true), 300)

// Hide when first token arrives
onFirstToken(() => setTyping(false))
```

### Database Schema (PostgreSQL)

```sql
-- Conversations
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255),
  message_count INTEGER DEFAULT 0,
  last_message_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Messages
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  has_correction BOOLEAN DEFAULT false,
  correction_id UUID REFERENCES message_corrections(id),
  reaction JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  idempotency_key VARCHAR(255),
  
  -- Indexes for performance
  INDEX idx_messages_conversation (conversation_id, created_at),
  INDEX idx_messages_idempotency (idempotency_key) WHERE idempotency_key IS NOT NULL
);

-- Idempotency keys table (for deduplication)
CREATE TABLE idempotency_keys (
  key VARCHAR(255) PRIMARY KEY,
  entity_type VARCHAR(50) NOT NULL,
  entity_id UUID NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Acceptance Criteria

### Must Have

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

### Should Have

- [ ] Virtualized message list (performance for long chats)
- [ ] Message read receipts
- [ ] Client-side message queue for offline
- [ ] Smooth typing indicator transitions
- [ ] Keyboard shortcuts (Enter to send, Shift+Enter for new line)

### Could Have

- [ ] Custom message animations
- [ ] Sound effects for new messages (optional)
- [ ] Message search within conversation
- [ ] Star/favorite messages

### Won't Have (This Epic)

- ❌ Voice messages
- ❌ File/image attachments
- ❌ Group chats
- ❌ Rich text formatting
- ❌ Message editing/deletion

---

## Dependencies

### External Dependencies

- **Next.js 14+** - App Router for chat pages
- **React** - UI components
- **TypeScript** - Type safety
- **Zustand/Jotai** - Client state management (TBD)
- **Tailwind CSS** - Styling (via shadcn/ui)
- **shadcn/ui** - UI component library

### Internal Dependencies

- **EPIC-00: Infrastructure & Project Setup** - Must complete first
  - Next.js project skeleton
  - FastAPI project skeleton
  - Database schema setup
- **EPIC-01: Security & Auth** - Parallel development
  - Authentication (chat routes protected)
  - User context propagation

---

## Timeline & Milestones

**Sprint 1: Scalable Gateway** (Target: 2 weeks, parallel with EPIC-01)

| Milestone | Target Date | Deliverable |
|-----------|-------------|-------------|
| M1 | Day 3 | Chat UI components (bubbles, input) |
| M2 | Day 5 | Conversation list/sidebar working |
| M3 | Day 7 | SSE endpoint in FastAPI |
| M4 | Day 8 | Frontend streaming integration |
| M5 | Day 9 | Message persistence working |
| M6 | Day 10 | Typing indicators implemented |
| M7 | Day 11 | Idempotency keys implemented |
| M8 | Day 12 | Optimistic updates working |
| M9 | Day 13 | Responsive design validated |
| M10 | Day 14 | Epic-02 acceptance criteria met |

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| SSE connection issues on mobile | Medium | Medium | Implement WebSocket fallback |
| Memory leak from unclosed EventSources | Medium | Low | Proper cleanup in useEffect |
| Duplicate messages on retry | High | Low | Idempotency keys, server dedup |
| Slow message history loading | Medium | Medium | Pagination, query optimization |
| Typing indicator feels unnatural | Low | Medium | Tune timing parameters |
| Bundle size too large | Medium | Low | Code splitting, lazy loading |

---

## Success Metrics

- **Time to First Message:** < 500ms (cached)
- **Stream Start Latency:** < 200ms
- **Typing Indicator Perception:** > 80% users rate as "natural"
- **Message Delivery Success Rate:** > 99.9%
- **Duplicate Message Rate:** < 0.1%
- **Mobile Responsiveness Score:** > 95 (Lighthouse)
- **User Retention (D1/D7):** > 20% / 10% (PRD target)
- **Average Session Length:** > 10 messages

---

## Out of Scope for This Epic

The following will be addressed in their respective epics:

- **EPIC-00:** Basic project setup, database migration framework, dev environment
- **EPIC-01:** Authentication, OAuth, safety gatekeeper
- **EPIC-03:** AI provider integration, memory extraction, persona engine
- **EPIC-04:** Correction generation (sparkle icon), progress cards
- **EPIC-05:** Production deployment, observability, scaling

---

## References

- [PRD-v1.md](../../PRD-v1.md) - Product requirements (REQ-001, REQ-001.1, REQ-005.2)
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - Architecture, chat flow, PostgreSQL/Redis usage
- [TECHSTACK.md](../../TECHSTACK.md) - Technology choices
- [PRINCIPLES.md](../../PRINCIPLES.md) - Design principles

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-26 | System | Initial version based on project documentation |
