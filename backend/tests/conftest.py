"""
Test configuration and shared fixtures for ADMIT backend tests.
No real database or external API calls are made here.
"""
import os
import pytest
from unittest.mock import MagicMock, AsyncMock

# Set required environment variables before any app imports
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DATABASE_URL", "postgresql://localhost/admit_test")
os.environ.setdefault("GROQ_API_KEY", "test-key")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-for-testing-only")
os.environ.setdefault("CONFIDENCE_THRESHOLD", "0.35")
os.environ.setdefault("ENVIRONMENT", "test")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def mock_db():
    """
    Return a mock AsyncSession so tests never touch a real database.
    All awaitable methods are AsyncMock; others are plain MagicMock.
    """
    session = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def client(mock_db):
    """
    FastAPI TestClient with the real app but with the DB dependency
    overridden to use the mock session.
    """
    # Patch fastembed model loading so the app doesn't try to download it
    from unittest.mock import patch
    import numpy as np

    dummy_embedding = [0.1] * 384

    with patch("services.embeddings.load_model", return_value=None), \
         patch("services.embeddings._model", new=MagicMock()), \
         patch("services.embeddings.embed", return_value=dummy_embedding):

        from fastapi.testclient import TestClient
        from main import app
        from db.database import get_db

        async def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        with TestClient(app, raise_server_exceptions=False) as c:
            yield c

        # Clean up override after each test
        app.dependency_overrides.pop(get_db, None)
