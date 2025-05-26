import React, { useState } from 'react';
import { 
  GameSystem,
  GAME_SYSTEM_LABELS,
  GameType, 
  PlayerSearchRequest, 
  PlayerSearchResult,
  GAME_TYPE_LABELS
} from '../types';
import { playerApi } from '../services/api';

interface PlayerSearchProps {
  userHasPreferences: boolean;
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
    [GameSystem.OTHER]: "Custom or unlisted game systems"
  };
  return descriptions[gameSystem] || "";
}

const PlayerSearch: React.FC<PlayerSearchProps> = ({ userHasPreferences }) => {
  const [searchRequest, setSearchRequest] = useState<PlayerSearchRequest>({
    games: [],
    game_type: undefined,
    max_distance_km: 50
  });
  const [searchResults, setSearchResults] = useState<PlayerSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

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
            <div className="games-filter">
              {AVAILABLE_GAMES.map(game => (
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
                      {Array.isArray(player.games) ? (
                        player.games.map((game, index) => {
                          // Handle both string game IDs and game objects
                          const gameId = typeof game === 'string' ? game : game.id;
                          const gameName = GAME_SYSTEM_LABELS[gameId as GameSystem] || 
                                         (typeof game === 'object' ? game.name : gameId) || 
                                         'Unknown Game';
                          
                          return (
                            <span key={gameId || index} className="game-tag">
                              {gameName}
                            </span>
                          );
                        })
                      ) : (
                        <span className="game-tag">No games listed</span>
                      )}
                    </div>
                  </div>
                  <div className="game-type">
                    <strong>Game Type:</strong>
                    <span className={`game-type-tag ${player.game_type}`}>
                      {GAME_TYPE_LABELS[player.game_type] || player.game_type}
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
                    <strong>Area:</strong> {player.location}
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