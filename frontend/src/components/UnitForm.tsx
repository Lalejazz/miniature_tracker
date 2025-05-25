import React, { useState, useEffect } from 'react';
import { 
  UnitCreate, 
  PaintingStatus, 
  GameSystem, 
  UnitType, 
  BaseDimension,
  STATUS_INFO, 
  GAME_SYSTEM_LABELS, 
  UNIT_TYPE_LABELS,
  BASE_DIMENSION_LABELS,
  GAME_SYSTEM_FACTIONS,
  Miniature
} from '../types';

interface UnitFormProps {
  onSubmit: (unit: UnitCreate) => void;
  onCancel: () => void;
  miniature?: Miniature;
  isEditing?: boolean;
}

const UnitForm: React.FC<UnitFormProps> = ({ onSubmit, onCancel, miniature, isEditing = false }) => {
  const [formData, setFormData] = useState<UnitCreate>({
    name: miniature?.name || '',
    game_system: miniature?.game_system || GameSystem.WARHAMMER_40K,
    faction: miniature?.faction || '',
    unit_type: miniature?.unit_type || UnitType.INFANTRY,
    quantity: miniature?.quantity || 1,
    base_dimension: miniature?.base_dimension || undefined,
    custom_base_size: miniature?.custom_base_size || '',
    cost: miniature?.cost || undefined,
    status: miniature?.status || PaintingStatus.WANT_TO_BUY,
    notes: miniature?.notes || ''
  });

  const [availableFactions, setAvailableFactions] = useState<string[]>([]);

  // Update available factions when game system changes
  useEffect(() => {
    const factions = GAME_SYSTEM_FACTIONS[formData.game_system] || ['Other'];
    setAvailableFactions(factions);
    
    // If current faction is not available in new game system, reset to first option
    if (!factions.includes(formData.faction)) {
      setFormData(prev => ({ ...prev, faction: factions[0] }));
    }
  }, [formData.game_system, formData.faction]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.name.trim() || !formData.faction.trim()) {
      alert('Please fill in all required fields');
      return;
    }

    // Clean up undefined/empty optional fields
    const cleanedData: UnitCreate = {
      ...formData,
      base_dimension: formData.base_dimension || undefined,
      custom_base_size: formData.custom_base_size || undefined,
      cost: formData.cost && formData.cost > 0 ? formData.cost : undefined,
      notes: formData.notes || undefined
    };

    onSubmit(cleanedData);
  };

  const handleChange = (field: keyof UnitCreate, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="miniature-form-overlay">
      <form className="miniature-form unit-form" onSubmit={handleSubmit}>
        <h3>{isEditing ? 'Edit Unit' : 'Add New Unit'}</h3>
        
        {/* Basic Information */}
        <div className="form-section">
          <h4>Basic Information</h4>
          
          <div className="form-group">
            <label htmlFor="name">Unit Name *</label>
            <input
              type="text"
              id="name"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="e.g., Space Marine Tactical Squad, Ork Boyz"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="game_system">Game System *</label>
              <select
                id="game_system"
                value={formData.game_system}
                onChange={(e) => handleChange('game_system', e.target.value as GameSystem)}
                required
              >
                {Object.entries(GAME_SYSTEM_LABELS).map(([system, label]) => (
                  <option key={system} value={system}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="faction">Faction *</label>
              <select
                id="faction"
                value={formData.faction}
                onChange={(e) => handleChange('faction', e.target.value)}
                required
              >
                <option value="">Select faction...</option>
                {availableFactions.map((faction) => (
                  <option key={faction} value={faction}>
                    {faction}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="unit_type">Unit Type *</label>
              <select
                id="unit_type"
                value={formData.unit_type}
                onChange={(e) => handleChange('unit_type', e.target.value as UnitType)}
                required
              >
                {Object.entries(UNIT_TYPE_LABELS).map(([type, label]) => (
                  <option key={type} value={type}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="quantity">Unit Size</label>
              <input
                type="number"
                id="quantity"
                value={formData.quantity}
                onChange={(e) => handleChange('quantity', parseInt(e.target.value) || 1)}
                min="1"
                max="100"
              />
              <small>Number of models in this unit</small>
            </div>
          </div>
        </div>

        {/* Physical Information */}
        <div className="form-section">
          <h4>Physical Details</h4>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="base_dimension">Base Size</label>
              <select
                id="base_dimension"
                value={formData.base_dimension || ''}
                onChange={(e) => handleChange('base_dimension', e.target.value as BaseDimension || undefined)}
              >
                <option value="">Select base size...</option>
                {Object.entries(BASE_DIMENSION_LABELS).map(([size, label]) => (
                  <option key={size} value={size}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            {formData.base_dimension === BaseDimension.CUSTOM && (
              <div className="form-group">
                <label htmlFor="custom_base_size">Custom Base Size</label>
                <input
                  type="text"
                  id="custom_base_size"
                  value={formData.custom_base_size || ''}
                  onChange={(e) => handleChange('custom_base_size', e.target.value)}
                  placeholder="e.g., 28.5mm round, 45x60mm oval"
                />
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="cost">Cost</label>
            <input
              type="number"
              id="cost"
              value={formData.cost || ''}
              onChange={(e) => handleChange('cost', parseFloat(e.target.value) || undefined)}
              min="0"
              step="0.01"
              placeholder="0.00"
            />
            <small>Purchase cost in your local currency</small>
          </div>
        </div>

        {/* Status and Notes */}
        <div className="form-section">
          <h4>Status & Notes</h4>
          
          <div className="form-group">
            <label htmlFor="status">Current Status</label>
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
              value={formData.notes || ''}
              onChange={(e) => handleChange('notes', e.target.value)}
              placeholder="Any additional notes about this unit..."
              rows={3}
            />
          </div>
        </div>

        <div className="form-buttons">
          <button type="submit" className="submit-button">
            {isEditing ? 'Update Unit' : 'Add Unit'}
          </button>
          <button type="button" onClick={onCancel} className="cancel-button">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default UnitForm; 