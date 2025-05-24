import React, { useState, useMemo } from 'react';
import { Miniature, PaintingStatus, STATUS_INFO } from '../types';
import MiniatureCard from './MiniatureCard';
import MiniatureTable from './MiniatureTable';

interface MiniatureListProps {
  miniatures: Miniature[];
  onUpdate: (id: string, updates: Partial<Miniature>) => void;
  onDelete: (id: string) => void;
}

type ViewMode = 'cards' | 'table';
type SortField = 'name' | 'faction' | 'model_type' | 'status' | 'created_at' | 'updated_at';
type SortOrder = 'asc' | 'desc';

interface FilterState {
  faction: string;
  model_type: string;
  status: string;
}

const MiniatureList: React.FC<MiniatureListProps> = ({
  miniatures,
  onUpdate,
  onDelete
}) => {
  // View and interaction state
  const [viewMode, setViewMode] = useState<ViewMode>('cards');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  
  // Filter state
  const [filters, setFilters] = useState<FilterState>({
    faction: '',
    model_type: '',
    status: ''
  });

  // Get unique values for filter dropdowns
  const uniqueValues = useMemo(() => {
    const factions = Array.from(new Set(miniatures.map(m => m.faction))).sort();
    const modelTypes = Array.from(new Set(miniatures.map(m => m.model_type))).sort();
    const statuses = Object.keys(STATUS_INFO);
    
    return { factions, modelTypes, statuses };
  }, [miniatures]);

  // Filtered and sorted miniatures
  const filteredAndSortedMiniatures = useMemo(() => {
    let filtered = miniatures.filter(miniature => {
      // Search filter - search in all text fields
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = !searchTerm || 
        miniature.name.toLowerCase().includes(searchLower) ||
        miniature.faction.toLowerCase().includes(searchLower) ||
        miniature.model_type.toLowerCase().includes(searchLower) ||
        STATUS_INFO[miniature.status].label.toLowerCase().includes(searchLower) ||
        (miniature.notes && miniature.notes.toLowerCase().includes(searchLower));

      // Dropdown filters
      const matchesFaction = !filters.faction || miniature.faction === filters.faction;
      const matchesModelType = !filters.model_type || miniature.model_type === filters.model_type;
      const matchesStatus = !filters.status || miniature.status === filters.status;

      return matchesSearch && matchesFaction && matchesModelType && matchesStatus;
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
        case 'model_type':
          aValue = a.model_type.toLowerCase();
          bValue = b.model_type.toLowerCase();
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
      model_type: '',
      status: ''
    });
  };

  if (miniatures.length === 0) {
    return (
      <div className="empty-state">
        <h3>No miniatures yet!</h3>
        <p>Add your first Warhammer miniature to start tracking your collection.</p>
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
        </div>
      </div>

      {/* Search and Filters */}
      <div className="search-and-filters">
        {/* Search Bar */}
        <div className="search-section">
          <input
            type="text"
            className="search-input"
            placeholder="🔍 Search miniatures... (name, faction, type, status, notes)"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Filters */}
        <div className="filters-section">
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
            value={filters.model_type}
            onChange={(e) => handleFilterChange('model_type', e.target.value)}
            className="filter-select"
          >
            <option value="">All Types</option>
            {uniqueValues.modelTypes.map(type => (
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
            {(['name', 'faction', 'model_type', 'status', 'created_at', 'updated_at'] as SortField[]).map(field => (
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
              onUpdate={onUpdate}
              onDelete={onDelete}
            />
          ))}
        </div>
      ) : (
        <MiniatureTable
          miniatures={filteredAndSortedMiniatures}
          onUpdate={onUpdate}
          onDelete={onDelete}
          sortField={sortField}
          sortOrder={sortOrder}
          onSort={handleSortChange}
        />
      )}

      {filteredAndSortedMiniatures.length === 0 && (miniatures.length > 0) && (
        <div className="no-results">
          <p>No miniatures match your current filters.</p>
          <button onClick={clearFilters} className="clear-filters-button">
            Clear filters
          </button>
        </div>
      )}
    </div>
  );
};

export default MiniatureList; 