# Review — ADMIT RAG Chatbot Enhancements

Workflow: `wf_131ae293a8a75d38`
Verdict: **APPROVED** — no blockers remain.

## Recorded verification evidence
The `code` step's final message records that all verification passed: Python
syntax checks, backend imports, and the frontend (Vite) build. These match the
three required verification categories (syntax / import / build). Per
instructions the suites were not re-run; the changed files were read directly
and are consistent with a passing build.

## Feature 1 — Source citations in chat UI
- `backend/models/pydantic_schemas.py`: `matched_kb_titles: List[str]` added to
  `ChatResponse` with `default_factory=list` (empty-list default). Additive; no
  other schema fields touched. ✓
- `backend/routers/chat.py` (`/api/chat`): on high confidence
  `matched_kb_titles = [match.title for match in matches]`; on low confidence
  and on LLM-generation failure `matched_kb_titles = []` with
  `was_fallback = True`. Titles are therefore only populated when
  `was_fallback` is False, exactly as specified. `KBMatch.title` is a real
  attribute (confirmed in `services/retrieval.py`). ✓
- `frontend/src/components/MessageBubble.jsx`: optional `sources` prop; renders a
  muted "Sources:" block with chip/badge per source and an open-book SVG icon,
  only for bot messages (`!isUser && sources && sources.length > 0`). ✓
- `frontend/src/components/ChatWindow.jsx`: both the non-streaming and streaming
  paths attach `sources` from `matched_kb_titles` to the bot message and pass it
  to `MessageBubble`. ✓
- `frontend/src/api/chatApi.js`: `sendMessage` normalizes
  `matched_kb_titles` (defaults to `[]`). ✓

## Feature 2 — Fix top unanswered queries analytics
- `backend/routers/admin.py` `get_analytics`: the old self-join was replaced with
  a correlated `EXISTS` over aliased `UserMsg`/`BotMsg`:
  - `UserMsg.sender == 'user'`, date-bounded by the analytics range.
  - EXISTS a `BotMsg` in the same `conversation_id`, `sender == 'bot'`,
    `was_fallback == True`, with `created_at` in
    `[UserMsg.created_at, UserMsg.created_at + 10s]`.
  - `group_by(UserMsg.content)`, `order_by(count desc)`, `limit(10)`.
  - Result is actually read (`top_unanswered_result.all()`) and mapped into
    `TopUnansweredQuery` objects that populate `top_unanswered_queries`
    (the `AnalyticsResponse` field already existed). ✓
  The EXISTS-with-window form is equivalent to "the immediately following bot
  message was a fallback" under the data model, where each user message yields
  exactly one bot response within ~10s (both `/api/chat` and `/api/chat/stream`
  create one bot message per user message). No reachable over/under-count path.
- `frontend/src/components/admin/AnalyticsDashboard.jsx`: renders
  "Top Unanswered Questions" with per-query frequency (`{query.count}x`) and an
  empty-state. Tailwind-styled, consistent with the dashboard. ✓

## Feature 3 — SSE streaming
- `backend/services/llm.py`: `generate_response_streaming(matches, query)` is a
  generator using `client.chat.completions.create(..., stream=True)`, same
  `build_prompt`/`MODEL_NAME`/`TEMPERATURE`, yielding
  `chunk.choices[0].delta.content` (guarded for empty deltas). No
  `validate_response` call, as required. ✓
- `backend/routers/chat.py`: new `POST /api/chat/stream` returning
  `StreamingResponse(media_type='text/event-stream')`.
  - Same RAG pipeline (`retrieve_relevant_context`), confidence gate, and
    `@limiter.limit("20/minute")` as `/api/chat`. ✓
  - Low confidence: fallback sent as a single `{"token": ...}` event; bot message
    is added+committed in setup; terminal `done` event carries
    `was_fallback:true, matched_kb_ids:[], matched_kb_titles:[]`. ✓
  - High confidence: tokens streamed as `{"token": ...}` events; after the
    stream, the complete bot message is logged via `get_db_context()` (which
    commits on exit — confirmed in `db/database.py`); terminal `done` event
    carries `session_id, was_fallback:false, matched_kb_ids,
    matched_kb_titles`. ✓
  - User message is committed before streaming starts (in setup) for both
    paths. ✓
  - The existing `POST /api/chat` is preserved (only the additive
    `matched_kb_titles` was added). ✓
- `frontend/src/api/chatApi.js`: `sendMessageStream(message, sessionId, token,
  onToken, onDone)` uses `fetch` + `response.body.getReader()` (not axios),
  parses SSE frames split on `\n\n`, calls `onToken` per token and `onDone` on
  the terminal `done` event; throws on `payload.error` / non-OK response. ✓
  (The extra `token` arg is additive auth parity with `sendMessage`; callers
  pass it positionally.)
- `frontend/src/components/ChatWindow.jsx`: `useStreaming` toggle; a bot
  placeholder is created on first token and grown token-by-token; the typing
  indicator is cleared on first token (`setIsLoading(false)`); `onDone`
  writes `wasFallback`/`matchedKbIds`/`sources`; on a pre-token failure the
    non-streaming endpoint is used as fallback (`sendViaRegularEndpoint`). ✓

## Constraints (additive-only)
- DB schema/models: `backend/models/schemas.py` is unchanged (not in `git
  status`). ✓
- Auth/JWT: `backend/routers/auth.py` and `backend/auth/` unchanged. ✓
- Deployment configs `vercel.json`, `render.yaml`, `Dockerfile` and `.env` are
  unchanged (none appear in `git status`). ✓
- Existing non-streaming `POST /api/chat` preserved and still returns a full
  `ChatResponse`. ✓
- The new `/api/chat/stream` applies the same rate limiter. ✓

## Scope note (not a blocker)
`git status` shows two additional modified files beyond the eight declared:
- `backend/db/seed_data.py`: adds three previously-missing GENERAL categories
  (Contact Information, Scholarships, Tuition and Payment) and makes category/KB
  dedup incremental (insert missing-only instead of skip-all). This is an
  additive, benign improvement to a manual seeding script; it does not alter
  DB schema/models, auth, deployment, or `.env`, and introduces no
  correctness/security/data failure. Noting for transparency; not a blocker.
- `.agents/audit-report.md`: documentation only; no runtime impact.

## Findings
None (no reachable correctness, security, or data failures identified).
