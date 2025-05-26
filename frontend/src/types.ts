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
  WARHAMMER_THE_OLD_WORLD = "warhammer_the_old_world",
  HORUS_HERESY = "horus_heresy",
  KILL_TEAM = "kill_team",
  WARCRY = "warcry",
  WARHAMMER_UNDERWORLDS = "warhammer_underworlds",
  ADEPTUS_TITANICUS = "adeptus_titanicus",
  NECROMUNDA = "necromunda",
  BLOOD_BOWL = "blood_bowl",
  MIDDLE_EARTH = "middle_earth",
  BOLT_ACTION = "bolt_action",
  FLAMES_OF_WAR = "flames_of_war",
  SAGA = "saga",
  KINGS_OF_WAR = "kings_of_war",
  INFINITY = "infinity",
  MALIFAUX = "malifaux",
  WARMACHINE_HORDES = "warmachine_hordes",
  X_WING = "x_wing",
  STAR_WARS_LEGION = "star_wars_legion",
  BATTLETECH = "battletech",
  DROPZONE_COMMANDER = "dropzone_commander",
  GUILD_BALL = "guild_ball",
  DUNGEONS_AND_DRAGONS = "dungeons_and_dragons",
  PATHFINDER = "pathfinder",
  FROSTGRAVE = "frostgrave",
  MORDHEIM = "mordheim",
  GASLANDS = "gaslands",
  ZOMBICIDE = "zombicide",
  TRENCH_CRUSADE = "trench_crusade",
  ART_DE_LA_GUERRE = "art_de_la_guerre",
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
  [GameSystem.WARHAMMER_THE_OLD_WORLD]: [
    "Empire", "Bretonnia", "High Elves", "Wood Elves", "Dark Elves", "Dwarfs",
    "Warriors of Chaos", "Daemons of Chaos", "Beastmen", "Orcs & Goblins",
    "Skaven", "Vampire Counts", "Tomb Kings", "Lizardmen", "Ogre Kingdoms",
    "Chaos Dwarfs", "Other"
  ],
  [GameSystem.HORUS_HERESY]: [
    "Dark Angels", "Emperor's Children", "Iron Warriors", "White Scars", "Space Wolves",
    "Imperial Fists", "Night Lords", "Blood Angels", "Iron Hands", "World Eaters",
    "Ultramarines", "Death Guard", "Thousand Sons", "Sons of Horus", "Word Bearers",
    "Salamanders", "Raven Guard", "Alpha Legion", "Imperial Army", "Mechanicum",
    "Custodes", "Sisters of Silence", "Blackshields", "Other"
  ],
  [GameSystem.WARHAMMER_UNDERWORLDS]: [
    "Steelheart's Champions", "Garrek's Reavers", "Sepulchral Guard", "Ironskull's Boyz",
    "The Chosen Axes", "Spiteclaw's Swarm", "Magore's Fiends", "The Farstriders",
    "Stormsire's Cursebreakers", "Thorns of the Briar Queen", "Eyes of the Nine",
    "Zarbag's Gitz", "Mollog's Mob", "Godsworn Hunt", "Ylthari's Guardians",
    "Thundrik's Profiteers", "Ironsoul's Condemners", "Lady Harrow's Mournflight",
    "Grashrak's Despoilers", "Skaeth's Wild Hunt", "Grymwatch", "Rippa's Snarlfangs",
    "Hrothgorn's Mantrappers", "The Wurmspat", "Morgok's Krushas", "Morgwaeth's Blade-coven",
    "The Crimson Court", "Hedkrakka's Madmob", "Kainan's Reapers", "Elathain's Soulraid",
    "Khagra's Ravagers", "The Starblood Stalkers", "Storm of Celestus", "Drepur's Wraithcreepers",
    "Blackpowder's Buccaneers", "Da Kunnin' Krew", "Hexbane's Hunters", "Tzeentch's Daemons",
    "Other"
  ],
  [GameSystem.ADEPTUS_TITANICUS]: [
    "Legio Gryphonicus", "Legio Astorum", "Legio Atarus", "Legio Crucius", "Legio Defensor",
    "Legio Fureans", "Legio Ignatum", "Legio Metalica", "Legio Mortis", "Legio Tempestus",
    "Legio Vulpa", "Legio Solaria", "Legio Vulcanum", "Legio Honorum", "Legio Lysanda",
    "Legio Magna", "Legio Osedax", "Legio Praesagius", "Legio Krytos", "Legio Audax",
    "Questor Imperialis", "Questor Mechanicus", "Questor Traitoris", "Other"
  ],
  [GameSystem.KILL_TEAM]: [
    "Space Marines", "Imperial Guard", "Adeptus Mechanicus", "Sisters of Battle",
    "Chaos Space Marines", "Death Guard", "Thousand Sons",
    "Aeldari", "Drukhari", "Harlequins",
    "Orks", "Tyranids", "Genestealer Cults", "Necrons", "T'au Empire",
    "Other"
  ],
  [GameSystem.WARCRY]: [
    "Stormcast Eternals", "Nighthaunt", "Gloomspite Gitz", "Ironjawz",
    "Slaves to Darkness", "Skaven", "Beasts of Chaos", "Flesh-eater Courts",
    "Daughters of Khaine", "Fyreslayers", "Kharadron Overlords", "Sylvaneth",
    "Other"
  ],
  [GameSystem.NECROMUNDA]: [
    "House Escher", "House Goliath", "House Van Saar", "House Orlock",
    "House Delaque", "House Cawdor", "Enforcers", "Corpse Grinder Cult",
    "Chaos Cult", "Genestealer Cult", "Other"
  ],
  [GameSystem.BLOOD_BOWL]: [
    "Human", "Orc", "Dwarf", "Elf", "Skaven", "Chaos", "Undead", "Halfling",
    "Amazon", "Lizardmen", "Norse", "Vampire", "Nurgle", "Khorne", "Other"
  ],
  [GameSystem.MIDDLE_EARTH]: [
    "Gondor", "Rohan", "The Shire", "Rivendell", "Lothlórien", "The White Council",
    "Mordor", "Isengard", "Haradrim", "Easterlings", "Corsairs of Umbar",
    "The Misty Mountains", "Moria", "Angmar", "Other"
  ],
  [GameSystem.BOLT_ACTION]: [
    "US Army", "British Army", "Soviet Army", "German Army", "Japanese Army",
    "Italian Army", "French Army", "Partisans", "Resistance", "Other"
  ],
  [GameSystem.FLAMES_OF_WAR]: [
    "US Forces", "British Forces", "Soviet Forces", "German Forces",
    "Italian Forces", "Finnish Forces", "Romanian Forces", "Hungarian Forces",
    "Other"
  ],
  [GameSystem.SAGA]: [
    "Vikings", "Anglo-Danes", "Welsh", "Irish", "Scots", "Normans",
    "Anglo-Saxons", "Byzantines", "Moors", "Crusaders", "Other"
  ],
  [GameSystem.KINGS_OF_WAR]: [
    "Kingdoms of Men", "Elves", "Dwarfs", "Orcs", "Goblins", "Undead",
    "Abyssal Dwarfs", "Ogres", "Basileans", "Nightstalkers", "Other"
  ],
  [GameSystem.INFINITY]: [
    "PanOceania", "Yu Jing", "Ariadna", "Haqqislam", "Nomads", "Combined Army",
    "ALEPH", "Tohaa", "O-12", "Starco", "Other"
  ],
  [GameSystem.MALIFAUX]: [
    "Guild", "Resurrectionists", "Arcanists", "Neverborn", "Outcasts",
    "Ten Thunders", "Gremlins", "Other"
  ],
  [GameSystem.WARMACHINE_HORDES]: [
    "Cygnar", "Khador", "Protectorate of Menoth", "Cryx", "Retribution of Scyrah",
    "Convergence of Cyriss", "Crucible Guard", "Trollbloods", "Circle Orboros",
    "Legion of Everblight", "Skorne", "Grymkin", "Minions", "Other"
  ],
  [GameSystem.X_WING]: [
    "Rebel Alliance", "Galactic Empire", "Scum and Villainy", "Resistance",
    "First Order", "Galactic Republic", "Separatist Alliance", "Other"
  ],
  [GameSystem.STAR_WARS_LEGION]: [
    "Rebel Alliance", "Galactic Empire", "Galactic Republic", "Separatist Alliance",
    "Other"
  ],
  [GameSystem.BATTLETECH]: [
    "Inner Sphere", "Clan", "ComStar", "Word of Blake", "Mercenary", "Other"
  ],
  [GameSystem.DROPZONE_COMMANDER]: [
    "United Colonies of Mankind", "Post-Human Republic", "Shaltari Tribes",
    "Scourge", "Resistance", "Other"
  ],
  [GameSystem.GUILD_BALL]: [
    "Alchemists", "Blacksmiths", "Brewers", "Butchers", "Cooks", "Engineers",
    "Farmers", "Fishermen", "Hunters", "Masons", "Morticians", "Navigators",
    "Order", "Ratcatchers", "Smiths", "Union", "Other"
  ],
  [GameSystem.DUNGEONS_AND_DRAGONS]: [
    "Player Characters", "NPCs", "Undead", "Fiends", "Celestials", "Elementals",
    "Fey", "Giants", "Humanoids", "Monstrosities", "Oozes", "Plants",
    "Beasts", "Dragons", "Constructs", "Aberrations", "Other"
  ],
  [GameSystem.PATHFINDER]: [
    "Player Characters", "NPCs", "Undead", "Fiends", "Celestials", "Elementals",
    "Fey", "Giants", "Humanoids", "Monstrosities", "Oozes", "Plants",
    "Beasts", "Dragons", "Constructs", "Aberrations", "Other"
  ],
  [GameSystem.FROSTGRAVE]: [
    "Wizard Warband", "Cultists", "Undead", "Demons", "Constructs", "Animals",
    "Soldiers", "Other"
  ],
  [GameSystem.MORDHEIM]: [
    "Human Mercenaries", "Reiklanders", "Middenheimers", "Marienburgers",
    "Witch Hunters", "Sisters of Sigmar", "Undead", "Skaven", "Orcs & Goblins",
    "Possessed", "Cult of the Possessed", "Other"
  ],
  [GameSystem.GASLANDS]: [
    "Mishkin", "Rutherford", "Miyazaki", "Verney", "Idris", "Warden", "Other"
  ],
  [GameSystem.ZOMBICIDE]: [
    "Survivors", "Zombies", "Abominations", "Other"
  ],
  [GameSystem.TRENCH_CRUSADE]: [
    "Iron Sultanate", "Heretic Legions", "Court of the Seven-Headed Serpent",
    "New Antioch", "Trench Pilgrims", "Mercenaries", "Other"
  ],
  [GameSystem.ART_DE_LA_GUERRE]: [
    "Early Imperial Roman", "Late Imperial Roman", "Early Byzantine", "Late Byzantine",
    "Gallic", "Germanic", "Hun", "Sassanid Persian", "Arab Conquest", "Abbasid",
    "Fatimid Egyptian", "Ayyubid Egyptian", "Mamluk Egyptian", "Ottoman Turkish",
    "Feudal French", "Medieval English", "Medieval German", "Italian Condotta",
    "Swiss", "Burgundian Ordonnance", "Later Polish", "Lithuanian", "Teutonic Orders",
    "Medieval Russian", "Mongol Conquest", "Yuan Chinese", "Ming Chinese",
    "Samurai", "Korean", "Khmer", "Burmese", "Thai", "Vietnamese", "Timurid",
    "Safavid Persian", "Mughal Indian", "Rajput Indian", "Vijayanagar", "Other"
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

// Trend Analysis Types
export interface TrendDataPoint {
  date: string; // Date in YYYY-MM-DD format
  count: number;
  cost?: number;
}

export interface StatusTrendData {
  status: PaintingStatus;
  data_points: TrendDataPoint[];
}

export interface TrendAnalysis {
  date_range: {
    from: string;
    to: string;
  };
  purchases_over_time: TrendDataPoint[];
  spending_over_time: TrendDataPoint[];
  status_trends: StatusTrendData[];
  total_purchased: number;
  total_spent?: number;
  most_active_month?: string;
  average_monthly_purchases: number;
  average_monthly_spending?: number;
}

export interface TrendRequest {
  from_date?: string; // YYYY-MM-DD format
  to_date?: string;   // YYYY-MM-DD format
  group_by: 'day' | 'week' | 'month' | 'year';
}

// User management types
export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_email_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  username: string;
  email: string;
  full_name?: string;
  password: string;
  accept_terms: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface EmailVerificationRequest {
  email: string;
}

export interface EmailVerificationConfirm {
  token: string;
}

// Status information for UI
export const STATUS_INFO = {
  [PaintingStatus.WANT_TO_BUY]: {
    label: "Want to Buy",
    description: "Unit you want to purchase",
    color: "#e0e0e0",
    textColor: "#000",
    icon: "🛍️"
  },
  [PaintingStatus.PURCHASED]: {
    label: "Purchased",
    description: "Unit has been bought but not assembled",
    color: "#ff9800",
    textColor: "#fff",
    icon: "🛒"
  },
  [PaintingStatus.ASSEMBLED]: {
    label: "Assembled",
    description: "Unit is assembled and ready for priming",
    color: "#2196f3",
    textColor: "#fff",
    icon: "🔧"
  },
  [PaintingStatus.PRIMED]: {
    label: "Primed", 
    description: "Unit has been primed and ready for painting",
    color: "#9c27b0",
    textColor: "#fff",
    icon: "🎨"
  },
  [PaintingStatus.GAME_READY]: {
    label: "Game Ready",
    description: "Unit is painted to tabletop standard",
    color: "#4caf50",
    textColor: "#fff",
    icon: "🎲"
  },
  [PaintingStatus.PARADE_READY]: {
    label: "Parade Ready",
    description: "Unit is painted to display quality",
    color: "#ffd700",
    textColor: "#000",
    icon: "🏆"
  }
};

// Game System labels
export const GAME_SYSTEM_LABELS = {
  [GameSystem.WARHAMMER_40K]: "Warhammer 40,000",
  [GameSystem.AGE_OF_SIGMAR]: "Age of Sigmar",
  [GameSystem.WARHAMMER_THE_OLD_WORLD]: "Warhammer: The Old World",
  [GameSystem.HORUS_HERESY]: "Horus Heresy",
  [GameSystem.KILL_TEAM]: "Kill Team",
  [GameSystem.WARCRY]: "Warcry",
  [GameSystem.WARHAMMER_UNDERWORLDS]: "Warhammer Underworlds",
  [GameSystem.ADEPTUS_TITANICUS]: "Adeptus Titanicus",
  [GameSystem.NECROMUNDA]: "Necromunda",
  [GameSystem.BLOOD_BOWL]: "Blood Bowl",
  [GameSystem.MIDDLE_EARTH]: "Middle-earth SBG",
  [GameSystem.BOLT_ACTION]: "Bolt Action",
  [GameSystem.FLAMES_OF_WAR]: "Flames of War",
  [GameSystem.SAGA]: "SAGA",
  [GameSystem.KINGS_OF_WAR]: "Kings of War",
  [GameSystem.INFINITY]: "Infinity",
  [GameSystem.MALIFAUX]: "Malifaux",
  [GameSystem.WARMACHINE_HORDES]: "Warmachine/Hordes",
  [GameSystem.X_WING]: "X-Wing",
  [GameSystem.STAR_WARS_LEGION]: "Star Wars: Legion",
  [GameSystem.BATTLETECH]: "BattleTech",
  [GameSystem.DROPZONE_COMMANDER]: "Dropzone Commander",
  [GameSystem.GUILD_BALL]: "Guild Ball",
  [GameSystem.DUNGEONS_AND_DRAGONS]: "D&D / RPG",
  [GameSystem.PATHFINDER]: "Pathfinder",
  [GameSystem.FROSTGRAVE]: "Frostgrave",
  [GameSystem.MORDHEIM]: "Mordheim",
  [GameSystem.GASLANDS]: "Gaslands",
  [GameSystem.ZOMBICIDE]: "Zombicide",
  [GameSystem.TRENCH_CRUSADE]: "Trench Crusade",
  [GameSystem.ART_DE_LA_GUERRE]: "Art de la Guerre",
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

// Availability and Hosting Types
export enum DayOfWeek {
  MONDAY = "monday",
  TUESDAY = "tuesday", 
  WEDNESDAY = "wednesday",
  THURSDAY = "thursday",
  FRIDAY = "friday",
  SATURDAY = "saturday",
  SUNDAY = "sunday"
}

export enum TimeOfDay {
  MORNING = "morning",     // 6:00 AM - 12:00 PM
  AFTERNOON = "afternoon", // 12:00 PM - 6:00 PM
  EVENING = "evening"      // 6:00 PM - 11:00 PM
}

export enum HostingPreference {
  CAN_HOST = "can_host",           // Can host at home with boards/scenery
  PREFER_STORE = "prefer_store",   // Prefer to play in game stores
  VISIT_OTHERS = "visit_others",   // Happy to play at other players' homes
  STORE_ONLY = "store_only"        // Only play in stores (no home games)
}

export interface AvailabilitySlot {
  day: DayOfWeek;
  times: TimeOfDay[];
}

export interface HostingDetails {
  preferences: HostingPreference[];
  has_gaming_space?: boolean;
  has_boards_scenery?: boolean;
  max_players?: number;
  notes?: string;
}

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
  availability?: AvailabilitySlot[];
  hosting?: HostingDetails;
}

export interface UserPreferencesUpdate {
  games?: string[];
  location?: string;
  game_type?: GameType;
  bio?: string;
  show_email?: boolean;
  availability?: AvailabilitySlot[];
  hosting?: HostingDetails;
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
  availability?: AvailabilitySlot[];
  hosting?: HostingDetails;
  created_at: string;
  updated_at: string;
}

export interface PlayerSearchRequest {
  games?: string[];
  game_type?: GameType;
  max_distance_km: number;
  availability_days?: DayOfWeek[];
  availability_times?: TimeOfDay[];
  hosting_preferences?: HostingPreference[];
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
  availability?: AvailabilitySlot[];
  hosting?: HostingDetails;
}

export const GAME_TYPE_LABELS = {
  competitive: "Competitive",
  narrative: "Narrative"
} as const;

export const DAY_OF_WEEK_LABELS = {
  [DayOfWeek.MONDAY]: "Monday",
  [DayOfWeek.TUESDAY]: "Tuesday", 
  [DayOfWeek.WEDNESDAY]: "Wednesday",
  [DayOfWeek.THURSDAY]: "Thursday",
  [DayOfWeek.FRIDAY]: "Friday",
  [DayOfWeek.SATURDAY]: "Saturday",
  [DayOfWeek.SUNDAY]: "Sunday"
} as const;

export const TIME_OF_DAY_LABELS = {
  [TimeOfDay.MORNING]: "Morning (6 AM - 12 PM)",
  [TimeOfDay.AFTERNOON]: "Afternoon (12 PM - 6 PM)",
  [TimeOfDay.EVENING]: "Evening (6 PM - 11 PM)"
} as const;

export const HOSTING_PREFERENCE_LABELS = {
  [HostingPreference.CAN_HOST]: "Can host at home",
  [HostingPreference.PREFER_STORE]: "Prefer game stores",
  [HostingPreference.VISIT_OTHERS]: "Happy to visit others",
  [HostingPreference.STORE_ONLY]: "Game stores only"
} as const;

export const HOSTING_PREFERENCE_DESCRIPTIONS = {
  [HostingPreference.CAN_HOST]: "I have space, boards, and scenery to host games at my place",
  [HostingPreference.PREFER_STORE]: "I prefer playing in game stores but am flexible",
  [HostingPreference.VISIT_OTHERS]: "I'm happy to play at other players' homes",
  [HostingPreference.STORE_ONLY]: "I only play in public game stores, no home games"
} as const;

// Project/List Management Types
export interface ProjectBase {
  name: string;
  description?: string;
  target_completion_date?: string; // YYYY-MM-DD format
  notes?: string;
  color?: string; // Hex color for visual organization
}

export interface ProjectCreate extends ProjectBase {}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  target_completion_date?: string;
  notes?: string;
  color?: string;
}

export interface Project extends ProjectBase {
  id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  
  // Computed fields (may not always be present)
  miniature_count?: number;
  completion_percentage?: number;
  status_breakdown?: { [key in PaintingStatus]?: number };
}

export interface ProjectMiniature {
  id: string;
  project_id: string;
  miniature_id: string;
  added_at: string;
  notes?: string; // Project-specific notes for this miniature
}

export interface ProjectMiniatureCreate {
  project_id: string;
  miniature_id: string;
  notes?: string;
}

export interface ProjectWithMiniatures extends Project {
  miniatures: Miniature[];
}

export interface ProjectStatistics {
  total_projects: number;
  active_projects: number;
  completed_projects: number;
  total_miniatures_in_projects: number;
  average_completion_rate: number;
  projects_by_status: {
    not_started: number;
    in_progress: number;
    nearly_complete: number;
    completed: number;
  };
}

export interface ProjectWithStats extends Project {
  miniature_count: number;
  completion_percentage: number;
  status_breakdown: { [key in PaintingStatus]?: number };
} 