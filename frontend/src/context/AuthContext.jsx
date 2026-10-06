/**
 * AuthContext — provides Google OAuth user state across the app.
 */
import { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext(null);

const API_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const stored = localStorage.getItem('admit_user_token');
    if (!stored) {
      setUser(null);
      setToken(null);
      setLoading(false);
      return;
    }

    // Check expiry via JWT payload
    try {
      const payload = JSON.parse(atob(stored.split('.')[1]));
      if (payload.exp && Date.now() / 1000 > payload.exp) {
        localStorage.removeItem('admit_user_token');
        setUser(null);
        setToken(null);
        setLoading(false);
        return;
      }
    } catch {
      localStorage.removeItem('admit_user_token');
      setUser(null);
      setToken(null);
      setLoading(false);
      return;
    }

    // Verify with backend /me
    try {
      const res = await fetch(`${API_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${stored}` },
      });
      if (!res.ok) throw new Error('Token rejected');
      const data = await res.json();
      setToken(stored);
      setUser(data);
    } catch {
      localStorage.removeItem('admit_user_token');
      setUser(null);
      setToken(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Run on mount
  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  function login() {
    window.location.href = `${API_URL}/api/auth/google`;
  }

  function logout() {
    localStorage.removeItem('admit_user_token');
    setUser(null);
    setToken(null);
  }

  const isAuthenticated = Boolean(user);

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, login, logout, refreshUser, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
