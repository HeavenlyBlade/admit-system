/**
 * Chat API client for ADMIT system
 * Handles communication with backend chat endpoints
 */
import axios from 'axios';

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  'http://localhost:8000';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Send message to chat endpoint
 * @param {string} message - User message
 * @param {string|null} sessionId - Optional session ID for conversation tracking
 * @param {string|null} token - Optional JWT for authenticated requests
 * @returns {Promise<Object>} Chat response with bot message and metadata
 */
export const sendMessage = async (message, sessionId = null, token = null) => {
  try {
    const headers = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    const response = await apiClient.post(
      '/api/chat',
      { message, session_id: sessionId },
      { headers }
    );
    // Normalize the response so callers always see matched_kb_titles,
    // even if an older backend omits the field.
    return {
      ...response.data,
      matched_kb_ids: response.data.matched_kb_ids || [],
      matched_kb_titles: response.data.matched_kb_titles || [],
    };
  } catch (error) {
    console.error('Error sending message:', error);
    throw new Error(
      error.response?.data?.detail?.error?.message ||
        'Failed to send message. Please try again.'
    );
  }
};

/**
 * Send a message using the SSE streaming endpoint.
 *
 * Uses fetch() + a ReadableStream reader (axios does not handle SSE well) to
 * parse the text/event-stream manually. For each `{"token": "..."}` event the
 * `onToken` callback is invoked with the incremental text; when the terminal
 * `{"done": true, ...}` event arrives `onDone` is invoked with the metadata
 * object and the same metadata is returned.
 *
 * @param {string} message - User message
 * @param {string|null} sessionId - Optional session ID for conversation tracking
 * @param {string|null} token - Optional JWT for authenticated requests
 * @param {(text: string) => void} onToken - Called for each streamed token
 * @param {(metadata: Object) => void} onDone - Called with the final metadata
 * @returns {Promise<Object>} Final metadata payload
 */
export const sendMessageStream = async (
  message,
  sessionId = null,
  token = null,
  onToken,
  onDone
) => {
  const headers = { 'Content-Type': 'application/json', Accept: 'text/event-stream' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (!response.ok || !response.body) {
    throw new Error('Failed to start streaming response');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let metadata = null;

  // eslint-disable-next-line no-constant-condition
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // SSE frames are separated by a blank line (\n\n). Process every complete
    // frame currently in the buffer and keep the remainder for the next chunk.
    let sepIndex;
    while ((sepIndex = buffer.indexOf('\n\n')) !== -1) {
      const rawFrame = buffer.slice(0, sepIndex);
      buffer = buffer.slice(sepIndex + 2);

      const line = rawFrame.trim();
      if (!line.startsWith('data:')) continue;

      const dataStr = line.slice(5).trim();
      if (!dataStr) continue;

      let payload;
      try {
        payload = JSON.parse(dataStr);
      } catch (err) {
        // Ignore malformed frames rather than aborting the whole stream.
        continue;
      }

      if (payload.error) {
        throw new Error(payload.error);
      }

      if (payload.token) {
        onToken?.(payload.token);
      } else if (payload.done) {
        metadata = {
          ...payload,
          matched_kb_ids: payload.matched_kb_ids || [],
          matched_kb_titles: payload.matched_kb_titles || [],
        };
        onDone?.(metadata);
        return metadata;
      }
    }
  }

  return metadata;
};

/**
 * Get quick reply buttons
 * @returns {Promise<Array>} Array of quick reply options
 */
export const getQuickReplies = async () => {
  try {
    const response = await apiClient.get('/api/quick-replies');
    return response.data;
  } catch (error) {
    console.error('Error fetching quick replies:', error);
    return [];
  }
};

export default apiClient;
