"""
Database initialization script for ADMIT system.
Creates all tables, enables pgvector extension, and sets up indexes.
"""
import asyncio
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from db.database import engine, Base
from models.schemas import KBCategory, KnowledgeBase, AdminUser, Conversation, Message


async def create_indexes(conn):
    """Create indexes for performance optimization"""
    print("Creating indexes...")
    
    # HNSW chosen over ivfflat: better recall at small KB sizes, no need to
    # REINDEX after data changes. Drop the old ivfflat index if it exists.
    await conn.execute(text("""
        DROP INDEX IF EXISTS idx_kb_embedding
    """))
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS kb_embedding_hnsw_idx
        ON knowledge_base
        USING hnsw (embedding vector_cosine_ops)
        WITH (m=16, ef_construction=64)
    """))
    print("  ✓ Created pgvector HNSW index on knowledge_base.embedding")
    
    # B-tree indexes for foreign keys and filtering
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_kb_category 
        ON knowledge_base (category_id)
    """))
    print("  ✓ Created index on knowledge_base.category_id")
    
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_kb_active 
        ON knowledge_base (is_active)
    """))
    print("  ✓ Created index on knowledge_base.is_active")
    
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_conv_session 
        ON conversations (session_id)
    """))
    print("  ✓ Created index on conversations.session_id")
    
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_conv_started 
        ON conversations (started_at)
    """))
    print("  ✓ Created index on conversations.started_at")
    
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_msg_conversation 
        ON messages (conversation_id)
    """))
    print("  ✓ Created index on messages.conversation_id")
    
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_msg_fallback 
        ON messages (was_fallback)
    """))
    print("  ✓ Created index on messages.was_fallback")
    
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_msg_created 
        ON messages (created_at)
    """))
    print("  ✓ Created index on messages.created_at")
    
    print("All indexes created successfully!")


async def init_database():
    """Initialize database with all tables and indexes"""
    print("=" * 60)
    print("ADMIT Database Initialization")
    print("=" * 60)
    
    async with engine.begin() as conn:
        print("\n1. Enabling pgvector extension...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        print("  ✓ pgvector extension enabled")
        
        print("\n2. Creating database tables...")
        # Drop all tables (use with caution in production!)
        # await conn.run_sync(Base.metadata.drop_all)
        # print("  ✓ Dropped existing tables")
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("  ✓ Created tables:")
        print("    - kb_categories")
        print("    - knowledge_base")
        print("    - admin_users")
        print("    - conversations")
        print("    - messages")
        
        print("\n3. Creating indexes...")
        await create_indexes(conn)
        
    print("\n" + "=" * 60)
    print("Database initialization completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run seed_data.py to populate initial data")
    print("  2. Start the FastAPI server with: uvicorn main:app --reload")


if __name__ == "__main__":
    asyncio.run(init_database())
