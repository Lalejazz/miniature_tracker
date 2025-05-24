import React, { useState, useEffect } from 'react';
import { 
  Game, 
  GameType, 
  PlayerSearchRequest, 
  PlayerSearchResult,
  GAME_TYPE_LABELS
} from '../types';
import { playerApi } from '../services/api';

interface PlayerSearchProps {
  userHasPreferences: boolean;
}

const PlayerSearch: React.FC<PlayerSearchProps> = ({ userHasPreferences }) => {
  const [games, setGames] = useState<Game[]>([]);
  const [searchRequest, setSearchRequest] = useState<PlayerSearchRequest>({
    games: [],
    game_type: undefined,
    max_distance_km: 50
  });
  const [searchResults, setSearchResults] = useState<PlayerSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingGames, setLoadingGames] = useState(true);
  const [hasSearched, setHasSearched] = useState(false);

  // Load available games on component mount
  useEffect(() => {
    const loadGames = async () => {
      try {
        const availableGames = await playerApi.getGames();
        setGames(availableGames);
      } catch (err) {
        console.error('Failed to load games:', err);
        setError('Failed to load available games');
      } finally {
        setLoadingGames(false);
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

  if (!userHasPreferences) {
    return (
      <div className="player-search no-preferences">
        <h2>Find Players Near You</h2>
        <p>You need to set up your gaming preferences first before you can search for other players.</p>
        <p>Please go to your preferences and add your postcode, games you play, and other details.</p>
      </div>
    );
  }

  if (loadingGames) {
    return <div className="loading">Loading search options...</div>;
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
            <div className="games-filter">
              {games.map(game => (
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
                <span>Any Preference</span>
              </label>
            </div>
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
                <div className="player-header">
                  <h4>{player.username}</h4>
                  <span className="distance">{player.distance_km} km away</span>
                </div>
                
                <div className="player-details">
                  <div className="games">
                    <strong>Games:</strong>
                    <div className="game-tags">
                      {player.games.map(game => (
                        <span key={game.id} className="game-tag">{game.name}</span>
                      ))}
                    </div>
                  </div>
                  <div className="game-type">
                    <strong>Game Type:</strong>
                    <span className={`game-type-tag ${player.game_type}`}>
                      {GAME_TYPE_LABELS[player.game_type]}
                    </span>
                  </div>
                  {player.email && (
                    <div className="contact">
                      <strong>Contact:</strong>
                      <a href={`mailto:${player.email}`} className="email-link">
                        {player.email}
                      </a>
                    </div>
                  )}
                  {player.bio && (
                    <div className="bio">
                      <strong>Bio:</strong>
                      <p>{player.bio}</p>
                    </div>
                  )}
                  <div className="player-location">
                    <strong>Area:</strong> {player.postcode}
                  </div>
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