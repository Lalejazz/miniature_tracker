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

export enum GameSystem {
  WARHAMMER_40K = "warhammer_40k",
  AGE_OF_SIGMAR = "age_of_sigmar",
  DUNGEONS_AND_DRAGONS = "dungeons_and_dragons",
  OTHER = "other"
}

export enum UnitType {
  INFANTRY = "infantry",
  CAVALRY = "cavalry",
  VEHICLE = "vehicle",
  MONSTER = "monster",
  CHARACTER = "character",
  TERRAIN = "terrain",
  OTHER = "other"
}

export enum BaseDimension {
  ROUND_25MM = "25mm_round",
  ROUND_32MM = "32mm_round",
  ROUND_40MM = "40mm_round",
  ROUND_50MM = "50mm_round",
  ROUND_60MM = "60mm_round",
  ROUND_80MM = "80mm_round",
  ROUND_90MM = "90mm_round",
  ROUND_100MM = "100mm_round",
  ROUND_120MM = "120mm_round",
  ROUND_160MM = "160mm_round",
  OVAL_60X35MM = "60x35mm_oval",
  OVAL_75X42MM = "75x42mm_oval",
  OVAL_90X52MM = "90x52mm_oval",
  OVAL_105X70MM = "105x70mm_oval",
  OVAL_120X92MM = "120x92mm_oval",
  SQUARE_20MM = "20mm_square",
  SQUARE_25MM = "25mm_square",
  SQUARE_40MM = "40mm_square",
  SQUARE_50MM = "50mm_square",
  RECTANGULAR_60X100MM = "60x100mm_rectangular",
  RECTANGULAR_70X105MM = "70x105mm_rectangular",
  RECTANGULAR_90X120MM = "90x120mm_rectangular",
  CUSTOM = "custom"
}

// Game System specific factions
export const GAME_SYSTEM_FACTIONS = {
  [GameSystem.WARHAMMER_40K]: [
    "Space Marines", "Imperial Guard", "Adeptus Mechanicus", "Sisters of Battle",
    "Imperial Knights", "Custodes", "Grey Knights", "Deathwatch",
    "Chaos Space Marines", "Death Guard", "Thousand Sons", "World Eaters",
    "Chaos Daemons", "Chaos Knights",
    "Aeldari", "Drukhari", "Harlequins", "Ynnari",
    "Orks", "Tyranids", "Genestealer Cults", "Necrons", "T'au Empire",
    "Other"
  ],
  [GameSystem.AGE_OF_SIGMAR]: [
    "Stormcast Eternals", "Cities of Sigmar", "Fyreslayers", "Kharadron Overlords",
    "Sylvaneth", "Daughters of Khaine", "Idoneth Deepkin", "Lumineth Realm-lords",
    "Seraphon", "Beasts of Chaos", "Blades of Khorne", "Disciples of Tzeentch",
    "Hedonites of Slaanesh", "Maggotkin of Nurgle", "Skaven", "Slaves to Darkness",
    "Flesh-eater Courts", "Legions of Nagash", "Nighthaunt", "Ossiarch Bonereapers",
    "Soulblight Gravelords", "Gloomspite Gitz", "Ironjawz", "Bonesplitterz",
    "Sons of Behemat", "Ogor Mawtribes", "Other"
  ],
  [GameSystem.DUNGEONS_AND_DRAGONS]: [
    "Player Characters", "NPCs", "Undead", "Fiends", "Celestials", "Elementals",
    "Fey", "Giants", "Humanoids", "Monstrosities", "Oozes", "Plants",
    "Beasts", "Dragons", "Constructs", "Aberrations", "Other"
  ],
  [GameSystem.OTHER]: ["Custom"]
};

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

export interface UnitBase {
  name: string;
  game_system: GameSystem;
  faction: string;
  unit_type: UnitType;
  quantity: number;
  base_dimension?: BaseDimension;
  custom_base_size?: string;
  cost?: number;
  status: PaintingStatus;
  notes?: string;
}

export interface UnitCreate extends UnitBase {}

export interface UnitUpdate {
  name?: string;
  game_system?: GameSystem;
  faction?: string;
  unit_type?: UnitType;
  quantity?: number;
  base_dimension?: BaseDimension;
  custom_base_size?: string;
  cost?: number;
  status?: PaintingStatus;
  notes?: string;
}

export interface Unit extends UnitBase {
  id: string;
  user_id: string;
  status_history: StatusLogEntry[];
  created_at: string;
  updated_at: string;
}

// Keep backward compatibility (deprecated)
export interface MiniatureBase extends UnitBase {
  model_type: string; // maps to unit_type for backward compatibility
}

export interface MiniatureCreate extends UnitCreate {}

export interface MiniatureUpdate extends UnitUpdate {}

export interface Miniature extends Unit {}

// Collection Statistics
export interface CollectionStatistics {
  total_units: number;
  total_models: number;
  total_cost?: number;
  status_breakdown: Record<PaintingStatus, number>;
  game_system_breakdown: Record<GameSystem, number>;
  faction_breakdown: Record<string, number>;
  unit_type_breakdown: Record<UnitType, number>;
  completion_percentage: number;
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
    description: "Unit you want to purchase",
    color: "#e0e0e0",
    textColor: "#000"
  },
  [PaintingStatus.PURCHASED]: {
    label: "Purchased",
    description: "Unit has been bought but not assembled",
    color: "#ff9800",
    textColor: "#fff"
  },
  [PaintingStatus.ASSEMBLED]: {
    label: "Assembled",
    description: "Unit is assembled and ready for priming",
    color: "#2196f3",
    textColor: "#fff"
  },
  [PaintingStatus.PRIMED]: {
    label: "Primed", 
    description: "Unit has been primed and ready for painting",
    color: "#9c27b0",
    textColor: "#fff"
  },
  [PaintingStatus.GAME_READY]: {
    label: "Game Ready",
    description: "Unit is painted to tabletop standard",
    color: "#4caf50",
    textColor: "#fff"
  },
  [PaintingStatus.PARADE_READY]: {
    label: "Parade Ready",
    description: "Unit is painted to display quality",
    color: "#ffd700",
    textColor: "#000"
  }
};

// Game System labels
export const GAME_SYSTEM_LABELS = {
  [GameSystem.WARHAMMER_40K]: "Warhammer 40,000",
  [GameSystem.AGE_OF_SIGMAR]: "Age of Sigmar",
  [GameSystem.DUNGEONS_AND_DRAGONS]: "D&D / RPG",
  [GameSystem.OTHER]: "Other Game System"
};

// Unit Type labels
export const UNIT_TYPE_LABELS = {
  [UnitType.INFANTRY]: "Infantry",
  [UnitType.CAVALRY]: "Cavalry",
  [UnitType.VEHICLE]: "Vehicle",
  [UnitType.MONSTER]: "Monster",
  [UnitType.CHARACTER]: "Character",
  [UnitType.TERRAIN]: "Terrain",
  [UnitType.OTHER]: "Other"
};

// Base Dimension labels
export const BASE_DIMENSION_LABELS = {
  [BaseDimension.ROUND_25MM]: "25mm Round",
  [BaseDimension.ROUND_32MM]: "32mm Round",
  [BaseDimension.ROUND_40MM]: "40mm Round",
  [BaseDimension.ROUND_50MM]: "50mm Round",
  [BaseDimension.ROUND_60MM]: "60mm Round",
  [BaseDimension.ROUND_80MM]: "80mm Round",
  [BaseDimension.ROUND_90MM]: "90mm Round",
  [BaseDimension.ROUND_100MM]: "100mm Round",
  [BaseDimension.ROUND_120MM]: "120mm Round",
  [BaseDimension.ROUND_160MM]: "160mm Round",
  [BaseDimension.OVAL_60X35MM]: "60x35mm Oval",
  [BaseDimension.OVAL_75X42MM]: "75x42mm Oval",
  [BaseDimension.OVAL_90X52MM]: "90x52mm Oval",
  [BaseDimension.OVAL_105X70MM]: "105x70mm Oval",
  [BaseDimension.OVAL_120X92MM]: "120x92mm Oval",
  [BaseDimension.SQUARE_20MM]: "20mm Square",
  [BaseDimension.SQUARE_25MM]: "25mm Square",
  [BaseDimension.SQUARE_40MM]: "40mm Square",
  [BaseDimension.SQUARE_50MM]: "50mm Square",
  [BaseDimension.RECTANGULAR_60X100MM]: "60x100mm Rectangular",
  [BaseDimension.RECTANGULAR_70X105MM]: "70x105mm Rectangular",
  [BaseDimension.RECTANGULAR_90X120MM]: "90x120mm Rectangular",
  [BaseDimension.CUSTOM]: "Custom Size"
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