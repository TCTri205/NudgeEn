# NudgeEn - AI Messaging Friend for English Practice (v1.0-Draft)

## 1. Project Inspiration

Creating an AI "texting friend" to help practice real-world reading/writing skills in a casual, low-pressure environment. Instead of rote grammar lessons, it provides a natural communication space to maintain user motivation.

## 2. Market Analysis

- **Traditional Platforms (Duolingo, Memrise):** Primarily offer roleplay with fixed scenarios. They can feel rigid and lack the personal connection of a real friend.
- **Dedicated Chatbots (Andy English):** Often feel like a series of exercises in a chat UI rather than natural conversation.
- **General AI (Character.ai, ChatGPT, Pi):**
  - *Character.ai:* Great for roleplay but lacks pedagogical features such as vocabulary tracking and subtle corrections.
  - *ChatGPT:* Helpful but often too assistant-like, missing the vibe of a casual friend.
- **Language Exchange (Tandem, HelloTalk):** Higher psychological pressure, slower response times, and social risk.
- **The Gap:** A hybrid solution that combines natural chat personality with explicit learning value.

## 3. Product Requirements Document (MVP)

### 3.1. Overview & Goals

- **Objective:** Build an AI chatbot that acts as a real friend in a messaging interface to improve daily English reading and writing.
- **Scope:** Text-only conversation. Voice/audio is out of scope for MVP.

### 3.2. Target Persona

- **Age:** 18-30
- **Profile:** Has basic grammar knowledge but struggles with fluency, typing speed, and natural vocabulary.
- **Behavior:** Comfortable with social apps, avoids high-pressure learning experiences.

### 3.3. Key Features (Functional Requirements)

#### [Group: User Experience]

- **[REQ-001] Messenger-like Interface**
  - Chat bubble display with support for emojis and reactions.
  - Real-time typing indicators.
  - Responsive design for desktop web first, mobile browser second.
- **[REQ-002] Persona Customization**
  - Users choose a vibe: Sarcastic/Banter, Gentle/Empathetic, or Tech-savvy.
- **[REQ-003] Dual-Channel Correction (Separate Flow)**
  - **Immersion Channel:** Primary chat interface focused on conversation. No automatic interruptions for corrections.
  - **Shadow Channel:** AI identifies errors in background.
  - **UI Trigger:** A subtle **Sparkle icon** appears next to messages with better alternatives, but viewing is optional.
  - **Recap Space:** A dedicated area (or recurring automated message) summarizing key learning points without cluttering the chat history.

#### [Group: Intelligence & Memory]

- **[REQ-004] Contextual Memory (User Profile)**
  - The system extracts key facts such as name, hobbies, and goals into a persistent user profile.
  - Past conversations are referenced naturally.
- **[REQ-005] Initial Calibration (Onboarding)**
  - A 3-turn interactive vibe check:
    1. Introduction and name
    2. Interest inquiry
    3. Short roleplay snippet for level assessment
- **[REQ-006] Weekly Vibe Check**
  - Automated summary of progress delivered as an in-chat card.
  - Highlights: most used new words, grammar improvement trend.
  - Triggered on the first user message after 7 days since the last summary.
- **[REQ-014] Bridge to Reality (Scenario Import)**
  - Users can input or upload a real-world context (text from email/Slack).
  - AI switches to "Simulation Mode" to help user practice.
- **[REQ-015] Emotional Bonding & Lore**
  - AI Persona has a background "Lore" and persistent mood states.
  - Progression system (UserGraph) unlocks deeper conversation topics over time.
- **[REQ-016] Adaptive Re-entry (Anti-Ghosting)**
  - If user is inactive > 48h, the next notification is a "Life Update" from AI, not a learning reminder.

#### [Group: Infrastructure & Security]

- **[REQ-007] Authentication**
  - Auth.js with OAuth2 (Google/GitHub) and Credentials (Email/Password).
- **[REQ-008] Safety Gatekeeper**
  - Lightweight prompt evaluating input/output for safety and scope.
  - Runs sequentially before the Persona Agent.
  - If triggered, replies gracefully and logs the attempt for monitoring.

### 3.4. Technical Architecture & Data Schemas

#### [Architecture & Deployment]

1. **Frontend:** **Next.js Web** on **Vercel**, acting as UI, auth boundary, and thin BFF.
2. **Backend:** **FastAPI API** on **Render / Railway / Fly**, optimized for chat orchestration and SSE streaming.
3. **Primary Database:** **PostgreSQL** as the system of record.
4. **Cache / Broker:** **Redis** for rate limiting, caching, and queue transport.
5. **Background Processing:** **Taskiq Workers** for memory extraction, weekly summaries, and analytics jobs.
6. **Logic Flow:**
   - User Message -> Next.js Web -> FastAPI API
   - Gatekeeper Agent -> Persona Agent
   - API persists the interaction and streams the response
   - API enqueues background jobs after commit
   - Workers update profile, memory facts, and derived progress data

#### [Data Schemas]

- **User Profile JSON Projection:**

```json
{
  "user_id": "string",
  "name": "string",
  "english_level": "A1-C2",
  "vibe_preference": "gentle",
  "onboarding_completed": true,
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601",
  "weekly_check_last_sent": "ISO-8601",
  "extracted_memories": [
    { "topic": "hobby", "detail": "loves hiking", "timestamp": "ISO-8601" }
  ],
  "stats": { "messages_sent": 0, "corrections_viewed": 0 }
}
```

- **AI Structured Output:**

```json
{
  "reply": "Hey! That sounds cool. Where did you hike?",
  "correction": {
    "has_correction": true,
    "original": "I go hike yesterday",
    "improved": "I went hiking yesterday",
    "explanation": "Past tense 'went' + 'hiking' for activities."
  }
}
```

### 3.5. Operational Constraints & Non-Functional Requirements

- **[REQ-009] Feasibility & Cost**
  - Primary: **Gemini 2.5 Flash**
  - Fallback: **Groq API**
- **[REQ-010] Rate Limiting**
  - MVP limit: **50 messages per 24 hours** per user.
- **[REQ-011] Fallback Strategy**
  - If model calls fail or time out, show a graceful fallback message.
- **[REQ-012] Scalability & Storage**
  - Use **PostgreSQL** from day one as the primary database.
  - Use **Redis** for queue transport, rate limiting, and ephemeral caching.
  - Run heavy post-processing in **Taskiq Workers**, not on the API request thread.
- **[REQ-013] Quality Evaluation**
  - Use **LLM-as-a-Judge** for automated regression testing.

### 3.6. Security & Privacy

- **Encryption:** PostgreSQL storage and backups must be encrypted at rest.
- **PII Scrubbing:** Memory extraction must filter phone numbers and specific addresses before persistence.
- **User Agency:** UI button for "Wipe My Memory" to delete stored memory/profile state.

### 3.7. Success Metrics

- **D3/D7 Retention:** Goal > 20% for MVP
- **Engagement:** > 10 messages/session
- **Learning Impact:** % of corrections expanded by users

---

## 4. Glossary / Definitions

- **Vibe Check (Onboarding):** Initial 3-turn conversation that calibrates personality and English proficiency.
- **Gatekeeper Agent:** Fast AI check that runs before the main AI to block unsafe or out-of-scope requests.
- **Persona Agent:** Primary AI that acts as the friend and returns conversational reply plus correction payload.
- **Memory Agent:** Background process that extracts facts and updates user profile projections.
- **Subtle Correction:** UX pattern where correction details are hidden behind a sparkle icon rather than interrupting flow.
