# Requirements Document

## Introduction

ADMIT (Admissions & Inquiries Technology) is a web-based conversational AI assistant designed to answer admissions and enrollment questions for SACLI (St. Anthony College of Ligao Inc.) across four departments: IBED, SHS, HED, and TESDA. The system uses Retrieval-Augmented Generation (RAG) to provide accurate, grounded responses from a predefined knowledge base while gracefully redirecting out-of-scope questions to appropriate SACLI offices. The system serves two user types: public users (students, applicants, parents) who interact with the chatbot, and system administrators who manage the knowledge base and monitor system performance.

## Glossary

- **ADMIT_System**: The complete conversational AI system including frontend, backend, and database components
- **Chat_Interface**: The public-facing chat window where users submit inquiries
- **RAG_Pipeline**: The Retrieval-Augmented Generation process that embeds queries, performs semantic search, and generates LLM responses
- **Knowledge_Base**: The PostgreSQL database containing predefined admissions/enrollment content with vector embeddings
- **Admin_Dashboard**: The JWT-protected interface for knowledge base management and analytics
- **Groq_LLM**: The Groq API service using Llama 3.1 for natural language generation
- **Embedding_Service**: The sentence-transformers service that converts text to vector embeddings
- **Pgvector_Search**: The PostgreSQL pgvector extension for semantic similarity search
- **Fallback_Response**: A redirect message to appropriate SACLI offices when confidence is below threshold
- **Confidence_Threshold**: The similarity score minimum (e.g., 0.35) below which queries are considered out-of-scope
- **KB_Entry**: A single knowledge base record with title, content, category, and embedding
- **Conversation_Log**: Persistent record of user-bot exchanges with matched KB IDs and fallback flags
- **Quick_Reply_Button**: Predefined category buttons that trigger common inquiry searches
- **JWT_Token**: JSON Web Token used for administrator authentication
- **SACLI**: St. Anthony College of Ligao Inc.
- **Department**: One of four SACLI departments: IBED, SHS, HED, TESDA, or GENERAL

## Requirements

### Requirement 1: Public Chat Interface

**User Story:** As a student, applicant, or parent, I want to ask admissions and enrollment questions through a chat interface, so that I can get immediate answers without contacting staff.

#### Acceptance Criteria

1. THE Chat_Interface SHALL display a messaging-style chat window for user input
2. WHEN a user submits a text message, THE Chat_Interface SHALL send the message to the RAG_Pipeline
3. WHEN the RAG_Pipeline returns a response, THE Chat_Interface SHALL display it as a bot message bubble
4. THE Chat_Interface SHALL display quick reply buttons for common inquiry categories (Admission Requirements, Enrollment Steps, Programs Offered, Tuition & Payment, Scholarships, Contact Info)
5. WHEN a user taps a quick reply button, THE Chat_Interface SHALL submit the corresponding query to the RAG_Pipeline
6. THE Chat_Interface SHALL display a typing indicator while the RAG_Pipeline processes queries
7. THE Chat_Interface SHALL be accessible without user authentication or login

### Requirement 2: Query Embedding and Vector Search

**User Story:** As the system, I want to convert user queries into semantic embeddings, so that I can find relevant knowledge base content through similarity search.

#### Acceptance Criteria

1. WHEN a user query is received, THE Embedding_Service SHALL generate a vector embedding using sentence-transformers
2. THE RAG_Pipeline SHALL use the query embedding to perform Pgvector_Search against Knowledge_Base embeddings
3. THE Pgvector_Search SHALL return the top 3-5 Knowledge_Base entries ranked by cosine similarity
4. THE RAG_Pipeline SHALL calculate a confidence score based on the best match similarity
5. IF the confidence score is below the Confidence_Threshold, THEN THE RAG_Pipeline SHALL set the fallback flag to true

### Requirement 3: Grounded Response Generation

**User Story:** As a system administrator, I want the AI to answer only from predefined knowledge base content, so that responses are accurate and controlled.

#### Acceptance Criteria

1. WHEN the confidence score is above the Confidence_Threshold, THE RAG_Pipeline SHALL construct a prompt containing retrieved KB_Entry content and the user query
2. THE RAG_Pipeline SHALL send the prompt to Groq_LLM with instructions to answer only from provided context
3. THE Groq_LLM SHALL generate a natural language response grounded in the retrieved KB_Entry content
4. THE RAG_Pipeline SHALL return the generated response to the Chat_Interface
5. IF the retrieved context does not fully answer the question, THEN THE Groq_LLM SHALL acknowledge the limitation and suggest contacting the relevant SACLI office

### Requirement 4: Fallback Mechanism for Out-of-Scope Queries

**User Story:** As a user, I want clear guidance when my question is outside the system's knowledge, so that I know where to get help.

#### Acceptance Criteria

1. WHEN the confidence score is below the Confidence_Threshold, THE RAG_Pipeline SHALL generate a Fallback_Response
2. THE Fallback_Response SHALL politely indicate the query is outside the system's knowledge
3. THE Fallback_Response SHALL direct the user to the appropriate SACLI office based on query context
4. THE RAG_Pipeline SHALL log the interaction with the fallback flag set to true
5. THE Fallback_Response SHALL not invoke Groq_LLM for generation

### Requirement 5: Conversation Logging

**User Story:** As a system administrator, I want all conversations logged with metadata, so that I can evaluate system performance and identify knowledge gaps.

#### Acceptance Criteria

1. WHEN a conversation begins, THE ADMIT_System SHALL create a Conversation_Log entry with unique session ID
2. WHEN a user sends a message, THE ADMIT_System SHALL log it with sender type "user"
3. WHEN the system generates a response, THE ADMIT_System SHALL log it with sender type "bot"
4. THE ADMIT_System SHALL store matched KB_Entry IDs for each bot response in the Conversation_Log
5. THE ADMIT_System SHALL store the fallback flag value for each bot response in the Conversation_Log
6. THE Conversation_Log SHALL include timestamps for all messages

### Requirement 6: Knowledge Base Management

**User Story:** As a system administrator, I want to create, read, update, and delete knowledge base entries, so that I can maintain accurate system knowledge.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL provide a table view of all KB_Entry records with title, category, department, and active status
2. WHEN an administrator creates a KB_Entry, THE ADMIT_System SHALL automatically generate vector embeddings using Embedding_Service
3. WHEN an administrator edits a KB_Entry, THE ADMIT_System SHALL regenerate vector embeddings for the updated content
4. THE Admin_Dashboard SHALL allow administrators to deactivate KB_Entry records without deletion
5. THE Admin_Dashboard SHALL associate each KB_Entry with a category and department (IBED, SHS, HED, TESDA, GENERAL)
6. THE Admin_Dashboard SHALL record which administrator last modified each KB_Entry and when

### Requirement 7: Administrator Authentication

**User Story:** As a system administrator, I want secure login access to the admin dashboard, so that only authorized staff can manage knowledge base content.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL be protected by JWT_Token authentication
2. WHEN an administrator submits valid credentials, THE ADMIT_System SHALL generate a JWT_Token
3. THE ADMIT_System SHALL validate JWT_Token on all admin API requests
4. THE ADMIT_System SHALL store administrator credentials using bcrypt password hashing
5. THE ADMIT_System SHALL reject admin API requests without valid JWT_Token with HTTP 401 status

### Requirement 8: Analytics and Performance Monitoring

**User Story:** As a system administrator, I want to view analytics on system performance, so that I can identify areas for knowledge base improvement.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL display the fallback rate (percentage of queries resulting in fallback)
2. THE Admin_Dashboard SHALL display the most common unanswered questions (queries that triggered fallback)
3. THE Admin_Dashboard SHALL provide a conversation log viewer with filters for date range, fallback status, and department
4. THE Admin_Dashboard SHALL display which KB_Entry records were matched for each logged response
5. THE Admin_Dashboard SHALL allow administrators to export conversation logs for analysis

### Requirement 9: Database Schema with Vector Support

**User Story:** As the system, I want a database schema supporting vector embeddings and relational data, so that semantic search and structured queries are both supported.

#### Acceptance Criteria

1. THE Knowledge_Base SHALL store KB_Entry records with id, category_id, title, content, embedding vector, is_active flag, updated_by, and updated_at fields
2. THE Knowledge_Base SHALL use pgvector extension for vector embedding storage with dimension matching Embedding_Service output (e.g., 384)
3. THE ADMIT_System SHALL maintain kb_categories table with id, name, and department fields
4. THE ADMIT_System SHALL maintain admin_users table with id, username, password_hash, role, and created_at fields
5. THE ADMIT_System SHALL maintain conversations table with id, session_id UUID, and started_at timestamp
6. THE ADMIT_System SHALL maintain messages table with id, conversation_id, sender, content, matched_kb_ids array, was_fallback flag, and created_at timestamp

### Requirement 10: API Endpoints for Chat and Administration

**User Story:** As a developer, I want well-defined REST API endpoints, so that frontend and backend communicate reliably.

#### Acceptance Criteria

1. THE ADMIT_System SHALL provide POST /api/chat endpoint for submitting user messages without authentication
2. THE ADMIT_System SHALL provide GET /api/quick-replies endpoint for retrieving category buttons without authentication
3. THE ADMIT_System SHALL provide POST /api/admin/login endpoint for administrator authentication
4. THE ADMIT_System SHALL provide GET /api/admin/kb endpoint for listing KB_Entry records (JWT-protected)
5. THE ADMIT_System SHALL provide POST /api/admin/kb endpoint for creating KB_Entry records (JWT-protected)
6. THE ADMIT_System SHALL provide PUT /api/admin/kb/{id} endpoint for updating KB_Entry records (JWT-protected)
7. THE ADMIT_System SHALL provide DELETE /api/admin/kb/{id} endpoint for deactivating KB_Entry records (JWT-protected)
8. THE ADMIT_System SHALL provide GET /api/admin/logs endpoint for retrieving conversation logs (JWT-protected)
9. THE ADMIT_System SHALL provide GET /api/admin/analytics endpoint for retrieving performance metrics (JWT-protected)

### Requirement 11: Frontend Technology Stack

**User Story:** As a developer, I want a modern, maintainable frontend stack, so that the user interface is responsive and easy to update.

#### Acceptance Criteria

1. THE Chat_Interface SHALL be built using React with Vite build tool
2. THE Chat_Interface SHALL use TailwindCSS for styling
3. THE Admin_Dashboard SHALL be a single-page application (SPA) within the same React application
4. THE ADMIT_System SHALL support deployment to Vercel for the frontend
5. THE Chat_Interface SHALL be responsive and functional on desktop and mobile browsers

### Requirement 12: Backend Technology Stack

**User Story:** As a developer, I want a Python-based backend with async support, so that LLM and database operations are efficient.

#### Acceptance Criteria

1. THE RAG_Pipeline SHALL be implemented using FastAPI framework
2. THE ADMIT_System SHALL use PostgreSQL (Neon) as the database with pgvector extension enabled
3. THE Embedding_Service SHALL use sentence-transformers library (e.g., all-MiniLM-L6-v2 model)
4. THE RAG_Pipeline SHALL integrate with Groq API for LLM response generation
5. THE ADMIT_System SHALL support deployment to Render or similar platform for the backend
6. THE ADMIT_System SHALL provide automatic OpenAPI documentation via FastAPI

### Requirement 13: Environment Configuration

**User Story:** As a developer, I want environment-based configuration, so that secrets and deployment-specific settings are managed securely.

#### Acceptance Criteria

1. THE ADMIT_System SHALL load database connection strings from environment variables
2. THE ADMIT_System SHALL load Groq API keys from environment variables
3. THE ADMIT_System SHALL load JWT secret keys from environment variables
4. THE ADMIT_System SHALL provide a .env.example file documenting required environment variables
5. THE ADMIT_System SHALL not commit actual secrets to version control

### Requirement 14: Parser for Knowledge Base Content

**User Story:** As a system administrator, I want to import knowledge base content from structured files, so that I can bulk-load admissions information efficiently.

#### Acceptance Criteria

1. WHEN a structured KB content file is provided, THE ADMIT_System SHALL parse it into KB_Entry records
2. WHEN parsing KB content, THE ADMIT_System SHALL validate required fields (title, content, category, department)
3. IF a KB content file contains invalid entries, THEN THE ADMIT_System SHALL return descriptive parsing errors
4. THE ADMIT_System SHALL provide a pretty printer to export KB_Entry records back to structured files
5. FOR ALL valid KB_Entry collections, parsing then printing then parsing SHALL produce equivalent KB_Entry records (round-trip property)

### Requirement 15: Error Handling and Resilience

**User Story:** As a user, I want the system to handle errors gracefully, so that temporary failures don't break my experience.

#### Acceptance Criteria

1. WHEN Groq_LLM API is unavailable, THE ADMIT_System SHALL return a user-friendly error message
2. WHEN Embedding_Service fails, THE ADMIT_System SHALL log the error and return a fallback message
3. WHEN database queries fail, THE ADMIT_System SHALL return HTTP 500 with a generic error message without exposing internals
4. THE ADMIT_System SHALL log all errors with timestamps and request context for debugging
5. WHEN the Admin_Dashboard receives API errors, THE Admin_Dashboard SHALL display user-friendly error notifications

### Requirement 16: CORS Configuration for Cross-Origin Requests

**User Story:** As a developer, I want CORS properly configured, so that the React frontend can communicate with the FastAPI backend across domains.

#### Acceptance Criteria

1. THE ADMIT_System SHALL configure CORS middleware in FastAPI
2. THE ADMIT_System SHALL allow requests from the frontend deployment domain (e.g., Vercel domain)
3. THE ADMIT_System SHALL allow requests from localhost during development
4. THE ADMIT_System SHALL specify allowed HTTP methods (GET, POST, PUT, DELETE, OPTIONS)
5. THE ADMIT_System SHALL allow Authorization header for JWT authentication

### Requirement 17: System Performance Requirements

**User Story:** As a user, I want fast response times, so that the chat experience feels natural and responsive.

#### Acceptance Criteria

1. WHEN a user submits a query, THE RAG_Pipeline SHALL return a response within 5 seconds under normal load
2. THE Pgvector_Search SHALL complete similarity search within 500 milliseconds for knowledge bases under 10,000 entries
3. THE Chat_Interface SHALL display the typing indicator within 100 milliseconds of query submission
4. THE Admin_Dashboard SHALL load the KB_Entry table within 2 seconds for up to 1,000 entries
5. THE ADMIT_System SHALL handle at least 10 concurrent chat requests without degradation

### Requirement 18: Data Privacy and Security

**User Story:** As a user, I want my conversations to be handled securely, so that my privacy is protected.

#### Acceptance Criteria

1. THE ADMIT_System SHALL not require user authentication or collect personal identifiable information for chat usage
2. THE Conversation_Log SHALL use anonymous session IDs without linking to user identities
3. THE ADMIT_System SHALL transmit all data over HTTPS in production
4. THE ADMIT_System SHALL not expose administrator password hashes in API responses
5. THE JWT_Token SHALL expire after a configurable duration (e.g., 24 hours)

### Requirement 19: System Maintainability and Documentation

**User Story:** As a developer, I want clear code structure and documentation, so that the system can be maintained and extended.

#### Acceptance Criteria

1. THE ADMIT_System SHALL organize backend code into routers, services, models, auth, and db modules
2. THE ADMIT_System SHALL organize frontend code into components, pages, and api modules
3. THE ADMIT_System SHALL provide a README documenting setup, environment variables, and deployment
4. THE ADMIT_System SHALL provide inline code comments for complex RAG_Pipeline logic
5. THE ADMIT_System SHALL provide OpenAPI documentation auto-generated by FastAPI at /docs endpoint

### Requirement 20: ISO/IEC 25010 Compliance for Thesis Evaluation

**User Story:** As a thesis researcher, I want the system to demonstrate functional suitability, reliability, and maintainability, so that it meets ISO/IEC 25010 quality standards for evaluation.

#### Acceptance Criteria

1. THE ADMIT_System SHALL log fallback rates to demonstrate functional suitability measurement
2. THE ADMIT_System SHALL maintain uptime and error logs to demonstrate reliability measurement
3. THE ADMIT_System SHALL provide knowledge base version tracking to demonstrate maintainability
4. THE Admin_Dashboard SHALL provide analytics supporting ISO/IEC 25010 evaluation metrics
5. THE ADMIT_System SHALL support thesis evaluation through conversation log exports and performance data
