import React, { useState, useRef } from 'react';
import { miniatureApi } from '../services/api';

interface ImportExportProps {
  onImportComplete?: () => void;
}

const ImportExport: React.FC<ImportExportProps> = ({ onImportComplete }) => {
  const [isExporting, setIsExporting] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [importResult, setImportResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [replaceExisting, setReplaceExisting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleExport = async (format: 'json' | 'csv') => {
    setIsExporting(true);
    setError(null);
    
    try {
      await miniatureApi.exportCollection(format);
      setImportResult(`Collection exported successfully as ${format.toUpperCase()}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
    } finally {
      setIsExporting(false);
    }
  };

  const handleImport = async (format: 'json' | 'csv') => {
    const fileInput = fileInputRef.current;
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
      setError('Please select a file to import');
      return;
    }

    const file = fileInput.files[0];
    const expectedExtension = format === 'json' ? '.json' : '.csv';
    
    if (!file.name.toLowerCase().endsWith(expectedExtension)) {
      setError(`Please select a ${format.toUpperCase()} file (${expectedExtension})`);
      return;
    }

    setIsImporting(true);
    setError(null);
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
      
      // Notify parent component
      if (onImportComplete) {
        onImportComplete();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Import failed');
    } finally {
      setIsImporting(false);
    }
  };

  const clearMessages = () => {
    setError(null);
    setImportResult(null);
  };

  return (
    <div className="import-export-container">
      <h3>Import/Export Collection</h3>
      
      {/* Export Section */}
      <div className="export-section">
        <h4>Export Collection</h4>
        <p>Download your collection data for backup or analysis.</p>
        <div className="export-buttons">
          <button
            onClick={() => handleExport('json')}
            disabled={isExporting}
            className="export-btn json-btn"
          >
            {isExporting ? 'Exporting...' : 'Export as JSON'}
          </button>
          <button
            onClick={() => handleExport('csv')}
            disabled={isExporting}
            className="export-btn csv-btn"
          >
            {isExporting ? 'Exporting...' : 'Export as CSV'}
          </button>
        </div>
      </div>

      {/* Import Section */}
      <div className="import-section">
        <h4>Import Collection</h4>
        <p>Upload a JSON or CSV file to import miniatures into your collection.</p>
        
        <div className="import-controls">
          <input
            ref={fileInputRef}
            type="file"
            accept=".json,.csv"
            onChange={clearMessages}
            className="file-input"
          />
          
          <div className="import-options">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={replaceExisting}
                onChange={(e) => setReplaceExisting(e.target.checked)}
              />
              Replace existing collection (⚠️ This will delete all current miniatures)
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
      </div>

      {/* Messages */}
      {error && (
        <div className="message error-message">
          <strong>Error:</strong> {error}
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
  );
};

export default ImportExport; 