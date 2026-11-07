# ADMIT — Testing Guide

This document covers how to test the ADMIT system: manual testing, backend unit/integration tests, and frontend build verification.

---

## 1. Live System Smoke Test

The quickest check — hit the live endpoints directly.

### Health check
```
GET https://admit-backend.onrender.com/health
```
Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "kb_entries_active": 35,
  "embedding_model_loaded": true
}
```
If `embedding_model_loaded` is `false`, the first chat request will trigger a lazy load (~10s). Subsequent requests will be fast.

### Quick replies
```
GET https://admit-backend.onrender.com/api/quick-replies
```
Should return 6 items (Admission Requirements, Enrollment Steps, Programs Offered, Tuition & Payment, Scholarships, Contact Info).

### Chat endpoint
```bash
curl -X POST https://admit-backend.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What programs does SACLI offer?"}'
```
Expected: `was_fallback: false`, non-empty `matched_kb_ids`, and a real answer from Groq.

---

## 2. Manual Chat Testing (Browser)

Open https://admit-system.vercel.app and test the following:

### In-scope questions (should return real answers, not fallback)
- "What programs does SACLI offer?"
- "How do I enroll at SACLI?"
- "What are the admission requirements for college?"
- "What scholarships are available?"
- "How do I contact the registrar?"
- "Tell me about SACLI's nursing program"
- "What are the SHS strands offered?"
- "How do I apply for TESDA courses?"

For each, verify:
- ✅ Response contains relevant SACLI information
- ✅ Source citation chips appear below the response
- ✅ `was_fallback` is NOT shown (no "Redirected to office" note)
- ✅ Markdown renders correctly (bold text, bullet points, links)

### Out-of-scope questions (should return fallback)
- "What is the weather today?"
- "Tell me a joke"
- "Who is the president of the Philippines?"

For each, verify:
- ✅ Fallback message appears with office contact details
- ✅ "Redirected to office" note is shown

### Quick reply buttons
- Click each of the 6 quick reply buttons
- Verify each triggers a relevant, non-fallback response

### Streaming (if enabled)
- Responses should appear word-by-word rather than all at once
- Typing indicator should disappear once first token arrives

---

## 3. Admin Dashboard Testing

Log in at https://admit-system.vercel.app/admin/login

Credentials: see `.env` → `ADMIN_USERNAME` / `ADMIN_PASSWORD`

### Knowledge Base Management
- [ ] View the list of KB entries (should show 35 active entries)
- [ ] Filter by department (IBED, SHS, HED, TESDA, GENERAL)
- [ ] Create a new KB entry — verify it gets embedded and appears in search
- [ ] Edit an existing entry — verify embedding is regenerated
- [ ] Deactivate an entry — verify it no longer appears in chat responses

### Conversation Logs
- [ ] View logs after sending a few test messages
- [ ] Filter by date range
- [ ] Filter by fallback status (fallback only / answered only)
- [ ] Verify each conversation shows the correct message sequence

### Analytics
- [ ] Fallback rate shows a percentage
- [ ] Total conversations count is accurate
- [ ] Top unanswered queries populates after sending some out-of-scope questions
- [ ] KB coverage percentage is shown

---

## 4. Backend Unit & Integration Tests

Tests are in `backend/tests/`. Run with pytest:

```bash
cd backend
venv\Scripts\activate
pytest tests/ -v --tb=short
```

### Test files
| File | Coverage |
|---|---|
| `test_admin_auth.py` | Admin login, JWT generation, protected route access |
| `test_chat.py` | Chat endpoint, RAG pipeline, fallback mechanism |
| `test_rate_limit.py` | Rate limiting on `/api/chat` |
| `conftest.py` | Shared fixtures (test DB session, mock data) |

### Running a specific test
```bash
pytest tests/test_chat.py -v
pytest tests/test_admin_auth.py::test_login_valid_credentials -v
```

### Environment for tests
Tests require these env vars (set in `.env` or as shell variables):
```
DATABASE_URL=<test DB or live Supabase>
GROQ_API_KEY=<your key>
JWT_SECRET=<any string for testing>
CONFIDENCE_THRESHOLD=0.35
ENVIRONMENT=test
```

---

## 5. Frontend Build Verification

Verify the frontend builds without errors before deploying:

```bash
cd frontend
npm install
npm run build
```

Expected output:
```
✓ built in ~7s
dist/index.html       ~0.5 kB
dist/assets/index.css ~45 kB
dist/assets/index.js  ~450 kB
```

### Lint check
```bash
npm run lint
```

---

## 6. Confidence Threshold Tuning

The `CONFIDENCE_THRESHOLD` env var (default `0.35`) controls when the bot falls back vs. answers.

To tune it:
1. Send test questions and check the similarity scores in Render logs
2. If the bot is falling back on questions it should answer → lower the threshold (e.g. `0.25`)
3. If the bot is answering questions it shouldn't → raise the threshold (e.g. `0.45`)
4. Update in Render → Environment Variables → Save (triggers redeploy)

The debug endpoint can help check similarity scores:
```
GET https://admit-backend.onrender.com/debug/retrieval
```

---

## 7. Regression Checklist (Before Each Deployment)

Run through this before pushing to main:

- [ ] `npm run build` passes in `frontend/`
- [ ] `pytest tests/` passes in `backend/`
- [ ] `/health` endpoint returns `status: healthy`
- [ ] At least 3 in-scope chat questions return real answers
- [ ] Admin login works
- [ ] No console errors in browser DevTools
