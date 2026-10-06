/**
 * MessageBubble - Individual message display component
 * Accepts optional `user` prop for authenticated user avatar display.
 */
const MessageBubble = ({ message, user }) => {
  const isUser = message.sender === 'user';
  const isError = message.isError;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} items-end gap-2 animate-fadeIn`}>
      {/* Bot side — placeholder for symmetry (no avatar needed) */}
      {!isUser && <div className="w-7 flex-shrink-0" />}

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

      {/* User avatar — shown on the right of user messages */}
      {isUser && (
        <div className="flex-shrink-0">
          {user?.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={user.name || 'You'}
              className="w-7 h-7 rounded-full object-cover"
            />
          ) : user ? (
            <div className="w-7 h-7 rounded-full bg-yellow-500 flex items-center justify-center text-xs font-bold text-white">
              {user.name?.charAt(0)?.toUpperCase() || 'Y'}
            </div>
          ) : (
            /* Anonymous user — small icon placeholder */
            <div className="w-7 h-7 rounded-full bg-white/20 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 text-white/60" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/>
              </svg>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MessageBubble;
