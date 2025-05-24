import React, { useState } from 'react';
import { Miniature, MiniatureUpdate, PaintingStatus, STATUS_INFO } from '../types';
import { miniatureApi } from '../services/api';

interface EditMiniatureFormProps {
  miniature: Miniature;
  onSave: (updatedMiniature: Miniature) => void;
  onCancel: () => void;
}

const EditMiniatureForm: React.FC<EditMiniatureFormProps> = ({ miniature, onSave, onCancel }) => {
  const [formData, setFormData] = useState<MiniatureUpdate>({
    name: miniature.name,
    faction: miniature.faction,
    model_type: miniature.model_type,
    status: miniature.status,
    notes: miniature.notes || ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const updatedMiniature = await miniatureApi.update(miniature.id, formData);
      onSave(updatedMiniature);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update miniature');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: keyof MiniatureUpdate, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="edit-form-overlay">
      <div className="edit-form">
        <div className="edit-form-header">
          <h3>Edit Miniature</h3>
          <button type="button" onClick={onCancel} className="close-button">×</button>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <label htmlFor="name">Name *</label>
            <input
              id="name"
              type="text"
              value={formData.name || ''}
              onChange={(e) => handleChange('name', e.target.value)}
              required
              maxLength={200}
            />
          </div>

          <div className="form-row">
            <label htmlFor="faction">Faction *</label>
            <input
              id="faction"
              type="text"
              value={formData.faction || ''}
              onChange={(e) => handleChange('faction', e.target.value)}
              required
              maxLength={100}
            />
          </div>

          <div className="form-row">
            <label htmlFor="model_type">Model Type *</label>
            <input
              id="model_type"
              type="text"
              value={formData.model_type || ''}
              onChange={(e) => handleChange('model_type', e.target.value)}
              required
              maxLength={100}
            />
          </div>

          <div className="form-row">
            <label htmlFor="status">Status</label>
            <select
              id="status"
              value={formData.status || PaintingStatus.WANT_TO_BUY}
              onChange={(e) => handleChange('status', e.target.value)}
            >
              {Object.values(PaintingStatus).map(status => (
                <option key={status} value={status}>
                  {STATUS_INFO[status].label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <label htmlFor="notes">Notes</label>
            <textarea
              id="notes"
              value={formData.notes || ''}
              onChange={(e) => handleChange('notes', e.target.value)}
              rows={4}
              maxLength={1000}
            />
          </div>

          <div className="form-actions">
            <button type="button" onClick={onCancel} disabled={isLoading}>
              Cancel
            </button>
            <button type="submit" disabled={isLoading} className="primary">
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditMiniatureForm; 