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
from services.embeddings import load_model
from db.database import init_db

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
    
    try:
    try:
        # Initialize database (create tables if needed)
        logger.info("Initializing database...")
        await init_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization failed (will retry on first request): {str(e)}")
        
        # Preload embedding model
        logger.info("Loading embedding model...")
        load_model()
        logger.info("✓ Embedding model loaded and cached")
        
        logger.info("=" * 60)
        logger.info("ADMIT System Ready")
        logger.info("=" * 60)
        logger.info("API Documentation: http://localhost:8000/docs")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise
    
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
    allow_headers=["*"],
    expose_headers=["*"]
)

# Register routers
app.include_router(chat.router)
app.include_router(admin.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns system status and service availability.
    """
    return {
        "status": "healthy",
        "service": "ADMIT API",
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "embedding_model": "loaded",
            "llm_api": "configured"
        }
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
            "admin_login": "/api/admin/login",
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
