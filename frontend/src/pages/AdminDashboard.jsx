/**
 * AdminDashboard - Main admin panel with navigation tabs
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { isAuthenticated, logout } from '../api/adminApi';
import KBTable from '../components/admin/KBTable';
import KBEditor from '../components/admin/KBEditor';
import LogsViewer from '../components/admin/LogsViewer';
import AnalyticsDashboard from '../components/admin/AnalyticsDashboard';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('kb');
  const [showEditor, setShowEditor] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/admin/login');
    }
  }, [navigate]);

  const handleLogout = () => {
    if (confirm('Are you sure you want to logout?')) {
      logout();
    }
  };

  const handleEdit = (entry) => {
    setEditingEntry(entry);
    setShowEditor(true);
  };

  const handleCreateNew = () => {
    setEditingEntry(null);
    setShowEditor(true);
  };

  const handleEditorClose = () => {
    setShowEditor(false);
    setEditingEntry(null);
  };

  const handleEditorSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const tabs = [
    { id: 'kb', label: 'Knowledge Base', icon: '📚' },
    { id: 'logs', label: 'Conversation Logs', icon: '💬' },
    { id: 'analytics', label: 'Analytics', icon: '📊' },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-sacli-green to-sacli-green-dark text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <span className="text-sacli-gold">🎓</span>
                ADMIT Admin
              </h1>
              <p className="text-sm text-sacli-gold-light">
                Knowledge Base Management
              </p>
            </div>
            <div className="flex gap-4 items-center">
              <a
                href="/"
                target="_blank"
                className="text-white hover:text-sacli-gold transition-colors"
              >
                View Chat →
              </a>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'text-sacli-green border-b-2 border-sacli-green'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* KB Management Tab */}
        {activeTab === 'kb' && (
          <div>
            <div className="mb-6 flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-800">Knowledge Base Entries</h2>
              <button
                onClick={handleCreateNew}
                className="px-6 py-3 bg-sacli-green text-white rounded-lg hover:bg-sacli-green-dark shadow-lg hover:shadow-xl transition-all"
              >
                + Create New Entry
              </button>
            </div>
            <KBTable
              key={refreshTrigger}
              onEdit={handleEdit}
              onRefresh={handleEditorSuccess}
            />
          </div>
        )}

        {/* Logs Tab */}
        {activeTab === 'logs' && (
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-800">Conversation Logs</h2>
              <p className="text-gray-600">View and analyze user conversations</p>
            </div>
            <LogsViewer />
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-800">System Analytics</h2>
              <p className="text-gray-600">Performance metrics and insights</p>
            </div>
            <AnalyticsDashboard />
          </div>
        )}
      </div>

      {/* KB Editor Modal */}
      {showEditor && (
        <KBEditor
          entry={editingEntry}
          onClose={handleEditorClose}
          onSuccess={handleEditorSuccess}
        />
      )}
    </div>
  );
};

export default AdminDashboard;
