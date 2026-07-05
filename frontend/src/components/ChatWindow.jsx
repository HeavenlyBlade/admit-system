/**
 * ChatWindow - Main chat interface component
 * Manages chat state and orchestrates message flow
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

  // Initialize or retrieve session ID
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

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (messageText = inputText) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      content: messageText,
      timestamp: new Date(),
    };

    // Add user message immediately (optimistic UI)
    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setError(null);
    setIsLoading(true);

    try {
      // Call backend API
      const response = await sendMessage(messageText, sessionId);

      // Update session ID if returned
      if (response.session_id && response.session_id !== sessionId) {
        setSessionId(response.session_id);
        localStorage.setItem('admit_session_id', response.session_id);
      }

      // Add bot response
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
      // Add error message as bot response
      const errorMessage = {
        id: Date.now() + 1,
        sender: 'bot',
        content: '⚠️ ' + err.message,
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
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

  const handleQuickReply = (query) => {
    handleSendMessage(query);
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-sacli-green to-sacli-green-dark text-white px-6 py-4 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <span className="text-sacli-gold">🎓</span>
            ADMIT
          </h1>
          <p className="text-sm text-sacli-gold-light">
            SACLI Admissions Assistant
          </p>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {/* Welcome message */}
          {messages.length === 0 && (
            <div className="text-center py-8">
              <div className="bg-white rounded-lg shadow-md p-6 border-2 border-sacli-gold/20">
                <h2 className="text-2xl font-bold text-sacli-green mb-2">
                  Welcome to ADMIT! 👋
                </h2>
                <p className="text-gray-600 mb-4">
                  I'm here to help with your SACLI admissions and enrollment questions.
                </p>
                <p className="text-sm text-gray-500">
                  Choose a topic below or type your question:
                </p>
              </div>
            </div>
          )}

          {/* Message list */}
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}

          {/* Typing indicator */}
          {isLoading && <TypingIndicator />}

          {/* Scroll anchor */}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Quick Replies */}
      {messages.length === 0 && (
        <div className="px-4 pb-2">
          <div className="max-w-4xl mx-auto">
            <QuickReplyButtons onSelect={handleQuickReply} />
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-4 py-4 shadow-lg">
        <div className="max-w-4xl mx-auto">
          {error && (
            <div className="mb-2 text-sm text-red-600 bg-red-50 px-3 py-2 rounded">
              {error}
            </div>
          )}
          <div className="flex gap-2">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your question here..."
              disabled={isLoading}
              maxLength={500}
              className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-sacli-green focus:ring-2 focus:ring-sacli-green/20 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={isLoading || !inputText.trim()}
              className="px-6 py-3 bg-gradient-to-r from-sacli-green to-sacli-green-dark text-white rounded-lg font-medium hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {isLoading ? '...' : 'Send'}
            </button>
          </div>
          <div className="mt-2 text-xs text-gray-500 text-right">
            {inputText.length}/500
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;
