"""
Chat router for public-facing conversational AI endpoints.
Orchestrates the full RAG pipeline: retrieval → generation → logging.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import logging

from db.database import get_db
from models.pydantic_schemas import ChatRequest, ChatResponse, QuickReply
from models.schemas import Conversation, Message
from services.retrieval import retrieve_relevant_context
from services.llm import generate_response, build_fallback_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Main chat endpoint - processes user messages through RAG pipeline.
    
    Flow:
    1. Validate input and manage session
    2. Embed query and search knowledge base
    3. Generate response (LLM or fallback)
    4. Log conversation
    5. Return response with metadata
    """
    try:
        # 1. Session management
        session_id = request.session_id or uuid.uuid4()
        
        # Get or create conversation
        result = await db.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        conversation = result.scalars().first()
        
        if not conversation:
            conversation = Conversation(session_id=session_id)
            db.add(conversation)
            await db.flush()  # Get conversation.id
            logger.info(f"Created new conversation: {session_id}")
        
        # 2. Log user message
        user_message = Message(
            conversation_id=conversation.id,
            sender="user",
            content=request.message,
            matched_kb_ids=None,
            was_fallback=False
        )
        db.add(user_message)
        
        # 3. RAG Pipeline: Retrieval
        logger.info(f"Processing query: '{request.message[:100]}...'")
        matches, is_high_confidence = await retrieve_relevant_context(
            db, request.message, top_k=5
        )
        
        # 4. RAG Pipeline: Generation or Fallback
        if is_high_confidence and matches:
            # High confidence - generate LLM response
            try:
                response_text = generate_response(matches, request.message)
                matched_kb_ids = [match.id for match in matches]
                was_fallback = False
                logger.info("Generated LLM response")
            except Exception as e:
                logger.error(f"LLM generation failed: {str(e)}, using fallback")
                response_text = build_fallback_message(request.message)
                matched_kb_ids = []
                was_fallback = True
        else:
            # Low confidence - use fallback
            response_text = build_fallback_message(request.message)
            matched_kb_ids = []
            was_fallback = True
            logger.info("Low confidence, using fallback response")
        
        # 5. Log bot response
        bot_message = Message(
            conversation_id=conversation.id,
            sender="bot",
            content=response_text,
            matched_kb_ids=matched_kb_ids,
            was_fallback=was_fallback
        )
        db.add(bot_message)
        
        await db.commit()
        
        # 6. Return response
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            was_fallback=was_fallback,
            matched_kb_ids=matched_kb_ids
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "CHAT_ERROR",
                    "message": "An error occurred processing your message",
                    "details": str(e)
                }
            }
        )


@router.get("/quick-replies", response_model=list[QuickReply])
async def get_quick_replies():
    """
    Get quick reply buttons for common inquiry categories.
    
    Returns predefined categories that users can tap to initiate queries.
    """
    quick_replies = [
        QuickReply(
            id=1,
            name="Admission Requirements",
            query="What are the admission requirements for SACLI?"
        ),
        QuickReply(
            id=2,
            name="Enrollment Steps",
            query="What are the steps to enroll at SACLI?"
        ),
        QuickReply(
            id=3,
            name="Programs Offered",
            query="What programs and courses does SACLI offer?"
        ),
        QuickReply(
            id=4,
            name="Tuition & Payment",
            query="What are the tuition fees and payment options?"
        ),
        QuickReply(
            id=5,
            name="Scholarships",
            query="What scholarships are available at SACLI?"
        ),
        QuickReply(
            id=6,
            name="Contact Info",
            query="How can I contact SACLI offices?"
        ),
    ]
    
    return quick_replies
