"""
ADMIT - Main FastAPI application entry point.
Conversational AI System for Admissions & Enrollment Assistance.
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from routers import chat, admin
from routers.auth import router as auth_router
from routers.sessions import router as sessions_router
from services.embeddings import load_model
from db.database import engine, init_db, Base

# Rate limiter — keyed by client IP; shared with routers via app.state
limiter = Limiter(key_func=get_remote_address)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CORS origins from environment
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")]

# C21 — Gate /docs and /redoc in production
_is_production = os.environ.get("ENVIRONMENT") == "production"
docs_url = None if _is_production else "/docs"
redoc_url = None if _is_production else "/redoc"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan event - runs on startup and shutdown.
    Preloads embedding model for performance.
    """
    # Startup
    logger.info("=" * 60)
    logger.info("ADMIT System Starting Up")
    logger.info("=" * 60)

    # Initialize database (non-blocking - warns but doesn't crash)
    try:
        logger.info("Initializing database...")
        await init_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.warning(f"Database init warning (will retry on first request): {str(e)}")

    # Preload embedding model
    try:
        logger.info("Loading embedding model...")
        load_model()
        logger.info("✓ Embedding model loaded and cached")
    except Exception as e:
        logger.warning(f"Embedding model load warning: {str(e)}")

    logger.info("=" * 60)
    logger.info("ADMIT System Ready")
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("ADMIT System shutting down...")


# Create FastAPI application
app = FastAPI(
    title="ADMIT API",
    description="Conversational AI System for SACLI Admissions & Enrollment Assistance",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=docs_url,
    redoc_url=redoc_url,
)

# Attach rate limiter to app state and register the 429 handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# C23 — Basic security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    """Add standard security headers to every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
    expose_headers=["Content-Type", "Authorization"],
)

# Register routers
app.include_router(chat.router)
app.include_router(admin.router)
app.include_router(auth_router, prefix="/api/auth")
app.include_router(sessions_router, prefix="/api")


@app.get("/debug/retrieval")
async def debug_retrieval():
    """Debug endpoint — test embedding + vector search end to end. Remove before final production."""
    from services.embeddings import load_model, embed, _model
    from sqlalchemy import text as sql_text

    result = {"embedding_model_loaded": _model is not None}

    # Step 1: embed
    try:
        load_model()
        emb = embed("What programs does SACLI offer?")
        result["embed_ok"] = True
        result["embed_dim"] = len(emb)
    except Exception as e:
        result["embed_ok"] = False
        result["embed_error"] = str(e)
        return result

    # Step 2: raw vector search
    try:
        emb_str = "[" + ",".join(map(str, emb)) + "]"
        async with engine.connect() as conn:
            r = await conn.execute(sql_text("""
                SELECT id, title,
                       1 - (embedding <=> CAST(:emb AS vector)) AS similarity
                FROM knowledge_base
                WHERE is_active = true
                ORDER BY embedding <=> CAST(:emb AS vector)
                LIMIT 5
            """), {"emb": emb_str})
            rows = r.fetchall()
            result["search_ok"] = True
            result["matches"] = [
                {"id": row[0], "title": row[1], "similarity": float(row[2])}
                for row in rows
            ]
    except Exception as e:
        result["search_ok"] = False
        result["search_error"] = str(e)

    return result
async def health_check():
    """Health check endpoint showing DB and service status."""
    from sqlalchemy import text as sql_text
    from services.embeddings import _model
    db_status = "unknown"
    db_error = None
    tables = []
    admin_count = 0
    kb_count = 0

    try:
        async with engine.connect() as conn:
            await conn.execute(sql_text("SELECT 1"))
            db_status = "connected"

            result = await conn.execute(sql_text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            ))
            tables = [row[0] for row in result.fetchall()]

            if "admin_users" in tables:
                result = await conn.execute(sql_text("SELECT COUNT(*) FROM admin_users"))
                admin_count = result.scalar()

            if "knowledge_base" in tables:
                result = await conn.execute(sql_text(
                    "SELECT COUNT(*) FROM knowledge_base WHERE is_active = true AND embedding IS NOT NULL"
                ))
                kb_count = result.scalar()

    except Exception as e:
        db_status = "error"
        db_error = str(e)

    embedding_model_loaded = _model is not None

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "ADMIT API",
        "version": "1.0.0",
        "database": db_status,
        "database_error": db_error,
        "tables": tables,
        "admin_users_count": admin_count,
        "kb_entries_active": kb_count,
        "embedding_model_loaded": embedding_model_loaded,
    }


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Welcome to ADMIT API",
        "description": "Conversational AI System for SACLI Admissions & Enrollment",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "chat": "/api/chat",
            "quick_replies": "/api/quick-replies",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
