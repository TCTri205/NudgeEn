# NudgeEn - AI Messaging Friend for English Practice (v1.0-Draft)

## 1. Project Inspiration

Creating an AI "texting friend" to help practice real-world reading/writing skills in a casual, low-pressure environment. Instead of rote grammar lessons, it provides a natural communication space to maintain user motivation.

## 2. Market Analysis

- **Traditional Platforms (Duolingo, Memrise):** Primarily offer roleplay with fixed scenarios (e.g., ordering at a restaurant). They can feel rigid and lack the personal connection of a real friend.
- **Dedicated Chatbots (Andy English):** Often feel like a series of multiple-choice questions in a chat UI rather than natural conversation.
- **General AI (Character.ai, ChatGPT, Pi):**
  - *Character.ai:* Great for roleplay but lacks pedagogical features (vocabulary tracking, subtle corrections).
  - *ChatGPT:* Professional and assistant-like, lacking the "vibe" of a casual friend.
- **Language Exchange (Tandem, HelloTalk):** High psychological pressure, slow response times, and potential social risks.
- **The Gap:** A hybrid solution that combines the natural personality of Character.ai with the clear learning objectives of Duolingo. It solves the pain point of wanting to practice without feeling judged or "graded."

## 3. Product Requirements Document (MVP)

### 3.1. Overview & Goals

- **Objective:** Build an AI chatbot that acts as a real friend in a messaging interface (like Messenger or Telegram) to improve daily English reading and writing.
- **Scope:** Text-only conversation (Reading & Writing). Voice/Audio is out of scope for MVP.

### 3.2. Target Persona

- **Age:** 18-30 (Students or Young Professionals).
- **Profile:** Basic grammar knowledge but struggles with fluency, typing speed, and practical vocabulary (slang, idioms, natural expressions).
- **Behavior:** Enjoys social media and messaging; avoids high-pressure traditional courses.

### 3.3. Key Features (Functional Requirements)

#### [Group: User Experience]

- **[REQ-001] Messenger-like Interface:**
  - Chat bubble display with support for emojis and message reactions.
  - Real-time feedback with typing indicators ("AI is typing...").
  - Responsive design (Primary: Desktop Web; Secondary: Mobile Browser).
- **[REQ-002] Persona Customization:**
  - Users choose a "Vibe": Sarcastic/Banter, Gentle/Empathetic, or Tech-savvy.
- **[REQ-003] Subtle Correction:**
  - Corrections are non-intrusive. A **Sparkle icon ✨** appears next to messages with better alternatives.
  - Tapping reveals: Original vs. Improved vs. Why (brief explanation).

#### [Group: Intelligence & Memory]

- **[REQ-004] Contextual Memory (User Profile):**
  - System extracts key facts (name, hobbies, goals) into a persistent JSON profile.
  - References past conversations naturally.
- **[REQ-005] Initial Calibration (Onboarding):**
  - A 3-turn interactive "Vibe Check":
    1. Introduction & Name.
    2. Interest inquiry.
    3. Short roleplay snippet for level assessment.
- **[REQ-006] Weekly Vibe Check:**
  - Automated summary of progress delivered as an in-chat "card".
  - Highlights: Most used new words, grammar improvement trend.
  - **Trigger:** Checked on first user message if `weekly_check_last_sent` > 7 days. Data generated from `stats` and recent memory.

#### [Group: Infrastructure & Security]

- **[REQ-007] Authentication:**
  - Self-hosted/Embedded IAM via **NextAuth.js (Auth.js)**.
  - Supports **OAuth2 (Google/GitHub)** and **Basic Authentication (Email/Password)**.
- **[REQ-008] Safety Gatekeeper:**
  - Lightweight prompt evaluating input/output for safety and scope (no code, no translation).
  - Runs **sequentially** (fail-fast) before Persona Agent.
  - If triggered, gracefully replies: "I'm not sure how to respond to that! Let's get back to chatting in English."
  - Attempts are logged for abuse monitoring.

### 3.4. Technical Architecture & Data Schemas

#### [Architecture & Deployment]

1. **Frontend:** Next.js deployed on **Vercel** (automatic CI/CD).
2. **Backend:** FastAPI hosted on **Railway / Render**.
3. **Logic Flow:**
   - User Message -> Webhook -> **Gatekeeper Agent** (Parallel/Pre-check) -> **Persona Agent**.
   - **Persona Agent** generates response + correction in one JSON object.
   - **Memory Agent** (Background/Async) updates User Profile JSON based on the interaction.

#### [Data Schemas]

- **User Profile JSON:**

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
    {"topic": "hobby", "detail": "loves hiking", "timestamp": "ISO-8601"}
  ],
  "stats": {"messages_sent": 0, "corrections_viewed": 0}
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

- **[REQ-009] Feasibility & Cost:**
  - Primary: **Gemini 2.5 Flash**.
  - Fallback: **Groq API** (for high speed/low latency fallback).
- **[REQ-010] Rate Limiting:**
  - MVP limit: **50 messages per 24 hours** per user to manage API costs.
- **[REQ-011] Fallback Strategy:**
  - If API fails/timeouts, display: "Sorry, I'm feeling a bit sleepy. Can we chat in a minute?"
- **[REQ-012] Scalability & Storage:**
  - Start with **SQLite + WAL mode**.
  - Migration path to **PostgreSQL/Supabase** once user base exceeds 1,000 active users.
- **[REQ-013] Quality Evaluation:** Use **LLM-as-a-Judge** for automated regression testing.

### 3.6. Security & Privacy

- **Encryption:** SQLite database must be encrypted at rest.
- **PII Scrubbing:** Memory extraction agent must filter out phone numbers and specific addresses.
- **User Agency:** UI button for "Wipe My Memory" (deletes Profile JSON).

### 3.7. Success Metrics

- **D3/D7 Retention:** Goal > 20% for MVP.
- **Engagement:** > 10 messages/session.
- **Learning Impact:** % of corrections expanded by users.

---

## 4. Glossary / Definitions

- **Vibe Check (Onboarding):** The initial 3-turn conversation where the AI calibrates to the user's personality and English proficiency.
- **Gatekeeper Agent:** A fast, lightweight AI check that runs before the main AI to block inappropriate, harmful, or out-of-scope requests.
- **Persona Agent:** The primary AI that acts as the friend, formatted to return both a conversational reply and a grammar correction.
- **Memory Agent:** A background AI process that summarizes chat history into actionable facts to update the User Profile JSON.
- **Subtle Correction:** The UI mechanism (e.g., a sparkle icon ✨) that allows users to view grammar corrections without interrupting the flow of the conversation.
