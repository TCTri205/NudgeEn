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

### 3.3. Key Features

- **[REQ-001] Messenger-like Interface:**
  - Chat bubble display.
  - Support for emojis and message reactions.
  - Real-time feel with typing indicators ("AI is typing...").
- **[REQ-002] Contextual Memory (User Profile System):**
  - Instead of full chat history embedding, the system extracts and updates a static **User Profile JSON** file (stored in SQLite/file-based DB).
  - Remembers names, hobbies, and past details (e.g., "How was that presentation you mentioned yesterday?").
- **[REQ-003] Subtle Correction (Structured Output):**
  - AI uses **Structured Output (JSON)** to return both the reply and an optional correction field in a single LLM call to optimize latency and costs.
  - Flow is never interrupted. Corrections are shown subtly in the UI (e.g., a **Sparkle icon ✨** next to the message that reveals the original vs. improved version on tap).
- **[REQ-004] Persona Customization:**
  - Users can choose a "Vibe": Sarcastic/Banter, Gentle/Empathetic, or Tech-savvy.
- **[REQ-009] Initial Calibration (Onboarding):**
  - A brief 3-turn interactive "Vibe Check" where the AI assesses the user's English level and preferred communication style to tailor the persona.
- **[REQ-008] Weekly Vibe Check:**
  - Once a week, the AI provides a friendly, high-level summary of progress (e.g., "You've been using way more natural slang this week!").

### 3.4. Non-Functional Requirements & Constraints

- **[REQ-005] Feasibility & Cost:** MVP focuses purely on text and high-speed models (**Gemini 1.5 Flash**) to minimize costs and latency.
- **[REQ-006] Safety & Guardrails (Gatekeeper Layer):**
  - **Multi-Agent Setup:** A lightweight "Gatekeeper" prompt (orchestrated in a single-turn or parallel call) evaluates input before the main persona for safety, jailbreaks, and scope.
  - Strict prevention of out-of-scope requests (e.g., code generation, translations).
- **[REQ-007] Testability:**
  - **LLM-as-a-Judge Evaluation:** An automated pipeline uses another AI to verify persona consistency, memory usage, and guardrail triggers across hundreds of test turn