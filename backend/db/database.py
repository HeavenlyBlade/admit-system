"""
Database connection and session management for ADMIT system.
Uses SQLAlchemy async engine with connection pooling.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Parse DATABASE_URL manually to handle special characters in password
def build_engine_url(url: str) -> str:
    """
    Ensure the URL uses asyncpg driver and handle special characters.
    Supabase pooler works best with explicit SSL via connect_args.
    """
    # Normalize driver prefix
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Remove any existing ssl param from URL (we pass it via connect_args)
    if "?ssl=" in url:
        url = url.split("?ssl=")[0]
    if "&ssl=" in url:
        url = url.split("&ssl=")[0]
    
    return url


CLEAN_URL = build_engine_url(DATABASE_URL)

# SSL required for Supabase
CONNECT_ARGS = {"ssl": "require"}

# Create async engine
engine = create_async_engine(
    CLEAN_URL,
    connect_args=CONNECT_ARGS,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def init_db():
    """Initialize database tables and pgvector extension."""
    from sqlalchemy import text
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """FastAPI dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    """Context manager for database sessions outside FastAPI routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
