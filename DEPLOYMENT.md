# ADMIT  EDeployment Guide

ADMIT is deployed across three free-tier services:

| Service | Platform | URL |
|---|---|---|
| Frontend | Vercel | https://admit-system.vercel.app |
| Backend | Render | https://admit-system-backend.onrender.com |
| Database | Supabase | PostgreSQL + pgvector |

---

## Current Deployment State

The system is already deployed. This guide covers:
- How the services are connected
- How to trigger redeployments
- How to update environment variables
- What to do if a service goes down

---

## Architecture

```
Browser ↁEVercel (React SPA)
              ↁEHTTPS REST
         Render (FastAPI)
              ↁEasyncpg + SSL
         Supabase (PostgreSQL + pgvector)
              ↁE
         Groq API (LLM generation)
```

---

## Frontend  EVercel

### Auto-deploy
Vercel is connected to the GitHub repo and auto-deploys on every push to `main`. No manual action needed.

### Manual redeploy
1. Go to https://vercel.com ↁEyour project ↁE**Deployments**
2. Click the latest deployment ↁE**Redeploy**

### Environment variables (Vercel dashboard)
| Variable | Value |
|---|---|
| `VITE_API_BASE_URL` | `https://admit-system-backend.onrender.com` |

To update: Vercel Dashboard ↁEProject ↁE**Settings ↁEEnvironment Variables**

### Build settings
- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Framework: Vite

---

## Backend  ERender

### Auto-deploy
Render is connected to the GitHub repo (`backend/` subdirectory) and auto-deploys on push to `main`.

> ⚠�E�EIf auto-deploy is not triggering, go to Render Dashboard ↁE`admit-backend` ↁE**Manual Deploy ↁEDeploy latest commit**

### Environment variables (Render dashboard)
Go to Render ↁE`admit-backend` ↁE**Environment**

| Variable | Value |
|---|---|
| `DATABASE_URL` | Supabase pooler URL (`postgresql+asyncpg://...pooler.supabase.com...`) |
| `GROQ_API_KEY` | Your Groq API key |
| `JWT_SECRET` | 64-char hex string |
| `JWT_EXPIRATION_HOURS` | `24` |
| `CONFIDENCE_THRESHOLD` | `0.35` |
| `ALLOWED_ORIGINS` | `https://admit-system.vercel.app,http://localhost:5173` |

After saving, Render triggers an automatic redeploy.

### Service settings
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Runtime: Python 3.11

### Free tier behavior
- Render spins down after **15 minutes of inactivity** ↁEfirst request after sleep takes ~30s
- The GitHub Actions keepalive (`.github/workflows/keepalive.yml`) pings `/health` every 3 days, which is enough to prevent Supabase from pausing but NOT enough to keep Render warm 24/7
- For always-on performance, upgrade Render to a paid plan or use UptimeRobot to ping every 5 minutes

---

## Database  ESupabase

### Connection
The backend uses the **transaction pooler URL** (port 5432) which is compatible with asyncpg. The direct connection URL (port 5432 on `db.*.supabase.co`) is for local scripts and migrations only.

### Free tier behavior
- Supabase **pauses after 7 days of inactivity**
- The keepalive GitHub Action prevents this by querying the DB every 3 days via the `/health` endpoint
- UptimeRobot pinging the backend every 5 minutes also keeps it active

### To unpause manually
1. Go to https://supabase.com ↁEyour project
2. Click **Restore project** in the paused banner
3. Wait ~2 minutes for it to come back up

### Running migrations
Use the direct connection URL from Supabase ↁESettings ↁEDatabase ↁEDirect connection:
```bash
cd backend
venv\Scripts\activate
# Set DATABASE_URL to the direct connection URL temporarily
python db/init_db.py
```

### Seeding KB content
```bash
cd backend
venv\Scripts\activate
python db/seed_data.py
```
Safe to re-run  Eskips existing categories and entries, only inserts missing ones.

---

## Groq API

- Free tier: rate-limited but sufficient for thesis evaluation
- Current model: `openai/gpt-oss-20b` (1000 t/s, free tier)
- To change the model: update `MODEL_NAME` in `backend/services/llm.py`
- Available models: https://console.groq.com/docs/models

---

## Keepalive  EGitHub Actions

`.github/workflows/keepalive.yml` runs every 3 days and pings `/health`.

To trigger manually:
1. Go to GitHub repo ↁE**Actions** ↁE**Keep Services Alive**
2. Click **Run workflow ↁERun workflow**

---

## Monitoring  EUptimeRobot

UptimeRobot monitors `https://admit-system-backend.onrender.com/health` every 5 minutes.
- If the backend goes down, you receive an email alert
- 5-minute pings also prevent Render spin-down and Supabase pause

---

## Deploying Changes

### Normal workflow
```bash
# Make your changes locally
git add <files>
git commit -m "your message"
git push origin main
# Vercel and Render auto-deploy from GitHub
```

### After changing backend Python dependencies
```bash
# Update requirements.txt
pip freeze > requirements.txt   # or edit manually with pinned versions
git add backend/requirements.txt
git commit -m "chore: update dependencies"
git push origin main
```

### After adding new KB content
Re-run the seed script locally (connects to live Supabase):
```bash
cd backend
venv\Scripts\activate
python db/seed_data.py
```
No redeployment needed  Ethe KB is in the database, not in the code.

---

## Rollback

To roll back to a previous version:
```bash
# Find the commit hash to roll back to
git log --oneline -10

# Reset to that commit (keep changes staged)
git revert <commit-hash>
git push origin main
```

Or via Vercel/Render dashboards  Eboth keep deployment history and allow one-click rollback.

---

## Checklist Before Going Live for Evaluation

- [ ] Change admin password from `admin123` to something strong
- [ ] Verify `https://admit-system-backend.onrender.com/health` shows `kb_entries_active: 35`
- [ ] Test at least 5 in-scope questions return real answers
- [ ] Test 2 out-of-scope questions return the fallback message
- [ ] Confirm UptimeRobot is actively monitoring
- [ ] Remove or gate `/debug/retrieval` endpoint in `main.py` before public launch
- [ ] Add a privacy notice to the chat page (RA 10173 compliance)
