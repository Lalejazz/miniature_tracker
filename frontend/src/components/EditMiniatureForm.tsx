import React, { useState, useEffect } from 'react';
import { Miniature, MiniatureUpdate, PaintingStatus, STATUS_INFO, UnitType, UNIT_TYPE_LABELS, GameSystem, GAME_SYSTEM_LABELS, BaseDimension, BASE_DIMENSION_LABELS, GAME_SYSTEM_FACTIONS } from '../types';
import { miniatureApi } from '../services/api';

interface EditMiniatureFormProps {
  miniature: Miniature;
  onSave: (updatedMiniature: Miniature) => void;
  onCancel: () => void;
}

const EditMiniatureForm: React.FC<EditMiniatureFormProps> = ({ miniature, onSave, onCancel }) => {
  const [formData, setFormData] = useState<MiniatureUpdate>({
    name: miniature.name,
    game_system: miniature.game_system,
    faction: miniature.faction,
    unit_type: miniature.unit_type,
    quantity: miniature.quantity,
    status: miniature.status,
    notes: miniature.notes || '',
    cost: miniature.cost,
    base_dimension: miniature.base_dimension,
    custom_base_size: miniature.custom_base_size
  });
  const [quantityInput, setQuantityInput] = useState<string>(miniature.quantity.toString());
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [availableFactions, setAvailableFactions] = useState<string[]>([]);

  // Update available factions when game system changes
  useEffect(() => {
    const gameSystem = formData.game_system || GameSystem.WARHAMMER_40K;
    const factions = GAME_SYSTEM_FACTIONS[gameSystem] || ['Other'];
    setAvailableFactions(factions);
    
    // If current faction is not available in new game system, reset to first option
    const currentFaction = formData.faction || '';
    if (!factions.includes(currentFaction)) {
      setFormData(prev => ({ ...prev, faction: factions[0] }));
    }
  }, [formData.game_system, formData.faction]);

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

  const handleChange = (field: keyof MiniatureUpdate, value: string | number | GameSystem | UnitType | BaseDimension | string | undefined) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Keep quantityInput in sync when quantity is updated
    if (field === 'quantity' && typeof value === 'number') {
      setQuantityInput(value.toString());
    }
  };

  const handleQuantityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuantityInput(value);
    
    // Only update formData if it's a valid number
    const numValue = parseInt(value);
    if (!isNaN(numValue) && numValue > 0) {
      setFormData(prev => ({ ...prev, quantity: numValue }));
    }
  };

  const handleQuantityBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const numValue = parseInt(value);
    
    if (isNaN(numValue) || numValue < 1) {
      // Reset to 1 if invalid
      setQuantityInput('1');
      setFormData(prev => ({ ...prev, quantity: 1 }));
    } else {
      // Ensure formData is updated with valid value
      setQuantityInput(numValue.toString());
      setFormData(prev => ({ ...prev, quantity: numValue }));
    }
  };

  return (
    <div className="edit-form-overlay">
      <div className="edit-form">
        <div className="edit-form-header">
          <h3>Edit Unit</h3>
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
            <label htmlFor="game_system">Game System *</label>
            <select
              id="game_system"
              value={formData.game_system || GameSystem.WARHAMMER_40K}
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

          <div className="form-row">
            <label htmlFor="faction">Faction *</label>
            <select
              id="faction"
              value={formData.faction || ''}
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

          <div className="form-row">
            <label htmlFor="unit_type">Unit Type *</label>
            <select
              id="unit_type"
              value={formData.unit_type || UnitType.INFANTRY}
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

          <div className="form-row">
            <label htmlFor="quantity">Unit Size</label>
            <input
              type="text"
              id="quantity"
              value={quantityInput}
              onChange={handleQuantityChange}
              onBlur={handleQuantityBlur}
              placeholder="Enter quantity"
            />
          </div>

          <div className="form-row">
            <label htmlFor="cost">Cost (optional)</label>
            <input
              type="number"
              id="cost"
              step="0.01"
              min="0"
              value={formData.cost || ''}
              onChange={(e) => handleChange('cost', parseFloat(e.target.value) || undefined)}
              placeholder="Amount paid for this unit"
            />
          </div>

          <div className="form-row">
            <label htmlFor="base_dimension">Base Size</label>
            <select
              id="base_dimension"
              value={formData.base_dimension || ''}
              onChange={(e) => handleChange('base_dimension', e.target.value as BaseDimension)}
            >
              <option value="">Select base size...</option>
              {Object.entries(BASE_DIMENSION_LABELS).map(([dimension, label]) => (
                <option key={dimension} value={dimension}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          {formData.base_dimension === BaseDimension.CUSTOM && (
            <div className="form-row">
              <label htmlFor="custom_base_size">Custom Base Size</label>
              <input
                type="text"
                id="custom_base_size"
                value={formData.custom_base_size || ''}
                onChange={(e) => handleChange('custom_base_size', e.target.value)}
                placeholder="e.g., 28mm round, 30x40mm oval"
                maxLength={50}
              />
            </div>
          )}

          <div className="form-row">
            <label htmlFor="status">Status</label>
            <select
              id="status"
              value={formData.status || PaintingStatus.WANT_TO_BUY}
              onChange={(e) => handleChange('status', e.target.value as PaintingStatus)}
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