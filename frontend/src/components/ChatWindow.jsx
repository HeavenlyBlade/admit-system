/**
 * ChatWindow - Main chat interface with video background
 */
import { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import QuickReplyButtons from './QuickReplyButtons';
import HistorySidebar from './HistorySidebar';
import { sendMessage } from '../api/chatApi';
import { getSession } from '../api/sessionsApi';
import { useAuth } from '../context/AuthContext';

const ChatWindow = ({ backButton }) => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEndRef = useRef(null);

  const { user, token, refreshUser } = useAuth();

  // On mount: restore session or create new; also handle ?token= from OAuth redirect
  useEffect(() => {
    // Handle OAuth token in URL
    const params = new URLSearchParams(window.location.search);
    const tokenParam = params.get('token');
    if (tokenParam) {
      localStorage.setItem('admit_user_token', tokenParam);
      window.history.replaceState({}, '', window.location.pathname);
      refreshUser();
    }

    // Restore or create session
    const storedSessionId = localStorage.getItem('admit_session_id');
    if (storedSessionId) {
      setSessionId(storedSessionId);
    } else {
      const newSessionId = uuidv4();
      setSessionId(newSessionId);
      localStorage.setItem('admit_session_id', newSessionId);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendMessage = async (messageText = inputText) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      content: messageText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setError(null);
    setIsLoading(true);

    try {
      const response = await sendMessage(messageText, sessionId, token);
      if (response.session_id && response.session_id !== sessionId) {
        setSessionId(response.session_id);
        localStorage.setItem('admit_session_id', response.session_id);
      }
      const botMessage = {
        id: Date.now() + 1,
        sender: 'bot',
        content: response.response,
        timestamp: new Date(),
        wasFallback: response.was_fallback,
        matchedKbIds: response.matched_kb_ids,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setError(err.message);
      setMessages((prev) => [...prev, {
        id: Date.now() + 1,
        sender: 'bot',
        content: '⚠️ ' + err.message,
        timestamp: new Date(),
        isError: true,
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  async function handleSessionSelect(session) {
    try {
      const data = await getSession(session.session_id, token);
      const mapped = data.messages.map((m) => ({
        id: m.id,
        sender: m.sender,
        content: m.content,
        timestamp: m.timestamp,
        wasFallback: m.was_fallback,
      }));
      setMessages(mapped);
      setSessionId(session.session_id);
      localStorage.setItem('admit_session_id', session.session_id);
      setSidebarOpen(false);
    } catch (err) {
      console.error('Failed to load session:', err);
    }
  }

  return (
    <>
      <div className="relative flex flex-col h-screen overflow-hidden">

        {/* Background Video */}
        <video
          autoPlay loop muted playsInline
          className="absolute inset-0 w-full h-full object-cover z-0"
        >
          <source src="/bg-video.mp4" type="video/mp4" />
        </video>

        {/* Dark overlay */}
        <div className="absolute inset-0 bg-black/60 z-10" />

        {/* Header */}
        <div className="relative z-20 backdrop-blur-md bg-black/30 border-b border-white/10 px-4 py-4">
          <div className="max-w-4xl mx-auto flex items-center gap-3">
            {backButton && backButton}
            <img
              src="/40THAnniv_Logo.png"
              alt="SACLI Logo"
              className="w-12 h-12 object-contain drop-shadow flex-shrink-0"
            />
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold text-white tracking-wide">ADMIT</h1>
              <p className="text-yellow-300 text-xs tracking-widest uppercase">
                SACLI Admissions Assistant
              </p>
            </div>

            {/* History button — right side of header */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="w-8 h-8 rounded-full border border-white/10 hover:bg-white/10 flex items-center justify-center transition-colors flex-shrink-0"
              aria-label="Conversation history"
            >
              {user?.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={user.name}
                  className="w-7 h-7 rounded-full object-cover"
                />
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 text-white/60" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div
          className="relative z-20 flex-1 overflow-y-auto px-4 py-6"
          aria-live="polite"
          aria-label="Chat messages"
        >
          <div className="max-w-4xl mx-auto space-y-4">

            {/* Welcome */}
            {messages.length === 0 && (
              <div className="text-center py-8">
                <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl p-8 shadow-xl">
                  <img
                    src="/40THAnniv_Logo.png"
                    alt="SACLI Logo"
                    className="w-20 h-20 object-contain mx-auto mb-4 drop-shadow"
                  />
                  <h2 className="text-2xl font-bold text-white mb-2">
                    Welcome to ADMIT! 👋
                  </h2>
                  <p className="text-white/70 mb-2">
                    I'm here to help with your SACLI admissions and enrollment questions.
                  </p>
                  <p className="text-white/50 text-sm">
                    Choose a topic below or type your question:
                  </p>
                </div>
              </div>
            )}

            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} user={message.sender === 'user' ? user : null} />
            ))}

            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Quick Replies */}
        {messages.length === 0 && (
          <div className="relative z-20 px-4 pb-2">
            <div className="max-w-4xl mx-auto">
              <QuickReplyButtons onSelect={handleSendMessage} />
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="relative z-20 backdrop-blur-md bg-black/30 border-t border-white/10 px-4 py-4">
          <div className="max-w-4xl mx-auto">
            {error && (
              <div className="mb-2 text-sm text-red-300 bg-red-500/20 border border-red-400/30 px-3 py-2 rounded-lg">
                {error}
              </div>
            )}
            <div className="flex gap-3">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your question here..."
                disabled={isLoading}
                maxLength={500}
                className="flex-1 px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/60 disabled:opacity-50 transition"
              />
              <button
                onClick={() => handleSendMessage()}
                disabled={isLoading || !inputText.trim()}
                className="px-6 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-yellow-500 to-yellow-400 hover:from-yellow-400 hover:to-yellow-300 shadow-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {isLoading ? '...' : 'Send'}
              </button>
            </div>
            <div className="mt-1 text-xs text-white/30 text-right">
              {inputText.length}/500
            </div>
          </div>
        </div>
      </div>

      {/* History Sidebar — rendered outside the overflow container */}
      <HistorySidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onSessionSelect={handleSessionSelect}
        currentSessionId={sessionId}
      />
    </>
  );
};

export default ChatWindow;
