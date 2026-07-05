"""
Embedding service using sentence-transformers for semantic search.
Model: all-MiniLM-L6-v2 (384 dimensions)
"""
from sentence_transformers import SentenceTransformer
from typing import List
import logging

logger = logging.getLogger(__name__)

# Global model instance (loaded once at startup)
_model: SentenceTransformer = None


def load_model() -> SentenceTransformer:
    """
    Load sentence-transformers model.
    Called once during FastAPI startup (lifespan event).
    
    Returns:
        SentenceTransformer: Loaded model instance
    """
    global _model
    
    if _model is not None:
        logger.info("Model already loaded, returning cached instance")
        return _model
    
    logger.info("Loading sentence-transformers model: all-MiniLM-L6-v2")
    try:
        _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        logger.info("Model loaded successfully (384 dimensions)")
        return _model
    except Exception as e:
        logger.error(f"Failed to load embedding model: {str(e)}")
        raise RuntimeError(f"Could not load embedding model: {str(e)}")


def get_model() -> SentenceTransformer:
    """
    Get the cached model instance.
    
    Returns:
        SentenceTransformer: Cached model instance
        
    Raises:
        RuntimeError: If model is not loaded
    """
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    return _model


def embed(text: str) -> List[float]:
    """
    Generate embedding for a single text.
    
    Args:
        text: Input text to embed
        
    Returns:
        List[float]: 384-dimensional embedding vector
        
    Raises:
        ValueError: If text is empty or too long
        RuntimeError: If model is not loaded
    """
    # Validation
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    if len(text) > 5000:
        logger.warning(f"Text length ({len(text)}) exceeds 5000 characters, truncating")
        text = text[:5000]
    
    # Get model and generate embedding
    model = get_model()
    
    try:
        # Encode returns numpy array, convert to list
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        raise RuntimeError(f"Failed to generate embedding: {str(e)}")


def batch_embed(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts efficiently.
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List[List[float]]: List of 384-dimensional embedding vectors
        
    Raises:
        ValueError: If texts list is empty
        RuntimeError: If model is not loaded
    """
    if not texts:
        raise ValueError("Texts list cannot be empty")
    
    # Validate and truncate texts
    processed_texts = []
    for text in texts:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty in batch")
        
        if len(text) > 5000:
            logger.warning(f"Text length ({len(text)}) exceeds 5000 characters, truncating")
            text = text[:5000]
        
        processed_texts.append(text)
    
    # Get model and generate embeddings
    model = get_model()
    
    try:
        # Batch encoding is more efficient than individual calls
        embeddings = model.encode(processed_texts, convert_to_numpy=True, show_progress_bar=False)
        return [emb.tolist() for emb in embeddings]
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {str(e)}")
        raise RuntimeError(f"Failed to generate batch embeddings: {str(e)}")


def get_embedding_dimension() -> int:
    """
    Get the dimension of embeddings produced by the model.
    
    Returns:
        int: Embedding dimension (384 for all-MiniLM-L6-v2)
    """
    return 384
