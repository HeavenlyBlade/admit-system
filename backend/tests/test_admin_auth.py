"""
Tests for admin authentication — verifies that the JWT guard is enforced
and that bad credentials are rejected.

All tests use the mock DB fixture so no real database is needed.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_scalars_result(value=None):
    """Build the nested mock that SQLAlchemy's result.scalars().first() needs."""
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = value
    mock_result.scalars.return_value = mock_scalars
    mock_result.scalar.return_value = 0
    return mock_result


# ---------------------------------------------------------------------------
# Tests: accessing /api/admin/kb without authentication
# ---------------------------------------------------------------------------

class TestAdminKBRequiresAuth:
    """GET /api/admin/kb must be protected — no token → 401/403."""

    def test_no_token_returns_unauthorized(self, client):
        response = client.get("/api/admin/kb")
        assert response.status_code in (401, 403), (
            f"Expected 401 or 403 when no token provided, got {response.status_code}"
        )

    def test_invalid_token_returns_unauthorized(self, client):
        response = client.get(
            "/api/admin/kb",
            headers={"Authorization": "Bearer this.is.not.a.valid.token"},
        )
        assert response.status_code in (401, 403), (
            f"Expected 401 or 403 with invalid token, got {response.status_code}"
        )

    def test_malformed_auth_header_returns_unauthorized(self, client):
        """A non-Bearer scheme should also be rejected."""
        response = client.get(
            "/api/admin/kb",
            headers={"Authorization": "Basic dXNlcjpwYXNz"},
        )
        assert response.status_code in (401, 403), (
            f"Expected 401 or 403 with non-Bearer header, got {response.status_code}"
        )


# ---------------------------------------------------------------------------
# Tests: POST /api/admin/login with wrong credentials
# ---------------------------------------------------------------------------

class TestAdminLogin:
    """Admin login endpoint should return 401 for bad credentials."""

    def test_wrong_password_returns_401(self, client, mock_db):
        # Simulate an admin user with a known hash that won't match "wrongpassword"
        import bcrypt

        real_hash = bcrypt.hashpw(b"correctpassword", bcrypt.gensalt()).decode()
        mock_admin = MagicMock()
        mock_admin.username = "admin"
        mock_admin.password_hash = real_hash

        mock_db.execute = AsyncMock(return_value=_make_scalars_result(mock_admin))

        response = client.post(
            "/api/admin/login",
            json={"username": "admin", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_nonexistent_user_returns_401(self, client, mock_db):
        # No admin record found in DB
        mock_db.execute = AsyncMock(return_value=_make_scalars_result(None))

        response = client.post(
            "/api/admin/login",
            json={"username": "ghost", "password": "doesnotmatter"},
        )
        assert response.status_code == 401

    def test_empty_credentials_returns_422(self, client):
        """Missing required fields → validation error."""
        response = client.post("/api/admin/login", json={})
        assert response.status_code == 422
