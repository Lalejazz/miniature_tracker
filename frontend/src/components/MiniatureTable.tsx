import React, { useState } from 'react';
import { Miniature, PaintingStatus, STATUS_INFO, UNIT_TYPE_LABELS, GAME_SYSTEM_LABELS } from '../types';
import StatusHistory from './StatusHistory';

interface MiniatureTableProps {
  miniatures: Miniature[];
  onEdit: (miniature: Miniature) => void;
  onDelete: (id: string) => void;
  sortField: string;
  sortOrder: 'asc' | 'desc';
  onSort: (field: any) => void;
}

const MiniatureTable: React.FC<MiniatureTableProps> = ({
  miniatures,
  onEdit,
  onDelete,
  sortField,
  sortOrder,
  onSort
}) => {
  const [editingField, setEditingField] = useState<{ id: string; field: string } | null>(null);
  const [editValue, setEditValue] = useState('');
  const [expandedHistoryId, setExpandedHistoryId] = useState<string | null>(null);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const handleStatusChange = (id: string, newStatus: PaintingStatus) => {
    const miniature = miniatures.find(m => m.id === id);
    if (miniature) {
      onEdit({ ...miniature, status: newStatus });
    }
  };

  const startEdit = (miniature: Miniature, field: string) => {
    setEditingField({ id: miniature.id, field });
    setEditValue(miniature[field as keyof Miniature] as string || '');
  };

  const saveEdit = (id: string, field: string) => {
    const miniature = miniatures.find(m => m.id === id);
    if (miniature) {
      onEdit({ ...miniature, [field]: editValue });
    }
    setEditingField(null);
  };

  const cancelEdit = () => {
    setEditingField(null);
  };

  const getSortIcon = (field: string) => {
    if (sortField !== field) return '↕️';
    return sortOrder === 'asc' ? '↑' : '↓';
  };

  const toggleHistoryExpansion = (id: string) => {
    setExpandedHistoryId(expandedHistoryId === id ? null : id);
  };

  const renderEditableCell = (miniature: Miniature, field: string, maxLength?: number) => {
    const isEditing = editingField?.id === miniature.id && editingField?.field === field;
    const value = miniature[field as keyof Miniature] as string;

    if (isEditing) {
      return (
        <div className="inline-edit">
          <input
            type="text"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            className="inline-edit-input"
            maxLength={maxLength}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                saveEdit(miniature.id, field);
              } else if (e.key === 'Escape') {
                cancelEdit();
              }
            }}
            onBlur={() => saveEdit(miniature.id, field)}
            autoFocus
          />
        </div>
      );
    }

    return (
      <div className="editable-cell" onClick={() => startEdit(miniature, field)}>
        <span className="cell-value">{value}</span>
        <span className="edit-icon">✏️</span>
      </div>
    );
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
              onClick={() => onSort('game_system')}
              className={`sortable ${sortField === 'game_system' ? 'active' : ''}`}
            >
              Game System {getSortIcon('game_system')}
            </th>
            <th 
              onClick={() => onSort('unit_type')}
              className={`sortable ${sortField === 'unit_type' ? 'active' : ''}`}
            >
              Type {getSortIcon('unit_type')}
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
            const isHistoryExpanded = expandedHistoryId === miniature.id;
            
            return (
              <React.Fragment key={miniature.id}>
                <tr>
                  <td className="name-cell">
                    {renderEditableCell(miniature, 'name', 200)}
                  </td>
                  <td>
                    {renderEditableCell(miniature, 'faction', 100)}
                  </td>
                  <td>
                    <div className="game-system-cell">
                      {GAME_SYSTEM_LABELS[miniature.game_system]}
                    </div>
                  </td>
                  <td>
                    <div className="unit-type-cell">
                      {UNIT_TYPE_LABELS[miniature.unit_type]}
                    </div>
                  </td>
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
                    {editingField?.id === miniature.id && editingField?.field === 'notes' ? (
                      <div className="notes-edit-table">
                        <textarea
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          className="notes-textarea-table"
                          rows={2}
                          maxLength={1000}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' && e.ctrlKey) {
                              saveEdit(miniature.id, 'notes');
                            } else if (e.key === 'Escape') {
                              cancelEdit();
                            }
                          }}
                          onBlur={() => saveEdit(miniature.id, 'notes')}
                          autoFocus
                        />
                      </div>
                    ) : (
                      <div className="notes-display-table" onClick={() => startEdit(miniature, 'notes')}>
                        <span className="notes-text">
                          {miniature.notes || 'No notes'}
                        </span>
                        <span className="edit-icon">✏️</span>
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
                      onClick={() => onEdit(miniature)}
                      className="edit-button-table"
                      title="Edit unit"
                    >
                      ✏️
                    </button>
                    <button 
                      onClick={() => toggleHistoryExpansion(miniature.id)}
                      className="history-button-table"
                      title="View status history"
                    >
                      📋 ({miniature.status_history.length})
                    </button>
                    <button 
                      onClick={() => onDelete(miniature.id)}
                      className="delete-button-table"
                      title="Delete unit"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
                {isHistoryExpanded && (
                  <tr className="history-row">
                    <td colSpan={9} className="history-cell">
                      <StatusHistory 
                        miniature={miniature}
                        onUpdate={onEdit}
                      />
                    </td>
                  </tr>
                )}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default MiniatureTable; 