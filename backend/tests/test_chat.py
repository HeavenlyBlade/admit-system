"""
Tests for the public chat endpoint (/api/chat).
Embedding service and Groq LLM are mocked so no external calls are made.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import uuid


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_scalars_result(value=None):
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = value
    mock_result.scalars.return_value = mock_scalars
    mock_result.scalar.return_value = 0
    return mock_result


def _post_chat(client, message, session_id=None):
    """POST /api/chat helper."""
    payload = {"message": message}
    if session_id:
        payload["session_id"] = str(session_id)
    return client.post("/api/chat", json=payload)


# ---------------------------------------------------------------------------
# Tests: basic chat flow
# ---------------------------------------------------------------------------

class TestChatEndpoint:
    """Happy-path and validation tests for POST /api/chat."""

    def test_valid_message_returns_200_with_answer(self, client, mock_db):
        """A normal message should return 200 and include a 'response' field."""
        # DB: no existing conversation found → create new
        mock_db.execute = AsyncMock(return_value=_make_scalars_result(None))

        # Mock the conversation object that gets added + flushed
        mock_conversation = MagicMock()
        mock_conversation.id = 1
        mock_conversation.session_id = uuid.uuid4()
        mock_conversation.user_id = None

        def fake_add(obj):
            if hasattr(obj, "session_id"):
                obj.id = 1

        mock_db.add.side_effect = fake_add

        with patch("routers.chat.retrieve_relevant_context", new_callable=AsyncMock) as mock_retrieve, \
             patch("routers.chat.generate_response") as mock_gen, \
             patch("routers.chat.build_fallback_message") as mock_fallback:

            mock_retrieve.return_value = ([], False)
            mock_fallback.return_value = "Please contact the admissions office."

            response = _post_chat(client, "What are the admission requirements?")

        assert response.status_code == 200
        body = response.json()
        assert "response" in body
        assert "session_id" in body
        assert "was_fallback" in body

    def test_message_over_500_chars_returns_422(self, client):
        """Messages exceeding the 500-character limit must be rejected."""
        long_msg = "a" * 501
        response = _post_chat(client, long_msg)
        assert response.status_code == 422

    def test_empty_message_returns_422(self, client):
        """Empty string must fail validation (min_length=1)."""
        response = _post_chat(client, "")
        assert response.status_code == 422

    def test_whitespace_only_message_fails_validation(self, client):
        """A message of only spaces still has length > 0, so 200 is acceptable,
        but it should never crash — just return a response."""
        with patch("routers.chat.retrieve_relevant_context", new_callable=AsyncMock) as mock_retrieve, \
             patch("routers.chat.build_fallback_message") as mock_fallback:

            mock_retrieve.return_value = ([], False)
            mock_fallback.return_value = "Please contact the admissions office."

            response = _post_chat(client, "   ")

        # Either 422 (if stripped) or 200 (with fallback) — must not be 500
        assert response.status_code in (200, 422)

    def test_high_confidence_returns_llm_response(self, client, mock_db):
        """When retrieval returns high-confidence matches, the LLM path is used."""
        mock_db.execute = AsyncMock(return_value=_make_scalars_result(None))

        mock_match = MagicMock()
        mock_match.id = 1

        with patch("routers.chat.retrieve_relevant_context", new_callable=AsyncMock) as mock_retrieve, \
             patch("routers.chat.generate_response") as mock_gen:

            mock_retrieve.return_value = ([mock_match], True)
            mock_gen.return_value = "SACLI requires Form 137 and a birth certificate."

            response = _post_chat(client, "What do I need to enroll?")

        assert response.status_code == 200
        body = response.json()
        assert body["was_fallback"] is False

    def test_low_confidence_returns_fallback(self, client, mock_db):
        """When retrieval returns low confidence, the fallback path is used."""
        mock_db.execute = AsyncMock(return_value=_make_scalars_result(None))

        with patch("routers.chat.retrieve_relevant_context", new_callable=AsyncMock) as mock_retrieve, \
             patch("routers.chat.build_fallback_message") as mock_fallback:

            mock_retrieve.return_value = ([], False)
            mock_fallback.return_value = "Please contact the admissions office."

            response = _post_chat(client, "Who won the World Cup?")

        assert response.status_code == 200
        body = response.json()
        assert body["was_fallback"] is True
