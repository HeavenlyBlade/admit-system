# Implementation Plan: ADMIT Conversational AI System

## Overview

This implementation plan converts the ADMIT design into actionable coding tasks organized in 8 phases: project scaffolding, database setup, backend core services (embedding/retrieval/LLM), backend API routers, authentication, frontend chat interface, frontend admin dashboard, and integration/testing. Each task builds incrementally to produce a working RAG-based conversational AI system for SACLI admissions inquiries.

The implementation follows a bottom-up approach: establish infrastructure first (database, environment), then build core RAG pipeline services, expose them through API routers, add authentication, and finally construct frontend interfaces. Testing tasks are integrated throughout to validate each component before moving to dependent layers.

## Tasks

### Phase 1: Project Scaffolding and Environment Setup

- [ ] 1. Initialize project structure and development environment
  - [ ] 1.1 Create backend directory structure (FastAPI)
    - Create `backend/` directory with subdirectories: `routers/`, `services/`, `models/`, `auth/`, `db/`
    - Initialize Python virtual environment and create `requirements.txt` with dependencies: fastapi, uvicorn, sqlalchemy, asyncpg, psycopg2-binary, pgvector, sentence-transformers, python-jose, passlib, bcrypt, groq, python-dotenv, pydantic
    - Create `.env.example` file documenting required environment variables: DATABASE_URL, GROQ_API_KEY, JWT_SECRET, JWT_EXPIRATION_HOURS, CONFIDENCE_THRESHOLD
    - _Requirements: 11.1, 12.1, 12.2, 13.1, 13.2, 13.3, 13.4_

  - [ ] 1.2 Create frontend directory structure (React + Vite)
    - Create `frontend/` directory and initialize Vite project with React template
    - Install dependencies: react, react-dom, react-router-dom, tailwindcss, axios, recharts, uuid
    - Configure TailwindCSS with `tailwind.config.js` and update `index.css`
    - Create subdirectories: `src/components/`, `src/pages/`, `src/api/`, `src/utils/`
    - _Requirements: 11.1, 11.2, 11.3_

  - [ ]* 1.3 Set up development environment configuration
    - Create `.gitignore` files for backend and frontend (exclude .env, __pycache__, node_modules, dist)
    - Document setup instructions in README.md (environment setup, running dev servers, deployment)
    - _Requirements: 13.5, 19.3_

- [ ] 2. Checkpoint - Verify project structure
  - Ensure all directories exist and dependencies install without errors. Ask user if questions arise.


### Phase 2: Database Schema and Models

- [ ] 3. Set up PostgreSQL database with pgvector extension
  - [ ] 3.1 Create database connection service
    - Implement `db/database.py` with SQLAlchemy async engine configuration
    - Create async session factory with connection pooling (pool_size=10, max_overflow=20)
    - Add database initialization function to enable pgvector extension
    - _Requirements: 12.2, 9.1, 9.2_

  - [ ] 3.2 Define SQLAlchemy ORM models
    - Create `models/schemas.py` with ORM models: `KBCategory`, `KnowledgeBase`, `AdminUser`, `Conversation`, `Message`
    - Implement `KnowledgeBase` model with pgvector VECTOR(384) field for embeddings
    - Add relationships (foreign keys) between models as per ER diagram
    - Include CHECK constraints for sender field and department field
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [ ]* 3.3 Write unit tests for ORM models
    - Test model validation (CHECK constraints, NOT NULL constraints)
    - Test default value generation (timestamps, UUIDs, booleans)
    - Test foreign key relationships
    - _Requirements: 9.1-9.6_

- [ ] 4. Create database initialization and migration scripts
  - [ ] 4.1 Implement database schema creation script
    - Create `db/init_db.py` script to create all tables with indexes
    - Add pgvector index creation for embeddings (ivfflat with lists=100)
    - Add B-tree indexes for foreign keys and frequently queried fields
    - _Requirements: 9.1, 9.2_

  - [ ] 4.2 Create seed data script for development
    - Implement `db/seed_data.py` to populate kb_categories table with predefined categories
    - Create sample admin user account (username: admin, password: hashed)
    - Create 5-10 sample KB entries covering different categories
    - _Requirements: 9.3, 9.4_

- [ ] 5. Checkpoint - Verify database schema
  - Run database initialization script. Verify all tables, indexes, and seed data are created. Ask user if questions arise.


### Phase 3: Backend Core Services (Embedding, Retrieval, LLM)

- [ ] 6. Implement embedding service
  - [ ] 6.1 Create sentence-transformers wrapper service
    - Implement `services/embeddings.py` with model loading function (all-MiniLM-L6-v2)
    - Create `embed(text: str) -> List[float]` function to generate 384-dim embeddings
    - Create `batch_embed(texts: List[str]) -> List[List[float]]` for bulk embedding
    - Add model preloading in FastAPI lifespan event for cold-start optimization
    - _Requirements: 2.1, 12.3_

  - [ ]* 6.2 Write unit tests for embedding service
    - Test embedding generation with known inputs (check output dimensions)
    - Test batch embedding consistency
    - Test model caching behavior
    - _Requirements: 2.1_

- [ ] 7. Implement retrieval service
  - [ ] 7.1 Create pgvector semantic search service
    - Implement `services/retrieval.py` with `search_kb(query_embedding, top_k=5)` function
    - Execute pgvector cosine similarity query: `SELECT ... ORDER BY embedding <=> $1 LIMIT 5`
    - Calculate confidence score from best match similarity (normalize to 0-1 range)
    - Return list of matched KB entries with similarity scores
    - _Requirements: 2.2, 2.3, 2.4_

  - [ ]* 7.2 Write unit tests for retrieval service
    - Test similarity search with mock database (verify SQL query construction)
    - Test confidence score calculation with various similarity scores
    - Test top-k ranking order
    - _Requirements: 2.2, 2.3, 2.4_

- [ ] 8. Implement LLM service for response generation
  - [ ] 8.1 Create Groq API integration service
    - Implement `services/llm.py` with `generate_response(context, query)` function
    - Create prompt template with system message and context injection
    - Integrate Groq API client (llama-3.1-8b-instant, temperature=0.3, max_tokens=256)
    - Add response validation to detect hallucination indicators
    - _Requirements: 3.1, 3.2, 3.3, 12.4_

  - [ ] 8.2 Implement fallback message generation
    - Create `build_fallback_message(query)` function with template-based responses
    - Add simple keyword matching to suggest appropriate SACLI office (Registrar, Guidance, Admin)
    - Include office contact details in fallback message
    - _Requirements: 4.1, 4.2, 4.3, 4.5_

  - [ ]* 8.3 Write unit tests for LLM service
    - Test prompt construction with various contexts
    - Mock Groq API to test error handling (API timeout, rate limit)
    - Test response validation logic
    - Test fallback message generation with different query types
    - _Requirements: 3.1-3.5, 4.1-4.5_

- [ ] 9. Checkpoint - Test core services integration
  - Manually test full pipeline: embed query → search KB → generate response. Verify embeddings, similarity scores, and LLM output. Ask user if questions arise.


### Phase 4: Backend API Routers (Chat and Admin)

- [ ] 10. Implement chat router and RAG pipeline orchestration
  - [ ] 10.1 Create chat API endpoints
    - Implement `routers/chat.py` with POST `/api/chat` endpoint
    - Define Pydantic request schema: `{message: str, session_id: Optional[UUID]}`
    - Define Pydantic response schema: `{response: str, session_id: UUID, was_fallback: bool, matched_kb_ids: List[int]}`
    - Orchestrate RAG pipeline: embed query → retrieve KB entries → check confidence → generate or fallback
    - _Requirements: 1.2, 2.1-2.5, 3.1-3.5, 10.1_

  - [ ] 10.2 Implement conversation and message logging
    - Create or retrieve conversation record by session_id
    - Log user message to messages table (sender="user")
    - Log bot response to messages table (sender="bot", matched_kb_ids, was_fallback)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [ ] 10.3 Create quick replies endpoint
    - Implement GET `/api/quick-replies` endpoint
    - Return predefined category queries: Admission Requirements, Enrollment Steps, Programs Offered, Tuition & Payment, Scholarships, Contact Info
    - _Requirements: 1.4, 10.2_

  - [ ]* 10.4 Write integration tests for chat endpoints
    - Test full RAG pipeline with real database and mocked Groq API
    - Test session creation and message logging
    - Test fallback mechanism with low-confidence queries
    - Test error responses (invalid input, API failures)
    - _Requirements: 1.2, 2.1-2.5, 3.1-3.5, 5.1-5.6_

- [ ] 11. Implement admin router for KB management
  - [ ] 11.1 Create KB CRUD endpoints
    - Implement `routers/admin.py` with GET `/api/admin/kb` (list with filters)
    - Implement POST `/api/admin/kb` (create with auto-embedding)
    - Implement PUT `/api/admin/kb/{id}` (update with re-embedding)
    - Implement DELETE `/api/admin/kb/{id}` (soft-delete: set is_active=false)
    - Define Pydantic schemas for KB create/update requests and responses
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 10.4, 10.5, 10.6, 10.7_

  - [ ] 11.2 Create conversation logs retrieval endpoint
    - Implement GET `/api/admin/logs` with query parameters: start_date, end_date, department, fallback_status
    - Join conversations and messages tables to return threaded conversations
    - Add pagination (page, per_page parameters)
    - _Requirements: 8.3, 8.4, 8.5, 10.8_

  - [ ] 11.3 Create analytics computation endpoint
    - Implement GET `/api/admin/analytics` with date range filters
    - Compute fallback rate: `COUNT(was_fallback=true) / COUNT(*)`
    - Query top unanswered questions (group by content where was_fallback=true)
    - Calculate KB coverage percentage (categories with active entries / total categories)
    - _Requirements: 8.1, 8.2, 8.3, 10.9, 20.1_

  - [ ]* 11.4 Write integration tests for admin endpoints
    - Test KB CRUD operations with database transactions
    - Test auto-embedding generation on KB create/update
    - Test conversation log retrieval with filters
    - Test analytics computation accuracy
    - _Requirements: 6.1-6.6, 8.1-8.5_

- [ ] 12. Configure FastAPI application and CORS
  - [ ] 12.1 Create main FastAPI application
    - Implement `main.py` with FastAPI app initialization
    - Register chat router and admin router
    - Add CORS middleware with allowed origins (frontend domain, localhost)
    - Add lifespan event for embedding model preloading
    - _Requirements: 12.1, 16.1, 16.2, 16.3, 16.4, 16.5_

  - [ ]* 12.2 Write unit tests for CORS configuration
    - Test preflight OPTIONS requests
    - Test allowed origins and methods
    - Test Authorization header support
    - _Requirements: 16.1-16.5_

- [ ] 13. Checkpoint - Test API endpoints
  - Use FastAPI's /docs interface to manually test all endpoints. Verify request/response schemas and error handling. Ask user if questions arise.


### Phase 5: Authentication Implementation

- [ ] 14. Implement JWT authentication service
  - [ ] 14.1 Create JWT token generation and validation
    - Implement `auth/jwt_handler.py` with `create_access_token(data, expires_delta)` function
    - Implement `verify_token(token)` function to decode and validate JWT
    - Configure JWT settings: HS256 algorithm, 24-hour expiration, secret from environment variable
    - _Requirements: 7.2, 7.3, 7.5_

  - [ ] 14.2 Create password hashing utilities
    - Implement `hash_password(password)` function using bcrypt
    - Implement `verify_password(plain, hashed)` function
    - Use bcrypt default work factor (12 rounds)
    - _Requirements: 7.4_

  - [ ]* 14.3 Write unit tests for authentication service
    - Test JWT generation with various payloads
    - Test JWT validation with expired/tampered tokens
    - Test password hashing and verification
    - Test bcrypt compatibility
    - _Requirements: 7.2, 7.3, 7.4_

- [ ] 15. Implement admin login endpoint
  - [ ] 15.1 Create login endpoint
    - Implement POST `/api/admin/login` in admin router
    - Define request schema: `{username: str, password: str}`
    - Query admin_users table, verify password, generate JWT token
    - Return response: `{access_token: str, token_type: "bearer"}`
    - _Requirements: 7.1, 7.2, 10.3_

  - [ ] 15.2 Create JWT dependency for protected routes
    - Implement FastAPI dependency to extract and validate JWT from Authorization header
    - Inject user_id into protected route handlers
    - Return HTTP 401 Unauthorized for invalid/missing tokens
    - _Requirements: 7.3, 7.5_

  - [ ] 15.3 Protect admin endpoints with JWT dependency
    - Add JWT dependency to all admin router endpoints (KB CRUD, logs, analytics)
    - Update route handlers to use injected user_id for audit logging
    - _Requirements: 7.5, 6.6_

  - [ ]* 15.4 Write integration tests for authentication
    - Test login with valid credentials (returns token)
    - Test login with invalid credentials (returns 401)
    - Test protected routes without token (returns 401)
    - Test protected routes with valid token (returns 200)
    - Test protected routes with expired token (returns 401)
    - _Requirements: 7.1-7.5_

- [ ] 16. Checkpoint - Test authentication flow
  - Test login flow and JWT validation on protected endpoints. Verify token expiration handling. Ask user if questions arise.


### Phase 6: Frontend Chat Interface

- [ ] 17. Implement chat API client
  - [ ] 17.1 Create API client module
    - Implement `src/api/chatApi.js` with functions: `sendMessage(message, sessionId)`, `getQuickReplies()`
    - Use axios for HTTP requests with base URL configuration
    - Add error handling and timeout configuration
    - _Requirements: 1.2, 10.1, 10.2_

  - [ ]* 17.2 Write unit tests for API client
    - Test request formatting (headers, body, URL construction)
    - Test response parsing
    - Test error handling and retry logic
    - _Requirements: 1.2_

- [ ] 18. Build chat interface components
  - [ ] 18.1 Create ChatWindow component
    - Implement `src/components/ChatWindow.jsx` as main chat container
    - Manage state: messages array, isLoading boolean, sessionId UUID
    - Integrate with chat API client to send/receive messages
    - Handle session ID generation and persistence
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ] 18.2 Create MessageBubble component
    - Implement `src/components/MessageBubble.jsx` for individual messages
    - Accept props: sender ("user" | "bot"), content (string), timestamp (Date)
    - Style with TailwindCSS: user messages right-aligned, bot messages left-aligned
    - _Requirements: 1.3, 11.2_

  - [ ] 18.3 Create TypingIndicator component
    - Implement `src/components/TypingIndicator.jsx` with pulsing three-dot animation
    - Display when isLoading state is true in ChatWindow
    - Use CSS animation for smooth pulsing effect
    - _Requirements: 1.6_

  - [ ] 18.4 Create QuickReplyButtons component
    - Implement `src/components/QuickReplyButtons.jsx` to display category buttons
    - Fetch quick replies from API on mount
    - Accept onSelect callback prop to submit query when button clicked
    - Style buttons with TailwindCSS (grid layout, hover effects)
    - _Requirements: 1.4, 1.5_

  - [ ]* 18.5 Write unit tests for chat components
    - Test MessageBubble renders correctly for user/bot messages
    - Test QuickReplyButtons calls callback on button click
    - Test TypingIndicator displays during loading state
    - Test ChatWindow integrates components correctly
    - _Requirements: 1.1-1.6_

- [ ] 19. Create chat page and routing
  - [ ] 19.1 Implement chat page
    - Create `src/pages/ChatPage.jsx` as root page for public chat
    - Integrate ChatWindow component
    - Add header with SACLI branding and system title
    - Make responsive for desktop and mobile (TailwindCSS breakpoints)
    - _Requirements: 1.1, 1.7, 11.5_

  - [ ] 19.2 Configure React Router
    - Set up React Router in `src/main.jsx` with routes: `/` (ChatPage), `/admin` (AdminDashboard)
    - _Requirements: 11.3_

- [ ] 20. Checkpoint - Test chat interface
  - Run frontend dev server and test chat flow end-to-end with backend. Verify message display, quick replies, and typing indicator. Ask user if questions arise.


### Phase 7: Frontend Admin Dashboard

- [ ] 21. Implement admin API client and authentication
  - [ ] 21.1 Create admin API client module
    - Implement `src/api/adminApi.js` with functions: `login(username, password)`, `listKB(filters)`, `createKB(data)`, `updateKB(id, data)`, `deleteKB(id)`, `getLogs(filters)`, `getAnalytics(dateRange)`
    - Store JWT token in localStorage on login
    - Add Authorization header to all admin requests
    - Handle 401 errors by clearing token and redirecting to login
    - _Requirements: 7.1, 7.2, 7.5, 10.3-10.9_

  - [ ]* 21.2 Write unit tests for admin API client
    - Test token storage and retrieval
    - Test Authorization header inclusion
    - Test 401 error handling
    - _Requirements: 7.1, 7.5_

- [ ] 22. Build admin login page
  - [ ] 22.1 Create Login component
    - Implement `src/pages/LoginPage.jsx` with username and password inputs
    - Add form validation (required fields)
    - Call admin API login function on submit
    - Redirect to admin dashboard on successful login
    - Display error message on authentication failure
    - _Requirements: 7.1, 7.2_

  - [ ]* 22.2 Write unit tests for login component
    - Test form validation
    - Test successful login flow
    - Test error handling
    - _Requirements: 7.1_

- [ ] 23. Build knowledge base management components
  - [ ] 23.1 Create KBTable component
    - Implement `src/components/KBTable.jsx` to display all KB entries
    - Add client-side pagination (25 entries per page)
    - Add filters: department dropdown, category dropdown, active status checkbox
    - Add sort controls: by title, category, updated_at
    - Add action buttons: Edit, Activate/Deactivate, Delete
    - _Requirements: 6.1, 6.4, 8.4_

  - [ ] 23.2 Create KBEditor component
    - Implement `src/components/KBEditor.jsx` as modal or separate page
    - Add form fields: title (text input, max 255 chars), content (textarea, markdown support), category_id (dropdown), is_active (checkbox)
    - Add client-side validation before submission
    - Call admin API to create or update KB entry
    - Display success/error notifications
    - _Requirements: 6.2, 6.3, 6.5_

  - [ ]* 23.3 Write unit tests for KB components
    - Test KBTable renders entries correctly
    - Test KBEditor validates form inputs
    - Test KBEditor calls API on submit
    - _Requirements: 6.1-6.5_

- [ ] 24. Build conversation logs viewer
  - [ ] 24.1 Create LogsViewer component
    - Implement `src/components/LogsViewer.jsx` to display conversation logs
    - Add filters: date range picker, department dropdown, fallback status radio buttons
    - Display expandable conversation threads showing message sequences
    - Add export button to download filtered logs as JSON
    - _Requirements: 8.3, 8.4, 8.5_

  - [ ]* 24.2 Write unit tests for logs viewer
    - Test filter functionality
    - Test expandable threads
    - Test export button
    - _Requirements: 8.3, 8.5_

- [ ] 25. Build analytics dashboard
  - [ ] 25.1 Create AnalyticsDashboard component
    - Implement `src/components/AnalyticsDashboard.jsx` to display metrics
    - Display fallback rate with trend graph (Chart.js or Recharts)
    - Display total conversations count by date
    - Display top unanswered questions list with frequency counts
    - Display KB coverage percentage (categories with active entries)
    - _Requirements: 8.1, 8.2, 20.1, 20.4_

  - [ ]* 25.2 Write unit tests for analytics dashboard
    - Test metrics display
    - Test graph rendering
    - _Requirements: 8.1, 8.2_

- [ ] 26. Create admin dashboard page and routing
  - [ ] 26.1 Implement AdminDashboard page
    - Create `src/pages/AdminDashboard.jsx` as root admin page
    - Add navigation tabs: KB Management, Conversation Logs, Analytics
    - Integrate KBTable, KBEditor, LogsViewer, AnalyticsDashboard components
    - Add protected route logic (redirect to login if no JWT token)
    - _Requirements: 11.3, 7.5_

  - [ ] 26.2 Add admin route to React Router
    - Update React Router configuration with `/admin` route pointing to AdminDashboard
    - Add route guard to check JWT token presence
    - _Requirements: 11.3_

- [ ] 27. Checkpoint - Test admin dashboard
  - Test full admin workflow: login → manage KB entries → view logs → view analytics. Verify JWT protection and CRUD operations. Ask user if questions arise.


### Phase 8: Integration, Testing, and Error Handling

- [ ] 28. Implement comprehensive error handling
  - [ ] 28.1 Add backend error handling middleware
    - Create custom exception classes in `utils/exceptions.py`: `GroqAPIError`, `EmbeddingError`, `DatabaseError`
    - Add FastAPI exception handlers for each error type with consistent JSON response format
    - Log all errors with structured format (timestamp, service, error_type, context)
    - _Requirements: 15.1, 15.2, 15.3, 15.4_

  - [ ] 28.2 Add frontend error handling
    - Create API error interceptor in `src/api/apiClient.js`
    - Display toast notifications for transient errors (API failures, network issues)
    - Add retry buttons for recoverable errors
    - Add error boundary component for React errors
    - _Requirements: 15.5_

  - [ ]* 28.3 Write unit tests for error handling
    - Test exception handlers with various error types
    - Test frontend error interceptor
    - Test error logging format
    - _Requirements: 15.1-15.5_

- [ ] 29. Add logging and monitoring
  - [ ] 29.1 Implement structured logging
    - Configure Python logging with JSON formatter
    - Add request ID generation for tracing
    - Log all RAG pipeline steps (embedding, retrieval, generation)
    - Log all admin actions (KB CRUD operations)
    - _Requirements: 15.4, 6.6, 20.2_

  - [ ] 29.2 Add performance monitoring
    - Add timing metrics for RAG pipeline steps
    - Log slow queries (>500ms for pgvector search)
    - Track Groq API latency and errors
    - _Requirements: 17.1, 17.2, 20.2_

- [ ] 30. Implement KB content parser (bonus feature)
  - [ ] 30.1 Create KB content parser utility
    - Implement `utils/kb_parser.py` to parse structured KB content files (JSON or YAML)
    - Validate required fields: title, content, category, department
    - Return descriptive parsing errors for invalid entries
    - _Requirements: 14.1, 14.2, 14.3_

  - [ ] 30.2 Create KB content pretty printer
    - Implement `utils/kb_printer.py` to export KB entries to structured files
    - _Requirements: 14.4_

  - [ ]* 30.3 Write property test for parser round-trip
    - **Property 1: Parser round-trip consistency**
    - **Validates: Requirements 14.5**
    - Test that parsing → printing → parsing produces equivalent KB entries
    - Use property-based testing library (Hypothesis) to generate random valid KB entries
    - _Requirements: 14.5_

- [ ] 31. Write integration tests for critical flows
  - [ ]* 31.1 Write end-to-end chat flow test
    - Test: user opens chat → clicks quick reply → receives response → sends follow-up
    - Verify conversation logged correctly in database
    - Mock Groq API for consistent testing
    - _Requirements: 1.1-1.7, 5.1-5.6_

  - [ ]* 31.2 Write end-to-end admin flow test
    - Test: admin logs in → creates KB entry → edits KB entry → deactivates KB entry
    - Verify embedding generation and database updates
    - Verify changes reflected in chat responses
    - _Requirements: 7.1-7.5, 6.1-6.6_

  - [ ]* 31.3 Write fallback mechanism test
    - Test: user asks out-of-scope question → system detects low confidence → returns fallback message
    - Verify was_fallback flag set correctly in database
    - _Requirements: 4.1-4.5_

  - [ ]* 31.4 Write performance tests
    - Test RAG pipeline response time (<5s requirement)
    - Test pgvector search latency (<500ms requirement)
    - Test concurrent request handling (10+ concurrent users)
    - _Requirements: 17.1, 17.2, 17.3, 17.5_

- [ ] 32. Create deployment configuration
  - [ ] 32.1 Configure backend deployment (Render)
    - Create `render.yaml` or Dockerfile for backend deployment
    - Document environment variables required for production
    - Configure database connection with SSL for Neon PostgreSQL
    - _Requirements: 12.5, 13.1-13.3_

  - [ ] 32.2 Configure frontend deployment (Vercel)
    - Create `vercel.json` for frontend deployment
    - Configure build settings (Vite build command, output directory)
    - Set environment variables for API base URL
    - _Requirements: 11.4_

  - [ ] 32.3 Update CORS for production
    - Update allowed origins in FastAPI CORS middleware to include production frontend URL
    - _Requirements: 16.1, 16.2_

- [ ] 33. Final checkpoint - End-to-end system test
  - Deploy to staging/production. Test full system: public chat flow, admin authentication, KB management, analytics. Verify all requirements met. Ask user if questions arise.


## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP delivery
- Each task references specific requirements from requirements.md for traceability
- Checkpoints ensure incremental validation after each major phase
- Property-based test (task 30.3) validates parser correctness with random inputs
- Unit tests and integration tests are complementary: unit tests validate individual functions, integration tests validate API endpoints with database
- The implementation follows a bottom-up approach: infrastructure → core services → API layer → frontend
- All core implementation tasks (not marked with `*`) must be completed for a functional system
- Optional test tasks provide additional quality assurance but are not required for basic functionality

## Task Dependency Graph

```json
{
  "waves": [
    {
      "id": 0,
      "tasks": ["1.1", "1.2"]
    },
    {
      "id": 1,
      "tasks": ["1.3", "3.1"]
    },
    {
      "id": 2,
      "tasks": ["3.2", "3.3"]
    },
    {
      "id": 3,
      "tasks": ["4.1"]
    },
    {
      "id": 4,
      "tasks": ["4.2", "6.1"]
    },
    {
      "id": 5,
      "tasks": ["6.2", "7.1"]
    },
    {
      "id": 6,
      "tasks": ["7.2", "8.1", "8.2"]
    },
    {
      "id": 7,
      "tasks": ["8.3", "10.1"]
    },
    {
      "id": 8,
      "tasks": ["10.2", "10.3"]
    },
    {
      "id": 9,
      "tasks": ["10.4", "11.1"]
    },
    {
      "id": 10,
      "tasks": ["11.2", "11.3"]
    },
    {
      "id": 11,
      "tasks": ["11.4", "12.1"]
    },
    {
      "id": 12,
      "tasks": ["12.2", "14.1", "14.2"]
    },
    {
      "id": 13,
      "tasks": ["14.3", "15.1"]
    },
    {
      "id": 14,
      "tasks": ["15.2", "15.3"]
    },
    {
      "id": 15,
      "tasks": ["15.4", "17.1"]
    },
    {
      "id": 16,
      "tasks": ["17.2", "18.1"]
    },
    {
      "id": 17,
      "tasks": ["18.2", "18.3", "18.4"]
    },
    {
      "id": 18,
      "tasks": ["18.5", "19.1"]
    },
    {
      "id": 19,
      "tasks": ["19.2", "21.1"]
    },
    {
      "id": 20,
      "tasks": ["21.2", "22.1"]
    },
    {
      "id": 21,
      "tasks": ["22.2", "23.1", "23.2"]
    },
    {
      "id": 22,
      "tasks": ["23.3", "24.1"]
    },
    {
      "id": 23,
      "tasks": ["24.2", "25.1"]
    },
    {
      "id": 24,
      "tasks": ["25.2", "26.1"]
    },
    {
      "id": 25,
      "tasks": ["26.2", "28.1", "28.2"]
    },
    {
      "id": 26,
      "tasks": ["28.3", "29.1", "29.2"]
    },
    {
      "id": 27,
      "tasks": ["30.1", "30.2"]
    },
    {
      "id": 28,
      "tasks": ["30.3", "31.1", "31.2", "31.3", "31.4"]
    },
    {
      "id": 29,
      "tasks": ["32.1", "32.2"]
    },
    {
      "id": 30,
      "tasks": ["32.3"]
    }
  ]
}
```
