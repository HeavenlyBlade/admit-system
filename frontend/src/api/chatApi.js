/**
 * Chat API client for ADMIT system
 * Handles communication with backend chat endpoints
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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
 * @returns {Promise<Object>} Chat response with bot message and metadata
 */
export const sendMessage = async (message, sessionId = null) => {
  try {
    const response = await apiClient.post('/api/chat', {
      message,
      session_id: sessionId,
    });
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw new Error(
      error.response?.data?.detail?.error?.message || 
      'Failed to send message. Please try again.'
    );
  }
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
