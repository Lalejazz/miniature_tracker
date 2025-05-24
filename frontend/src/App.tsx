import React, { useState, useEffect } from 'react';
import './App.css';
import { Miniature, MiniatureCreate } from './types';
import { miniatureApi } from './services/api';
import MiniatureList from './components/MiniatureList';
import MiniatureForm from './components/MiniatureForm';

function App() {
  const [miniatures, setMiniatures] = useState<Miniature[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  // Load miniatures on mount
  useEffect(() => {
    loadMiniatures();
  }, []);

  const loadMiniatures = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await miniatureApi.getAll();
      setMiniatures(data);
    } catch (err) {
      setError('Failed to load miniatures. Make sure the backend is running.');
      console.error('Error loading miniatures:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMiniature = async (miniatureData: MiniatureCreate) => {
    try {
      setError(null);
      const newMiniature = await miniatureApi.create(miniatureData);
      setMiniatures(prev => [...prev, newMiniature]);
      setShowForm(false);
    } catch (err) {
      setError('Failed to create miniature');
      console.error('Error creating miniature:', err);
    }
  };

  const handleUpdateMiniature = async (id: string, updates: Partial<Miniature>) => {
    try {
      setError(null);
      const updated = await miniatureApi.update(id, updates);
      setMiniatures(prev => 
        prev.map(m => m.id === id ? updated : m)
      );
    } catch (err) {
      setError('Failed to update miniature');
      console.error('Error updating miniature:', err);
    }
  };

  const handleDeleteMiniature = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this miniature?')) {
      return;
    }

    try {
      setError(null);
      await miniatureApi.delete(id);
      setMiniatures(prev => prev.filter(m => m.id !== id));
    } catch (err) {
      setError('Failed to delete miniature');
      console.error('Error deleting miniature:', err);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎨 Miniature Tracker</h1>
        <p>Track your Warhammer miniature collection and painting progress</p>
      </header>

      <main className="App-main">
        {error && (
          <div className="error-banner">
            <span>⚠️ {error}</span>
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        <div className="controls">
          <button 
            className="add-button"
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? '✕ Cancel' : '+ Add Miniature'}
          </button>
          <button 
            className="refresh-button"
            onClick={loadMiniatures}
            disabled={loading}
          >
            🔄 Refresh
          </button>
        </div>

        {showForm && (
          <MiniatureForm
            onSubmit={handleCreateMiniature}
            onCancel={() => setShowForm(false)}
          />
        )}

        {loading ? (
          <div className="loading">Loading miniatures...</div>
        ) : (
          <MiniatureList
            miniatures={miniatures}
            onUpdate={handleUpdateMiniature}
            onDelete={handleDeleteMiniature}
          />
        )}
      </main>

      <footer className="App-footer">
        <p>Built with React + FastAPI | {miniatures.length} miniatures tracked</p>
      </footer>
    </div>
  );
}

export default App; 