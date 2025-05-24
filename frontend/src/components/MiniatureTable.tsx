import React, { useState } from 'react';
import { Miniature, PaintingStatus, STATUS_INFO } from '../types';

interface MiniatureTableProps {
  miniatures: Miniature[];
  onUpdate: (id: string, updates: Partial<Miniature>) => void;
  onDelete: (id: string) => void;
  sortField: string;
  sortOrder: 'asc' | 'desc';
  onSort: (field: any) => void;
}

const MiniatureTable: React.FC<MiniatureTableProps> = ({
  miniatures,
  onUpdate,
  onDelete,
  sortField,
  sortOrder,
  onSort
}) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editNotes, setEditNotes] = useState('');

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const handleStatusChange = (id: string, newStatus: PaintingStatus) => {
    onUpdate(id, { status: newStatus });
  };

  const startEditNotes = (miniature: Miniature) => {
    setEditingId(miniature.id);
    setEditNotes(miniature.notes || '');
  };

  const saveNotes = (id: string) => {
    onUpdate(id, { notes: editNotes });
    setEditingId(null);
    setEditNotes('');
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditNotes('');
  };

  const getSortIcon = (field: string) => {
    if (sortField !== field) return '↕️';
    return sortOrder === 'asc' ? '↑' : '↓';
  };

  return (
    <div className="miniature-table-container">
      <table className="miniature-table">
        <thead>
          <tr>
            <th 
              onClick={() => onSort('name')}
              className={`sortable ${sortField === 'name' ? 'active' : ''}`}
            >
              Name {getSortIcon('name')}
            </th>
            <th 
              onClick={() => onSort('faction')}
              className={`sortable ${sortField === 'faction' ? 'active' : ''}`}
            >
              Faction {getSortIcon('faction')}
            </th>
            <th 
              onClick={() => onSort('model_type')}
              className={`sortable ${sortField === 'model_type' ? 'active' : ''}`}
            >
              Type {getSortIcon('model_type')}
            </th>
            <th 
              onClick={() => onSort('status')}
              className={`sortable ${sortField === 'status' ? 'active' : ''}`}
            >
              Status {getSortIcon('status')}
            </th>
            <th className="notes-column">Notes</th>
            <th 
              onClick={() => onSort('created_at')}
              className={`sortable ${sortField === 'created_at' ? 'active' : ''}`}
            >
              Created {getSortIcon('created_at')}
            </th>
            <th 
              onClick={() => onSort('updated_at')}
              className={`sortable ${sortField === 'updated_at' ? 'active' : ''}`}
            >
              Updated {getSortIcon('updated_at')}
            </th>
            <th className="actions-column">Actions</th>
          </tr>
        </thead>
        <tbody>
          {miniatures.map(miniature => {
            const statusInfo = STATUS_INFO[miniature.status];
            
            return (
              <tr key={miniature.id}>
                <td className="name-cell">
                  <strong>{miniature.name}</strong>
                </td>
                <td>{miniature.faction}</td>
                <td>{miniature.model_type}</td>
                <td>
                  <div className="status-cell">
                    <select 
                      value={miniature.status}
                      onChange={(e) => handleStatusChange(miniature.id, e.target.value as PaintingStatus)}
                      className="status-select-table"
                      style={{ borderColor: statusInfo.color }}
                    >
                      {Object.entries(STATUS_INFO).map(([status, info]) => (
                        <option key={status} value={status}>
                          {info.label}
                        </option>
                      ))}
                    </select>
                    <div 
                      className="status-badge-small"
                      style={{ backgroundColor: statusInfo.color }}
                      title={statusInfo.description}
                    />
                  </div>
                </td>
                <td className="notes-cell">
                  {editingId === miniature.id ? (
                    <div className="notes-edit-table">
                      <textarea
                        value={editNotes}
                        onChange={(e) => setEditNotes(e.target.value)}
                        className="notes-textarea-table"
                        rows={2}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && e.ctrlKey) {
                            saveNotes(miniature.id);
                          } else if (e.key === 'Escape') {
                            cancelEdit();
                          }
                        }}
                      />
                      <div className="notes-buttons-table">
                        <button 
                          onClick={() => saveNotes(miniature.id)}
                          className="save-button-small"
                          title="Save (Ctrl+Enter)"
                        >
                          ✓
                        </button>
                        <button 
                          onClick={cancelEdit}
                          className="cancel-button-small"
                          title="Cancel (Esc)"
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="notes-display-table">
                      <span className="notes-text">
                        {miniature.notes || 'No notes'}
                      </span>
                      <button 
                        onClick={() => startEditNotes(miniature)}
                        className="edit-button-small"
                        title="Edit notes"
                      >
                        ✏️
                      </button>
                    </div>
                  )}
                </td>
                <td className="date-cell">
                  {formatDate(miniature.created_at)}
                </td>
                <td className="date-cell">
                  {formatDate(miniature.updated_at)}
                </td>
                <td className="actions-cell">
                  <button 
                    onClick={() => onDelete(miniature.id)}
                    className="delete-button-table"
                    title="Delete miniature"
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default MiniatureTable; 