/**
 * AdminDashboard tests — verifies that unauthenticated users are redirected
 * to the login page.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

// Mock the admin API module so no real HTTP calls are made
vi.mock('../api/adminApi', () => ({
  isAuthenticated: vi.fn(),
  logout: vi.fn(),
  listKB: vi.fn().mockResolvedValue({ entries: [], total: 0, page: 1, per_page: 25 }),
  getLogs: vi.fn().mockResolvedValue({ conversations: [], total_count: 0, page: 1, per_page: 20 }),
  getAnalytics: vi.fn().mockResolvedValue({
    fallback_rate: 0,
    total_conversations: 0,
    total_messages: 0,
    date_range: {},
    top_unanswered_queries: [],
    kb_coverage: {},
  }),
}));

// Mock axios to prevent any residual network calls
vi.mock('axios', () => {
  const instance = {
    get: vi.fn().mockResolvedValue({ data: {} }),
    post: vi.fn().mockResolvedValue({ data: {} }),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  };
  return {
    default: { create: vi.fn(() => instance), ...instance },
    create: vi.fn(() => instance),
  };
});

import AdminDashboard from '../pages/AdminDashboard';
import { isAuthenticated } from '../api/adminApi';

// ---------------------------------------------------------------------------
// Helper: render the dashboard inside a router with a /admin/login route
// ---------------------------------------------------------------------------

function renderDashboard() {
  return render(
    <MemoryRouter initialEntries={['/admin']}>
      <Routes>
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/login" element={<div data-testid="login-page">Login Page</div>} />
      </Routes>
    </MemoryRouter>
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('AdminDashboard — authentication guard', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('redirects to /admin/login when localStorage token is absent', () => {
    // isAuthenticated reads from localStorage; token is absent
    isAuthenticated.mockReturnValue(false);
    renderDashboard();
    expect(screen.getByTestId('login-page')).toBeInTheDocument();
  });

  it('does not render the dashboard UI when unauthenticated', () => {
    isAuthenticated.mockReturnValue(false);
    renderDashboard();
    expect(screen.queryByText(/knowledge base/i)).not.toBeInTheDocument();
  });

  it('shows the dashboard when authenticated', () => {
    isAuthenticated.mockReturnValue(true);
    renderDashboard();
    // The header text "ADMIT Admin" should be visible
    expect(screen.getByText(/ADMIT Admin/i)).toBeInTheDocument();
  });
});
