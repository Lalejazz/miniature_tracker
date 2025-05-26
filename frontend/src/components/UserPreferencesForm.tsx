import React, { useState } from 'react';
import { 
  GameSystem,
  GAME_SYSTEM_LABELS,
  GameType, 
  UserPreferences, 
  UserPreferencesCreate,
  DayOfWeek,
  TimeOfDay,
  HostingPreference,
  HostingDetails,
  DAY_OF_WEEK_LABELS,
  TIME_OF_DAY_LABELS,
  HOSTING_PREFERENCE_LABELS,
  HOSTING_PREFERENCE_DESCRIPTIONS,
  Theme
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

// Create a list of games based on the GameSystem enum
const AVAILABLE_GAMES = Object.entries(GameSystem).map(([key, value]) => ({
  id: value,
  name: GAME_SYSTEM_LABELS[value],
  description: getGameDescription(value),
  is_active: true
}));

function getGameDescription(gameSystem: GameSystem): string {
  const descriptions: Record<GameSystem, string> = {
    [GameSystem.WARHAMMER_40K]: "The iconic grimdark sci-fi wargame",
    [GameSystem.AGE_OF_SIGMAR]: "Fantasy battles in the Mortal Realms",
    [GameSystem.WARHAMMER_THE_OLD_WORLD]: "Classic fantasy battles in the Old World",
    [GameSystem.HORUS_HERESY]: "The galaxy-spanning civil war in the 31st millennium",
    [GameSystem.KILL_TEAM]: "Small-scale skirmish battles in the 40K universe",
    [GameSystem.WARCRY]: "Fast-paced skirmish combat in Age of Sigmar",
    [GameSystem.WARHAMMER_UNDERWORLDS]: "Competitive deck-based skirmish game",
    [GameSystem.ADEPTUS_TITANICUS]: "Epic-scale Titan warfare",
    [GameSystem.NECROMUNDA]: "Gang warfare in the underhive",
    [GameSystem.BLOOD_BOWL]: "Fantasy football with violence",
    [GameSystem.MIDDLE_EARTH]: "Battle in Tolkien's world",
    [GameSystem.BOLT_ACTION]: "World War II historical wargaming",
    [GameSystem.FLAMES_OF_WAR]: "World War II tank combat",
    [GameSystem.SAGA]: "Dark Age skirmish gaming",
    [GameSystem.KINGS_OF_WAR]: "Mass fantasy battles",
    [GameSystem.INFINITY]: "Sci-fi skirmish with anime aesthetics",
    [GameSystem.MALIFAUX]: "Gothic horror skirmish game",
    [GameSystem.WARMACHINE_HORDES]: "Steampunk fantasy battles",
    [GameSystem.X_WING]: "Star Wars space combat",
    [GameSystem.STAR_WARS_LEGION]: "Ground battles in the Star Wars universe",
    [GameSystem.BATTLETECH]: "Giant robot combat",
    [GameSystem.DROPZONE_COMMANDER]: "10mm sci-fi warfare",
    [GameSystem.GUILD_BALL]: "Fantasy sports meets skirmish gaming",
    [GameSystem.DUNGEONS_AND_DRAGONS]: "Dungeons & Dragons and RPG miniatures",
    [GameSystem.PATHFINDER]: "Fantasy RPG miniatures",
    [GameSystem.FROSTGRAVE]: "Wizard warband skirmish",
    [GameSystem.MORDHEIM]: "Skirmish in the City of the Damned",
    [GameSystem.GASLANDS]: "Post-apocalyptic vehicular combat",
    [GameSystem.ZOMBICIDE]: "Cooperative zombie survival",
    [GameSystem.TRENCH_CRUSADE]: "Grimdark alternate history warfare",
    [GameSystem.ART_DE_LA_GUERRE]: "Ancient and medieval historical wargaming",
    [GameSystem.OTHER]: "Custom or unlisted game systems"
  };
  return descriptions[gameSystem] || "";
}

const UserPreferencesForm: React.FC<UserPreferencesFormProps> = ({ 
  existingPreferences, 
  onSave,
  onCancel,
  onAccountDeleted
}) => {
  const [formData, setFormData] = useState<UserPreferencesCreate>({
    games: existingPreferences?.games || [],
    location: existingPreferences?.location || '',
    game_type: existingPreferences?.game_type || 'competitive' as GameType,
    bio: existingPreferences?.bio || '',
    show_email: existingPreferences?.show_email || false,
    availability: existingPreferences?.availability || [],
    hosting: existingPreferences?.hosting || {
      preferences: [],
      has_gaming_space: false,
      has_boards_scenery: false,
      max_players: undefined,
      notes: ''
    },
    theme: existingPreferences?.theme || Theme.BLUE_GRADIENT
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  const handleAvailabilityToggle = (day: DayOfWeek, time: TimeOfDay) => {
    setFormData(prev => {
      const availability = [...(prev.availability || [])];
      const dayIndex = availability.findIndex(slot => slot.day === day);
      
      if (dayIndex === -1) {
        // Day doesn't exist, create new slot
        availability.push({ day, times: [time] });
      } else {
        // Day exists, toggle time
        const daySlot = availability[dayIndex];
        if (daySlot.times.includes(time)) {
          // Remove time
          daySlot.times = daySlot.times.filter(t => t !== time);
          // Remove day if no times left
          if (daySlot.times.length === 0) {
            availability.splice(dayIndex, 1);
          }
        } else {
          // Add time
          daySlot.times.push(time);
        }
      }
      
      return { ...prev, availability };
    });
  };

  const isTimeSelected = (day: DayOfWeek, time: TimeOfDay): boolean => {
    const daySlot = formData.availability?.find(slot => slot.day === day);
    return daySlot?.times.includes(time) || false;
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

  const handleThemeChange = (theme: Theme) => {
    setFormData(prev => ({
      ...prev,
      theme
    }));
  };

  const isFormValid = formData.games.length > 0 && formData.location.trim().length > 0;

  return (
    <div className="preferences-form">
      <h2>{existingPreferences ? 'Update' : 'Set'} Your Gaming Preferences</h2>
      
      {error && <div className="error-message">{error}</div>}
      
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
          <div className="games-grid">
            {AVAILABLE_GAMES.map(game => (
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

        <ThemeSelector
          selectedTheme={formData.theme || Theme.BLUE_GRADIENT}
          onThemeChange={handleThemeChange}
        />

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

        <div className="form-group">
          <label>When are you available to play?</label>
          <div className="availability-grid">
            {Object.values(DayOfWeek).map(day => (
              <div key={day} className="day-availability">
                <h4>{DAY_OF_WEEK_LABELS[day]}</h4>
                <div className="time-slots">
                  {Object.values(TimeOfDay).map(time => (
                    <label key={`${day}-${time}`} className="time-slot-checkbox">
                      <input
                        type="checkbox"
                        checked={isTimeSelected(day, time)}
                        onChange={() => handleAvailabilityToggle(day, time)}
                      />
                      <span>{TIME_OF_DAY_LABELS[time]}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <small>Select the days and times when you're typically available to play games</small>
        </div>

        <div className="form-group">
          <label>Gaming Location Preferences</label>
          <div className="hosting-preferences">
            {Object.values(HostingPreference).map(preference => (
              <label key={preference} className="hosting-preference-checkbox">
                <input
                  type="checkbox"
                  checked={formData.hosting!.preferences.includes(preference)}
                  onChange={() => handleHostingPreferenceToggle(preference)}
                />
                <div className="preference-content">
                  <span className="preference-name">{HOSTING_PREFERENCE_LABELS[preference]}</span>
                  <small className="preference-description">{HOSTING_PREFERENCE_DESCRIPTIONS[preference]}</small>
                </div>
              </label>
            ))}
          </div>
          <small>Select all options that apply to your gaming preferences</small>
        </div>

        {formData.hosting!.preferences.includes(HostingPreference.CAN_HOST) && (
          <div className="form-group hosting-details">
            <label>Hosting Details</label>
            <div className="hosting-details-grid">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={formData.hosting!.has_gaming_space || false}
                  onChange={(e) => handleHostingDetailChange('has_gaming_space', e.target.checked)}
                />
                <span>I have a dedicated gaming space</span>
              </label>
              
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={formData.hosting!.has_boards_scenery || false}
                  onChange={(e) => handleHostingDetailChange('has_boards_scenery', e.target.checked)}
                />
                <span>I have gaming boards and scenery</span>
              </label>
              
              <div className="max-players-input">
                <label htmlFor="max_players">Maximum players I can host</label>
                <input
                  type="number"
                  id="max_players"
                  min="2"
                  max="12"
                  value={formData.hosting!.max_players || ''}
                  onChange={(e) => handleHostingDetailChange('max_players', e.target.value ? parseInt(e.target.value) : undefined)}
                  placeholder="e.g., 4"
                />
              </div>
              
              <div className="hosting-notes">
                <label htmlFor="hosting_notes">Additional hosting notes</label>
                <textarea
                  id="hosting_notes"
                  value={formData.hosting!.notes || ''}
                  onChange={(e) => handleHostingDetailChange('notes', e.target.value)}
                  placeholder="e.g., 'Large dining table, parking available, pets friendly'"
                  maxLength={200}
                  rows={3}
                />
                <small>{(formData.hosting!.notes || '').length}/200 characters</small>
              </div>
            </div>
          </div>
        )}

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