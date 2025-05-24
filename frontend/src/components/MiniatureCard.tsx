import React, { useState } from 'react';
import { Miniature, PaintingStatus, STATUS_INFO } from '../types';

interface MiniatureCardProps {
  miniature: Miniature;
  onUpdate: (id: string, updates: Partial<Miniature>) => void;
  onDelete: (id: string) => void;
}

const MiniatureCard: React.FC<MiniatureCardProps> = ({
  miniature,
  onUpdate,
  onDelete
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editNotes, setEditNotes] = useState(miniature.notes || '');

  const statusInfo = STATUS_INFO[miniature.status];

  const handleStatusChange = (newStatus: PaintingStatus) => {
    onUpdate(miniature.id, { status: newStatus });
  };

  const handleNotesUpdate = () => {
    onUpdate(miniature.id, { notes: editNotes });
    setIsEditing(false);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="miniature-card">
      <div className="card-header">
        <h3>{miniature.name}</h3>
        <button 
          className="delete-button"
          onClick={() => onDelete(miniature.id)}
          title="Delete miniature"
        >
          🗑️
        </button>
      </div>

      <div className="card-content">
        <div className="info-row">
          <span className="label">Faction:</span>
          <span>{miniature.faction}</span>
        </div>
        
        <div className="info-row">
          <span className="label">Type:</span>
          <span>{miniature.model_type}</span>
        </div>

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
          {isEditing ? (
            <div className="notes-edit">
              <textarea
                value={editNotes}
                onChange={(e) => setEditNotes(e.target.value)}
                placeholder="Add notes about this miniature..."
                rows={3}
              />
              <div className="notes-buttons">
                <button onClick={handleNotesUpdate}>Save</button>
                <button onClick={() => setIsEditing(false)}>Cancel</button>
              </div>
            </div>
          ) : (
            <div className="notes-display">
              <p>{miniature.notes || 'No notes yet'}</p>
              <button onClick={() => setIsEditing(true)}>✏️ Edit</button>
            </div>
          )}
        </div>
      </div>

      <div className="card-footer">
        <small>
          Created: {formatDate(miniature.created_at)} | 
          Updated: {formatDate(miniature.updated_at)}
        </small>
      </div>
    </div>
  );
};

export default MiniatureCard; 