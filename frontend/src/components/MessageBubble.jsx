/**
 * MessageBubble - Individual message display component
 * Renders user and bot messages with appropriate styling
 */
const MessageBubble = ({ message }) => {
  const isUser = message.sender === 'user';
  const isError = message.isError;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 shadow-md ${
          isUser
            ? 'bg-gradient-to-r from-sacli-green to-sacli-green-dark text-white rounded-br-none'
            : isError
            ? 'bg-red-50 text-red-700 border-2 border-red-200 rounded-bl-none'
            : 'bg-white text-gray-800 border-2 border-sacli-gold/20 rounded-bl-none'
        }`}
      >
        {/* Message content */}
        <div className="whitespace-pre-wrap break-words text-sm leading-relaxed">
          {message.content}
        </div>

        {/* Timestamp */}
        <div
          className={`text-xs mt-2 ${
            isUser ? 'text-sacli-gold-light' : 'text-gray-500'
          }`}
        >
          {new Date(message.timestamp).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>

        {/* Fallback indicator (for debugging) */}
        {message.wasFallback && (
          <div className="text-xs text-gray-500 mt-1 italic">
            ℹ️ Out of scope - contact office suggested
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
