/**
 * HistorySidebar — right-side conversation history drawer.
 * Displays sessions grouped by date; requires auth to view history.
 */
import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { getSessions } from '../api/sessionsApi';

/**
 * Classify a date into a relative bucket.
 */
function dateBucket(dateStr) {
  const now = new Date();
  const d = new Date(dateStr);
  const diffDays = Math.floor((now - d) / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays <= 7) return 'Last 7 Days';
  return 'Older';
}

function formatRelative(dateStr) {
  const now = new Date();
  const d = new Date(dateStr);
  const diffMs = now - d;
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHrs = Math.floor(diffMins / 60);
  if (diffHrs < 24) return `${diffHrs}h ago`;
  const diffDays = Math.floor(diffHrs / 24);
  return `${diffDays}d ago`;
}

function groupSessions(sessions) {
  const buckets = {};
  const order = ['Today', 'Yesterday', 'Last 7 Days', 'Older'];
  for (const s of sessions) {
    const b = dateBucket(s.started_at);
    if (!buckets[b]) buckets[b] = [];
    buckets[b].push(s);
  }
  return order.filter((b) => buckets[b]).map((b) => ({ label: b, items: buckets[b] }));
}

const HistorySidebar = ({ isOpen, onClose, onSessionSelect, currentSessionId }) => {
  const { user, token, isAuthenticated, login, logout } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showSignOutConfirm, setShowSignOutConfirm] = useState(false);

  useEffect(() => {
    if (isOpen && isAuthenticated && token) {
      setLoading(true);
      setError(null);
      getSessions(token)
        .then((data) => { setSessions(Array.isArray(data) ? data : []); })
        .catch(() => setError('Failed to load history. Please try again.'))
        .finally(() => setLoading(false));
    }
  }, [isOpen, isAuthenticated, token]);

  if (!isOpen) return null;

  const grouped = groupSessions(sessions);

  return (
    <>
      {/* Backdrop on mobile */}
      <div
        className="fixed inset-0 bg-black/50 z-40 md:hidden"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Sidebar panel */}
      <div
        className="sidebar-enter fixed top-0 right-0 h-full z-50 flex flex-col
                   w-full md:w-[280px]
                   bg-gray-950/95 backdrop-blur-xl
                   border-l border-white/10 text-white"
        role="dialog"
        aria-modal="true"
        aria-label="Conversation history"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-4 border-b border-white/10 flex-shrink-0">
          <span className="text-sm font-semibold text-white/80 tracking-wide uppercase">
            History
          </span>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-full hover:bg-white/10 text-white/60 hover:text-white transition-colors"
            aria-label="Close history"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto">
          {!isAuthenticated ? (
            /* Unauthenticated state */
            <div className="flex flex-col items-center justify-center h-full px-6 gap-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="w-12 h-12 text-white/20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 11c0-1.657 1.343-3 3-3s3 1.343 3 3-1.343 3-3 3m-6 0c0-1.657-1.343-3-3-3S3 9.343 3 11s1.343 3 3 3m6-3H6m6 0h6" />
              </svg>
              <p className="text-white/50 text-sm text-center">
                Sign in to save and view your conversation history.
              </p>
              <button
                onClick={login}
                className="flex items-center gap-2 px-4 py-2 bg-white text-gray-800 rounded-full text-sm font-medium hover:bg-gray-100 transition-colors shadow"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
                Sign in with Google
              </button>
            </div>
          ) : (
            <>
              {/* User info strip + sign out */}
              <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10">
                {user?.avatar_url ? (
                  <img
                    src={user.avatar_url}
                    alt={user.name}
                    className="w-8 h-8 rounded-full object-cover flex-shrink-0"
                  />
                ) : (
                  <div className="w-8 h-8 rounded-full bg-yellow-500 flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
                    {user?.name?.charAt(0)?.toUpperCase() || '?'}
                  </div>
                )}
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-white truncate">{user?.name}</p>
                  <p className="text-xs text-white/40 truncate">{user?.email}</p>
                </div>
                <button
                  onClick={() => setShowSignOutConfirm(true)}
                  className="flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-full hover:bg-white/10 text-white/40 hover:text-red-400 transition-colors"
                  aria-label="Sign out"
                  title="Sign out"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h6a2 2 0 012 2v1" />
                  </svg>
                </button>
              </div>

              {/* Session list */}
              <div className="px-2 py-2">
                {loading && (
                  <div className="space-y-2 px-2 py-2">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="h-10 rounded-lg bg-white/10 animate-pulse" />
                    ))}
                  </div>
                )}

                {!loading && error && (
                  <p className="text-xs text-red-400 text-center py-4">{error}</p>
                )}

                {!loading && !error && sessions.length === 0 && (
                  <p className="text-xs text-white/40 text-center py-8">
                    No conversations yet. Start chatting!
                  </p>
                )}

                {!loading && !error && grouped.map(({ label, items }) => (
                  <div key={label}>
                    <p className="px-2 py-1 text-xs text-white/30 font-semibold tracking-wider uppercase">
                      {label}
                    </p>
                    {items.map((session) => {
                      const isActive = session.session_id === currentSessionId;
                      const title = session.title.length > 50
                        ? session.title.slice(0, 50) + '...'
                        : session.title;
                      return (
                        <button
                          key={session.session_id}
                          onClick={() => onSessionSelect(session)}
                          className={`w-full text-left px-3 py-2 rounded-lg mb-0.5 transition-colors group
                            ${isActive
                              ? 'bg-white/15 border-l-2 border-yellow-400'
                              : 'hover:bg-white/10 border-l-2 border-transparent'
                            }`}
                        >
                          <p className="text-sm text-white/80 truncate">{title}</p>
                          <p className="text-xs text-white/30 mt-0.5">
                            {formatRelative(session.started_at)} · {session.message_count} msgs
                          </p>
                        </button>
                      );
                    })}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      {/* Sign out confirmation modal */}
      {showSignOutConfirm && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-gray-900 border border-white/15 rounded-2xl p-6 mx-4 shadow-2xl text-center">
            <p className="text-white font-semibold mb-1">Sign out?</p>
            <p className="text-white/50 text-sm mb-5">Your chat history will be saved and available next time you sign in.</p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowSignOutConfirm(false)}
                className="flex-1 py-2 rounded-xl border border-white/20 text-white/70 hover:bg-white/10 text-sm transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => { logout(); setShowSignOutConfirm(false); onClose(); }}
                className="flex-1 py-2 rounded-xl bg-red-500/80 hover:bg-red-500 text-white text-sm font-semibold transition-colors"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      )}
      </div>
    </>
  );
};

export default HistorySidebar;
