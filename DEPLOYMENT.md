# ADMIT Deployment Guide

## Overview
- **Frontend** → Vercel (free tier)
- **Backend** → Render (free tier)
- **Database** → Supabase (free tier, PostgreSQL + pgvector)
- **LLM** → Groq API (free tier)
- **Source Control** → GitHub

---

## Step 1 — Push to GitHub

```bash
# From c:\Users\Asus\Desktop\ADMIT
git init
git add .
git commit -m "Initial commit: ADMIT system"

# Create a new repo on github.com named "admit-system"
git remote add origin https://github.com/YOUR_USERNAME/admit-system.git
git branch -M main
git push -u origin main
```

---

## Step 2 — Set up Supabase (Database)

1. Go to https://supabase.com and create a free account
2. Click **New Project** → name it `admit-db`
3. Set a strong database password and save it
4. Once created, go to **SQL Editor**
5. Paste the entire contents of `backend/db/supabase_migration.sql` and click **Run**
6. Go to **Settings → Database** and copy the **Connection String (URI)**
   - It looks like: `postgresql://postgres:[PASSWORD]@db.xxxx.supabase.co:5432/postgres`
   - Change `postgresql://` to `postgresql+asyncpg://` for async support

---

## Step 3 — Get Groq API Key

1. Go to https://console.groq.com
2. Sign up for a free account
3. Go to **API Keys** → Create new API key
4. Copy and save it securely

---

## Step 4 — Deploy Backend to Render

1. Go to https://render.com and sign in with GitHub
2. Click **New → Web Service**
3. Connect your `admit-system` GitHub repo
4. Configure:
   - **Name**: `admit-backend`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add **Environment Variables**:
   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | Your Supabase connection string (asyncpg) |
   | `GROQ_API_KEY` | Your Groq API key |
   | `JWT_SECRET` | Generate: `openssl rand -hex 32` |
   | `JWT_EXPIRATION_HOURS` | `24` |
   | `CONFIDENCE_THRESHOLD` | `0.35` |
   | `ALLOWED_ORIGINS` | `https://your-app.vercel.app,http://localhost:5173` |
6. Click **Create Web Service**
7. Wait for deployment. Copy the Render URL (e.g. `https://admit-backend.onrender.com`)

---

## Step 5 — Deploy Frontend to Vercel

1. Go to https://vercel.com and sign in with GitHub
2. Click **Add New → Project**
3. Import your `admit-system` repo
4. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add **Environment Variables**:
   | Key | Value |
   |-----|-------|
   | `VITE_API_BASE_URL` | Your Render backend URL |
6. Click **Deploy**
7. Copy your Vercel URL (e.g. `https://admit-system.vercel.app`)

---

## Step 6 — Update CORS on Render

Go back to Render → Environment Variables and update:
```
ALLOWED_ORIGINS = https://admit-system.vercel.app,http://localhost:5173
```

Then click **Save Changes** — Render will auto-redeploy.

---

## Step 7 — Verify Deployment

1. Open your Vercel URL → Chat interface should load
2. Open `https://admit-backend.onrender.com/docs` → API docs should load
3. Go to `/admin/login` and log in with `admin / admin123`
4. **Change the admin password immediately!**

---

## Summary of URLs

| Service | URL |
|---------|-----|
| Chat Interface | `https://admit-system.vercel.app` |
| Admin Dashboard | `https://admit-system.vercel.app/admin/login` |
| API Docs | `https://admit-backend.onrender.com/docs` |
| Health Check | `https://admit-backend.onrender.com/health` |

---

## Notes

- Render free tier **spins down** after 15 mins of inactivity — first request takes ~30s to wake up
- Supabase free tier has a 500MB database limit — more than enough for ADMIT
- Groq free tier has rate limits — sufficient for thesis evaluation
- Change `admin123` password after first login!
