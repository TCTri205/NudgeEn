# EPIC-04: Pedagogical Layer

- **Status:** Pending (Planned for Sprint 3)
- **Priority:** P1 - High
- **Source requirement:** PRD-v1.md (REQ-003, REQ-006)
- **Impacted domains:** Pedagogy, AI, Frontend, Analytics

---

## Summary

Implement the pedagogical features that transform NudgeEn from an entertaining chatbot into an effective English learning tool. This epic delivers subtle, non-intrusive corrections (Sparkle Icon), weekly progress summaries, and learning analytics that help users improve their language skills without breaking the natural flow of conversation. It balances the "friend" persona with educational value. This epic builds on the memory foundation from EPIC-03 and adds the learning layer that differentiates NudgeEn from generic chatbots.

---

## Current State / Gap

- **Implemented:** Infrastructure (EPIC-00), authentication (EPIC-01), messaging (EPIC-02), persona and memory (EPIC-03).
- **Missing:** Correction generation service, sparkle icon UI, correction modal, weekly progress cards, learning metrics dashboard, vocabulary tracking, adaptive correction logic, user feedback on corrections.

---

## Problem / Opportunity

Without pedagogical features, NudgeEn is just a friendly chatbot — not an English learning tool. Users need:
- Subtle corrections that don't interrupt conversation flow
- Visible progress over time (motivation)
- Explanations that match their English level
- Tracking of vocabulary and grammar improvements

Building corrections after the AI pipeline is solid ensures corrections are accurate and contextually appropriate. Retrofitting corrections later would require restructuring the entire response generation flow.

---

## Desired Outcome

After this epic is complete:
- Sparkle icon (✨) appears next to messages with corrections
- Users can click to see original vs improved vs explanation
- Weekly progress cards summarize learning achievements
- Dashboard shows vocabulary growth and grammar trends
- Corrections adapt to user's English level (A1-C2)
- Users can mark corrections as helpful/not helpful
- Progress data can be exported (CSV/PDF)

This outcome matters because educational efficacy is the core value proposition — users stay for measurable improvement, not just entertainment.

---

## Users / Use Cases

- **Primary users:** End users (learning English), Development team (pedagogy infrastructure)
- **Main use cases:**
  - User sends message with grammar error
  - AI detects error and generates correction
  - User clicks sparkle icon to view correction details
  - User marks correction as helpful
  - User views weekly progress card
  - User exports learning progress data
- **Important edge cases:**
  - Over-correction (too many corrections per message)
  - Incorrect corrections (low confidence)
  - User ignores corrections (engagement tracking)
  - Advanced users want fewer corrections

---

## Scope

### In scope

- ✅ Subtle correction system (Sparkle Icon UX)
- ✅ Correction display modal (Original vs Improved vs Explanation)
- ✅ Grammar/vocabulary correction generation
- ✅ Correction severity levels (minor, moderate, major)
- ✅ Correction storage and tracking
- ✅ Weekly progress cards (automatic, in-chat)
- ✅ Learning metrics (new words, grammar trends, accuracy)
- ✅ Correction expansion rate tracking (% viewed by users)
- ✅ Vocabulary tracking (new words learned, review suggestions)
- ✅ Grammar rule categorization (tense, articles, prepositions, etc.)
- ✅ Progress visualization (trends over time)
- ✅ Correction confidence scoring
- ✅ User feedback on corrections (helpful/not helpful)
- ✅ Adaptive correction frequency (based on user level)
- ✅ Correction timing (immediate vs end-of-response)
- ✅ Memory integration (track corrected phrases in memory)
- ✅ Export progress data (PDF/CSV)
- ✅ Streaks and achievements (optional encouragement)

### Out of scope

- ❌ Formal lesson plans or curriculum
- ❌ Flashcard system (spaced repetition)
- ❌ Grammar exercises or quizzes
- ❌ Pronunciation scoring (audio)
- ❌ Writing assignments or essays
- ❌ Teacher dashboard or parent controls
- ❌ Multi-language support (English only for MVP)
- ❌ Certification or testing

---

## Capability Slices

- **Slice 1: Correction Generation** — LLM-based correction, severity classification, confidence scoring
- **Slice 2: Sparkle Icon UI** — Inline correction indicator, modal component, copy functionality
- **Slice 3: Progress Cards** — Weekly summaries, in-chat delivery, achievement highlights
- **Slice 4: Learning Metrics** — Vocabulary tracking, grammar trends, accuracy over time
- **Slice 5: Adaptive Corrections** — Level-based frequency, user preferences, feedback loop
- **Slice 6: Data Export** — CSV/PDF export, progress reports, study lists

---

## Facts / Assumptions / Constraints / Unknowns

- **Facts:**
  - Corrections are generated as part of structured LLM output
  - PostgreSQL stores corrections in `message_corrections` table
  - Maximum 1-2 corrections per message (avoid overwhelming)
  - CEFR levels (A1-C2) determine correction frequency
- **Assumptions:**
  - Users want to learn English (primary use case)
  - Subtle corrections preserve friendship vibe
  - Weekly summaries motivate continued use
  - 60%+ of users will click sparkle icons
- **Constraints:**
  - Maximum 1-2 corrections per message
  - Explanations must match user's English level
  - Corrections must not interrupt conversation flow
  - Confidence score threshold: >0.7 to show correction
  - Severity levels: minor (typos), moderate (tense), major (structure)
- **Unknowns:**
  - Optimal correction frequency per level
  - Best explanation style (concise vs detailed)
  - User preference for correction timing

---

## Proposed Solution

**Correction Generation Architecture:**
```
User Message → Gatekeeper → Persona → Correction Service → LLM → {reply, correction}
```

**Structured Output:**
```json
{
  "reply": "Oh, you went hiking yesterday? That sounds cool! Where did you go?",
  "correction": {
    "has_correction": true,
    "original": "I go hike yesterday",
    "improved": "I went hiking yesterday",
    "explanation": "Use past tense 'went' for completed actions. 'Hiking' is the correct gerund form.",
    "grammar_rule": "past_simple_tense",
    "severity": "moderate",
    "confidence": 0.95
  }
}
```

**Correction Service:**
```python
class CorrectionService:
    async def generate_correction(
        self,
        user_text: str,
        user_level: str,
        context: Optional[str] = None
    ) -> Optional[Correction]:
        # Skip if too short or likely correct
        if len(user_text.split()) < 3:
            return None

        # Call LLM with correction prompt
        response = await self.llm.complete(
            prompt,
            response_format=CorrectionSchema
        )

        if not response.has_correction:
            return None

        return Correction(...)
```

**Weekly Progress Card:**
- Messages sent this week
- Corrections received (by grammar rule)
- New vocabulary learned
- Accuracy trend (corrections per 100 messages)
- Encouraging message from AI

**Key tradeoffs:**
- Chose inline sparkle icon (subtle) over interruptive corrections
- Chose LLM-based correction (contextual) over rule-based (brittle)
- Chose weekly summaries (balanced frequency) over daily (spammy) or monthly (too infrequent)

---

## Dependencies / Rollout / Risks

### Dependencies

- **External:**
  - LLM APIs (Gemini/Groq) — For correction generation
  - CEFR vocabulary lists — For word level classification

- **Internal:**
  - **EPIC-00:** Infrastructure, database setup
  - **EPIC-01:** Authentication, user profiles
  - **EPIC-02:** Messaging system, message storage
  - **EPIC-03:** Memory system, user context, AI integration

### Rollout notes

- Correction frequency should start conservative (avoid overwhelming)
- Weekly cards should be tested for engagement metrics
- A/B test different explanation styles

### Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Over-correction annoys users | High | Medium | Limit to 1-2 per message, severity-based |
| Corrections are wrong | High | Low | Confidence scores, "not helpful" feedback |
| Explanations too complex | Medium | Medium | Level-adaptive explanations |
| Users ignore corrections | Medium | High | Make engaging, track effectiveness |
| Performance impact on streaming | Low | Medium | Generate corrections in parallel |

---

## Epic Done Criteria

- [ ] Sparkle icon appears on corrected messages
- [ ] Correction modal opens with original/improved/explanation
- [ ] Corrections generated for grammar errors (tense, articles, etc.)
- [ ] Corrections stored in database with all fields
- [ ] Weekly progress card generated after 7 days inactive
- [ ] Progress card includes: new words, grammar trends, message count
- [ ] Learning metrics dashboard in settings
- [ ] User can mark corrections as helpful/not helpful
- [ ] Correction confidence scores tracked
- [ ] Adaptive correction frequency by user level
- [ ] Vocabulary tracking and new word detection
- [ ] Correction severity classification (minor/moderate/major)
- [ ] Export progress data (CSV)

---

## Task Writer Handoff

- **Epic slug:** EPIC-04
- **Epic file path:** `docs/project-management/epics/EPIC-04.md`
- **Original requirement:** PRD-v1.md (REQ-003, REQ-006)
- **Epic summary:** Pedagogical features for English learning (corrections, progress tracking)
- **Impacted domains:** Pedagogy, AI, Frontend, Analytics
- **Desired outcome:** Users measurably improve English through subtle corrections and progress tracking
- **In-scope outcomes:** Correction system, sparkle UI, progress cards, metrics dashboard, vocabulary tracking
- **Non-goals:** Formal lessons, flashcards, quizzes, pronunciation scoring
- **Capability slices:** 6 slices (correction generation, UI, progress cards, metrics, adaptive, export)
- **Facts:** LLM corrections, PostgreSQL storage, CEFR levels, 1-2 corrections/msg max
- **Assumptions:** Users want to learn, subtle corrections work, weekly summaries motivate
- **Constraints:** 1-2 corrections/msg, level-adaptive explanations, >0.7 confidence, non-interruptive
- **Unknowns:** Optimal frequency, explanation style, correction timing preference
- **Proposed solution summary:** LLM correction service + sparkle icon UI + weekly progress cards + metrics
- **Dependencies:** EPIC-00, EPIC-01, EPIC-02, EPIC-03 (all must be complete)
- **Rollout notes:** Conservative frequency, A/B test explanations, track engagement
- **Risks:** Over-correction, wrong corrections, complex explanations, user ignores
- **Task splitting hints:** Split by slice (generation → UI → progress → metrics → adaptive → export)
- **Validation expectations:** All criteria testable, corrections distinguishable by severity in tests

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-26 | System | Initial version based on project documentation |
| 2.0 | 2026-04-27 | Assistant | Standardized to epic-template.md format |
