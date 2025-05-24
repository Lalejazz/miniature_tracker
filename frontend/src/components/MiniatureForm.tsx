import React, { useState } from 'react';
import { MiniatureCreate, PaintingStatus, STATUS_INFO } from '../types';

interface MiniatureFormProps {
  onSubmit: (miniature: MiniatureCreate) => void;
  onCancel: () => void;
}

const MiniatureForm: React.FC<MiniatureFormProps> = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState<MiniatureCreate>({
    name: '',
    faction: '',
    model_type: '',
    status: PaintingStatus.WANT_TO_BUY,
    notes: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.name.trim() || !formData.faction.trim() || !formData.model_type.trim()) {
      alert('Please fill in all required fields');
      return;
    }

    onSubmit(formData);
  };

  const handleChange = (field: keyof MiniatureCreate, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="miniature-form-overlay">
      <form className="miniature-form" onSubmit={handleSubmit}>
        <h3>Add New Miniature</h3>
        
        <div className="form-group">
          <label htmlFor="name">Name *</label>
          <input
            type="text"
            id="name"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="e.g., Space Marine Captain"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="faction">Faction *</label>
          <input
            type="text"
            id="faction"
            value={formData.faction}
            onChange={(e) => handleChange('faction', e.target.value)}
            placeholder="e.g., Ultramarines, Orks, Necrons"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="model_type">Model Type *</label>
          <input
            type="text"
            id="model_type"
            value={formData.model_type}
            onChange={(e) => handleChange('model_type', e.target.value)}
            placeholder="e.g., HQ, Troops, Elite"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="status">Status</label>
          <select
            id="status"
            value={formData.status}
            onChange={(e) => handleChange('status', e.target.value as PaintingStatus)}
          >
            {Object.entries(STATUS_INFO).map(([status, info]) => (
              <option key={status} value={status}>
                {info.label} - {info.description}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="notes">Notes</label>
          <textarea
            id="notes"
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
            placeholder="Any additional notes about this miniature..."
            rows={3}
          />
        </div>

        <div className="form-buttons">
          <button type="submit" className="submit-button">
            Add Miniature
          </button>
          <button type="button" onClick={onCancel} className="cancel-button">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default MiniatureForm; 