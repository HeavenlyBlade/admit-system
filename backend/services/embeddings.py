"""
Embedding service using fastembed (lightweight, no torch/CUDA).
Model: BAAI/bge-small-en-v1.5 (384 dimensions, ~130MB RAM)
"""
from fastembed import TextEmbedding
from typing import List
import logging

logger = logging.getLogger(__name__)

# Global model instance (loaded once at startup)
_model: TextEmbedding = None


def load_model() -> TextEmbedding:
    """
    Load fastembed model on startup.
    Much lighter than sentence-transformers (no torch dependency).
    """
    global _model
    if _model is not None:
        return _model

    logger.info("Loading fastembed model: BAAI/bge-small-en-v1.5")
    try:
        _model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        logger.info("Fastembed model loaded successfully (384 dimensions)")
        return _model
    except Exception as e:
        logger.error(f"Failed to load embedding model: {str(e)}")
        raise RuntimeError(f"Could not load embedding model: {str(e)}")


def get_model() -> TextEmbedding:
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    return _model


def embed(text: str) -> List[float]:
    """Generate 384-dim embedding for a single text."""
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    if len(text) > 5000:
        text = text[:5000]

    model = get_model()
    try:
        # fastembed returns a generator of numpy arrays
        embeddings = list(model.embed([text]))
        return embeddings[0].tolist()
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        raise RuntimeError(f"Failed to generate embedding: {str(e)}")


def batch_embed(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts."""
    if not texts:
        raise ValueError("Texts list cannot be empty")

    model = get_model()
    try:
        embeddings = list(model.embed(texts))
        return [emb.tolist() for emb in embeddings]
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {str(e)}")
        raise RuntimeError(f"Failed to generate batch embeddings: {str(e)}")


def get_embedding_dimension() -> int:
    return 384
