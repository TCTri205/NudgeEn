# NudgeEn Core Principles

These principles guide the design, development, and architectural decisions of NudgeEn.

## 1. Zero-Base Costing (Efficiency)

- **Principle**: Prioritize tools and services that cost $0 during the MVP phase.
- **Goal**: Minimize financial risk and allow the project to iterate without burning cash.
- **Examples**: Using **Auth.js** (Self-hosted) instead of paid IAM, **SQLite** instead of managed DBs, and the **Gemini Free Tier**.

## 2. Pedagogy as a Sidekick (Experience)

- **Principle**: Learning should be non-intrusive.
- **Goal**: Maintain the "friendship vibe" by avoiding constant corrections.
- **Implementation**: use the **Sparkle Icon ✨** for subtle feedback rather than interrupting the chat flow with red ink.

## 3. Privacy by Design (Trust)

- **Principle**: User data is sacred but must be scrubbed.
- **Goal**: Enable powerful memory without storing sensitive PII.
- **Implementation**: The **Memory Agent** must filter out addresses, phone numbers, and PII before saving to the user profile JSON.

## 4. Web-First, Responsive Packaging (UI/UX)

- **Principle**: Prioritize the desktop browser experience while maintaining layout flexibility for mobile browsers.
- **Goal**: Deliver a polished, high-quality web messaging interface as the primary MVP platform, with mobile-friendliness achieved through responsive design rather than dedicated mobile-first features.

## 5. Logical Mapping (Consistency)

- **Principle**: Align Project Management artifacts for zero confusion.
- **Implementation**: Use **0-indexed numbering** for both Epics and Sprints (e.g., EPIC-00 aligns with Sprint 0). This ensures a direct, one-to-one logical map between goals and execution.
