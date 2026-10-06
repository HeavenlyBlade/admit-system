/**
 * ChatPage - Main public-facing chat page
 */
import TransitionLink from '../components/TransitionLink';
import ChatWindow from '../components/ChatWindow';

const ChatPage = () => {
  return (
    <div className="relative">
      {/* Back to Home — icon only to avoid overlapping mobile header */}
      <div className="absolute top-3 left-3 z-30">
        <TransitionLink
          to="/"
          className="flex items-center justify-center w-8 h-8 text-white/70 hover:text-white backdrop-blur-sm bg-black/20 rounded-full border border-white/10 transition-all hover:bg-black/40"
          aria-label="Back to Home"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </TransitionLink>
      </div>
      <ChatWindow />
    </div>
  );
};

export default ChatPage;
