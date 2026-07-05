/**
 * TypingIndicator - Shows animated typing indicator while bot is processing
 */
const TypingIndicator = () => {
  return (
    <div className="flex justify-start animate-fadeIn">
      <div className="bg-white text-gray-800 border-2 border-sacli-gold/20 rounded-2xl rounded-bl-none px-5 py-3 shadow-md">
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 bg-sacli-green rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-sacli-green rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-sacli-green rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
