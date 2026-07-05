/**
 * LogsViewer - Displays conversation logs with filters
 */
import { useState, useEffect } from 'react';
import { getLogs } from '../../api/adminApi';

const LogsViewer = () => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [expandedIds, setExpandedIds] = useState(new Set());
  const [filters, setFilters] = useState({
    fallback_only: false,
  });

  useEffect(() => {
    loadLogs();
  }, [page, filters]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params = {
        page,
        per_page: 20,
        fallback_only: filters.fallback_only || undefined,
      };
      const data = await getLogs(params);
      setConversations(data.conversations);
      setTotal(data.total_count);
    } catch (error) {
      console.error('Error loading logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleExpanded = (sessionId) => {
    setExpandedIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sessionId)) {
        newSet.delete(sessionId);
      } else {
        newSet.add(sessionId);
      }
      return newSet;
    });
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow flex gap-4 items-center">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={filters.fallback_only}
            onChange={(e) => setFilters({ ...filters, fallback_only: e.target.checked })}
            className="w-4 h-4 text-sacli-green focus:ring-sacli-green"
          />
          <span className="text-sm">Show only fallback conversations</span>
        </label>
        <button
          onClick={loadLogs}
          className="ml-auto px-4 py-2 bg-sacli-green text-white rounded-lg hover:bg-sacli-green-dark"
        >
          Refresh
        </button>
      </div>

      {/* Conversations List */}
      <div className="space-y-3">
        {loading ? (
          <div className="bg-white p-8 rounded-lg shadow text-center text-gray-500">
            Loading conversations...
          </div>
        ) : conversations.length === 0 ? (
          <div className="bg-white p-8 rounded-lg shadow text-center text-gray-500">
            No conversations found
          </div>
        ) : (
          conversations.map((conv) => {
            const isExpanded = expandedIds.has(conv.session_id);
            const hasFallback = conv.messages.some(m => m.was_fallback && m.sender === 'bot');
            
            return (
              <div key={conv.session_id} className="bg-white rounded-lg shadow overflow-hidden">
                {/* Conversation Header */}
                <div
                  onClick={() => toggleExpanded(conv.session_id)}
                  className="px-4 py-3 bg-gray-50 border-b cursor-pointer hover:bg-gray-100 flex justify-between items-center"
                >
                  <div>
                    <div className="font-medium text-gray-800">
                      Session: {conv.session_id.slice(0, 8)}...
                    </div>
                    <div className="text-sm text-gray-600">
                      {new Date(conv.started_at).toLocaleString()} • {conv.messages.length} messages
                      {hasFallback && (
                        <span className="ml-2 px-2 py-0.5 bg-yellow-100 text-yellow-700 rounded text-xs">
                          Contains Fallback
                        </span>
                      )}
                    </div>
                  </div>
                  <span className="text-gray-400">
                    {isExpanded ? '▼' : '▶'}
                  </span>
                </div>

                {/* Messages */}
                {isExpanded && (
                  <div className="p-4 space-y-3">
                    {conv.messages.map((msg) => (
                      <div
                        key={msg.id}
                        className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[80%] rounded-lg px-4 py-2 ${
                            msg.sender === 'user'
                              ? 'bg-sacli-green text-white'
                              : msg.was_fallback
                              ? 'bg-yellow-50 text-gray-800 border border-yellow-200'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          <div className="text-xs font-medium mb-1 opacity-70">
                            {msg.sender === 'user' ? 'User' : 'Bot'}
                            {msg.was_fallback && ' (Fallback)'}
                          </div>
                          <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                          {msg.matched_kb_ids && msg.matched_kb_ids.length > 0 && (
                            <div className="text-xs mt-2 opacity-70">
                              KB IDs: {msg.matched_kb_ids.join(', ')}
                            </div>
                          )}
                          <div className="text-xs mt-1 opacity-70">
                            {new Date(msg.created_at).toLocaleTimeString()}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Pagination */}
      {total > 20 && (
        <div className="bg-white p-4 rounded-lg shadow flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Total: {total} conversations
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            <span className="px-3 py-1">Page {page}</span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={conversations.length < 20}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LogsViewer;
