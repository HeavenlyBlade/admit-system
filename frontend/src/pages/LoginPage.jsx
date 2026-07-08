/**
 * LoginPage - Admin authentication page with background video
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../api/adminApi';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate('/admin/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail?.error?.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden">

      {/* Background Video */}
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute inset-0 w-full h-full object-cover z-0"
      >
        <source src="/bg-video.mp4" type="video/mp4" />
      </video>

      {/* Dark overlay for readability */}
      <div className="absolute inset-0 bg-black/55 z-10" />

      {/* Content */}
      <div className="relative z-20 w-full max-w-md px-6 py-10">

        {/* Logo + Title */}
        <div className="flex flex-col items-center mb-8">
          <img
            src="/40THAnniv_Logo.png"
            alt="SACLI Logo"
            className="w-24 h-24 object-contain drop-shadow-lg mb-4"
          />
          <h1 className="text-4xl font-bold text-white drop-shadow-md tracking-wide">
            ADMIT
          </h1>
          <p className="text-yellow-300 text-sm mt-1 tracking-widest uppercase font-medium">
            Admin Portal
          </p>
        </div>

        {/* Glass Card */}
        <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl shadow-2xl p-8">
          <h2 className="text-xl font-semibold text-white text-center mb-6">
            Sign in to your account
          </h2>

          {error && (
            <div className="mb-4 px-4 py-3 bg-red-500/20 border border-red-400/40 rounded-lg text-red-200 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-white/80 mb-1">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="Enter username"
                className="w-full px-4 py-3 rounded-lg bg-white/10 border border-white/25 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/60 focus:border-yellow-400/60 transition"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-white/80 mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Enter password"
                className="w-full px-4 py-3 rounded-lg bg-white/10 border border-white/25 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/60 focus:border-yellow-400/60 transition"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-lg font-semibold text-white bg-gradient-to-r from-yellow-500 to-yellow-400 hover:from-yellow-400 hover:to-yellow-300 shadow-lg hover:shadow-yellow-400/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        </div>

        {/* Back to Chat */}
        <div className="text-center mt-6">
          <a
            href="/"
            className="text-white/60 hover:text-yellow-300 text-sm transition-colors"
          >
            ← Back to Chat
          </a>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
