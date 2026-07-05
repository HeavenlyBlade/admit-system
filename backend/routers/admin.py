"""
Admin router for knowledge base management and analytics.
All endpoints require JWT authentication (except login).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload
from typing import Optional
from datetime import datetime, timedelta
import logging

from db.database import get_db
from models.pydantic_schemas import (
    LoginRequest, LoginResponse,
    KBEntryCreate, KBEntryUpdate, KBEntryResponse, KBEntryListResponse,
    ConversationLogsResponse, ConversationResponse, MessageResponse,
    AnalyticsResponse, TopUnansweredQuery
)
from models.schemas import AdminUser, KnowledgeBase, KBCategory, Conversation, Message
from auth.jwt_handler import create_access_token, verify_password, get_current_user
from services.embeddings import embed

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ============================================================================
# Authentication Endpoints
# ============================================================================

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Admin login - generates JWT token.
    
    Returns:
        LoginResponse: Access token and token type
    """
    # Find admin user
    result = await db.execute(
        select(AdminUser).where(AdminUser.username == request.username)
    )
    admin_user = result.scalars().first()
    
    if not admin_user or not verify_password(request.password, admin_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid username or password"
                }
            }
        )
    
    # Generate JWT token
    token = create_access_token(
        data={"sub": admin_user.username, "user_id": admin_user.id}
    )
    
    logger.info(f"Admin user '{admin_user.username}' logged in")
    
    return LoginResponse(access_token=token, token_type="bearer")


# ============================================================================
# Knowledge Base CRUD Endpoints
# ============================================================================

@router.get("/kb", response_model=KBEntryListResponse)
async def list_kb_entries(
    page: int = 1,
    per_page: int = 25,
    department: Optional[str] = None,
    category_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List knowledge base entries with filtering and pagination.
    
    Query Parameters:
        - page: Page number (default 1)
        - per_page: Items per page (default 25)
        - department: Filter by department (IBED, SHS, HED, TESDA, GENERAL)
        - category_id: Filter by category ID
        - is_active: Filter by active status
        - search: Search in title and content
    """
    # Build query
    query = select(KnowledgeBase).options(joinedload(KnowledgeBase.category))
    
    # Apply filters
    if department:
        query = query.join(KBCategory).where(KBCategory.department == department)
    
    if category_id:
        query = query.where(KnowledgeBase.category_id == category_id)
    
    if is_active is not None:
        query = query.where(KnowledgeBase.is_active == is_active)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                KnowledgeBase.title.ilike(search_term),
                KnowledgeBase.content.ilike(search_term)
            )
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page).order_by(KnowledgeBase.updated_at.desc())
    
    # Execute query
    result = await db.execute(query)
    entries = result.scalars().all()
    
    return KBEntryListResponse(
        entries=[KBEntryResponse.model_validate(entry) for entry in entries],
        total=total,
        page=page,
        per_page=per_page
    )


@router.post("/kb", response_model=KBEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_kb_entry(
    request: KBEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create new knowledge base entry with automatic embedding generation.
    """
    try:
        # Generate embedding
        logger.info(f"Generating embedding for new KB entry: '{request.title}'")
        embedding = embed(request.content)
        
        # Create KB entry
        kb_entry = KnowledgeBase(
            category_id=request.category_id,
            title=request.title,
            content=request.content,
            embedding=embedding,
            is_active=request.is_active,
            updated_by=current_user["user_id"]
        )
        
        db.add(kb_entry)
        await db.flush()
        
        # Load category for response
        await db.refresh(kb_entry, ["category"])
        await db.commit()
        
        logger.info(f"Created KB entry ID: {kb_entry.id}")
        return KBEntryResponse.model_validate(kb_entry)
        
    except Exception as e:
        logger.error(f"Error creating KB entry: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "KB_CREATE_ERROR",
                    "message": "Failed to create knowledge base entry",
                    "details": str(e)
                }
            }
        )


@router.put("/kb/{kb_id}", response_model=KBEntryResponse)
async def update_kb_entry(
    kb_id: int,
    request: KBEntryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update knowledge base entry with automatic embedding regeneration.
    """
    # Find entry
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
    )
    kb_entry = result.scalars().first()
    
    if not kb_entry:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "KB_NOT_FOUND", "message": "Knowledge base entry not found"}}
        )
    
    try:
        # Update fields
        if request.title is not None:
            kb_entry.title = request.title
        
        if request.content is not None:
            kb_entry.content = request.content
            # Regenerate embedding
            logger.info(f"Regenerating embedding for KB entry ID: {kb_id}")
            kb_entry.embedding = embed(request.content)
        
        if request.category_id is not None:
            kb_entry.category_id = request.category_id
        
        if request.is_active is not None:
            kb_entry.is_active = request.is_active
        
        kb_entry.updated_by = current_user["user_id"]
        kb_entry.updated_at = datetime.utcnow()
        
        await db.refresh(kb_entry, ["category"])
        await db.commit()
        
        logger.info(f"Updated KB entry ID: {kb_id}")
        return KBEntryResponse.model_validate(kb_entry)
        
    except Exception as e:
        logger.error(f"Error updating KB entry: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "KB_UPDATE_ERROR",
                    "message": "Failed to update knowledge base entry",
                    "details": str(e)
                }
            }
        )


@router.delete("/kb/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kb_entry(
    kb_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Soft delete knowledge base entry (set is_active = false).
    """
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
    )
    kb_entry = result.scalars().first()
    
    if not kb_entry:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "KB_NOT_FOUND", "message": "Knowledge base entry not found"}}
        )
    
    kb_entry.is_active = False
    kb_entry.updated_by = current_user["user_id"]
    kb_entry.updated_at = datetime.utcnow()
    
    await db.commit()
    logger.info(f"Soft deleted KB entry ID: {kb_id}")
    
    return None


# ============================================================================
# Conversation Logs Endpoint
# ============================================================================

@router.get("/logs", response_model=ConversationLogsResponse)
async def get_conversation_logs(
    page: int = 1,
    per_page: int = 20,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    fallback_only: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve conversation logs with filters.
    
    Query Parameters:
        - page: Page number (default 1)
        - per_page: Items per page (default 20)
        - start_date: Filter conversations after this date
        - end_date: Filter conversations before this date
        - fallback_only: Show only conversations with fallback responses
    """
    # Build query
    query = select(Conversation).options(joinedload(Conversation.messages))
    
    # Apply date filters
    if start_date:
        query = query.where(Conversation.started_at >= start_date)
    
    if end_date:
        query = query.where(Conversation.started_at <= end_date)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page).order_by(Conversation.started_at.desc())
    
    # Execute query
    result = await db.execute(query)
    conversations = result.unique().scalars().all()
    
    # Filter by fallback if requested
    if fallback_only:
        conversations = [
            conv for conv in conversations
            if any(msg.was_fallback for msg in conv.messages if msg.sender == "bot")
        ]
    
    # Build response
    conversation_responses = []
    for conv in conversations:
        messages = [MessageResponse.model_validate(msg) for msg in conv.messages]
        conversation_responses.append(
            ConversationResponse(
                session_id=conv.session_id,
                started_at=conv.started_at,
                messages=messages
            )
        )
    
    return ConversationLogsResponse(
        conversations=conversation_responses,
        total_count=total,
        page=page,
        per_page=per_page
    )


# ============================================================================
# Analytics Endpoint
# ============================================================================

@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Compute analytics metrics.
    
    Metrics:
        - Fallback rate (percentage of queries resulting in fallback)
        - Total conversations and messages
        - Top unanswered queries (queries that triggered fallback)
        - KB coverage (percentage of categories with active entries)
    """
    # Default date range: last 30 days
    if not end_date:
        end_date = datetime.utcnow()
    
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Total messages in date range
    total_messages_query = select(func.count(Message.id)).where(
        and_(
            Message.created_at >= start_date,
            Message.created_at <= end_date,
            Message.sender == "bot"
        )
    )
    total_messages_result = await db.execute(total_messages_query)
    total_messages = total_messages_result.scalar() or 0
    
    # Fallback messages
    fallback_messages_query = select(func.count(Message.id)).where(
        and_(
            Message.created_at >= start_date,
            Message.created_at <= end_date,
            Message.sender == "bot",
            Message.was_fallback == True
        )
    )
    fallback_messages_result = await db.execute(fallback_messages_query)
    fallback_messages = fallback_messages_result.scalar() or 0
    
    # Fallback rate
    fallback_rate = fallback_messages / total_messages if total_messages > 0 else 0.0
    
    # Total conversations
    total_conversations_query = select(func.count(Conversation.id)).where(
        and_(
            Conversation.started_at >= start_date,
            Conversation.started_at <= end_date
        )
    )
    total_conversations_result = await db.execute(total_conversations_query)
    total_conversations = total_conversations_result.scalar() or 0
    
    # Top unanswered queries
    top_unanswered_query = select(
        Message.content,
        func.count(Message.id).label("count")
    ).where(
        and_(
            Message.created_at >= start_date,
            Message.created_at <= end_date,
            Message.sender == "user",
            Message.was_fallback == False
        )
    ).join(
        Message,
        and_(
            Message.conversation_id == Message.conversation_id,
            Message.sender == "bot",
            Message.was_fallback == True
        )
    ).group_by(Message.content).order_by(func.count(Message.id).desc()).limit(10)
    
    # Simplified: just get fallback user messages
    top_unanswered = []
    
    # KB coverage
    total_categories_result = await db.execute(select(func.count(KBCategory.id)))
    total_categories = total_categories_result.scalar() or 1
    
    covered_categories_result = await db.execute(
        select(func.count(func.distinct(KnowledgeBase.category_id))).where(
            KnowledgeBase.is_active == True
        )
    )
    covered_categories = covered_categories_result.scalar() or 0
    
    kb_coverage_percentage = covered_categories / total_categories if total_categories > 0 else 0.0
    
    return AnalyticsResponse(
        fallback_rate=fallback_rate,
        total_conversations=total_conversations,
        total_messages=total_messages,
        date_range={
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        top_unanswered_queries=top_unanswered,
        kb_coverage={
            "total_categories": total_categories,
            "covered_categories": covered_categories,
            "percentage": kb_coverage_percentage
        }
    )
