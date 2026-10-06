/**
 * Sessions API client — conversation history endpoints.
 */
const BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Fetch all sessions for the authenticated user.
 * @param {string} token - JWT access token
 * @returns {Promise<Array>}
 */
export async function getSessions(token) {
  const res = await fetch(`${BASE_URL}/api/sessions`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Failed to fetch sessions');
  return res.json();
}

/**
 * Fetch messages for a single session.
 * @param {string} id - session_id UUID string
 * @param {string} token - JWT access token
 * @returns {Promise<Object>}
 */
export async function getSession(id, token) {
  const res = await fetch(`${BASE_URL}/api/sessions/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Failed to fetch session');
  return res.json();
}
