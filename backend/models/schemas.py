"""
SQLAlchemy ORM models for ADMIT system database schema.
Includes support for pgvector embeddings and PostgreSQL-specific types.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, ARRAY, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid
from db.database import Base


class KBCategory(Base):
    """Knowledge base categories (Admission Requirements, Enrollment Steps, etc.)"""
    __tablename__ = "kb_categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    department = Column(
        String(20),
        CheckConstraint("department IN ('IBED', 'SHS', 'HED', 'TESDA', 'GENERAL')"),
        nullable=False
    )
    
    # Relationship to knowledge base entries
    kb_entries = relationship("KnowledgeBase", back_populates="category")
    
    def __repr__(self):
        return f"<KBCategory(id={self.id}, name='{self.name}', department='{self.department}')>"


class KnowledgeBase(Base):
    """Knowledge base entries with vector embeddings for semantic search"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("kb_categories.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)  # 384-dim for all-MiniLM-L6-v2
    is_active = Column(Boolean, default=True, nullable=False)
    updated_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    category = relationship("KBCategory", back_populates="kb_entries")
    updater = relationship("AdminUser", back_populates="kb_updates")
    
    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, title='{self.title}', is_active={self.is_active})>"


class AdminUser(Base):
    """Administrator user accounts with bcrypt password hashing"""
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="admin", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to KB updates
    kb_updates = relationship("KnowledgeBase", back_populates="updater")
    
    def __repr__(self):
        return f"<AdminUser(id={self.id}, username='{self.username}', role='{self.role}')>"


class Conversation(Base):
    """Conversation sessions for anonymous users"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, session_id='{self.session_id}')>"


class Message(Base):
    """Individual messages in conversations with RAG metadata"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender = Column(
        String(10),
        CheckConstraint("sender IN ('user', 'bot')"),
        nullable=False
    )
    content = Column(Text, nullable=False)
    matched_kb_ids = Column(ARRAY(Integer), nullable=True)  # NULL for user messages
    was_fallback = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, sender='{self.sender}', was_fallback={self.was_fallback})>"
