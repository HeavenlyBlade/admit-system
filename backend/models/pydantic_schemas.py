"""
Pydantic models for API request/response validation.
Separate from SQLAlchemy models for clean separation of concerns.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID


# ============================================================================
# Chat API Schemas
# ============================================================================

class ChatRequest(BaseModel):
    """Request schema for POST /api/chat"""
    message: str = Field(..., min_length=1, max_length=500, description="User message")
    session_id: Optional[UUID] = Field(None, description="Session ID for conversation tracking")


class ChatResponse(BaseModel):
    """Response schema for POST /api/chat"""
    response: str = Field(..., description="Bot response message")
    session_id: UUID = Field(..., description="Session ID for this conversation")
    was_fallback: bool = Field(..., description="True if response was fallback redirect")
    matched_kb_ids: List[int] = Field(default_factory=list, description="KB entry IDs used in response")


class QuickReply(BaseModel):
    """Quick reply button schema"""
    id: int
    name: str
    query: str


# ============================================================================
# Admin Authentication Schemas
# ============================================================================

class LoginRequest(BaseModel):
    """Request schema for POST /api/admin/login"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class LoginResponse(BaseModel):
    """Response schema for POST /api/admin/login"""
    access_token: str
    token_type: str = "bearer"


# ============================================================================
# Knowledge Base Schemas
# ============================================================================

class KBCategoryResponse(BaseModel):
    """KB category response schema"""
    id: int
    name: str
    department: str
    
    class Config:
        from_attributes = True


class KBEntryCreate(BaseModel):
    """Request schema for creating KB entry"""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=10, max_length=5000)
    category_id: int = Field(..., gt=0)
    is_active: bool = True


class KBEntryUpdate(BaseModel):
    """Request schema for updating KB entry"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=10, max_length=5000)
    category_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None


class KBEntryResponse(BaseModel):
    """Response schema for KB entry"""
    id: int
    category_id: int
    title: str
    content: str
    is_active: bool
    updated_by: Optional[int]
    updated_at: datetime
    category: Optional[KBCategoryResponse] = None
    
    class Config:
        from_attributes = True


class KBEntryListResponse(BaseModel):
    """Response schema for KB entry list with pagination"""
    entries: List[KBEntryResponse]
    total: int
    page: int
    per_page: int


# ============================================================================
# Conversation Log Schemas
# ============================================================================

class MessageResponse(BaseModel):
    """Individual message response"""
    id: int
    sender: str
    content: str
    matched_kb_ids: Optional[List[int]]
    was_fallback: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation with messages"""
    session_id: UUID
    started_at: datetime
    messages: List[MessageResponse]
    
    class Config:
        from_attributes = True


class ConversationLogsResponse(BaseModel):
    """Response schema for conversation logs with pagination"""
    conversations: List[ConversationResponse]
    total_count: int
    page: int
    per_page: int


# ============================================================================
# Analytics Schemas
# ============================================================================

class TopUnansweredQuery(BaseModel):
    """Top unanswered query with count"""
    query: str
    count: int


class AnalyticsResponse(BaseModel):
    """Response schema for analytics dashboard"""
    fallback_rate: float = Field(..., description="Percentage of queries resulting in fallback (0.0-1.0)")
    total_conversations: int
    total_messages: int
    date_range: dict  # {start: datetime, end: datetime}
    top_unanswered_queries: List[TopUnansweredQuery]
    kb_coverage: dict  # {total_categories: int, covered_categories: int, percentage: float}


# ============================================================================
# Error Response Schema
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response schema"""
    error: dict = Field(
        ...,
        description="Error details",
        example={
            "code": "VALIDATION_ERROR",
            "message": "Invalid input",
            "details": "Field 'message' is required"
        }
    )
