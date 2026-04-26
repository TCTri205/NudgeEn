# EPIC-03: AI Persona & Memory Engine

- **Status:** Pending (Planned for Sprint 2)
- **Priority:** P0 - Critical Path
- **Source requirement:** PRD-v1.md (REQ-002, REQ-002.1, REQ-003, REQ-005, REQ-006, REQ-009, REQ-010)
- **Impacted domains:** AI, Persona, Memory, Pedagogy

---

## Summary

Implement the AI persona system and memory extraction pipeline that transforms NudgeEn from a simple chatbot into a persistent, contextually aware friend. This epic enables the AI to remember user details across conversations, adapt its personality based on user preferences, and proactively engage based on historical context. It creates the "brain" that makes the AI feel like a real friend who knows and remembers you. This epic delivers the core intelligence layer that personalizes the user experience and provides the foundation for the pedagogical features in EPIC-04.

---

## Current State / Gap

- **Implemented:** Infrastructure (EPIC-00), authentication (EPIC-01), messaging interface (EPIC-02).
- **Missing:** Persona configuration, onboarding vibe check, memory extraction pipeline, user profile projection, context retrieval, proactive engagement, AI provider integration (Gemini/Groq), structured output parsing, guardrail integration.

---

## Problem / Opportunity

Without memory and persona, the AI is a generic chatbot with no continuity. Users expect their AI friend to:
- Remember their name, hobbies, and preferences
- Adapt communication style to their personality
- Reference past conversations naturally
- Proactively engage based on what it knows

Building these features after EPIC-04 (pedagogy) would mean corrections lack context and personalization, reducing learning effectiveness.

---

## Desired Outcome

After this epic is complete:
- AI has distinct personas (Gentle, Sarcastic, Tech-savvy) with consistent tones
- Users complete a 3-turn onboarding to calibrate their AI friend
- Memory extraction runs asynchronously after conversations
- User profiles are updated with extracted facts
- AI responses reference memories naturally
- Weekly check-ins engage inactive users
- PII is scrubbed before memory persistence
- Context window is managed efficiently (recent messages + memories)

This outcome matters because memory and persona are what differentiate NudgeEn from generic chatbots and create emotional attachment.

---

## Users / Use Cases

- **Primary users:** End users (personalized AI experience), Development team (AI infrastructure)
- **Main use cases:**
  - User selects persona vibe during onboarding
  - User completes 3-turn calibration conversation
  - System extracts memories from conversations asynchronously
  - AI references user memories in responses
  - System generates weekly progress summaries
  - User profile displays current state projection
- **Important edge cases:**
  - Memory extraction fails (retry logic)
  - Context window overflow (compression strategy)
  - PII detected in conversation (scrubbing)
  - User changes persona preference mid-conversation

---

## Scope

### In scope

- ✅ Vibe/persona customization (Sarcastic, Gentle/Empathetic, Tech-savvy)
- ✅ 3-turn onboarding vibe check (calibration)
- ✅ Contextual memory extraction from conversations
- ✅ User profile JSON projection in PostgreSQL
- ✅ Memory fact storage (append-oriented `user_memories` table)
- ✅ Profile update pipeline (asynchronous via Taskiq workers)
- ✅ Conversation context retrieval for persona prompts
- ✅ Compacted memory summary injection into prompts
- ✅ Proactive engagement based on memory triggers
- ✅ Initial calibration flow (REQ-005 from PRD)
- ✅ Weekly vibe check / progress summary (REQ-006 from PRD)
- ✅ AI provider integration (Gemini 2.5 Flash primary, Groq fallback)
- ✅ Structured output parsing (reply + correction payload)
- ✅ Guardrail agent integration (pre-persona check)
- ✅ Memory extraction as background job (Taskiq)
- ✅ Profile rebuild from memory history
- ✅ Memory expiration/archival policies
- ✅ PII scrubbing before memory persistence
- ✅ Memory retrieval for context (most recent N facts)
- ✅ Conversation context window management

### Out of scope

- ❌ Voice/audio processing (text-only MVP)
- ❌ Real-time video or camera integration
- ❌ Advanced ML model training (use existing LLMs)
- ❌ Multi-persona training (user-trained personas)
- ❌ Long-term memory beyond extracted facts (infinite context)
- ❌ Cross-user memory sharing or social features
- ❌ Emotional state detection (beyond stated preferences)
- ❌ Voice synthesis or text-to-speech

---

## Capability Slices

- **Slice 1: Persona System** — Persona configs, prompt templates, tone consistency
- **Slice 2: Onboarding Flow** — 3-turn calibration, English level assessment, vibe selection
- **Slice 3: Memory Extraction** — LLM-based extraction, Taskiq workers, confidence scoring
- **Slice 4: Profile Projection** — user_profiles table, JSONB updates, rebuild capability
- **Slice 5: Context Management** — Memory retrieval, context window, compression
- **Slice 6: AI Integration** — Gemini/Groq providers, structured output, fallback logic

---

## Facts / Assumptions / Constraints / Unknowns

- **Facts:**
  - Gemini 2.5 Flash is the primary LLM provider
  - Groq is the fallback provider
  - Taskiq workers handle async memory extraction
  - PostgreSQL stores memories and profiles
  - PII must be scrubbed before persistence
- **Assumptions:**
  - Users will complete onboarding (80%+ completion rate expected)
  - Memory extraction completes within 30 seconds
  - Context window of 20 messages + 10 memories is sufficient
- **Constraints:**
  - Persona prompts must not exceed 500 tokens
  - Context window budget: ~2000 tokens
  - Memory extraction runs asynchronously (non-blocking)
  - PII patterns: phone numbers, emails, SSN, addresses
  - Tokens must be scrubbed before storage
- **Unknowns:**
  - Exact prompt templates (requires iteration)
  - Memory confidence threshold for auto-acceptance
  - Optimal memory expiration policy

---

## Proposed Solution

**Persona Configuration:**
```python
PERSONAS = {
    "gentle": {
        "name": "Gentle Emma",
        "tone": "warm, encouraging, patient",
        "system_prompt": "...",
        "greeting": "Hey there! How's it going? 😊"
    },
    "sarcastic": {
        "name": "Sarcastic Sam",
        "tone": "witty, playful banter",
        "system_prompt": "...",
        "greeting": "Oh great, it's you. What do you want? 😏"
    },
    "tech_savvy": {
        "name": "Tech Alex",
        "tone": "analytical, precise",
        "system_prompt": "...",
        "greeting": "Connection established. Ready to chat. 💻"
    }
}
```

**Memory Extraction Pipeline:**
1. User sends message → API persists → Streams response
2. API commits transaction → Enqueues Taskiq job
3. Worker fetches conversation → Calls LLM for extraction
4. Worker inserts `user_memories` → Updates `user_profiles`

**Profile Projection:**
```json
{
  "user_id": "uuid",
  "name": "John",
  "english_level": "B1",
  "vibe_preference": "gentle",
  "onboarding_completed": true,
  "weekly_check_last_sent": "2026-04-26T10:00:00Z",
  "extracted_memories": [...],
  "stats": {"messages_sent": 42, "corrections_viewed": 15}
}
```

**Key tradeoffs:**
- Chose async extraction (non-blocking) over synchronous (simpler but slow)
- Chose append-only memories (audit trail) over upsert (simpler, safer)
- Chose JSONB profile projection (flexible) over normalized tables (faster reads)

---

## Dependencies / Rollout / Risks

### Dependencies

- **External:**
  - Google Generative AI — Gemini 2.5 Flash
  - Groq — Fallback LLM provider
  - Taskiq + Redis — Background job processing
  - Pydantic — Structured output validation

- **Internal:**
  - **EPIC-00: Infrastructure** — Project setup, database, workers
  - **EPIC-01: Security** — Auth, user context, safety gatekeeper
  - **EPIC-02: Messaging** — Message persistence, conversation persistence

**Outgoing Dependency (Consumed By):**
- **EPIC-04: Pedagogy** — Will consume memory system for correction context

### Rollout notes

- Prompt templates require iteration and A/B testing
- Memory extraction should start in logging mode
- Weekly checks should be tested with internal users first

### Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LLM hallucinations in memory | Medium | Medium | Confidence scores, human review option |
| Prompt too large (context overflow) | High | Medium | Context window management, compression |
| Memory extraction too slow | Medium | Low | Async workers, optimized prompts |
| Persona feels inconsistent | Medium | Medium | Clear system prompts, testing |
| PII leakage in memories | Critical | Low | Aggressive scrubbing, audit |
| Weekly check spamming users | Medium | Low | Proper "last sent" tracking |

---

## Epic Done Criteria

- [ ] Three personas implemented with distinct tones
- [ ] Onboarding vibe check (3 turns) functional
- [ ] Memory extraction worker processing messages
- [ ] `user_memories` table populated from conversations
- [ ] `user_profiles` table updated after extraction
- [ ] Persona uses memories in prompt context
- [ ] Profile rebuild job working
- [ ] Weekly vibe check triggered after 7 days inactive
- [ ] Gemini 2.5 Flash integrated
- [ ] Groq fallback configured
- [ ] Structured output parsing (reply + correction)
- [ ] Guardrail runs before persona agent
- [ ] PII scrubbing in memory pipeline
- [ ] Context window management (20 msgs + 10 memories)
- [ ] Memory retrieval for chat context

---

## Task Writer Handoff

- **Epic slug:** EPIC-03
- **Epic file path:** `docs/project-management/epics/EPIC-03.md`
- **Original requirement:** PRD-v1.md (REQ-002, REQ-002.1, REQ-003, REQ-005, REQ-006, REQ-009, REQ-010)
- **Epic summary:** AI persona system and memory extraction pipeline
- **Impacted domains:** AI, Persona, Memory, Pedagogy
- **Desired outcome:** AI remembers users, adapts personality, engages proactively
- **In-scope outcomes:** Personas, onboarding, memory extraction, profile projection, AI integration
- **Non-goals:** Voice processing, custom personas, infinite context
- **Capability slices:** 6 slices (persona, onboarding, memory extraction, profile, context, AI)
- **Facts:** Gemini 2.5 Flash, Groq fallback, Taskiq workers, PostgreSQL, PII scrubbing
- **Assumptions:** 80% onboarding completion, 30s extraction time, 20+10 context sufficient
- **Constraints:** <500 token prompts, ~2000 token context, async extraction, PII scrubbing
- **Unknowns:** Prompt templates, confidence thresholds, expiration policy
- **Proposed solution summary:** Persona configs + async memory extraction + profile projection + Gemini/Groq
- **Dependencies:** EPIC-00, EPIC-01, EPIC-02 (all must be complete)
- **Rollout notes:** Iterate prompts, logging mode for extraction, internal testing for weekly checks
- **Risks:** Hallucinations, context overflow, slow extraction, PII leakage
- **Task splitting hints:** Split by slice (persona → onboarding → memory → profile → context → AI)
- **Validation expectations:** All criteria testable, persona tones distinguishable in chat tests

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-26 | System | Initial version based on project documentation |
| 2.0 | 2026-04-27 | Assistant | Standardized to epic-template.md format |
