/**
 * KBEditor - Form for creating/editing KB entries
 */
import { useState, useEffect } from 'react';
import { createKB, updateKB } from '../../api/adminApi';

const KBEditor = ({ entry, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category_id: '',
    is_active: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Categories (hardcoded for now - could be fetched from API)
  const categories = [
    { id: 1, name: 'Admission Requirements', department: 'IBED' },
    { id: 2, name: 'Enrollment Steps', department: 'IBED' },
    { id: 3, name: 'Programs Offered', department: 'IBED' },
    { id: 7, name: 'Admission Requirements', department: 'SHS' },
    { id: 13, name: 'Admission Requirements', department: 'HED' },
    { id: 19, name: 'Admission Requirements', department: 'TESDA' },
    { id: 25, name: 'About SACLI', department: 'GENERAL' },
  ];

  useEffect(() => {
    if (entry) {
      setFormData({
        title: entry.title,
        content: entry.content,
        category_id: entry.category_id,
        is_active: entry.is_active,
      });
    }
  }, [entry]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (entry) {
        await updateKB(entry.id, formData);
      } else {
        await createKB(formData);
      }
      onSuccess();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail?.error?.message || 'Failed to save entry');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-sacli-green text-white px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-bold">
            {entry ? 'Edit KB Entry' : 'Create KB Entry'}
          </h2>
          <button onClick={onClose} className="text-2xl hover:text-sacli-gold">
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              maxLength={255}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sacli-green focus:outline-none"
              placeholder="Enter KB entry title"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Content <span className="text-red-500">*</span>
            </label>
            <textarea
              name="content"
              value={formData.content}
              onChange={handleChange}
              required
              rows={10}
              minLength={10}
              maxLength={5000}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sacli-green focus:outline-none font-mono text-sm"
              placeholder="Enter KB entry content (supports markdown)"
            />
            <div className="text-xs text-gray-500 text-right mt-1">
              {formData.content.length}/5000 characters
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category <span className="text-red-500">*</span>
            </label>
            <select
              name="category_id"
              value={formData.category_id}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sacli-green focus:outline-none"
            >
              <option value="">Select a category</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name} ({cat.department})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
              className="w-4 h-4 text-sacli-green focus:ring-sacli-green"
            />
            <label className="ml-2 text-sm text-gray-700">
              Active (visible in search)
            </label>
          </div>

          <div className="flex gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-sacli-green text-white rounded-lg hover:bg-sacli-green-dark disabled:opacity-50"
            >
              {loading ? 'Saving...' : entry ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default KBEditor;
