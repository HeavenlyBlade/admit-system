# ADMIT — Conversational AI System for Admissions & Enrollment Assistance
### System Build Specification & Prompt for Kiro
Based on: Ortega, D.M.C. — Thesis Proposal, SACLI, 2026 (Chapters 1–3)

---

## 0. How to use this document

This is written so you can paste it (in full, or section by section) to Kiro as a build brief. It translates the thesis's scope, use cases, and UML descriptions (Chapters I–III) into a concrete, working tech stack and architecture — the thesis itself deliberately stays generic ("appropriate frameworks," "appropriate NLP tools") since it's a proposal document, not an implementation plan.

**Chosen approach: RAG (Retrieval-Augmented Generation)** — an LLM (Groq free tier) generates natural responses, but only from content retrieved out of SACLI's own knowledge base. This satisfies the thesis's "predefined knowledge base" constraint (Ch. I, Scope and Constraints) while still producing natural, non-robotic conversation — a strong point for a defense panel, since it maps cleanly onto the thesis's NLP Framework + Knowledge Base + Intent Classification description (Ch. III).

---

## 1. System Overview

**Name:** ADMIT
**Type:** Web-based conversational AI assistant
**Purpose:** Answer admissions/enrollment questions for SACLI (IBED, SHS, HED, TESDA) without a human agent, escalate gracefully when out of scope.

**Actors (from Ch. III Use Case Diagram):**
| Actor | Capabilities |
|---|---|
| Student / Applicant / Parent | Submit text inquiry, receive AI response, tap quick-reply buttons, view program/enrollment info |
| System Administrator | Update knowledge base, review interaction logs, manage system settings |

**Explicitly out of scope (Ch. I Constraints):** no real enrollment registration, no payment processing, no handling of case-specific concerns needing human judgment. Out-of-scope questions get a courteous redirect to the right office.

---

## 2. Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | React + Vite + TailwindCSS | Fast to scaffold, matches chat-UI needs, free hosting on Vercel |
| Backend | FastAPI (Python) | Async, clean for LLM/API orchestration, easy to document for thesis (auto OpenAPI docs) |
| Database | PostgreSQL (Neon free tier) | Persistent KB storage, chat logs, admin accounts |
| LLM (generation) | Groq API (free tier — e.g. Llama 3.1 8B/70B) | Free, fast inference, good enough for grounded Q&A |
| Embeddings / Retrieval | `sentence-transformers` (local, free) or Groq-hosted embeddings if available + pgvector extension on Neon | Enables semantic search over KB instead of brittle keyword matching |
| Auth (admin only) | JWT (FastAPI + passlib/bcrypt) | Matches your existing TeleRehab pattern — reuse what already works |
| Deployment | Vercel (frontend) + Render (backend) | Free tier, matches your usual deployment pattern |
| Diagramming (for thesis Ch. III/IV) | draw.io / Lucidchart / Mermaid | For UML: use case, activity, sequence, deployment diagrams |

> Note: this stack mirrors what you used successfully on TeleRehab (FastAPI + Neon + JWT + Vercel/Render), so debugging patterns you already know (CORS, bcrypt/passlib compatibility, env var suffixes) will transfer directly.

---

## 3. High-Level Architecture

```
┌─────────────────────────┐
│   React Chat Frontend    │  (student/parent/applicant)
│  - Chat window            │
│  - Quick-reply buttons    │
│  - Admin dashboard (SPA)  │
└────────────┬─────────────┘
             │ REST (HTTPS/JSON)
┌────────────▼─────────────┐
│      FastAPI Backend       │
│  ┌───────────────────────┐ │
│  │ Chat Router            │ │  POST /api/chat
│  │  - receives message    │ │
│  │  - calls Retrieval     │ │
│  │  - calls Groq LLM      │ │
│  │  - logs interaction    │ │
│  └───────────┬───────────┘ │
│  ┌───────────▼───────────┐ │
│  │ Retrieval Module        │ │  embeds query → pgvector similarity search
│  └───────────┬───────────┘ │
│  ┌───────────▼───────────┐ │
│  │ Admin Router            │ │  CRUD knowledge base, view logs, manage settings
│  │  (JWT-protected)        │ │
│  └───────────────────────┘ │
└────────────┬─────────────┘
             │
┌────────────▼─────────────┐
│  PostgreSQL (Neon)         │
│  - knowledge_base           │
│  - kb_categories             │
│  - conversations/messages    │
│  - admin_users                │
└───────────────────────────┘
             │
┌────────────▼─────────────┐
│   Groq API (external)      │  LLM completion, grounded on retrieved KB chunks
└───────────────────────────┘
```

This maps directly onto the thesis's Sequence Diagram description (Ch. III): user input → NLP intent classification layer → knowledge base retrieval module → response generation engine → chat interface output — and its Deployment Diagram (web client → application server hosting NLP engine + KB → institutional network).

---

## 4. Database Schema

```sql
-- Knowledge base categories (Admissions Requirements, Enrollment Steps, Programs, Fees, Scholarships, Contacts, About SACLI)
CREATE TABLE kb_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(20) CHECK (department IN ('IBED','SHS','HED','TESDA','GENERAL'))
);

-- Knowledge base entries (the actual retrievable content)
CREATE TABLE knowledge_base (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES kb_categories(id),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(384),          -- pgvector; dim depends on embedding model
    is_active BOOLEAN DEFAULT TRUE,
    updated_by INTEGER REFERENCES admin_users(id),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Admin accounts
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversation sessions (anonymous, no login required for students)
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id UUID DEFAULT gen_random_uuid(),
    started_at TIMESTAMP DEFAULT NOW()
);

-- Individual messages (for logs + evaluation + retraining)
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    sender VARCHAR(10) CHECK (sender IN ('user','bot')),
    content TEXT NOT NULL,
    matched_kb_ids INTEGER[],        -- which KB entries were retrieved for this response
    was_fallback BOOLEAN DEFAULT FALSE,  -- true if system had to give the "contact office" redirect
    created_at TIMESTAMP DEFAULT NOW()
);
```

`was_fallback` and `matched_kb_ids` give you exactly the data you need for the thesis's evaluation phase (functional suitability / reliability metrics) and for demonstrating maintainability (how easily staff can spot KB gaps).

---

## 5. API Endpoints

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| POST | `/api/chat` | Send user message, get AI response | none |
| GET | `/api/quick-replies` | Get common inquiry category buttons | none |
| POST | `/api/admin/login` | Admin authentication | none |
| GET | `/api/admin/kb` | List knowledge base entries | JWT |
| POST | `/api/admin/kb` | Add KB entry (auto-generates embedding) | JWT |
| PUT | `/api/admin/kb/{id}` | Edit KB entry (re-embeds on save) | JWT |
| DELETE | `/api/admin/kb/{id}` | Deactivate/delete KB entry | JWT |
| GET | `/api/admin/logs` | View conversation logs | JWT |
| GET | `/api/admin/analytics` | Fallback rate, top unanswered questions | JWT |

---

## 6. Chat Pipeline (the RAG flow)

1. **User sends message** → `POST /api/chat`
2. **Embed the query** using `sentence-transformers` (e.g. `all-MiniLM-L6-v2`, free, runs locally)
3. **Vector similarity search** against `knowledge_base.embedding` (pgvector `<=>` cosine distance) → top 3–5 matches
4. **Confidence check**: if best match similarity is below a threshold (e.g. 0.35) → this is out of scope → return the fallback/redirect message, log `was_fallback = true`
5. **If in scope** → build a prompt for Groq:
   ```
   System: You are ADMIT, SACLI's admissions assistant. Answer ONLY using the
   context below. If the context doesn't fully answer the question, say so
   and suggest contacting [relevant office]. Be concise and warm.

   Context:
   {retrieved KB chunks}

   Question: {user message}
   ```
6. **Return response** to frontend, log both user message and bot response with `matched_kb_ids`
7. **Quick-reply buttons** are just pre-set queries mapped to `kb_categories` — tapping one runs the same pipeline as typing it.

This structure is what lets you honestly claim "intent classification" and "knowledge-base-driven response" in your thesis defense (Ch. III language) — the retrieval step *is* the intent classification, and the confidence threshold *is* the fallback logic described in Ch. I.

---

## 7. Frontend Structure

```
admit-frontend/
├── src/
│   ├── components/
│   │   ├── ChatWindow.jsx
│   │   ├── MessageBubble.jsx
│   │   ├── QuickReplyButtons.jsx
│   │   ├── TypingIndicator.jsx
│   │   └── admin/
│   │       ├── KBTable.jsx
│   │       ├── KBEditor.jsx
│   │       ├── LogsViewer.jsx
│   │       └── AnalyticsDashboard.jsx
│   ├── pages/
│   │   ├── ChatPage.jsx          # public-facing
│   │   ├── AdminLogin.jsx
│   │   └── AdminDashboard.jsx
│   ├── api/
│   │   └── client.js             # fetch wrappers
│   └── App.jsx
```

## 8. Backend Structure

```
admit-backend/
├── main.py
├── routers/
│   ├── chat.py
│   └── admin.py
├── services/
│   ├── retrieval.py       # embedding + pgvector search
│   ├── llm.py              # Groq API call + prompt building
│   └── embeddings.py       # sentence-transformers wrapper
├── models/
│   └── schemas.py          # SQLAlchemy models
├── auth/
│   └── jwt_handler.py
└── db/
    └── database.py
```

---

## 9. Build Phases (mirrors thesis Ch. III Agile phases — use these as your commit/milestone checkpoints)

1. **Planning** — finalize KB content categories with Registrar/CCO-equivalent info you gather; set up Neon DB, Groq API key, repo scaffolding
2. **Analysis & Design** — build the UML diagrams (use case, activity, sequence, deployment — see §3 for content to diagram)
3. **Implementation** —
   - Backend: DB schema → embeddings service → retrieval → Groq integration → chat endpoint → admin CRUD + auth
   - Frontend: chat UI → quick replies → admin dashboard
4. **Testing** — feed it real SACLI-style questions (in/out of scope), tune the confidence threshold, check fallback quality
5. **Evaluation** — ISO/IEC 25010 questionnaire (already defined in thesis Ch. III) against real respondents

---

## 10. Ready-to-paste prompt for Kiro

> Build ADMIT, a web-based conversational AI assistant for SACLI admissions/enrollment inquiries.
>
> **Stack:** React + Vite + TailwindCSS frontend, FastAPI backend, PostgreSQL (Neon) with pgvector, Groq API for LLM generation, sentence-transformers for local embeddings, JWT auth for admin only.
>
> **Core flow:** Student types a question → backend embeds it → pgvector cosine similarity search against a `knowledge_base` table → if similarity is below threshold, return a polite redirect to the right SACLI office; otherwise send the retrieved KB chunks + question to Groq with a system prompt restricting it to answer only from that context → return the answer and log the full exchange (message, matched KB ids, fallback flag) to a `messages` table.
>
> **Entities:** `kb_categories`, `knowledge_base` (with embedding column), `admin_users`, `conversations`, `messages`.
>
> **Admin dashboard:** JWT-protected CRUD for knowledge base entries (auto re-embed on save/edit), a logs viewer, and a simple analytics view showing fallback rate and most common unanswered questions.
>
> **Chat UI:** messaging-app style chat window with quick-reply buttons for common categories (Admission Requirements, Enrollment Steps, Programs Offered, Tuition & Payment, Scholarships, Contact Info).
>
> Scaffold the project structure first (frontend + backend folders, DB schema, `.env.example`), then implement backend chat pipeline end-to-end before building the admin dashboard.

---

## 11. Notes for your thesis defense

- The confidence-threshold fallback directly satisfies the Ch. I constraint that ADMIT should redirect (not guess) on out-of-scope questions.
- `was_fallback` logging gives you real numbers for "how often did the system know the answer" — useful evidence for the Functional Suitability criterion in your ISO/IEC 25010 evaluation.
- Because retrieval is grounded (RAG), you can honestly say the system's knowledge is fully constrained to admin-managed content — important if a panelist asks "how do you stop it from hallucinating answers about SACLI policy."
