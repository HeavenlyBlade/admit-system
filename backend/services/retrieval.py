"""
Retrieval service for semantic search using pgvector.
Performs cosine similarity search and confidence scoring.
"""
from typing import List, Dict, Any
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
import os
import logging

from models.schemas import KnowledgeBase, KBCategory
from services.embeddings import embed

logger = logging.getLogger(__name__)

# Confidence threshold from environment (default 0.35)
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.35"))


class KBMatch:
    """Container for knowledge base search match"""
    def __init__(self, kb_entry: KnowledgeBase, similarity_score: float, category: KBCategory = None):
        self.id = kb_entry.id
        self.title = kb_entry.title
        self.content = kb_entry.content
        self.category_id = kb_entry.category_id
        self.similarity_score = similarity_score
        self.category = category
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category_id": self.category_id,
            "similarity_score": self.similarity_score,
            "category_name": self.category.name if self.category else None,
            "department": self.category.department if self.category else None,
        }


async def search_kb(
    db: AsyncSession,
    query_embedding: List[float],
    top_k: int = 5
) -> List[KBMatch]:
    """
    Perform semantic search against knowledge base using pgvector.
    
    Args:
        db: Database session
        query_embedding: 384-dimensional query vector
        top_k: Number of top matches to return (default 5)
        
    Returns:
        List[KBMatch]: Top K most similar KB entries with scores
    """
    try:
        # Convert embedding to PostgreSQL vector format
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        # Pgvector cosine similarity query
        # Note: <=> operator returns cosine distance (0 = identical, 2 = opposite)
        # We convert to similarity score: 1 - (distance / 2)
        query = text("""
            SELECT 
                kb.id,
                kb.category_id,
                kb.title,
                kb.content,
                kb.is_active,
                kb.updated_by,
                kb.updated_at,
                1 - (kb.embedding <=> :embedding::vector) AS similarity_score
            FROM knowledge_base kb
            WHERE kb.is_active = true
            ORDER BY kb.embedding <=> :embedding::vector
            LIMIT :top_k
        """)
        
        result = await db.execute(
            query,
            {"embedding": embedding_str, "top_k": top_k}
        )
        
        rows = result.fetchall()
        
        if not rows:
            logger.warning("No active KB entries found")
            return []
        
        # Fetch categories for matched entries
        category_ids = [row[1] for row in rows]
        category_result = await db.execute(
            select(KBCategory).where(KBCategory.id.in_(category_ids))
        )
        categories = {cat.id: cat for cat in category_result.scalars().all()}
        
        # Build KBMatch objects
        matches = []
        for row in rows:
            # Reconstruct KnowledgeBase object from row
            kb_entry = KnowledgeBase(
                id=row[0],
                category_id=row[1],
                title=row[2],
                content=row[3],
                is_active=row[4],
                updated_by=row[5],
                updated_at=row[6],
            )
            
            similarity_score = float(row[7])
            category = categories.get(kb_entry.category_id)
            
            matches.append(KBMatch(kb_entry, similarity_score, category))
        
        logger.info(f"Found {len(matches)} KB matches (best score: {matches[0].similarity_score:.3f})")
        return matches
        
    except Exception as e:
        logger.error(f"Error during KB search: {str(e)}")
        raise RuntimeError(f"Knowledge base search failed: {str(e)}")


def calculate_confidence(similarity_score: float) -> float:
    """
    Calculate confidence score from similarity.
    
    Args:
        similarity_score: Cosine similarity (0.0 to 1.0)
        
    Returns:
        float: Confidence score (0.0 to 1.0)
    """
    # For now, confidence = similarity
    # Could be extended with more sophisticated logic
    return max(0.0, min(1.0, similarity_score))


def is_high_confidence(similarity_score: float) -> bool:
    """
    Check if similarity score exceeds confidence threshold.
    
    Args:
        similarity_score: Best match similarity score
        
    Returns:
        bool: True if confidence is high enough for LLM generation
    """
    confidence = calculate_confidence(similarity_score)
    return confidence >= CONFIDENCE_THRESHOLD


async def retrieve_relevant_context(
    db: AsyncSession,
    query: str,
    top_k: int = 5
) -> tuple[List[KBMatch], bool]:
    """
    End-to-end retrieval: embed query, search KB, check confidence.
    
    Args:
        db: Database session
        query: User query text
        top_k: Number of matches to retrieve
        
    Returns:
        tuple: (List of KB matches, is_high_confidence flag)
    """
    # Generate query embedding
    try:
        query_embedding = embed(query)
    except Exception as e:
        logger.error(f"Failed to embed query: {str(e)}")
        return [], False
    
    # Search knowledge base
    matches = await search_kb(db, query_embedding, top_k)
    
    if not matches:
        logger.info("No KB matches found, triggering fallback")
        return [], False
    
    # Check confidence
    best_score = matches[0].similarity_score
    is_confident = is_high_confidence(best_score)
    
    logger.info(
        f"Query: '{query[:50]}...' | Best score: {best_score:.3f} | "
        f"Threshold: {CONFIDENCE_THRESHOLD} | High confidence: {is_confident}"
    )
    
    return matches, is_confident
