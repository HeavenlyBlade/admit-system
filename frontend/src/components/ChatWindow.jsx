/**
 * ChatWindow - Main chat interface with video background
 */
import { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import QuickReplyButtons from './QuickReplyButtons';
import { sendMessage } from '../api/chatApi';

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const storedSessionId = localStorage.getItem('admit_session_id');
    if (storedSessionId) {
      setSessionId(storedSessionId);
    } else {
      const newSessionId = uuidv4();
      setSessionId(newSessionId);
      localStorage.setItem('admit_session_id', newSessionId);
    }
  }, []);

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
      const response = await sendMessage(messageText, sessionId);
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

  return (
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
      <div className="relative z-20 backdrop-blur-md bg-black/30 border-b border-white/10 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center gap-4">
          <img
            src="/40THAnniv_Logo.png"
            alt="SACLI Logo"
            className="w-12 h-12 object-contain drop-shadow"
          />
          <div>
            <h1 className="text-2xl font-bold text-white tracking-wide">ADMIT</h1>
            <p className="text-yellow-300 text-xs tracking-widest uppercase">
              SACLI Admissions Assistant
            </p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="relative z-20 flex-1 overflow-y-auto px-4 py-6">
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
            <MessageBubble key={message.id} message={message} />
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
  );
};

export default ChatWindow;
