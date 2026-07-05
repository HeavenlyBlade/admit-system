/**
 * KBTable - Knowledge base entries table with filters
 */
import { useState, useEffect } from 'react';
import { listKB, deleteKB } from '../../api/adminApi';

const KBTable = ({ onEdit, onRefresh }) => {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState({
    department: '',
    is_active: '',
    search: '',
  });

  useEffect(() => {
    loadEntries();
  }, [page, filters]);

  const loadEntries = async () => {
    setLoading(true);
    try {
      const params = {
        page,
        per_page: 25,
        ...filters,
      };
      const data = await listKB(params);
      setEntries(data.entries);
      setTotal(data.total);
    } catch (error) {
      console.error('Error loading KB entries:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to deactivate this entry?')) return;
    
    try {
      await deleteKB(id);
      loadEntries();
      if (onRefresh) onRefresh();
    } catch (error) {
      alert('Failed to delete entry');
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(1);
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            type="text"
            placeholder="Search title/content..."
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sacli-green focus:outline-none"
          />
          
          <select
            value={filters.department}
            onChange={(e) => handleFilterChange('department', e.target.value)}
            className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sacli-green focus:outline-none"
          >
            <option value="">All Departments</option>
            <option value="IBED">IBED</option>
            <option value="SHS">SHS</option>
            <option value="HED">HED</option>
            <option value="TESDA">TESDA</option>
            <option value="GENERAL">GENERAL</option>
          </select>

          <select
            value={filters.is_active}
            onChange={(e) => handleFilterChange('is_active', e.target.value)}
            className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sacli-green focus:outline-none"
          >
            <option value="">All Status</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>

          <button
            onClick={loadEntries}
            className="px-4 py-2 bg-sacli-green text-white rounded-lg hover:bg-sacli-green-dark"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-sacli-green text-white">
              <tr>
                <th className="px-4 py-3 text-left">ID</th>
                <th className="px-4 py-3 text-left">Title</th>
                <th className="px-4 py-3 text-left">Category</th>
                <th className="px-4 py-3 text-left">Department</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-left">Updated</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {loading ? (
                <tr>
                  <td colSpan="7" className="px-4 py-8 text-center text-gray-500">
                    Loading...
                  </td>
                </tr>
              ) : entries.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-4 py-8 text-center text-gray-500">
                    No entries found
                  </td>
                </tr>
              ) : (
                entries.map((entry) => (
                  <tr key={entry.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">{entry.id}</td>
                    <td className="px-4 py-3 font-medium">{entry.title}</td>
                    <td className="px-4 py-3">{entry.category?.name}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 bg-sacli-gold/20 text-sacli-green-dark rounded text-xs">
                        {entry.category?.department}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded text-xs ${
                        entry.is_active 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-red-100 text-red-700'
                      }`}>
                        {entry.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {new Date(entry.updated_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-right space-x-2">
                      <button
                        onClick={() => onEdit(entry)}
                        className="text-blue-600 hover:underline"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(entry.id)}
                        className="text-red-600 hover:underline"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {total > 25 && (
          <div className="px-4 py-3 border-t flex justify-between items-center">
            <div className="text-sm text-gray-600">
              Showing {entries.length} of {total} entries
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
                disabled={entries.length < 25}
                className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default KBTable;
