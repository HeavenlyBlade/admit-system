/**
 * ChatPage - Main public-facing chat page
 * Back button is passed as a prop so ChatWindow renders it inside the header,
 * avoiding any overlap with the logo on mobile.
 */
import TransitionLink from '../components/TransitionLink';
import ChatWindow from '../components/ChatWindow';

const BackButton = () => (
  <TransitionLink
    to="/"
    className="flex items-center justify-center w-8 h-8 text-white/60 hover:text-white rounded-full border border-white/10 hover:bg-white/10 transition-all flex-shrink-0"
    aria-label="Back to Home"
  >
    <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
    </svg>
  </TransitionLink>
);

const ChatPage = () => {
  return (
    <div className="relative">
      <ChatWindow backButton={<BackButton />} />
    </div>
  );
};

export default ChatPage;
