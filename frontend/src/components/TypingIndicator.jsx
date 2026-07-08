/**
 * TypingIndicator - Animated typing dots for dark/glass theme
 */
const TypingIndicator = () => {
  return (
    <div className="flex justify-start animate-fadeIn">
      <div className="bg-white/15 backdrop-blur border border-white/20 rounded-2xl rounded-bl-none px-5 py-3 shadow-lg">
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 bg-yellow-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-yellow-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-yellow-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
