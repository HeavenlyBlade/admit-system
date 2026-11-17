# ADMIT  EConversational AI Admissions Assistant

ADMIT (Admissions & Inquiries Technology) is a web-based RAG chatbot that answers admissions and enrollment questions for **St. Anne College Lucena, Inc. (SACLI)**. It uses Retrieval-Augmented Generation to ground every answer in admin-managed knowledge base content, and falls back gracefully to office redirects when a question is out of scope.

---

## Live URLs

| Service | URL |
|---|---|
| Chat Interface | https://admit-system.vercel.app |
| Admin Dashboard | https://admit-system.vercel.app/admin/login |
| Backend Health | https://admit-system-backend.onrender.com/health |
| API Docs | https://admit-system-backend.onrender.com/docs |

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 + Vite 8 + Tailwind CSS v4 |
| Backend | FastAPI (Python 3.11) |
| Database | PostgreSQL + pgvector (Supabase) |
| Embeddings | fastembed  EBAAI/bge-small-en-v1.5 (384-dim, local) |
| LLM | Groq API  Eopenai/gpt-oss-20b |
| Auth | JWT (admin only) + Google OAuth (users) |
| Deployment | Vercel (frontend) + Render (backend) |

---

## How it works

1. User sends a message ↁEbackend embeds it with fastembed
2. pgvector cosine similarity search finds the top 5 KB matches
3. If best match score ≥ `CONFIDENCE_THRESHOLD` (default 0.35) ↁEGroq generates a grounded response from the retrieved context
4. If below threshold ↁEpolite fallback message directing user to the appropriate SACLI office
5. Full conversation is logged (user message, bot response, matched KB IDs, fallback flag)

---

## Local Development

### Prerequisites
- Python 3.11
- Node.js 18+
- A Supabase project with pgvector enabled (or the live DB credentials from `.env`)

### Backend

```bash
cd backend
py -3.11 -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
# Copy root .env so the backend can find DATABASE_URL, GROQ_API_KEY, etc.
uvicorn main:app --reload
```

API docs available at http://localhost:8000/docs

### Seed the database (first time only)

```bash
cd backend
venv\Scripts\activate
python db/seed_data.py
```

### Frontend

```bash
cd frontend
npm install
# Create frontend/.env:
# VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

Frontend available at http://localhost:5173

---

## Project Structure

```
ADMIT/
├── backend/
━E  ├── auth/               # JWT handler + password hashing
━E  ├── db/                 # DB connection, init, seed data
━E  ├── models/             # SQLAlchemy ORM + Pydantic schemas
━E  ├── routers/            # chat, admin, auth, sessions endpoints
━E  ├── services/           # embeddings, retrieval, LLM
━E  ├── tests/              # pytest test suite
━E  ├── main.py             # FastAPI app entry point
━E  ├── requirements.txt
━E  ├── Dockerfile
━E  └── render.yaml
├── frontend/
━E  ├── src/
━E  ━E  ├── api/            # chatApi, adminApi, sessionsApi
━E  ━E  ├── components/     # ChatWindow, MessageBubble, etc.
━E  ━E  ├── components/admin/ # KBTable, KBEditor, LogsViewer, AnalyticsDashboard
━E  ━E  ├── context/        # AuthContext
━E  ━E  └── pages/          # HomePage, ChatPage, LoginPage, AdminDashboard
━E  ├── public/             # Static assets (logo, bg-video)
━E  └── vercel.json
├── .github/workflows/
━E  ├── deploy.yml          # CI  Ebuild + test on push
━E  └── keepalive.yml       # Scheduled ping every 3 days (prevents Supabase pause)
├── ADMIT_Interview_Question_Bank.md   # Questions for gathering KB content from SACLI offices
├── ADMIT_System_Build_Spec.md         # Original system design brief
├── TESTING.md
└── DEPLOYMENT.md
```

---

## Admin Access

| Field | Value |
|---|---|
| URL | /admin/login |
| Username | admin |
| Password | See `.env` ↁE`ADMIN_PASSWORD` |

---

## Environment Variables

All variables live in the root `.env` file (gitignored). See `.env.example` for the full list. Key variables:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Supabase PostgreSQL (pooler URL for Render) |
| `GROQ_API_KEY` | Groq API key for LLM generation |
| `JWT_SECRET` | Secret for signing admin JWT tokens |
| `CONFIDENCE_THRESHOLD` | Similarity cutoff for fallback (default: 0.35) |
| `ALLOWED_ORIGINS` | CORS whitelist  Ecomma-separated |

---

## Author

Ortega, D.M.C.  EThesis Project, SACLI, 2026
