import React, { useState } from 'react';
import { Miniature, StatusLogEntry, StatusLogEntryCreate, StatusLogEntryUpdate, PaintingStatus, STATUS_INFO } from '../types';
import { miniatureApi } from '../services/api';

interface StatusHistoryProps {
  miniature: Miniature;
  onUpdate: (updatedMiniature: Miniature) => void;
}

const StatusHistory: React.FC<StatusHistoryProps> = ({ miniature, onUpdate }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingLogId, setEditingLogId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state for adding new log entry
  const [newLogData, setNewLogData] = useState<StatusLogEntryCreate>({
    from_status: undefined,
    to_status: PaintingStatus.WANT_TO_BUY,
    date: new Date().toISOString().slice(0, 16), // Format for datetime-local input
    notes: '',
    is_manual: true
  });

  // Form state for editing existing log entry
  const [editLogData, setEditLogData] = useState<StatusLogEntryUpdate>({
    date: '',
    notes: ''
  });

  const sortedHistory = [...miniature.status_history].sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
  );

  const handleAddLog = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const logWithDate = {
        ...newLogData,
        date: new Date(newLogData.date).toISOString()
      };
      
      await miniatureApi.addStatusLog(miniature.id, logWithDate);
      
      // Refresh miniature data
      const updatedMiniature = await miniatureApi.getById(miniature.id);
      onUpdate(updatedMiniature);
      
      // Reset form
      setNewLogData({
        from_status: undefined,
        to_status: PaintingStatus.WANT_TO_BUY,
        date: new Date().toISOString().slice(0, 16),
        notes: '',
        is_manual: true
      });
      setShowAddForm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add log entry');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditLog = async (logId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const updateData = {
        ...editLogData,
        date: editLogData.date ? new Date(editLogData.date).toISOString() : undefined
      };
      
      await miniatureApi.updateStatusLog(miniature.id, logId, updateData);
      
      // Refresh miniature data
      const updatedMiniature = await miniatureApi.getById(miniature.id);
      onUpdate(updatedMiniature);
      
      setEditingLogId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update log entry');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteLog = async (logId: string) => {
    if (!confirm('Are you sure you want to delete this log entry?')) return;

    setIsLoading(true);
    setError(null);

    try {
      await miniatureApi.deleteStatusLog(miniature.id, logId);
      
      // Refresh miniature data
      const updatedMiniature = await miniatureApi.getById(miniature.id);
      onUpdate(updatedMiniature);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete log entry');
    } finally {
      setIsLoading(false);
    }
  };

  const startEdit = (log: StatusLogEntry) => {
    setEditingLogId(log.id);
    setEditLogData({
      date: new Date(log.date).toISOString().slice(0, 16),
      notes: log.notes || ''
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusTransitionText = (log: StatusLogEntry) => {
    if (!log.from_status) {
      return `Set to ${STATUS_INFO[log.to_status].label}`;
    }
    return `${STATUS_INFO[log.from_status].label} → ${STATUS_INFO[log.to_status].label}`;
  };

  return (
    <div className="status-history">
      <div className="status-history-header">
        <h4>Status History ({miniature.status_history.length})</h4>
        <div className="status-history-actions">
          <button
            type="button"
            onClick={() => setShowAddForm(!showAddForm)}
            className="add-log-button"
          >
            + Add Entry
          </button>
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="expand-button"
          >
            {isExpanded ? '▼' : '▶'}
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showAddForm && (
        <form onSubmit={handleAddLog} className="add-log-form">
          <div className="form-row">
            <label>From Status</label>
            <select
              value={newLogData.from_status || ''}
              onChange={(e) => setNewLogData(prev => ({
                ...prev,
                from_status: e.target.value ? e.target.value as PaintingStatus : undefined
              }))}
            >
              <option value="">Initial status</option>
              {Object.values(PaintingStatus).map(status => (
                <option key={status} value={status}>
                  {STATUS_INFO[status].label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <label>To Status *</label>
            <select
              value={newLogData.to_status}
              onChange={(e) => setNewLogData(prev => ({
                ...prev,
                to_status: e.target.value as PaintingStatus
              }))}
              required
            >
              {Object.values(PaintingStatus).map(status => (
                <option key={status} value={status}>
                  {STATUS_INFO[status].label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <label>Date *</label>
            <input
              type="datetime-local"
              value={newLogData.date}
              onChange={(e) => setNewLogData(prev => ({
                ...prev,
                date: e.target.value
              }))}
              required
            />
          </div>

          <div className="form-row">
            <label>Notes</label>
            <input
              type="text"
              value={newLogData.notes}
              onChange={(e) => setNewLogData(prev => ({
                ...prev,
                notes: e.target.value
              }))}
              placeholder="Optional notes..."
              maxLength={500}
            />
          </div>

          <div className="form-actions">
            <button type="button" onClick={() => setShowAddForm(false)}>Cancel</button>
            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Adding...' : 'Add Entry'}
            </button>
          </div>
        </form>
      )}

      {isExpanded && (
        <div className="status-history-list">
          {sortedHistory.length === 0 ? (
            <p className="no-history">No status history available.</p>
          ) : (
            sortedHistory.map((log) => (
              <div key={log.id} className={`status-log-entry ${log.is_manual ? 'manual' : 'automatic'}`}>
                {editingLogId === log.id ? (
                  <div className="edit-log-form">
                    <div className="form-row">
                      <label>Date</label>
                      <input
                        type="datetime-local"
                        value={editLogData.date}
                        onChange={(e) => setEditLogData(prev => ({
                          ...prev,
                          date: e.target.value
                        }))}
                      />
                    </div>
                    <div className="form-row">
                      <label>Notes</label>
                      <input
                        type="text"
                        value={editLogData.notes}
                        onChange={(e) => setEditLogData(prev => ({
                          ...prev,
                          notes: e.target.value
                        }))}
                        maxLength={500}
                      />
                    </div>
                    <div className="form-actions">
                      <button type="button" onClick={() => setEditingLogId(null)}>Cancel</button>
                      <button type="button" onClick={() => handleEditLog(log.id)} disabled={isLoading}>
                        Save
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="log-content">
                      <div className="log-status">
                        <span className="status-transition">
                          {getStatusTransitionText(log)}
                        </span>
                        <span className="log-type">{log.is_manual ? '(Manual)' : '(Auto)'}</span>
                      </div>
                      <div className="log-date">{formatDate(log.date)}</div>
                      {log.notes && <div className="log-notes">{log.notes}</div>}
                    </div>
                    {log.is_manual && (
                      <div className="log-actions">
                        <button type="button" onClick={() => startEdit(log)} disabled={isLoading}>
                          Edit
                        </button>
                        <button type="button" onClick={() => handleDeleteLog(log.id)} disabled={isLoading}>
                          Delete
                        </button>
                      </div>
                    )}
                  </>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default StatusHistory; 