/**
 * MessageBubble - Individual message display component
 */
const MessageBubble = ({ message }) => {
  const isUser = message.sender === 'user';
  const isError = message.isError;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 shadow-lg ${
          isUser
            ? 'bg-yellow-500/80 backdrop-blur text-white rounded-br-none border border-yellow-400/30'
            : isError
            ? 'bg-red-500/20 backdrop-blur text-red-200 border border-red-400/30 rounded-bl-none'
            : 'bg-white/15 backdrop-blur text-white border border-white/20 rounded-bl-none'
        }`}
      >
        <div className="whitespace-pre-wrap break-words text-sm leading-relaxed">
          {message.content}
        </div>
        <div className={`text-xs mt-2 ${isUser ? 'text-white/60' : 'text-white/40'}`}>
          {new Date(message.timestamp).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
        {message.wasFallback && (
          <div className="text-xs text-white/40 mt-1 italic">
            ℹ️ Redirected to office
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
