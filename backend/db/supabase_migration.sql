-- ============================================================
-- ADMIT System - Supabase / PostgreSQL Migration Script
-- Run this in Supabase SQL Editor before first deploy
-- ============================================================

-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. KB Categories
CREATE TABLE IF NOT EXISTS kb_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(20) NOT NULL CHECK (department IN ('IBED','SHS','HED','TESDA','GENERAL'))
);

-- 3. Admin Users
CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. Knowledge Base
CREATE TABLE IF NOT EXISTS knowledge_base (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES kb_categories(id),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(384),
    is_active BOOLEAN DEFAULT TRUE,
    updated_by INTEGER REFERENCES admin_users(id),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 5. Conversations
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    session_id UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    started_at TIMESTAMP DEFAULT NOW()
);

-- 6. Messages
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    sender VARCHAR(10) NOT NULL CHECK (sender IN ('user','bot')),
    content TEXT NOT NULL,
    matched_kb_ids INTEGER[],
    was_fallback BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────
-- Indexes
-- ─────────────────────────────
CREATE INDEX IF NOT EXISTS idx_kb_embedding   ON knowledge_base USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_kb_category    ON knowledge_base (category_id);
CREATE INDEX IF NOT EXISTS idx_kb_active      ON knowledge_base (is_active);
CREATE INDEX IF NOT EXISTS idx_conv_session   ON conversations (session_id);
CREATE INDEX IF NOT EXISTS idx_conv_started   ON conversations (started_at);
CREATE INDEX IF NOT EXISTS idx_msg_conv       ON messages (conversation_id);
CREATE INDEX IF NOT EXISTS idx_msg_fallback   ON messages (was_fallback);
CREATE INDEX IF NOT EXISTS idx_msg_created    ON messages (created_at);

-- ─────────────────────────────
-- Seed: KB Categories
-- ─────────────────────────────
INSERT INTO kb_categories (name, department) VALUES
  ('Admission Requirements','IBED'),
  ('Enrollment Steps','IBED'),
  ('Programs Offered','IBED'),
  ('Tuition and Payment','IBED'),
  ('Scholarships','IBED'),
  ('Contact Information','IBED'),
  ('Admission Requirements','SHS'),
  ('Enrollment Steps','SHS'),
  ('Programs Offered','SHS'),
  ('Tuition and Payment','SHS'),
  ('Scholarships','SHS'),
  ('Contact Information','SHS'),
  ('Admission Requirements','HED'),
  ('Enrollment Steps','HED'),
  ('Programs Offered','HED'),
  ('Tuition and Payment','HED'),
  ('Scholarships','HED'),
  ('Contact Information','HED'),
  ('Admission Requirements','TESDA'),
  ('Enrollment Steps','TESDA'),
  ('Programs Offered','TESDA'),
  ('Tuition and Payment','TESDA'),
  ('Scholarships','TESDA'),
  ('Contact Information','TESDA'),
  ('About SACLI','GENERAL'),
  ('Campus Facilities','GENERAL'),
  ('Student Services','GENERAL')
ON CONFLICT DO NOTHING;

-- ─────────────────────────────
-- Seed: Default Admin User
-- password = admin123 (bcrypt)
-- CHANGE THIS IN PRODUCTION!
-- ─────────────────────────────
INSERT INTO admin_users (username, password_hash, role) VALUES
  ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PtefO2', 'admin')
ON CONFLICT (username) DO NOTHING;
