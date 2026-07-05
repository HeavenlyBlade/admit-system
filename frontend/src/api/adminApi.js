/**
 * Admin API client for ADMIT system
 * Handles JWT authentication and admin operations
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance
const adminClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
adminClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admit_admin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle 401 errors
adminClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('admit_admin_token');
      window.location.href = '/admin/login';
    }
    return Promise.reject(error);
  }
);

/**
 * Admin login
 */
export const login = async (username, password) => {
  const response = await adminClient.post('/api/admin/login', {
    username,
    password,
  });
  
  // Store token
  localStorage.setItem('admit_admin_token', response.data.access_token);
  return response.data;
};

/**
 * Logout
 */
export const logout = () => {
  localStorage.removeItem('admit_admin_token');
  window.location.href = '/admin/login';
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = () => {
  return !!localStorage.getItem('admit_admin_token');
};

/**
 * List KB entries with filters
 */
export const listKB = async (params = {}) => {
  const response = await adminClient.get('/api/admin/kb', { params });
  return response.data;
};

/**
 * Create KB entry
 */
export const createKB = async (data) => {
  const response = await adminClient.post('/api/admin/kb', data);
  return response.data;
};

/**
 * Update KB entry
 */
export const updateKB = async (id, data) => {
  const response = await adminClient.put(`/api/admin/kb/${id}`, data);
  return response.data;
};

/**
 * Delete KB entry (soft delete)
 */
export const deleteKB = async (id) => {
  await adminClient.delete(`/api/admin/kb/${id}`);
};

/**
 * Get conversation logs
 */
export const getLogs = async (params = {}) => {
  const response = await adminClient.get('/api/admin/logs', { params });
  return response.data;
};

/**
 * Get analytics
 */
export const getAnalytics = async (params = {}) => {
  const response = await adminClient.get('/api/admin/analytics', { params });
  return response.data;
};

export default adminClient;
