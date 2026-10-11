/**
 * ChatWindow tests — privacy notice banner behaviour.
 * axios is mocked so no real HTTP requests are made.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

// Mock axios globally (used by chatApi / sessionsApi)
vi.mock('axios', () => {
  const instance = {
    get: vi.fn().mockResolvedValue({ data: [] }),
    post: vi.fn().mockResolvedValue({ data: { response: 'ok', session_id: '00000000-0000-0000-0000-000000000000', was_fallback: false, matched_kb_ids: [] } }),
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

// Mock the AuthContext so ChatWindow doesn't need a full provider tree
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({ user: null, token: null, refreshUser: vi.fn() }),
}));

// Mock QuickReplyButtons (makes a real API call we don't want)
vi.mock('../components/QuickReplyButtons', () => ({
  default: () => <div data-testid="quick-replies" />,
}));

// Mock HistorySidebar
vi.mock('../components/HistorySidebar', () => ({
  default: () => <div data-testid="history-sidebar" />,
}));

// Mock video element (jsdom doesn't support HTMLVideoElement.play)
Object.defineProperty(window.HTMLMediaElement.prototype, 'play', {
  configurable: true,
  value: vi.fn(),
});

import ChatWindow from '../components/ChatWindow';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderChatWindow() {
  // Clear sessionStorage so privacy notice always shows
  sessionStorage.clear();
  return render(
    <MemoryRouter>
      <ChatWindow />
    </MemoryRouter>
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('ChatWindow — privacy notice banner', () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it('renders the privacy notice banner on first visit', () => {
    renderChatWindow();
    expect(
      screen.getByText(/your conversation may be stored/i)
    ).toBeInTheDocument();
  });

  it('hides the banner after clicking the OK button', () => {
    renderChatWindow();
    const dismissBtn = screen.getByRole('button', { name: /dismiss privacy notice/i });
    fireEvent.click(dismissBtn);
    expect(
      screen.queryByText(/your conversation may be stored/i)
    ).not.toBeInTheDocument();
  });

  it('does not show the banner when already acknowledged', () => {
    sessionStorage.setItem('admit_privacy_acknowledged', '1');
    renderChatWindow();
    expect(
      screen.queryByText(/your conversation may be stored/i)
    ).not.toBeInTheDocument();
  });
});
