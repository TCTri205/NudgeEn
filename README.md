# NudgeEn

> An AI chatbot that feels like a real messaging friend and helps users improve daily English reading and writing through natural conversation.

---

## 🌟 Project Vision

NudgeEn is designed to be more than just a translator or a correction tool. It's a "persona-driven English companion" that lives in your chat interface, nudging you towards better English usage through subtle corrections and long-term memory of your progress.

## 🏗️ Architecture: Modular Monolith

NudgeEn follows a **Modular Monolith** pattern:

- **Clean Separation**: Logical modules (`auth`, `chat`, `persona`, `memory`, etc.) with strict boundary rules.
- **Distributed Runtime**: Independently scalable Web, API, and Worker processes.
- **Solid Foundation**: PostgreSQL as the single source of truth, Redis for high-throughput messaging/caching.

## 🛠️ Tech Stack

- **Frontend**: Next.js (App Router), TypeScript, Auth.js, Tailwind CSS.
- **Backend API**: FastAPI, Pydantic v2, SQLAlchemy (Async).
- **Background Workers**: Taskiq, Redis Broker.
- **Database**: PostgreSQL 16.
- **AI**: Gemini 2.5 Flash (Primary), Groq (Fallback).

## 🚀 Quick Start (Development)

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose (for local DB/Redis)

### Setup

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd NudgeEn
   ```

2. **Start Infrastructure Services**

   ```bash
   docker-compose up -d
   ```

3. **Backend Setup (API & Workers)**

   ```bash
   cd api
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   alembic upgrade head
   python -m app.main  # Start API
   ```

4. **Frontend Setup**

   ```bash
   cd web
   npm install
   npm run dev
   ```

## 📝 Documentation

Detailed documentation can be found in the `/docs` directory:

- [Architecture Overview](./docs/ARCHITECTURE.md)
- [Product Requirements (PRD)](./docs/PRD-v1.md)
- [Tech Stack & Rationale](./docs/TECHSTACK.md)
- [Onboarding Guide](./docs/ONBOARDING.md)
- [Project Roadmap](./docs/project-management/ROADMAP.md)

---

## 🇻🇳 Hướng dẫn nhanh (Vietnamese)

NudgeEn là chatbot học tiếng Anh qua trò chuyện tự nhiên.

**Cách chạy project nhanh:**

1. Chạy Postgres/Redis: `docker-compose up -d`
2. Backend (FastAPI): Cài đặt venv và chạy `pip install -r requirements.txt`, sau đó chạy app.
3. Frontend (Next.js): `npm install && npm run dev`

Chi tiết xem tại [Tài liệu Onboarding](./docs/ONBOARDING.md).
