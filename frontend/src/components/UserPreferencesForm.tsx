import React, { useState, useEffect } from 'react';
import { 
  GameType, 
  UserPreferences, 
  UserPreferencesCreate,
  Theme,
  Game,
  DayOfWeek,
  TimeOfDay,
  HostingPreference,
  HostingDetails,
  DAY_OF_WEEK_LABELS,
  TIME_OF_DAY_LABELS,
  HOSTING_PREFERENCE_LABELS
} from '../types';
import { playerApi } from '../services/api';
import AccountDeletion from './AccountDeletion';
import ThemeSelector from './ThemeSelector';

interface UserPreferencesFormProps {
  existingPreferences?: UserPreferences | null;
  onSave: (preferences: UserPreferences) => void;
  onCancel?: () => void;
  onAccountDeleted?: () => void;
}

const UserPreferencesForm: React.FC<UserPreferencesFormProps> = ({
  existingPreferences,
  onSave,
  onCancel,
  onAccountDeleted
}) => {
  const [availableGames, setAvailableGames] = useState<Game[]>([]);
  const [gamesLoading, setGamesLoading] = useState(true);
  const [formData, setFormData] = useState<UserPreferencesCreate>({
    games: existingPreferences?.games || [],
    location: existingPreferences?.location || '',
    game_type: existingPreferences?.game_type || 'competitive' as GameType,
    bio: existingPreferences?.bio || '',
    show_email: existingPreferences?.show_email || false,
    theme: existingPreferences?.theme || Theme.BLUE_GRADIENT,
    availability: existingPreferences?.availability || [],
    hosting: existingPreferences?.hosting || {
      preferences: [],
      has_gaming_space: false,
      has_boards_scenery: false,
      max_players: undefined,
      notes: ''
    }
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Load available games from backend
  useEffect(() => {
    const loadGames = async () => {
      try {
        setGamesLoading(true);
        const games = await playerApi.getGames();
        setAvailableGames(games);
      } catch (err) {
        console.error('Failed to load games:', err);
        setError('Failed to load available games');
      } finally {
        setGamesLoading(false);
      }
    };

    loadGames();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      let result: UserPreferences;
      
      // Prepare the data to match backend expectations
      const backendData = {
        games: formData.games, // Keep as strings since backend expects UUID strings in JSON
        location: formData.location,
        game_type: formData.game_type,
        bio: formData.bio || undefined,
        show_email: formData.show_email || false,
        theme: formData.theme || Theme.BLUE_GRADIENT
      };
      
      if (existingPreferences) {
        // Update existing preferences
        result = await playerApi.updatePreferences(backendData);
        setSuccessMessage('Your preferences have been updated successfully!');
      } else {
        // Create new preferences
        result = await playerApi.createPreferences(backendData);
        setSuccessMessage('Your preferences have been saved successfully!');
      }
      
      onSave(result);
    } catch (err) {
      console.error('Preferences save error:', err);
      
      // Handle different error types
      let errorMessage = 'Failed to save preferences';
      
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === 'object' && err !== null) {
        // Handle object errors (like ApiError or validation errors)
        if ('message' in err && typeof err.message === 'string') {
          errorMessage = err.message;
        } else if ('detail' in err && typeof err.detail === 'string') {
          errorMessage = err.detail;
        } else if (Array.isArray(err)) {
          // Handle validation error arrays
          errorMessage = err.map(e => typeof e === 'string' ? e : JSON.stringify(e)).join(', ');
        } else {
          // Fallback for complex error objects
          errorMessage = JSON.stringify(err);
        }
      } else if (typeof err === 'string') {
        errorMessage = err;
      }
      
      setError(errorMessage);
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

  const handleThemeChange = (theme: Theme) => {
    setFormData(prev => ({
      ...prev,
      theme
    }));
  };

  const handleAvailabilityToggle = (day: DayOfWeek, time: TimeOfDay) => {
    setFormData(prev => {
      const availability = [...(prev.availability || [])];
      const daySlotIndex = availability.findIndex(slot => slot.day === day);
      
      if (daySlotIndex >= 0) {
        const daySlot = availability[daySlotIndex];
        const timeIndex = daySlot.times.indexOf(time);
        
        if (timeIndex >= 0) {
          // Remove time from existing day slot
          daySlot.times.splice(timeIndex, 1);
          if (daySlot.times.length === 0) {
            // Remove day slot if no times left
            availability.splice(daySlotIndex, 1);
          }
        } else {
          // Add time to existing day slot
          daySlot.times.push(time);
        }
      } else {
        // Create new day slot with this time
        availability.push({ day, times: [time] });
      }
      
      return { ...prev, availability };
    });
  };

  const handleHostingPreferenceToggle = (preference: HostingPreference) => {
    setFormData(prev => ({
      ...prev,
      hosting: {
        ...prev.hosting!,
        preferences: prev.hosting!.preferences.includes(preference)
          ? prev.hosting!.preferences.filter(p => p !== preference)
          : [...prev.hosting!.preferences, preference]
      }
    }));
  };

  const handleHostingDetailChange = (field: keyof HostingDetails, value: any) => {
    setFormData(prev => ({
      ...prev,
      hosting: {
        ...prev.hosting!,
        [field]: value
      }
    }));
  };

  const isFormValid = !gamesLoading && formData.games.length > 0 && formData.location.trim().length > 0;

  return (
    <div className="preferences-form">
      <h2>{existingPreferences ? 'Update' : 'Set'} Your Gaming Preferences</h2>
      
      {error && <div className="error-message">{error}</div>}
      {successMessage && <div className="success-message">{successMessage}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="location">Location *</label>
          <input
            type="text"
            id="location"
            value={formData.location}
            onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
            placeholder="Enter your city, postcode, or address"
            required
            maxLength={100}
          />
          <small>Enter your city, postcode, or address to help us find players near you</small>
        </div>

        <div className="form-group">
          <label>Games You Play *</label>
          {gamesLoading ? (
            <div className="loading-message">Loading available games...</div>
          ) : (
            <div className="games-grid">
              {availableGames.map(game => (
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
          {!gamesLoading && formData.games.length === 0 && (
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

        <ThemeSelector
          selectedTheme={formData.theme || Theme.BLUE_GRADIENT}
          onThemeChange={handleThemeChange}
        />

        <div className="form-group">
          <label>When are you available to play? (optional)</label>
          <div className="availability-grid">
            {(Object.keys(DAY_OF_WEEK_LABELS) as DayOfWeek[]).map(day => (
              <div key={day} className="availability-day">
                <h4>{DAY_OF_WEEK_LABELS[day]}</h4>
                <div className="time-slots">
                  {(Object.keys(TIME_OF_DAY_LABELS) as TimeOfDay[]).map(time => {
                    const isSelected = formData.availability?.some(slot => 
                      slot.day === day && slot.times.includes(time)
                    ) || false;
                    
                    return (
                      <label key={time} className="time-slot-checkbox">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => handleAvailabilityToggle(day, time)}
                        />
                        <span>{TIME_OF_DAY_LABELS[time]}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
          <small>Select the days and times when you're typically available to play</small>
        </div>

        <div className="form-group">
          <label>Hosting Preferences (optional)</label>
          <div className="hosting-preferences">
            {(Object.keys(HOSTING_PREFERENCE_LABELS) as HostingPreference[]).map(preference => (
              <label key={preference} className="hosting-checkbox">
                <input
                  type="checkbox"
                  checked={formData.hosting?.preferences.includes(preference) || false}
                  onChange={() => handleHostingPreferenceToggle(preference)}
                />
                <span>{HOSTING_PREFERENCE_LABELS[preference]}</span>
              </label>
            ))}
          </div>
          
          {formData.hosting?.preferences.includes(HostingPreference.CAN_HOST) && (
            <div className="hosting-details">
              <h4>Hosting Details</h4>
              
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={formData.hosting?.has_gaming_space || false}
                  onChange={(e) => handleHostingDetailChange('has_gaming_space', e.target.checked)}
                />
                <span>I have a dedicated gaming space</span>
              </label>
              
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={formData.hosting?.has_boards_scenery || false}
                  onChange={(e) => handleHostingDetailChange('has_boards_scenery', e.target.checked)}
                />
                <span>I have gaming boards and scenery</span>
              </label>
              
              <div className="form-group">
                <label htmlFor="max_players">Maximum players you can host</label>
                <input
                  id="max_players"
                  type="number"
                  min="2"
                  max="20"
                  value={formData.hosting?.max_players || ''}
                  onChange={(e) => handleHostingDetailChange('max_players', e.target.value ? parseInt(e.target.value) : undefined)}
                  placeholder="e.g., 4"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="hosting_notes">Additional hosting notes</label>
                <textarea
                  id="hosting_notes"
                  value={formData.hosting?.notes || ''}
                  onChange={(e) => handleHostingDetailChange('notes', e.target.value)}
                  placeholder="e.g., 'Large dining table, parking available, pets friendly'"
                  maxLength={200}
                />
                <small>Optional details about your hosting setup</small>
              </div>
            </div>
          )}
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

      {onAccountDeleted && (
        <AccountDeletion onAccountDeleted={onAccountDeleted} />
      )}
    </div>
  );
};

export default UserPreferencesForm; 