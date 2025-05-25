import React, { useState } from 'react';
import { Miniature, PaintingStatus, STATUS_INFO, UNIT_TYPE_LABELS, GAME_SYSTEM_LABELS, BASE_DIMENSION_LABELS } from '../types';
import EditMiniatureForm from './EditMiniatureForm';
import StatusHistory from './StatusHistory';

interface MiniatureCardProps {
  miniature: Miniature;
  onUpdate: (id: string, updates: Partial<Miniature>) => void;
  onDelete: (id: string) => void;
  onMiniatureUpdate: (updatedMiniature: Miniature) => void;
}

const MiniatureCard: React.FC<MiniatureCardProps> = ({
  miniature,
  onUpdate,
  onDelete,
  onMiniatureUpdate
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [isEditingNotes, setIsEditingNotes] = useState(false);
  const [editNotes, setEditNotes] = useState(miniature.notes || '');

  const statusInfo = STATUS_INFO[miniature.status];

  const handleStatusChange = (newStatus: PaintingStatus) => {
    onUpdate(miniature.id, { status: newStatus });
  };

  const handleNotesUpdate = () => {
    onUpdate(miniature.id, { notes: editNotes });
    setIsEditingNotes(false);
  };

  const handleEditSave = (updatedMiniature: Miniature) => {
    onMiniatureUpdate(updatedMiniature);
    setIsEditing(false);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <>
      <div className="miniature-card">
        <div className="card-header">
          <h3>{miniature.name}</h3>
          <div className="card-actions">
            <button 
              className="edit-button"
              onClick={() => setIsEditing(true)}
              title="Edit unit"
            >
              ✏️
            </button>
            <button 
              className="delete-button"
              onClick={() => onDelete(miniature.id)}
              title="Delete unit"
            >
              🗑️
            </button>
          </div>
        </div>

        <div className="card-content">
          <div className="info-row">
            <span className="label">Game System:</span>
            <span>{GAME_SYSTEM_LABELS[miniature.game_system]}</span>
          </div>

          <div className="info-row">
            <span className="label">Faction:</span>
            <span>{miniature.faction}</span>
          </div>
          
          <div className="info-row">
            <span className="label">Type:</span>
            <span>{UNIT_TYPE_LABELS[miniature.unit_type]}</span>
          </div>

          <div className="info-row">
            <span className="label">Unit Size:</span>
            <span>{miniature.quantity} model{miniature.quantity !== 1 ? 's' : ''}</span>
          </div>

          {miniature.cost && (
            <div className="info-row">
              <span className="label">Cost:</span>
              <span>${miniature.cost}</span>
            </div>
          )}

          {miniature.base_dimension && (
            <div className="info-row">
              <span className="label">Base Size:</span>
              <span>
                {miniature.base_dimension === 'custom' && miniature.custom_base_size 
                  ? miniature.custom_base_size 
                  : BASE_DIMENSION_LABELS[miniature.base_dimension]
                }
              </span>
            </div>
          )}

          <div className="status-section">
            <span className="label">Status:</span>
            <select 
              value={miniature.status}
              onChange={(e) => handleStatusChange(e.target.value as PaintingStatus)}
              className="status-select"
              style={{ borderColor: statusInfo.color }}
            >
              {Object.entries(STATUS_INFO).map(([status, info]) => (
                <option key={status} value={status}>
                  {info.label}
                </option>
              ))}
            </select>
            <div 
              className="status-badge"
              style={{ backgroundColor: statusInfo.color }}
              title={statusInfo.description}
            >
              {statusInfo.label}
            </div>
          </div>

          <div className="notes-section">
            <span className="label">Notes:</span>
            {isEditingNotes ? (
              <div className="notes-edit">
                <textarea
                  value={editNotes}
                  onChange={(e) => setEditNotes(e.target.value)}
                  placeholder="Add notes about this unit..."
                  rows={3}
                />
                <div className="notes-buttons">
                  <button onClick={handleNotesUpdate}>Save</button>
                  <button onClick={() => setIsEditingNotes(false)}>Cancel</button>
                </div>
              </div>
            ) : (
              <div className="notes-display">
                <p>{miniature.notes || 'No notes yet'}</p>
                <button onClick={() => setIsEditingNotes(true)}>✏️ Edit</button>
              </div>
            )}
          </div>

          <StatusHistory 
            miniature={miniature}
            onUpdate={onMiniatureUpdate}
          />
        </div>

        <div className="card-footer">
          <small>
            Created: {formatDate(miniature.created_at)} | 
            Updated: {formatDate(miniature.updated_at)}
          </small>
        </div>
      </div>

      {isEditing && (
        <EditMiniatureForm
          miniature={miniature}
          onSave={handleEditSave}
          onCancel={() => setIsEditing(false)}
        />
      )}
    </>
  );
};

export default MiniatureCard; 