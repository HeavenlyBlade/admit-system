"""
Tests for rate limiting on POST /api/chat.
Verifies that the 21st request in a burst returns HTTP 429.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


RATE_LIMIT = 20  # Must match the @limiter.limit("20/minute") in chat.py


def _make_scalars_result(value=None):
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = value
    mock_result.scalars.return_value = mock_scalars
    mock_result.scalar.return_value = 0
    return mock_result


class TestChatRateLimit:
    """The chat endpoint is limited to 20 req/min per IP."""

    def test_21st_request_returns_429(self, client, mock_db):
        """Send RATE_LIMIT+1 requests in quick succession; last one must be 429."""
        mock_db.execute = AsyncMock(return_value=_make_scalars_result(None))

        with patch("routers.chat.retrieve_relevant_context", new_callable=AsyncMock) as mock_retrieve, \
             patch("routers.chat.build_fallback_message") as mock_fallback:

            mock_retrieve.return_value = ([], False)
            mock_fallback.return_value = "Please contact the admissions office."

            statuses = []
            for i in range(RATE_LIMIT + 1):
                r = client.post(
                    "/api/chat",
                    json={"message": f"Test message {i}"},
                )
                statuses.append(r.status_code)

        # The first 20 should succeed (200); the 21st should be 429
        assert statuses[-1] == 429, (
            f"Expected 429 on request {RATE_LIMIT + 1}, got {statuses[-1]}. "
            f"All statuses: {statuses}"
        )
        # At least the first request should have succeeded
        assert statuses[0] == 200, (
            f"Expected first request to succeed (200), got {statuses[0]}"
        )
