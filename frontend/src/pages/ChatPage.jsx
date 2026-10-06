/**
 * ChatPage - Main public-facing chat page
 */
import { Link } from 'react-router-dom';
import ChatWindow from '../components/ChatWindow';

const ChatPage = () => {
  return (
    <div className="relative">
      {/* Back to Home link */}
      <div className="absolute top-4 left-4 z-30">
        <Link
          to="/"
          className="flex items-center gap-1 text-white/70 hover:text-white text-sm backdrop-blur-sm bg-black/20 px-3 py-1.5 rounded-lg border border-white/10 transition-all hover:bg-black/40"
        >
          ← Home
        </Link>
      </div>
      <ChatWindow />
    </div>
  );
};

export default ChatPage;
