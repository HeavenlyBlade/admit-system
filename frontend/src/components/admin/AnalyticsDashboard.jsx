/**
 * AnalyticsDashboard - Displays system performance metrics
 */
import { useState, useEffect } from 'react';
import { getAnalytics } from '../../api/adminApi';

const AnalyticsDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const data = await getAnalytics();
      setAnalytics(data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white p-8 rounded-lg shadow text-center text-gray-500">
        Loading analytics...
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="bg-white p-8 rounded-lg shadow text-center text-gray-500">
        Failed to load analytics
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Date Range */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="text-sm text-gray-600">
          Analytics Period: {new Date(analytics.date_range.start).toLocaleDateString()} - {new Date(analytics.date_range.end).toLocaleDateString()}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Fallback Rate */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-sm text-gray-600 mb-2">Fallback Rate</div>
          <div className="text-3xl font-bold text-sacli-green">
            {(analytics.fallback_rate * 100).toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500 mt-2">
            {analytics.fallback_rate < 0.2 ? '✅ Good' : analytics.fallback_rate < 0.4 ? '⚠️ Moderate' : '❌ High'}
          </div>
        </div>

        {/* Total Conversations */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-sm text-gray-600 mb-2">Total Conversations</div>
          <div className="text-3xl font-bold text-sacli-green">
            {analytics.total_conversations.toLocaleString()}
          </div>
          <div className="text-xs text-gray-500 mt-2">
            {analytics.total_messages} messages
          </div>
        </div>

        {/* KB Coverage */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-sm text-gray-600 mb-2">KB Coverage</div>
          <div className="text-3xl font-bold text-sacli-green">
            {(analytics.kb_coverage.percentage * 100).toFixed(0)}%
          </div>
          <div className="text-xs text-gray-500 mt-2">
            {analytics.kb_coverage.covered_categories} / {analytics.kb_coverage.total_categories} categories
          </div>
        </div>
      </div>

      {/* Top Unanswered Queries */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h3 className="font-bold text-lg text-gray-800">Top Unanswered Questions</h3>
          <p className="text-sm text-gray-600">Questions that triggered fallback responses</p>
        </div>
        <div className="p-6">
          {analytics.top_unanswered_queries.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              No unanswered queries in this period
            </div>
          ) : (
            <div className="space-y-3">
              {analytics.top_unanswered_queries.map((query, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <div className="flex-1">
                    <div className="text-sm text-gray-800">{query.query}</div>
                  </div>
                  <div className="ml-4 px-3 py-1 bg-sacli-gold/20 text-sacli-green-dark rounded font-medium text-sm">
                    {query.count}x
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Refresh Button */}
      <div className="flex justify-center">
        <button
          onClick={loadAnalytics}
          className="px-6 py-3 bg-sacli-green text-white rounded-lg hover:bg-sacli-green-dark shadow-lg"
        >
          Refresh Analytics
        </button>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
