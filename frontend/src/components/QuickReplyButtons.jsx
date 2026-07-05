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

  if (loading) {
    return <div className="text-center text-gray-500">Loading options...</div>;
  }

  return (
    <div className="space-y-2">
      <p className="text-sm text-gray-600 font-medium text-center mb-3">
        ✨ Quick Topics
      </p>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
        {quickReplies.map((reply) => (
          <button
            key={reply.id}
            onClick={() => onSelect(reply.query)}
            className="px-4 py-3 bg-white border-2 border-sacli-green/30 text-sacli-green-dark rounded-lg font-medium text-sm hover:bg-sacli-green hover:text-white hover:border-sacli-green hover:shadow-lg transition-all transform hover:scale-105 active:scale-95"
          >
            {reply.name}
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickReplyButtons;
