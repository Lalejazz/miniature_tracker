import React, { useState, useEffect } from 'react';
import { 
  PlayerSearchRequest, 
  PlayerSearchResult, 
  GameType,
  GAME_TYPE_LABELS,
  Game,
  DayOfWeek,
  TimeOfDay,
  HostingPreference,
  DAY_OF_WEEK_LABELS,
  TIME_OF_DAY_LABELS,
  HOSTING_PREFERENCE_LABELS
} from '../types';
import { playerApi } from '../services/api';

interface PlayerSearchProps {
  userHasPreferences: boolean;
}

const PlayerSearch: React.FC<PlayerSearchProps> = ({ userHasPreferences }) => {
  const [availableGames, setAvailableGames] = useState<Game[]>([]);
  const [gamesLoading, setGamesLoading] = useState(true);
  const [searchRequest, setSearchRequest] = useState<PlayerSearchRequest>({
    games: [],
    game_type: undefined,
    max_distance_km: 50,
    availability_days: [],
    availability_times: [],
    hosting_preferences: []
  });
  const [searchResults, setSearchResults] = useState<PlayerSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

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

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const results = await playerApi.searchPlayers(searchRequest);
      console.log('Player search results:', results);
      setSearchResults(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search players');
      setSearchResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGameToggle = (gameId: string) => {
    setSearchRequest(prev => ({
      ...prev,
      games: prev.games?.includes(gameId)
        ? prev.games.filter(id => id !== gameId)
        : [...(prev.games || []), gameId]
    }));
  };

  const handleGameTypeToggle = (gameType: GameType) => {
    setSearchRequest(prev => ({
      ...prev,
      game_type: prev.game_type === gameType ? undefined : gameType
    }));
  };

  const handleAvailabilityDayToggle = (day: DayOfWeek) => {
    setSearchRequest(prev => ({
      ...prev,
      availability_days: prev.availability_days?.includes(day)
        ? prev.availability_days.filter(d => d !== day)
        : [...(prev.availability_days || []), day]
    }));
  };

  const handleAvailabilityTimeToggle = (time: TimeOfDay) => {
    setSearchRequest(prev => ({
      ...prev,
      availability_times: prev.availability_times?.includes(time)
        ? prev.availability_times.filter(t => t !== time)
        : [...(prev.availability_times || []), time]
    }));
  };

  const handleHostingPreferenceToggle = (preference: HostingPreference) => {
    setSearchRequest(prev => ({
      ...prev,
      hosting_preferences: prev.hosting_preferences?.includes(preference)
        ? prev.hosting_preferences.filter(p => p !== preference)
        : [...(prev.hosting_preferences || []), preference]
    }));
  };

  if (!userHasPreferences) {
    return (
      <div className="player-search no-preferences">
        <h2>Find Players Near You</h2>
        <p>You need to set up your gaming preferences first before you can search for other players.</p>
        <p>Please go to your preferences and add your location, games you play, and other details.</p>
      </div>
    );
  }

  return (
    <div className="player-search">
      <h2>Find Players Near You</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSearch} className="search-form">
        <div className="search-filters">
          <div className="form-group">
            <label>Distance (km)</label>
            <input
              type="range"
              min="5"
              max="500"
              step="5"
              value={searchRequest.max_distance_km}
              onChange={(e) => setSearchRequest(prev => ({ 
                ...prev, 
                max_distance_km: parseInt(e.target.value) 
              }))}
            />
            <span className="distance-value">{searchRequest.max_distance_km} km</span>
          </div>

          <div className="form-group">
            <label>Filter by Games (optional)</label>
            {gamesLoading ? (
              <div className="loading-message">Loading available games...</div>
            ) : (
              <div className="games-filter">
                {availableGames.map(game => (
                  <label key={game.id} className="game-checkbox">
                    <input
                      type="checkbox"
                      checked={searchRequest.games?.includes(game.id) || false}
                      onChange={() => handleGameToggle(game.id)}
                    />
                    <span>{game.name}</span>
                  </label>
                ))}
              </div>
            )}
          </div>

          <div className="form-group">
            <label>Filter by Game Type (optional)</label>
            <div className="game-types-filter">
              {(Object.keys(GAME_TYPE_LABELS) as GameType[]).map(gameType => (
                <label key={gameType} className="game-type-checkbox">
                  <input
                    type="radio"
                    name="game_type"
                    checked={searchRequest.game_type === gameType}
                    onChange={() => handleGameTypeToggle(gameType)}
                  />
                  <span>{GAME_TYPE_LABELS[gameType]}</span>
                </label>
              ))}
              <label className="game-type-checkbox">
                <input
                  type="radio"
                  name="game_type"
                  checked={searchRequest.game_type === undefined}
                  onChange={() => setSearchRequest(prev => ({ ...prev, game_type: undefined }))}
                />
                <span>Any</span>
              </label>
            </div>
          </div>

          <div className="form-group">
            <label>Filter by Availability Days (optional)</label>
            <div className="availability-days-filter">
              {(Object.keys(DAY_OF_WEEK_LABELS) as DayOfWeek[]).map(day => (
                <label key={day} className="availability-day-checkbox">
                  <input
                    type="checkbox"
                    checked={searchRequest.availability_days?.includes(day) || false}
                    onChange={() => handleAvailabilityDayToggle(day)}
                  />
                  <span>{DAY_OF_WEEK_LABELS[day]}</span>
                </label>
              ))}
            </div>
            <small>Find players available on these days</small>
          </div>

          <div className="form-group">
            <label>Filter by Availability Times (optional)</label>
            <div className="availability-times-filter">
              {(Object.keys(TIME_OF_DAY_LABELS) as TimeOfDay[]).map(time => (
                <label key={time} className="availability-time-checkbox">
                  <input
                    type="checkbox"
                    checked={searchRequest.availability_times?.includes(time) || false}
                    onChange={() => handleAvailabilityTimeToggle(time)}
                  />
                  <span>{TIME_OF_DAY_LABELS[time]}</span>
                </label>
              ))}
            </div>
            <small>Find players available at these times</small>
          </div>

          <div className="form-group">
            <label>Filter by Hosting Preferences (optional)</label>
            <div className="hosting-preferences-filter">
              {(Object.keys(HOSTING_PREFERENCE_LABELS) as HostingPreference[]).map(preference => (
                <label key={preference} className="hosting-preference-checkbox">
                  <input
                    type="checkbox"
                    checked={searchRequest.hosting_preferences?.includes(preference) || false}
                    onChange={() => handleHostingPreferenceToggle(preference)}
                  />
                  <span>{HOSTING_PREFERENCE_LABELS[preference]}</span>
                </label>
              ))}
            </div>
            <small>Find players with these hosting preferences</small>
          </div>
        </div>

        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Searching...' : 'Search Players'}
        </button>
      </form>

      {hasSearched && (
        <div className="search-results">
          <h3>
            {searchResults.length === 0 
              ? 'No players found' 
              : `Found ${searchResults.length} player${searchResults.length === 1 ? '' : 's'}`
            }
          </h3>
          
          {searchResults.length === 0 && (
            <p>Try expanding your search distance or removing some filters.</p>
          )}

          <div className="players-list">
            {searchResults.map(player => (
              <div key={player.user_id} className="player-card">
                <div className="player-info">
                  <h4>{player.username}</h4>
                  <p className="distance">{player.distance_km.toFixed(1)} km away</p>
                  <p className="location">{player.location}</p>
                  <p className="game-type">Prefers: {GAME_TYPE_LABELS[player.game_type]}</p>
                  
                  <div className="player-games">
                    <strong>Games:</strong>
                    <div className="games-list">
                      {player.games.map(game => (
                        <span key={game.id} className="game-tag">{game.name}</span>
                      ))}
                    </div>
                  </div>
                  
                  {player.availability && player.availability.length > 0 && (
                    <div className="player-availability">
                      <strong>Available:</strong>
                      <div className="availability-summary">
                        {player.availability.map(slot => (
                          <span key={slot.day} className="availability-slot">
                            {DAY_OF_WEEK_LABELS[slot.day]}: {slot.times.map(time => TIME_OF_DAY_LABELS[time]).join(', ')}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {player.hosting && player.hosting.preferences.length > 0 && (
                    <div className="player-hosting">
                      <strong>Hosting:</strong>
                      <div className="hosting-summary">
                        {player.hosting.preferences.map(pref => (
                          <span key={pref} className="hosting-tag">{HOSTING_PREFERENCE_LABELS[pref]}</span>
                        ))}
                        {player.hosting.preferences.includes(HostingPreference.CAN_HOST) && (
                          <div className="hosting-details">
                            {player.hosting.has_gaming_space && <span className="hosting-detail">Gaming space</span>}
                            {player.hosting.has_boards_scenery && <span className="hosting-detail">Boards & scenery</span>}
                            {player.hosting.max_players && <span className="hosting-detail">Max {player.hosting.max_players} players</span>}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {player.bio && (
                    <p className="bio">{player.bio}</p>
                  )}
                  
                  {player.email && (
                    <p className="contact">
                      <strong>Contact:</strong> 
                      <a href={`mailto:${player.email}`}>{player.email}</a>
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PlayerSearch; 