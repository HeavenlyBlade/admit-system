"""
Database connection using individual env vars to avoid URL password encoding issues.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# Support both combined URL and individual components
# Individual components take priority to avoid URL encoding issues
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "6543")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "postgres")
DATABASE_URL = os.getenv("DATABASE_URL")

if DB_HOST and DB_USER and DB_PASSWORD:
    # Build URL from components (password handled safely by SQLAlchemy)
    from sqlalchemy.engine import URL
    engine_url = URL.create(
        drivername="postgresql+asyncpg",
        username=DB_USER,
        password=DB_PASSWORD,  # SQLAlchemy handles special chars automatically
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
    )
    CLEAN_URL = str(engine_url)
elif DATABASE_URL:
    # Fall back to combined URL
    url = DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine_url = url
    CLEAN_URL = url
else:
    raise ValueError("Either DATABASE_URL or DB_HOST/DB_USER/DB_PASSWORD must be set")

engine = create_async_engine(
    engine_url,
    connect_args={"ssl": "require"},
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def init_db():
    from sqlalchemy import text
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
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
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
