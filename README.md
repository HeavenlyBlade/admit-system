# ADMIT - Conversational AI System for Admissions & Enrollment Assistance

ADMIT (Admissions & Inquiries Technology) is a web-based conversational AI assistant designed to answer admissions and enrollment questions for SACLI (St. Anthony College of Ligao Inc.) using Retrieval-Augmented Generation (RAG).

## System Overview

- **Frontend**: React + Vite + TailwindCSS
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with pgvector extension
- **LLM**: Groq API (Llama 3.1)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)

## Features

- Public chat interface with quick-reply buttons
- RAG pipeline for grounded, accurate responses
- Semantic search using pgvector
- Admin dashboard for knowledge base management
- Conversation logging and analytics
- Fallback mechanism for out-of-scope queries
- JWT authentication for admin users

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ with pgvector extension
- Groq API key

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

5. Configure environment variables in `.env`:
   - `DATABASE_URL`: PostgreSQL connection string
   - `GROQ_API_KEY`: Your Groq API key
   - `JWT_SECRET`: Generate with `openssl rand -hex 32`
   - `JWT_EXPIRATION_HOURS`: Token expiration (default: 24)
   - `CONFIDENCE_THRESHOLD`: Confidence threshold for fallback (default: 0.35)

6. Initialize database:
```bash
python db/init_db.py
python db/seed_data.py
```

7. Run development server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API documentation will be available at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

4. Run development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Project Structure

### Backend
```
backend/
├── routers/         # API route handlers
├── services/        # Business logic (embedding, retrieval, LLM)
├── models/          # SQLAlchemy ORM models
├── auth/            # JWT authentication
├── db/              # Database connection and initialization
├── main.py          # FastAPI application entry point
└── requirements.txt # Python dependencies
```

### Frontend
```
frontend/
├── src/
│   ├── components/  # React components
│   ├── pages/       # Page components
│   ├── api/         # API client functions
│   └── utils/       # Utility functions
├── index.html
└── package.json
```

## Usage

### For Students/Applicants (Public Chat)

1. Open the chat interface at `http://localhost:5173`
2. Type your question or click a quick-reply button
3. Receive AI-generated responses grounded in SACLI knowledge base

### For Administrators

1. Log in at `http://localhost:5173/admin/login`
2. Manage knowledge base entries (create, edit, deactivate)
3. View conversation logs and analytics
4. Monitor system performance (fallback rate, top unanswered questions)

## Deployment

### Backend (Render)

1. Create `render.yaml` or use Dockerfile
2. Set environment variables in Render dashboard
3. Deploy to Render

### Frontend (Vercel)

1. Connect GitHub repository to Vercel
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Set environment variable: `VITE_API_BASE_URL`

## Environment Variables

### Backend
- `DATABASE_URL`: PostgreSQL connection string with pgvector
- `GROQ_API_KEY`: Groq API key for LLM generation
- `JWT_SECRET`: Secret key for JWT token signing
- `JWT_EXPIRATION_HOURS`: JWT token expiration time (default: 24)
- `CONFIDENCE_THRESHOLD`: Similarity threshold for fallback (default: 0.35)
- `ALLOWED_ORIGINS`: CORS allowed origins (comma-separated)

### Frontend
- `VITE_API_BASE_URL`: Backend API URL

## Development

- Backend auto-reloads on code changes (uvicorn --reload)
- Frontend hot-reloads on code changes (Vite HMR)
- API documentation available at `/docs` (FastAPI auto-generated)

## Testing

### Backend
```bash
pytest
```

### Frontend
```bash
npm run test
```

## License

This project is part of a thesis for SACLI.

## Author

Ortega, D.M.C. - Thesis Project, 2026
