# ADMIT System — Full Code Audit Report

**Date:** June 2026  
**Auditor:** Kiro AI Audit Agent  
**Project:** `C:\Users\Asus\Desktop\ADMIT`  
**Scope:** Code quality, architecture, security, dependencies, performance, testing, accessibility

---

## Executive Summary

ADMIT (Admissions & Inquiries Technology) is a well-structured, production-deployed full-stack web application for SACLI (St. Anthony College of Ligao Inc.). The tech stack is modern and appropriate: FastAPI + PostgreSQL/pgvector on the backend, React + Vite + TailwindCSS on the frontend, with a clean RAG (Retrieval-Augmented Generation) pipeline using Groq and fastembed.

**The most critical finding is that a `.env` file containing live production secrets — a real Groq API key, a real Supabase database password, and a JWT signing key — exists in the project root.** Although the file is not currently tracked by git (it is listed in `.gitignore`), the fact that it coexists alongside committed code and deployment documentation creates ongoing exposure risk if it is ever accidentally staged and pushed.

Secondary concerns include: no test suite of any kind, a SQL injection vector in the vector search query, a hardcoded default admin password (`admin123`) baked into committed SQL files, an incomplete analytics query that was abandoned mid-implementation, a hardcoded partial category list in a frontend form, and the `App.css` file containing stale Vite scaffolding code that was never cleaned up.

Overall code quality is solid for a thesis project. The codebase is well-commented, consistently named, logically organized, and the backend separation of concerns (routers / services / models / auth / db) is clean. The most impactful improvements are in security and testing.

---

## 1. Project Overview

### Type & Purpose
A web-based conversational AI chatbot for St. Anthony College of Ligao Inc. (SACLI). Prospective students interact with the chat interface to ask admissions and enrollment questions; a RAG pipeline retrieves relevant knowledge base entries and passes them to an LLM for grounded response generation. Administrators manage the knowledge base, review conversation logs, and monitor system analytics through a protected dashboard.

### Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 8, TailwindCSS 4, React Router 7, Recharts 3, Axios 1.18, uuid 14 |
| Backend | FastAPI 0.115, Python 3.11, Uvicorn 0.32 |
| Database | PostgreSQL (Supabase) + pgvector 0.3.5 |
| ORM | SQLAlchemy 2.0 (async, asyncpg) |
| Embeddings | fastembed 0.3.6, model: BAAI/bge-small-en-v1.5 (384-dim) |
| LLM | Groq API, model: llama-3.1-8b-instant |
| Auth | python-jose (JWT HS256), bcrypt via passlib/bcrypt |
| Deployment | Frontend → Vercel, Backend → Render, DB → Supabase |

### Project Structure (high-level)
```
ADMIT/
├── backend/               # FastAPI application
│   ├── main.py            # App entry point, middleware, CORS, lifecycle
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── render.yaml
│   ├── auth/jwt_handler.py
│   ├── db/
│   │   ├── database.py      # Engine, session, init_db
│   │   ├── init_db.py       # CLI init script
│   │   ├── seed_data.py     # CLI seed script
│   │   └── supabase_migration.sql
│   ├── models/
│   │   ├── schemas.py       # SQLAlchemy ORM models
│   │   └── pydantic_schemas.py  # Pydantic request/response models
│   ├── routers/
│   │   ├── chat.py          # Public chat endpoint (RAG orchestration)
│   │   └── admin.py         # KB CRUD, logs, analytics (JWT-protected)
│   └── services/
│       ├── embeddings.py    # fastembed wrapper
│       ├── llm.py           # Groq client, prompt builder, fallback
│       └── retrieval.py     # pgvector search, confidence scoring
└── frontend/              # React/Vite SPA
    ├── src/
    │   ├── App.jsx          # Router
    │   ├── main.jsx
    │   ├── api/
    │   │   ├── chatApi.js   # Axios client for /api/chat
    │   │   └── adminApi.js  # Axios client + JWT interceptor for admin
    │   ├── components/
    │   │   ├── ChatWindow.jsx
    │   │   ├── MessageBubble.jsx
    │   │   ├── QuickReplyButtons.jsx
    │   │   ├── TypingIndicator.jsx
    │   │   └── admin/
    │   │       ├── KBEditor.jsx
    │   │       ├── KBTable.jsx
    │   │       ├── LogsViewer.jsx
    │   │       └── AnalyticsDashboard.jsx
    └── pages/
        ├── ChatPage.jsx
        ├── LoginPage.jsx
        └── AdminDashboard.jsx
```

---

## 2. Code Quality

### Organization & Naming
**Good.** The backend follows a clean layered architecture: routers → services → models → db → auth. Every file has a module-level docstring. Function names are descriptive (`retrieve_relevant_context`, `build_fallback_message`, `get_current_user`). The frontend separates API clients (`api/`), pages (`pages/`), and components (`components/`) cleanly.

### DRY / Code Duplication
**Minor issue.** The categories list in `frontend/src/components/admin/KBEditor.jsx` is hardcoded as a partial subset of 7 categories (`id: 1, 2, 3, 7, 13, 19, 25`) rather than fetched from the API. The full 27-category list exists in `backend/db/supabase_migration.sql`, `backend/db/seed_data.py`, and inline in `backend/main.py`'s `/setup` endpoint. This creates a maintenance burden: adding a new category requires updating four places.

```jsx
// KBEditor.jsx line 14 — only 7 of 27 categories exposed in the UI
const categories = [
  { id: 1, name: 'Admission Requirements', department: 'IBED' },
  { id: 2, name: 'Enrollment Steps', department: 'IBED' },
  ...
```

### Dead Code
**Minor issue.** `frontend/src/App.css` contains the full Vite/React scaffolding template CSS (`.counter`, `.hero`, `.vite`, `#center`, `#next-steps`, etc.) that was never removed after project creation. It is imported in `main.jsx` but applies to no components in the application.

`frontend/src/assets/react.svg`, `frontend/src/assets/vite.svg`, and `frontend/src/assets/hero.png` appear to be unmodified scaffolding assets that are not used by any component.

### Incomplete Implementation
**Major issue.** In `backend/routers/admin.py`, the `get_analytics` endpoint contains an abandoned SQL query for top unanswered queries that was never completed, and `top_unanswered` is always returned as an empty list:

```python
# admin.py lines ~230-245
top_unanswered_query = select(
    Message.content,
    func.count(Message.id).label("count")
).where(...).join(
    Message,   # self-join — this is logically incorrect
    ...
).group_by(Message.content)...

# Simplified: just get fallback user messages
top_unanswered = []  # ← never computed, always empty
```

The self-join `Message.join(Message, ...)` would join the table to itself on `conversation_id == conversation_id`, which is semantically wrong. The feature is silently disabled.

### Error Handling
**Good overall.** All async endpoints use try/except and return structured error dicts with error codes. The `get_db` dependency rolls back on exception. LLM failures fall back gracefully rather than crashing.

**Minor issue.** `backend/services/embeddings.py` truncates text silently at 5000 characters without warning the caller or logging the truncation:

```python
if len(text) > 5000:
    text = text[:5000]   # silent truncation
```

### Comments & Documentation
**Good.** Every Python module has a docstring. All significant functions have docstrings with Args/Returns/Raises where appropriate. JSDoc-style `/** */` comments on React components and API functions are consistent.

### TypeScript / Type Safety
The frontend uses plain JavaScript with no TypeScript. Given the project's academic scope this is acceptable, but PropTypes are also absent from all React components, meaning no runtime type checking on component props.

---

## 3. Architecture & Design

### Backend Architecture
The backend is well-structured. `main.py` handles application lifecycle, CORS, and routing registration. Routers delegate to service functions rather than containing business logic directly. The RAG pipeline flow in `chat.py` is clearly commented and easy to follow:  
`input → embed → pgvector search → confidence check → LLM/fallback → log → respond`.

### Frontend Architecture
Simple and appropriate for the project size. Three pages, a handful of components, two API client modules. State is managed with local React state and `localStorage` (session ID, auth token), which is appropriate for this scale.

**Route guard weakness:** `AdminDashboard.jsx` uses `useEffect` to redirect unauthenticated users, but the check is `!!localStorage.getItem('admit_admin_token')` — it only tests token presence, not validity. An expired or invalid token will pass this check; the actual validation happens on the first API call. This means a brief flash of the dashboard UI is visible before the 401 redirect fires.

### State Management
Local `useState` throughout. No Redux, Zustand, or Context API. This is the right call for this scope.

### API Integration
Axios instances are created in `chatApi.js` and `adminApi.js` with appropriate `baseURL`, timeout, and content-type headers. The admin client correctly adds the JWT via a request interceptor and handles 401 with a response interceptor. This is a well-implemented pattern.

### Routing
React Router v7 with three routes. No lazy loading (`React.lazy`). The admin route has no client-side route guard beyond the `useEffect` check (see above).

### Anti-Patterns
1. **`/debug-env` endpoint left in production code** (`main.py` line ~75). This endpoint exposes partial database credentials (first 4 chars of password). It was added for debugging a deployment issue and never removed.
2. **`/setup` endpoint is unauthenticated** (`main.py`). This endpoint creates database tables and seeds an admin user with a known password. If called on a live system it could overwrite the admin password hash. It has no authentication guard.
3. **SQL injection in pgvector query** (see Security section).

---

## 4. Security

### CRITICAL — Hardcoded Production Secrets in `.env`
`C:\Users\Asus\Desktop\ADMIT\.env` contains live production credentials:

```
DATABASE_URL="postgresql+asyncpg://postgres.<redacted>:<redacted>@aws-0-ap-southeast-2.pooler.supabase.com:..."
GROQ_API_KEY="<redacted>"
JWT_SECRET="<redacted>"
```

The `.gitignore` does list `.env`, and the file is not currently tracked by git. However:
- The file exists in the working directory with real credentials while the repo is also a git repo.
- The Groq API key should be considered **compromised** due to its prior exposure, and rotated immediately.
- The Supabase database password and JWT secret should similarly be rotated.

### CRITICAL — SQL Injection in pgvector Query
`backend/services/retrieval.py` constructs a raw SQL query by string-interpolating the embedding vector directly into the query text:

```python
# retrieval.py lines ~58-72
embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
query = text(f"""
    SELECT ...
    FROM knowledge_base kb
    WHERE kb.is_active = true
    ORDER BY kb.embedding <=> '{embedding_str}'::vector
    LIMIT :top_k
""")
```

The `embedding_str` comes from user input (the user's chat message is embedded and the embedding is then injected into the query). While embeddings are floating-point numbers that are unlikely to contain SQL in practice, this pattern is architecturally incorrect and violates parameterized query rules. A future refactor or a library change that produces non-float embedding values could introduce a real injection path. The code comment even acknowledges this: *"Use raw vector literal instead of parameter binding for the embedding — asyncpg doesn't support ::vector casting with named parameters."* A safer approach is to use a PostgreSQL cast function or a custom type adapter.

### HIGH — Default Admin Password Committed to Source
`backend/db/supabase_migration.sql` contains a hardcoded bcrypt hash of `admin123`:

```sql
INSERT INTO admin_users (username, password_hash, role) VALUES
  ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PtefO2', 'admin')
```

The hash maps to `admin123`. This is committed to the public repository (the repo is connected to GitHub per the deployment docs). Any attacker who obtains the database connection string can verify this hash easily. The `DEPLOYMENT.md` does remind the user to change the password after first login, but it remains in the git history permanently.

### HIGH — Unauthenticated `/setup` Endpoint
`backend/main.py` exposes `POST /setup` with no authentication. This endpoint:
1. Creates database tables.
2. Seeds the admin user with `admin/admin123` (overwriting any existing password hash on conflict).

An unauthenticated external actor who discovers this endpoint can reset the admin credentials at any time. This should require a one-time setup token or be removed entirely after initial deployment.

### MEDIUM — `/debug-env` Endpoint in Production
`backend/main.py` exposes `GET /debug-env`, which returns a partially-masked database URL. The masking shows only `password[:4]` then `***`, but this leaks the beginning of the password. This is a debugging endpoint that was never removed before deployment. It should be deleted.

### MEDIUM — JWT Token Stored in `localStorage`
`adminApi.js` stores the JWT in `localStorage.setItem('admit_admin_token', ...)`. This is accessible to any JavaScript on the page, making it vulnerable to XSS-based token theft. The industry-standard alternative is an `httpOnly` cookie, which is inaccessible to JavaScript. Given the admin-only scope and thesis context this is lower priority, but is worth noting.

### MEDIUM — `isAuthenticated()` Does Not Validate Token
```javascript
// adminApi.js
export const isAuthenticated = () => {
  return !!localStorage.getItem('admit_admin_token');
};
```
This only checks for token presence. An expired token will pass this check, causing a flash of the admin dashboard before the first API call returns a 401. The fix is to decode the token client-side and check the `exp` claim before rendering.

### LOW — CORS `expose_headers=["*"]`
`main.py` sets `expose_headers=["*"]`. This exposes all response headers to client JavaScript, including any sensitive headers that might be added later. It should be scoped to only headers the client actually needs.

### LOW — `datetime.utcnow()` Deprecated
Multiple files use `datetime.utcnow()` (deprecated in Python 3.12+). This should be replaced with `datetime.now(timezone.utc)`.

### Input Validation
The `ChatRequest` model limits `message` to 500 characters (`max_length=500`). This is enforced by Pydantic. `KBEntryCreate` and `KBEntryUpdate` also have appropriate `min_length`/`max_length` constraints. No XSS sanitization is performed, but the React frontend renders bot content as `whitespace-pre-wrap` text (not `dangerouslySetInnerHTML`), so XSS via the chat content is not a concern.

### Sensitive Data Exposure
The `/health` endpoint returns the list of all table names and admin user count. While not directly harmful, it reveals internal schema information to unauthenticated callers.

---

## 5. Dependencies

### Backend (`backend/requirements.txt`)

| Package | Version | Notes |
|---|---|---|
| fastapi | 0.115.6 | Current |
| uvicorn[standard] | 0.32.1 | Current |
| sqlalchemy | 2.0.36 | Current |
| asyncpg | 0.30.0 | Current |
| psycopg2-binary | 2.9.10 | Likely unused (asyncpg is the async driver; psycopg2 would only be needed for sync code) |
| pgvector | 0.3.5 | Current |
| fastembed | 0.3.6 | Current |
| groq | 0.9.0 | Pinned old version (current is 0.28+). Pinned to avoid httpx compatibility issues, per commit history |
| httpx | 0.27.2 | Pinned old version for same reason |
| python-jose[cryptography] | 3.3.0 | Last release 2021. The `python-jose` library has known security vulnerabilities (CVE-2022-29217 — algorithm confusion on EC keys). Since only HS256 is used, the specific CVE is not directly exploitable here, but migration to `PyJWT` or `authlib` is recommended |
| passlib[bcrypt] | 1.7.4 | Last release 2022, maintenance-mode. Imported in `seed_data.py` but `auth/jwt_handler.py` uses `bcrypt` directly. Dual password-hashing paths exist |
| pydantic | 2.11.5 | Current |
| python-multipart | 0.0.17 | Current |

**Unused dependency:** `psycopg2-binary` is included but the application exclusively uses `asyncpg` for database connections. This can be removed.

**Dual bcrypt paths:** `auth/jwt_handler.py` uses `import bcrypt` directly and calls `bcrypt.hashpw/checkpw`. `db/seed_data.py` uses `passlib.context.CryptContext(schemes=["bcrypt"])`. This inconsistency means two separate codepaths hash passwords differently (though both correctly use bcrypt). They should be unified — preferably using the `auth/jwt_handler.py` approach via `hash_password()` everywhere, which already works correctly.

### Frontend (`frontend/package.json`)

| Package | Version | Notes |
|---|---|---|
| react | ^19.2.7 | Current (React 19 is latest stable) |
| react-dom | ^19.2.7 | Current |
| react-router-dom | ^7.18.1 | Current |
| axios | ^1.18.1 | Current |
| recharts | ^3.9.2 | Current |
| uuid | ^14.0.1 | Current |
| vite | ^8.1.1 | Current |
| tailwindcss | ^4.3.2 | Current (v4 beta/RC) |

The `recharts` import in `package.json` is listed as a dependency but is **not used anywhere in the current source code.** No component imports from `recharts`. It should be removed.

The `^` (caret) version ranges in production dependencies mean `npm install` could install newer patch or minor versions that may introduce breaking changes. For a production deployment, pinning exact versions is safer.

---

## 6. Performance

### Embedding Model Load Time
`services/embeddings.py` loads the BAAI/bge-small-en-v1.5 model globally at startup via the FastAPI lifespan event. This is the correct pattern — the model is loaded once and cached in the global `_model` variable. The `fastembed` library was specifically chosen over `sentence-transformers` to avoid PyTorch OOM on Render's free tier (per commit `b1df90a`). This is a good, pragmatic decision.

### Text Truncation
`embed()` silently truncates text to 5000 characters. For KB entries this is unlikely to be an issue; entries should be far shorter. However, there is no index on embedding vector size and no enforcement at the database schema level.

### pgvector Index
`init_db.py` creates an `ivfflat` index with `lists = 100` for cosine similarity. This is appropriate for a small KB (< 10k entries). For a thesis evaluation dataset this will be fast.

### No Caching
Quick replies are fetched from the backend on every initial chat page load. Since they are static, they could be cached client-side or served as a constant. This is a micro-optimization for a thesis project.

### Large Assets in `/public`
`frontend/public/bg-video.mp4` is a background video served as a static asset. Videos can be large; no information about its file size is available from the audit, but this should be compressed (H.265/AV1) and served with appropriate `Cache-Control` headers if deployed to production at scale.

### Fallback Rate Filter (Logs)
In `admin.py` `get_conversation_logs`, the `fallback_only` filter is applied **after** fetching data from the database (Python-side filtering), not in the SQL query:

```python
if fallback_only:
    conversations = [
        conv for conv in conversations
        if any(msg.was_fallback for msg in conv.messages if msg.sender == "bot")
    ]
```

This is O(n) post-fetch filtering. For large log volumes this wastes both database bandwidth and API memory. The filter should be pushed into the SQL query using a subquery or EXISTS clause.

---

## 7. Testing

### Test Coverage: None
There are no test files anywhere in the project. The `README.md` references `pytest` for backend and `npm run test` for frontend, but neither is configured:
- No `tests/` or `test_*.py` files exist in `backend/`.
- No test runner is configured in `frontend/package.json` (no `vitest`, `jest`, or similar).
- The CI workflow (`deploy.yml`) runs `pytest --tb=short || true` — the `|| true` makes it non-blocking, so no tests means no CI failure.

This is the single biggest quality gap for a production RAG system. The RAG pipeline, confidence scoring, JWT validation, and admin CRUD operations all have zero automated test coverage.

### What Should Be Tested
At minimum:
- `services/retrieval.py`: `calculate_confidence`, `is_high_confidence` with boundary values around the 0.35 threshold.
- `services/llm.py`: `validate_response` (hallucination detection), `build_fallback_message` (office routing by keyword).
- `auth/jwt_handler.py`: `hash_password`/`verify_password` round-trip, `create_access_token`/`decode_token`, expired token rejection.
- `routers/chat.py`: POST `/api/chat` with mocked db and services — test high confidence path, low confidence fallback path, session management.
- `routers/admin.py`: Login with correct and incorrect credentials, JWT-protected endpoint rejection without token.

---

## 8. Accessibility

### Positive
- All `<img>` tags have `alt` attributes (`alt="SACLI Logo"`).
- Form inputs have associated `<label>` elements.
- The login form uses `type="password"` and `required` correctly.
- Buttons have descriptive text content.
- Error messages are visible and use appropriate color contrast (red on white).

### Concerns
- **No `aria-live` region for chat messages.** Screen readers will not announce incoming bot responses. The chat interface should wrap the messages area in `aria-live="polite"` so assistive technology reads new messages aloud.
- **No keyboard focus management.** After sending a message, focus remains on the input field (which is acceptable), but the send button has no visible focus ring override (relies on browser default via Tailwind's `focus:ring-2` which may be removed by `focus:outline-none`).
- **Background video has no `prefers-reduced-motion` check.** Users who have requested reduced motion (vestibular disorder accommodations) will still see the autoplay background video. `@media (prefers-reduced-motion: reduce)` should pause or hide it.
- **Color contrast.** Some text uses `text-white/40` and `text-white/30` opacity variants over a semi-transparent dark overlay. These low-opacity white texts may fail WCAG AA (4.5:1) contrast ratio requirements for body text, depending on the video frame behind them. Manual testing with a contrast checker is required.
- **Emoji used as icons.** Several emoji are used as UI icons (`📚`, `💬`, `📊`, `🎓`). These should have `aria-hidden="true"` if purely decorative, or `aria-label` if they convey meaning.
- **No `<html lang="...">` attribute.** `frontend/index.html` does not set a `lang` attribute on the `<html>` element, which is a WCAG 2.1 Level A failure (Success Criterion 3.1.1).

---

## 9. Issues & Recommendations

### Critical (Must Fix)

**C-1: Rotate all production secrets immediately.**
`C:\Users\Asus\Desktop\ADMIT\.env` contains a live Groq API key (value redacted), Supabase database password, and JWT secret. Even though the file is not in git, these secrets have been read during this audit and should be considered observed. Rotate all three in their respective service dashboards (Groq Console, Supabase Dashboard, and regenerate the JWT secret with `openssl rand -hex 32` then redeploy to Render).

**C-2: Remove or authenticate the `/setup` endpoint.**
`POST /setup` in `main.py` can reset admin credentials without authentication. Add a `Depends(get_current_user)` guard, protect it with a one-time setup token environment variable, or delete it entirely now that the database is initialized.

**C-3: Remove the `/debug-env` endpoint.**
`GET /debug-env` in `main.py` exposes partial database credentials. Delete this endpoint.

**C-4: Fix SQL injection risk in vector search.**
`backend/services/retrieval.py` interpolates `embedding_str` directly into the SQL query. Use SQLAlchemy's `cast` with a pgvector type adapter or register a custom asyncpg type codec to pass the embedding safely as a parameter rather than via f-string interpolation.

### Major (Should Fix)

**M-1: Add a basic test suite.**
The absence of tests is the biggest quality gap. Add at minimum unit tests for `retrieval.py` confidence functions, `llm.py` validation and fallback routing, and `jwt_handler.py` authentication flows using `pytest` + `pytest-asyncio`. The CI workflow already has pytest configured; it just needs test files.

**M-2: Migrate from `python-jose` to `PyJWT` or `authlib`.**
`python-jose` 3.3.0 is in maintenance mode and has known CVEs. Replace with `PyJWT>=2.8.0` or `authlib` for JWT encoding/decoding. The API is similar; `jwt.encode`/`jwt.decode` calls in `jwt_handler.py` are the only lines to change.

**M-3: Fix the top unanswered queries analytics.**
The `top_unanswered_queries` field in the analytics response is always an empty list. Implement it properly: query `Message` rows where `sender='user'` and the next bot message in the same conversation had `was_fallback=True`, group by content, and order by count descending.

**M-4: Fetch categories from the API in `KBEditor.jsx`.**
Replace the hardcoded 7-item list with `GET /api/admin/kb/categories` (which would need to be added, or reuse existing data from the list endpoint) to ensure all 27 categories are available and stay in sync with the database.

**M-5: Push the `fallback_only` filter into SQL.**
In `admin.py` `get_conversation_logs`, move the fallback filter from Python post-processing to a SQL subquery. This is important for correctness too — the current implementation applies the filter after pagination, meaning page 1 with `fallback_only=true` may return fewer than `per_page` items even when more fallback conversations exist on page 2+.

### Minor (Improvements)

**m-1: Remove dead code from `App.css`.**
Delete all Vite scaffolding CSS from `frontend/src/App.css` and remove unused scaffolding assets (`react.svg`, `vite.svg`, `hero.png`).

**m-2: Remove `recharts` dependency.**
`recharts` appears in `package.json` as a dependency but is not imported anywhere. Remove it with `npm uninstall recharts`.

**m-3: Remove `psycopg2-binary` from backend requirements.**
The backend uses `asyncpg` exclusively. `psycopg2-binary` adds unnecessary installation weight and a native extension build step. Remove it from `requirements.txt`.

**m-4: Unify bcrypt usage.**
`db/seed_data.py` uses `passlib.CryptContext` while `auth/jwt_handler.py` uses `bcrypt` directly. Change `seed_data.py` to call `from auth.jwt_handler import hash_password` instead of using its own hashing, then remove the `passlib` import from that file.

**m-5: Replace `datetime.utcnow()` with timezone-aware datetimes.**
`datetime.utcnow()` is deprecated in Python 3.12. Replace with `datetime.now(timezone.utc)` in `admin.py`, `schemas.py`, and `jwt_handler.py`.

**m-6: Add `lang` attribute to `index.html`.**
Add `lang="en"` (or `lang="fil"` if the primary language is Filipino) to the `<html>` tag in `frontend/index.html`. This is a WCAG 2.1 Level A requirement.

**m-7: Add `aria-live` to chat message area.**
Wrap the messages container in `ChatWindow.jsx` with `aria-live="polite"` so screen readers announce new messages.

**m-8: Add `prefers-reduced-motion` handling for the background video.**
In `ChatWindow.jsx` and `LoginPage.jsx`, conditionally render or pause the `<video>` element when `window.matchMedia('(prefers-reduced-motion: reduce)').matches` is true.

**m-9: Pin exact dependency versions in `package.json`.**
Change `^` caret ranges to exact versions for production dependencies to ensure reproducible builds.

**m-10: Upgrade `groq` and `httpx` when Render's environment allows.**
Both are pinned to old versions due to a compatibility issue resolved in commit history. Periodically check whether newer versions are compatible and upgrade.

**m-11: Improve token validation in `isAuthenticated()`.**
Decode the JWT client-side and check the `exp` claim to avoid the brief dashboard flash on expired tokens.

---

## 10. Quick Wins (< 30 minutes each)

1. Delete `GET /debug-env` from `main.py`. One-line removal.
2. Add `lang="en"` to `<html>` in `frontend/index.html`.
3. Delete `App.css` content and remove unused asset imports.
4. Remove `recharts` from `package.json`.
5. Remove `psycopg2-binary` from `requirements.txt`.
6. Add `aria-live="polite"` to the messages container in `ChatWindow.jsx`.
7. Add `|| true` guard removal and a real `pytest` test file (even a single smoke test that imports the app) so CI actually verifies something.

---

*Full validation of WCAG compliance requires manual testing with assistive technologies (NVDA, VoiceOver, JAWS) and expert accessibility review beyond the static analysis performed here.*
