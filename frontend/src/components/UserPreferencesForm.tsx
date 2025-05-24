import React, { useState, useEffect } from 'react';
import { 
  Game, 
  GameType, 
  UserPreferences, 
  UserPreferencesCreate
} from '../types';
import { playerApi } from '../services/api';

interface UserPreferencesFormProps {
  existingPreferences?: UserPreferences | null;
  onSave: (preferences: UserPreferences) => void;
  onCancel?: () => void;
}

const UserPreferencesForm: React.FC<UserPreferencesFormProps> = ({ 
  existingPreferences, 
  onSave,
  onCancel 
}) => {
  const [games, setGames] = useState<Game[]>([]);
  const [formData, setFormData] = useState<UserPreferencesCreate>({
    games: existingPreferences?.games || [],
    postcode: existingPreferences?.postcode || '',
    game_type: existingPreferences?.game_type || 'competitive' as GameType,
    bio: existingPreferences?.bio || '',
    show_email: existingPreferences?.show_email || false
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingGames, setLoadingGames] = useState(true);

  // Load available games on component mount
  useEffect(() => {
    const loadGames = async () => {
      try {
        setLoadingGames(true);
        const availableGames = await playerApi.getGames();
        setGames(availableGames);
        console.log('Loaded games:', availableGames); // Debug log
      } catch (err) {
        console.error('Failed to load games:', err);
        setError('Failed to load available games');
      } finally {
        setLoadingGames(false);
      }
    };

    loadGames();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      let result: UserPreferences;
      
      if (existingPreferences) {
        // Update existing preferences
        result = await playerApi.updatePreferences(formData);
      } else {
        // Create new preferences
        result = await playerApi.createPreferences(formData);
      }
      
      onSave(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save preferences');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGameToggle = (gameId: string) => {
    setFormData(prev => ({
      ...prev,
      games: prev.games.includes(gameId)
        ? prev.games.filter(id => id !== gameId)
        : [...prev.games, gameId]
    }));
  };

  const isFormValid = formData.games.length > 0 && formData.postcode.trim().length > 0;

  if (loadingGames) {
    return <div className="loading">Loading games...</div>;
  }

  return (
    <div className="preferences-form">
      <h2>{existingPreferences ? 'Update' : 'Set'} Your Gaming Preferences</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="postcode">Postcode *</label>
          <input
            type="text"
            id="postcode"
            value={formData.postcode}
            onChange={(e) => setFormData(prev => ({ ...prev, postcode: e.target.value }))}
            placeholder="Enter your postcode"
            required
            maxLength={20}
          />
          <small>This helps us find players near you</small>
        </div>

        <div className="form-group">
          <label>Games You Play *</label>
          {games.length === 0 ? (
            <div className="no-games">
              <p>No games available. Please try refreshing the page.</p>
            </div>
          ) : (
            <div className="games-grid">
              {games.map(game => (
                <label key={game.id} className="game-checkbox">
                  <input
                    type="checkbox"
                    checked={formData.games.includes(game.id)}
                    onChange={() => handleGameToggle(game.id)}
                  />
                  <span className="game-name">{game.name}</span>
                  {game.description && (
                    <small className="game-description">{game.description}</small>
                  )}
                </label>
              ))}
            </div>
          )}
          {formData.games.length === 0 && (
            <small className="error">Please select at least one game</small>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="game_type">Game Type *</label>
          <select
            id="game_type"
            value={formData.game_type}
            onChange={(e) => setFormData(prev => ({ ...prev, game_type: e.target.value as GameType }))}
            required
          >
            <option value="competitive">Competitive</option>
            <option value="narrative">Narrative</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="bio">Bio</label>
          <textarea
            id="bio"
            value={formData.bio || ''}
            onChange={(e) => setFormData(prev => ({ ...prev, bio: e.target.value }))}
            placeholder="Tell other players about yourself (max 160 characters)"
            maxLength={160}
            rows={3}
          />
          <small>{(formData.bio || '').length}/160 characters</small>
        </div>

        <div className="form-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={formData.show_email || false}
              onChange={(e) => setFormData(prev => ({ ...prev, show_email: e.target.checked }))}
            />
            <span>Show my email in player discovery (so others can contact me)</span>
          </label>
          <small>When enabled, other players will see your email as a contact option</small>
        </div>

        <div className="form-actions">
          <button 
            type="submit" 
            disabled={isLoading || !isFormValid}
          >
            {isLoading ? 'Saving...' : existingPreferences ? 'Update Preferences' : 'Save Preferences'}
          </button>
          {onCancel && (
            <button type="button" onClick={onCancel}>
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default UserPreferencesForm; 