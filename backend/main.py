"""
ADMIT - Main FastAPI application entry point.
Conversational AI System for Admissions & Enrollment Assistance.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from routers import chat, admin
from routers.auth import router as auth_router
from routers.sessions import router as sessions_router
from services.embeddings import load_model
from db.database import engine, init_db, Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CORS origins from environment
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")


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
    docs_url="/docs",
    redoc_url="/redoc"
)

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


@app.post("/api/migrate")
async def run_migration():
    """Force-create all database tables. Safe to call multiple times (CREATE IF NOT EXISTS)."""
    try:
        await init_db()
        return {"status": "ok", "message": "Database tables created/verified"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/health")
async def health_check():
    """Health check endpoint showing DB and service status."""
    from sqlalchemy import text as sql_text
    from sqlalchemy import inspect
    db_status = "unknown"
    db_error = None
    tables = []
    admin_count = 0

    try:
        async with engine.connect() as conn:
            await conn.execute(sql_text("SELECT 1"))
            db_status = "connected"

            # Check if tables exist
            result = await conn.execute(sql_text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            ))
            tables = [row[0] for row in result.fetchall()]

            # Check admin user count
            if "admin_users" in tables:
                result = await conn.execute(sql_text("SELECT COUNT(*) FROM admin_users"))
                admin_count = result.scalar()

    except Exception as e:
        db_status = "error"
        db_error = str(e)

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "ADMIT API",
        "version": "1.0.0",
        "database": db_status,
        "database_error": db_error,
        "tables": tables,
        "admin_users_count": admin_count,
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
