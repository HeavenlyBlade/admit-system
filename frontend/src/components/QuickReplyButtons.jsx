/**
 * QuickReplyButtons - Quick action buttons for common inquiry categories
 */
import { useEffect, useState } from 'react';
import { getQuickReplies } from '../api/chatApi';

const QuickReplyButtons = ({ onSelect }) => {
  const [quickReplies, setQuickReplies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQuickReplies();
  }, []);

  const loadQuickReplies = async () => {
    try {
      const replies = await getQuickReplies();
      setQuickReplies(replies);
    } catch (error) {
      console.error('Failed to load quick replies:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return null;

  return (
    <div className="space-y-2">
      <p className="text-sm text-white/50 font-medium text-center mb-3">
        ✨ Quick Topics
      </p>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
        {quickReplies.map((reply) => (
          <button
            key={reply.id}
            onClick={() => onSelect(reply.query)}
            className="px-4 py-3 backdrop-blur-sm bg-white/10 border border-white/20 text-white/80 rounded-xl text-sm font-medium hover:bg-yellow-500/30 hover:border-yellow-400/50 hover:text-white transition-all"
          >
            {reply.name}
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickReplyButtons;
