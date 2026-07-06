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
    allow_headers=["*"],
    expose_headers=["*"]
)

# Register routers
app.include_router(chat.router)
app.include_router(admin.router)


# Health check endpoint
@app.get("/debug-env")
async def debug_env():
    """Temporary debug endpoint."""
    import os
    db_url = os.getenv("DATABASE_URL", "NOT SET")
    if "@" in db_url:
        parts = db_url.split("@")
        user_part = parts[0].split(":")
        password = user_part[-1]
        masked = ":".join(user_part[:-1]) + f":{password[:4]}***@" + parts[1]
    else:
        masked = db_url
    return {"DATABASE_URL": masked}


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


@app.post("/setup")
async def setup_database():
    """
    One-time setup: run migration and seed initial data.
    Run this once after deployment to initialize tables and admin user.
    """
    from sqlalchemy import text as sql_text
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    results = []

    try:
        async with engine.begin() as conn:
            # Enable pgvector
            await conn.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector"))
            results.append("✓ pgvector extension enabled")

            # Create tables
            await conn.run_sync(Base.metadata.create_all)
            results.append("✓ Tables created")

            # Seed categories
            await conn.execute(sql_text("""
                INSERT INTO kb_categories (name, department) VALUES
                ('Admission Requirements','IBED'),('Enrollment Steps','IBED'),
                ('Programs Offered','IBED'),('Tuition and Payment','IBED'),
                ('Scholarships','IBED'),('Contact Information','IBED'),
                ('Admission Requirements','SHS'),('Enrollment Steps','SHS'),
                ('Programs Offered','SHS'),('Tuition and Payment','SHS'),
                ('Scholarships','SHS'),('Contact Information','SHS'),
                ('Admission Requirements','HED'),('Enrollment Steps','HED'),
                ('Programs Offered','HED'),('Tuition and Payment','HED'),
                ('Scholarships','HED'),('Contact Information','HED'),
                ('Admission Requirements','TESDA'),('Enrollment Steps','TESDA'),
                ('Programs Offered','TESDA'),('Tuition and Payment','TESDA'),
                ('Scholarships','TESDA'),('Contact Information','TESDA'),
                ('About SACLI','GENERAL'),('Campus Facilities','GENERAL'),
                ('Student Services','GENERAL')
                ON CONFLICT DO NOTHING
            """))
            results.append("✓ KB categories seeded")

            # Seed admin user
            password_hash = pwd_context.hash("admin123")
            await conn.execute(sql_text(
                f"INSERT INTO admin_users (username, password_hash, role) "
                f"VALUES ('admin', '{password_hash}', 'admin') "
                f"ON CONFLICT (username) DO NOTHING"
            ))
            results.append("✓ Admin user created (admin/admin123)")

        return {"status": "success", "steps": results}

    except Exception as e:
        return {"status": "error", "message": str(e), "steps": results}


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
