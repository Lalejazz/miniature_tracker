import React, { useState, useEffect } from 'react';
import { Miniature } from '../types';
import { miniatureApi, projectApi } from '../services/api';

interface AddMiniaturesToProjectProps {
  projectId: string;
  existingMiniatureIds: string[];
  onClose: () => void;
  onMiniaturesAdded: (miniatures: Miniature[]) => void;
  onError: (error: string) => void;
}

const AddMiniaturesToProject: React.FC<AddMiniaturesToProjectProps> = ({
  projectId,
  existingMiniatureIds,
  onClose,
  onMiniaturesAdded,
  onError
}) => {
  const [allMiniatures, setAllMiniatures] = useState<Miniature[]>([]);
  const [selectedMiniatureIds, setSelectedMiniatureIds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAdding, setIsAdding] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadMiniatures();
  }, []);

  const loadMiniatures = async () => {
    try {
      const miniatures = await miniatureApi.getAll();
      // Filter out miniatures already in the project
      const availableMiniatures = miniatures.filter(m => !existingMiniatureIds.includes(m.id));
      setAllMiniatures(availableMiniatures);
    } catch (error: any) {
      onError(error.message || 'Failed to load miniatures');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleMiniature = (miniatureId: string) => {
    setSelectedMiniatureIds(prev => 
      prev.includes(miniatureId)
        ? prev.filter(id => id !== miniatureId)
        : [...prev, miniatureId]
    );
  };

  const handleSelectAll = () => {
    const filteredMiniatures = getFilteredMiniatures();
    const allIds = filteredMiniatures.map(m => m.id);
    setSelectedMiniatureIds(allIds);
  };

  const handleDeselectAll = () => {
    setSelectedMiniatureIds([]);
  };

  const handleAddMiniatures = async () => {
    if (selectedMiniatureIds.length === 0) {
      return;
    }

    setIsAdding(true);
    try {
      await projectApi.addMultipleMiniatures(projectId, selectedMiniatureIds);
      
      // Get the added miniatures to return to parent
      const addedMiniatures = allMiniatures.filter(m => selectedMiniatureIds.includes(m.id));
      onMiniaturesAdded(addedMiniatures);
    } catch (error: any) {
      onError(error.message || 'Failed to add miniatures to project');
      setIsAdding(false);
    }
  };

  const getFilteredMiniatures = () => {
    if (!searchTerm) return allMiniatures;
    
    const searchLower = searchTerm.toLowerCase();
    return allMiniatures.filter(miniature =>
      miniature.name.toLowerCase().includes(searchLower) ||
      miniature.faction.toLowerCase().includes(searchLower)
    );
  };

  const filteredMiniatures = getFilteredMiniatures();

  if (isLoading) {
    return (
      <div className="add-miniatures-overlay">
        <div className="add-miniatures-modal">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading miniatures...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="add-miniatures-overlay">
      <div className="add-miniatures-modal">
        <div className="modal-header">
          <h3>Add Miniatures to Project</h3>
          <button onClick={onClose} className="close-button">×</button>
        </div>

        <div className="modal-content">
          {allMiniatures.length === 0 ? (
            <div className="no-available-miniatures">
              <p>All your miniatures are already in this project!</p>
              <button onClick={onClose} className="close-button-text">
                Close
              </button>
            </div>
          ) : (
            <>
              <div className="search-and-controls">
                <input
                  type="text"
                  placeholder="Search miniatures..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-input"
                />
                <div className="selection-controls">
                  <button 
                    onClick={handleSelectAll}
                    className="select-all-button"
                    disabled={filteredMiniatures.length === 0}
                  >
                    Select All ({filteredMiniatures.length})
                  </button>
                  <button 
                    onClick={handleDeselectAll}
                    className="deselect-all-button"
                    disabled={selectedMiniatureIds.length === 0}
                  >
                    Deselect All
                  </button>
                </div>
              </div>

              <div className="miniatures-selection-list">
                {filteredMiniatures.length === 0 ? (
                  <p className="no-results">No miniatures match your search.</p>
                ) : (
                  filteredMiniatures.map(miniature => (
                    <div 
                      key={miniature.id} 
                      className={`miniature-selection-item ${
                        selectedMiniatureIds.includes(miniature.id) ? 'selected' : ''
                      }`}
                      onClick={() => handleToggleMiniature(miniature.id)}
                    >
                      <input
                        type="checkbox"
                        checked={selectedMiniatureIds.includes(miniature.id)}
                        onChange={() => handleToggleMiniature(miniature.id)}
                        className="miniature-checkbox"
                      />
                      <div className="miniature-info">
                        <h4>{miniature.name}</h4>
                        <p>{miniature.faction} • {miniature.quantity} model{miniature.quantity !== 1 ? 's' : ''}</p>
                        <span className="miniature-status">{miniature.status.replace('_', ' ')}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </>
          )}
        </div>

        {allMiniatures.length > 0 && (
          <div className="modal-footer">
            <div className="selected-count">
              {selectedMiniatureIds.length} miniature{selectedMiniatureIds.length !== 1 ? 's' : ''} selected
            </div>
            <div className="modal-buttons">
              <button 
                onClick={onClose} 
                className="cancel-button"
                disabled={isAdding}
              >
                Cancel
              </button>
              <button 
                onClick={handleAddMiniatures}
                className="add-button"
                disabled={selectedMiniatureIds.length === 0 || isAdding}
              >
                {isAdding ? 'Adding...' : `Add ${selectedMiniatureIds.length} Miniature${selectedMiniatureIds.length !== 1 ? 's' : ''}`}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AddMiniaturesToProject; 