"""
Sessions router — returns conversation history for authenticated users.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from db.database import get_db
from models.schemas import Conversation, Message, User
from routers.auth import get_optional_user

router = APIRouter(tags=["Sessions"])


@router.get("/sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Return all conversation sessions for the authenticated user."""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    # Fetch all conversations for this user
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.started_at.desc())
    )
    conversations = result.scalars().all()

    sessions_out = []
    for conv in conversations:
        # Get first user message as title
        first_msg_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conv.id, Message.sender == "user")
            .order_by(Message.created_at.asc())
            .limit(1)
        )
        first_msg = first_msg_result.scalars().first()

        if first_msg:
            title = first_msg.content
            if len(title) > 60:
                title = title[:60] + "..."
        else:
            title = "New Conversation"

        # Count messages
        count_result = await db.execute(
            select(func.count()).where(Message.conversation_id == conv.id)
        )
        message_count = count_result.scalar() or 0

        sessions_out.append({
            "session_id": str(conv.session_id),
            "title": title,
            "started_at": conv.started_at,
            "message_count": message_count,
        })

    return sessions_out


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Return full message history for a conversation session."""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    result = await db.execute(
        select(Conversation).where(Conversation.session_id.cast(str) == session_id)
    )
    conversation = result.scalars().first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Session not found")

    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    messages_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
    )
    messages = messages_result.scalars().all()

    return {
        "session_id": str(conversation.session_id),
        "started_at": conversation.started_at,
        "messages": [
            {
                "id": m.id,
                "sender": m.sender,
                "content": m.content,
                "timestamp": m.created_at,
                "was_fallback": m.was_fallback,
            }
            for m in messages
        ],
    }
