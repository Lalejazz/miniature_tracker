import React, { useState, useMemo } from 'react';
import { Miniature, PaintingStatus, STATUS_INFO, UNIT_TYPE_LABELS, GAME_SYSTEM_LABELS } from '../types';
import { miniatureApi } from '../services/api';
import MiniatureCard from './MiniatureCard';
import MiniatureTable from './MiniatureTable';

interface MiniatureListProps {
  miniatures: Miniature[];
  onEdit: (miniature: Miniature) => void;
  onDelete: (id: string) => void;
  onRefresh?: () => void;
}

type ViewMode = 'cards' | 'table';
type SortField = 'name' | 'faction' | 'unit_type' | 'status' | 'created_at' | 'updated_at';
type SortOrder = 'asc' | 'desc';

interface FilterState {
  faction: string;
  game_system: string;
  unit_type: string;
  status: string;
}

const MiniatureList: React.FC<MiniatureListProps> = ({
  miniatures,
  onEdit,
  onDelete,
  onRefresh
}) => {
  // View and interaction state
  const [viewMode, setViewMode] = useState<ViewMode>('cards');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [isExporting, setIsExporting] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [importResult, setImportResult] = useState<string | null>(null);
  const [importError, setImportError] = useState<string | null>(null);
  const [replaceExisting, setReplaceExisting] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  
  // Filter state
  const [filters, setFilters] = useState<FilterState>({
    faction: '',
    game_system: '',
    unit_type: '',
    status: ''
  });

  // Get unique values for filter dropdowns
  const uniqueValues = useMemo(() => {
    const factions = Array.from(new Set(miniatures.map(m => m.faction))).sort();
    const gameSystems = Array.from(new Set(miniatures.map(m => GAME_SYSTEM_LABELS[m.game_system]))).sort();
    const unitTypes = Array.from(new Set(miniatures.map(m => UNIT_TYPE_LABELS[m.unit_type]))).sort();
    const statuses = Object.keys(STATUS_INFO);
    
    return { factions, gameSystems, unitTypes, statuses };
  }, [miniatures]);

  // Filtered and sorted miniatures
  const filteredAndSortedMiniatures = useMemo(() => {
    let filtered = miniatures.filter(miniature => {
      // Search filter - search in all text fields
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = !searchTerm || 
        miniature.name.toLowerCase().includes(searchLower) ||
        miniature.faction.toLowerCase().includes(searchLower) ||
        GAME_SYSTEM_LABELS[miniature.game_system].toLowerCase().includes(searchLower) ||
        UNIT_TYPE_LABELS[miniature.unit_type].toLowerCase().includes(searchLower) ||
        STATUS_INFO[miniature.status].label.toLowerCase().includes(searchLower) ||
        (miniature.notes && miniature.notes.toLowerCase().includes(searchLower));

      // Dropdown filters
      const matchesFaction = !filters.faction || miniature.faction === filters.faction;
      const matchesGameSystem = !filters.game_system || GAME_SYSTEM_LABELS[miniature.game_system] === filters.game_system;
      const matchesUnitType = !filters.unit_type || UNIT_TYPE_LABELS[miniature.unit_type] === filters.unit_type;
      const matchesStatus = !filters.status || miniature.status === filters.status;

      return matchesSearch && matchesFaction && matchesGameSystem && matchesUnitType && matchesStatus;
    });

    // Sort the filtered results
    filtered.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortField) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'faction':
          aValue = a.faction.toLowerCase();
          bValue = b.faction.toLowerCase();
          break;
        case 'unit_type':
          aValue = UNIT_TYPE_LABELS[a.unit_type].toLowerCase();
          bValue = UNIT_TYPE_LABELS[b.unit_type].toLowerCase();
          break;
        case 'status':
          aValue = STATUS_INFO[a.status].label.toLowerCase();
          bValue = STATUS_INFO[b.status].label.toLowerCase();
          break;
        case 'created_at':
        case 'updated_at':
          aValue = new Date(a[sortField]);
          bValue = new Date(b[sortField]);
          break;
        default:
          return 0;
      }

      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [miniatures, searchTerm, filters, sortField, sortOrder]);

  const handleFilterChange = (filterType: keyof FilterState, value: string) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const handleSortChange = (field: SortField) => {
    if (sortField === field) {
      // Toggle order if same field
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      // New field, default to ascending
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const clearFilters = () => {
    setSearchTerm('');
    setFilters({
      faction: '',
      game_system: '',
      unit_type: '',
      status: ''
    });
  };

  const handleExport = async (format: 'json' | 'csv') => {
    setIsExporting(true);
    try {
      await miniatureApi.exportCollection(format);
    } catch (error) {
      console.error(`Export failed:`, error);
      alert(`Failed to export collection as ${format.toUpperCase()}`);
    } finally {
      setIsExporting(false);
    }
  };

  const handleImport = async (format: 'json' | 'csv') => {
    const fileInput = fileInputRef.current;
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
      setImportError('Please select a file to import');
      return;
    }

    const file = fileInput.files[0];
    const expectedExtension = format === 'json' ? '.json' : '.csv';
    
    if (!file.name.toLowerCase().endsWith(expectedExtension)) {
      setImportError(`Please select a ${format.toUpperCase()} file (${expectedExtension})`);
      return;
    }

    setIsImporting(true);
    setImportError(null);
    setImportResult(null);

    try {
      const result = await miniatureApi.importCollection(format, file, replaceExisting);
      setImportResult(
        `${result.message}. Imported ${result.imported_count} out of ${result.total_in_file} miniatures.`
      );
      
      // Clear the file input
      if (fileInput) {
        fileInput.value = '';
      }
      
      // Refresh the miniatures list
      if (onRefresh) {
        onRefresh();
      }
      
      // Close modal after successful import
      setTimeout(() => {
        setShowImportModal(false);
        setImportResult(null);
      }, 3000);
    } catch (error) {
      setImportError(error instanceof Error ? error.message : 'Import failed');
    } finally {
      setIsImporting(false);
    }
  };

  const clearImportMessages = () => {
    setImportError(null);
    setImportResult(null);
  };

  if (miniatures.length === 0) {
    return (
      <div className="empty-state">
        <h3>No units yet!</h3>
        <p>Add your first unit to start tracking your collection.</p>
      </div>
    );
  }

  return (
    <div className="miniature-list">
      <div className="list-header">
        <h2>Your Collection ({filteredAndSortedMiniatures.length} of {miniatures.length})</h2>
        
        {/* View Mode Toggle */}
        <div className="view-controls">
          <button 
            className={`view-button ${viewMode === 'cards' ? 'active' : ''}`}
            onClick={() => setViewMode('cards')}
            title="Card View"
          >
            📋 Cards
          </button>
          <button 
            className={`view-button ${viewMode === 'table' ? 'active' : ''}`}
            onClick={() => setViewMode('table')}
            title="Table View"
          >
            📊 Table
          </button>
          
          {/* Export Controls */}
          <div className="export-controls">
            <button 
              className="export-button"
              onClick={() => handleExport('csv')}
              disabled={isExporting || miniatures.length === 0}
              title="Export collection as CSV"
            >
              📄 CSV
            </button>
            <button 
              className="export-button"
              onClick={() => handleExport('json')}
              disabled={isExporting || miniatures.length === 0}
              title="Export collection as JSON"
            >
              📋 JSON
            </button>
            <button 
              className="import-button"
              onClick={() => setShowImportModal(true)}
              disabled={isImporting}
              title="Import collection from file"
            >
              📥 Import
            </button>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="search-and-filters">
        {/* Search Bar */}
        <div className="search-section">
          <input
            type="text"
            className="search-input"
            placeholder="🔍 Search units... (name, faction, type, status, notes)"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Filters */}
        <div className="filters-section">
          <select
            value={filters.game_system}
            onChange={(e) => handleFilterChange('game_system', e.target.value)}
            className="filter-select"
          >
            <option value="">All Game Systems</option>
            {uniqueValues.gameSystems.map(system => (
              <option key={system} value={system}>{system}</option>
            ))}
          </select>

          <select
            value={filters.faction}
            onChange={(e) => handleFilterChange('faction', e.target.value)}
            className="filter-select"
          >
            <option value="">All Factions</option>
            {uniqueValues.factions.map(faction => (
              <option key={faction} value={faction}>{faction}</option>
            ))}
          </select>

          <select
            value={filters.unit_type}
            onChange={(e) => handleFilterChange('unit_type', e.target.value)}
            className="filter-select"
          >
            <option value="">All Types</option>
            {uniqueValues.unitTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>

          <select
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="filter-select"
          >
            <option value="">All Statuses</option>
            {uniqueValues.statuses.map(status => (
              <option key={status} value={status}>
                {STATUS_INFO[status as PaintingStatus].label}
              </option>
            ))}
          </select>

          <button 
            onClick={clearFilters}
            className="clear-filters-button"
            title="Clear all filters"
          >
            ✕ Clear
          </button>
        </div>

        {/* Sort Controls (only show in table view) */}
        {viewMode === 'table' && (
          <div className="sort-section">
            <span>Sort by:</span>
            {(['name', 'faction', 'unit_type', 'status', 'created_at', 'updated_at'] as SortField[]).map(field => (
              <button
                key={field}
                onClick={() => handleSortChange(field)}
                className={`sort-button ${sortField === field ? 'active' : ''}`}
              >
                {field.replace('_', ' ')} {sortField === field ? (sortOrder === 'asc' ? '↑' : '↓') : ''}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Content */}
      {viewMode === 'cards' ? (
        <div className="miniature-grid">
          {filteredAndSortedMiniatures.map(miniature => (
            <MiniatureCard
              key={miniature.id}
              miniature={miniature}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          ))}
        </div>
      ) : (
        <MiniatureTable
          miniatures={filteredAndSortedMiniatures}
          onEdit={onEdit}
          onDelete={onDelete}
          sortField={sortField}
          sortOrder={sortOrder}
          onSort={handleSortChange}
        />
      )}

      {filteredAndSortedMiniatures.length === 0 && (miniatures.length > 0) && (
        <div className="no-results">
          <p>No units match your current filters.</p>
          <button onClick={clearFilters} className="clear-filters-button">
            Clear filters
          </button>
        </div>
      )}

      {/* Import Modal */}
      {showImportModal && (
        <div className="import-modal-overlay" onClick={() => setShowImportModal(false)}>
          <div className="import-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="import-modal-header">
              <h3>Import Collection</h3>
              <button 
                className="close-button"
                onClick={() => setShowImportModal(false)}
                title="Close"
              >
                ✕
              </button>
            </div>
            
            <div className="import-modal-body">
              <p>Upload a JSON or CSV file to import miniatures into your collection.</p>
              
              <div className="import-controls">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".json,.csv"
                  onChange={clearImportMessages}
                  className="file-input"
                />
                
                <div className="import-options">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={replaceExisting}
                      onChange={(e) => setReplaceExisting(e.target.checked)}
                    />
                    <span>Replace existing collection (⚠️ This will delete all current miniatures)</span>
                  </label>
                </div>
                
                <div className="import-buttons">
                  <button
                    onClick={() => handleImport('json')}
                    disabled={isImporting}
                    className="import-btn json-btn"
                  >
                    {isImporting ? 'Importing...' : 'Import JSON'}
                  </button>
                  <button
                    onClick={() => handleImport('csv')}
                    disabled={isImporting}
                    className="import-btn csv-btn"
                  >
                    {isImporting ? 'Importing...' : 'Import CSV'}
                  </button>
                </div>
              </div>

              {/* Messages */}
              {importError && (
                <div className="message error-message">
                  <strong>Error:</strong> {importError}
                </div>
              )}
              
              {importResult && (
                <div className="message success-message">
                  <strong>Success:</strong> {importResult}
                </div>
              )}

              {/* Format Information */}
              <div className="format-info">
                <h4>Format Information</h4>
                <div className="format-details">
                  <div className="format-item">
                    <strong>JSON:</strong> Complete data including status history and metadata. Best for full backups.
                  </div>
                  <div className="format-item">
                    <strong>CSV:</strong> Simplified format for spreadsheet analysis. Status history not included.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MiniatureList; 