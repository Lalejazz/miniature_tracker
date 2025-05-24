/**
 * TypeScript interfaces for miniature tracker data models
 */

export enum PaintingStatus {
  WANT_TO_BUY = "want_to_buy",
  PURCHASED = "purchased", 
  ASSEMBLED = "assembled",
  PRIMED = "primed",
  GAME_READY = "game_ready",
  PARADE_READY = "parade_ready"
}

export interface StatusLogEntry {
  id: string;
  from_status?: PaintingStatus;
  to_status: PaintingStatus;
  date: string;
  notes?: string;
  is_manual: boolean;
  created_at: string;
}

export interface StatusLogEntryCreate {
  from_status?: PaintingStatus;
  to_status: PaintingStatus;
  date: string;
  notes?: string;
  is_manual?: boolean;
}

export interface StatusLogEntryUpdate {
  date?: string;
  notes?: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordReset {
  token: string;
  new_password: string;
}

export interface MiniatureBase {
  name: string;
  faction: string;
  model_type: string;
  status: PaintingStatus;
  notes?: string;
}

export interface MiniatureCreate extends MiniatureBase {}

export interface MiniatureUpdate {
  name?: string;
  faction?: string;
  model_type?: string;
  status?: PaintingStatus;
  notes?: string;
}

export interface Miniature extends MiniatureBase {
  id: string;
  user_id: string;
  status_history: StatusLogEntry[];
  created_at: string;
  updated_at: string;
}

// User management types
export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  username: string;
  email: string;
  full_name?: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

// Status information for UI
export const STATUS_INFO = {
  [PaintingStatus.WANT_TO_BUY]: {
    label: "Want to Buy",
    description: "Miniature you want to purchase",
    color: "#e0e0e0",
    textColor: "#000"
  },
  [PaintingStatus.PURCHASED]: {
    label: "Purchased",
    description: "Miniature has been bought but not assembled",
    color: "#ff9800",
    textColor: "#fff"
  },
  [PaintingStatus.ASSEMBLED]: {
    label: "Assembled",
    description: "Miniature is assembled and ready for priming",
    color: "#2196f3",
    textColor: "#fff"
  },
  [PaintingStatus.PRIMED]: {
    label: "Primed", 
    description: "Miniature has been primed and ready for painting",
    color: "#9c27b0",
    textColor: "#fff"
  },
  [PaintingStatus.GAME_READY]: {
    label: "Game Ready",
    description: "Miniature is painted to tabletop standard",
    color: "#4caf50",
    textColor: "#fff"
  },
  [PaintingStatus.PARADE_READY]: {
    label: "Parade Ready",
    description: "Miniature is painted to display quality",
    color: "#ffd700",
    textColor: "#000"
  }
};

// Changelog types
export interface ChangelogEntry {
  id: string;
  date: string;
  version: string;
  title: string;
  description: string;
  type: 'feature' | 'improvement' | 'bugfix' | 'security';
  items: string[];
}

// Player Discovery Types

export type GameType = "competitive" | "narrative";

export interface Game {
  id: string;
  name: string;
  description?: string;
  is_active: boolean;
}

export interface UserPreferencesCreate {
  games: string[];
  location: string;
  game_type: GameType;
  bio?: string;
  show_email?: boolean;
}

export interface UserPreferencesUpdate {
  games?: string[];
  location?: string;
  game_type?: GameType;
  bio?: string;
  show_email?: boolean;
}

export interface UserPreferences {
  id: string;
  user_id: string;
  games: string[];
  location: string;
  game_type: GameType;
  bio?: string;
  show_email: boolean;
  latitude?: number;
  longitude?: number;
  created_at: string;
  updated_at: string;
}

export interface PlayerSearchRequest {
  games?: string[];
  game_type?: GameType;
  max_distance_km: number;
}

export interface PlayerSearchResult {
  user_id: string;
  username: string;
  email?: string;
  games: Game[];
  game_type: GameType;
  bio?: string;
  distance_km: number;
  location: string;
}

export const GAME_TYPE_LABELS = {
  competitive: "Competitive",
  narrative: "Narrative"
} as const; 