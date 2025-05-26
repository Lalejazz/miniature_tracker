"""Data models for the miniature tracker application."""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class PaintingStatus(str, Enum):
    """Enum for miniature painting status progression."""
    
    WANT_TO_BUY = "want_to_buy"
    PURCHASED = "purchased"
    ASSEMBLED = "assembled"
    PRIMED = "primed"
    GAME_READY = "game_ready"
    PARADE_READY = "parade_ready"


class GameSystem(str, Enum):
    """Enum for supported game systems."""
    
    WARHAMMER_40K = "warhammer_40k"
    AGE_OF_SIGMAR = "age_of_sigmar"
    WARHAMMER_THE_OLD_WORLD = "warhammer_the_old_world"
    HORUS_HERESY = "horus_heresy"
    KILL_TEAM = "kill_team"
    WARCRY = "warcry"
    WARHAMMER_UNDERWORLDS = "warhammer_underworlds"
    ADEPTUS_TITANICUS = "adeptus_titanicus"
    NECROMUNDA = "necromunda"
    BLOOD_BOWL = "blood_bowl"
    MIDDLE_EARTH = "middle_earth"
    BOLT_ACTION = "bolt_action"
    FLAMES_OF_WAR = "flames_of_war"
    SAGA = "saga"
    KINGS_OF_WAR = "kings_of_war"
    INFINITY = "infinity"
    MALIFAUX = "malifaux"
    WARMACHINE_HORDES = "warmachine_hordes"
    X_WING = "x_wing"
    STAR_WARS_LEGION = "star_wars_legion"
    BATTLETECH = "battletech"
    DROPZONE_COMMANDER = "dropzone_commander"
    GUILD_BALL = "guild_ball"
    DUNGEONS_AND_DRAGONS = "dungeons_and_dragons"
    PATHFINDER = "pathfinder"
    FROSTGRAVE = "frostgrave"
    MORDHEIM = "mordheim"
    GASLANDS = "gaslands"
    ZOMBICIDE = "zombicide"
    TRENCH_CRUSADE = "trench_crusade"
    OTHER = "other"


class UnitType(str, Enum):
    """Enum for unit types."""
    
    INFANTRY = "infantry"
    CAVALRY = "cavalry"
    VEHICLE = "vehicle"
    MONSTER = "monster"
    CHARACTER = "character"
    TERRAIN = "terrain"
    OTHER = "other"


class BaseDimension(str, Enum):
    """Enum for base dimensions."""
    
    ROUND_25MM = "25mm_round"
    ROUND_32MM = "32mm_round"
    ROUND_40MM = "40mm_round"
    ROUND_50MM = "50mm_round"
    ROUND_60MM = "60mm_round"
    ROUND_80MM = "80mm_round"
    ROUND_90MM = "90mm_round"
    ROUND_100MM = "100mm_round"
    ROUND_120MM = "120mm_round"
    ROUND_160MM = "160mm_round"
    OVAL_60X35MM = "60x35mm_oval"
    OVAL_75X42MM = "75x42mm_oval"
    OVAL_90X52MM = "90x52mm_oval"
    OVAL_105X70MM = "105x70mm_oval"
    OVAL_120X92MM = "120x92mm_oval"
    SQUARE_20MM = "20mm_square"
    SQUARE_25MM = "25mm_square"
    SQUARE_40MM = "40mm_square"
    SQUARE_50MM = "50mm_square"
    RECTANGULAR_60X100MM = "60x100mm_rectangular"
    RECTANGULAR_70X105MM = "70x105mm_rectangular"
    RECTANGULAR_90X120MM = "90x120mm_rectangular"
    CUSTOM = "custom"


# Game System specific factions
GAME_SYSTEM_FACTIONS = {
    GameSystem.WARHAMMER_40K: [
        "Space Marines", "Imperial Guard", "Adeptus Mechanicus", "Sisters of Battle",
        "Imperial Knights", "Custodes", "Grey Knights", "Deathwatch",
        "Chaos Space Marines", "Death Guard", "Thousand Sons", "World Eaters",
        "Chaos Daemons", "Chaos Knights",
        "Aeldari", "Drukhari", "Harlequins", "Ynnari",
        "Orks", "Tyranids", "Genestealer Cults", "Necrons", "T'au Empire",
        "Other"
    ],
    GameSystem.AGE_OF_SIGMAR: [
        "Stormcast Eternals", "Cities of Sigmar", "Fyreslayers", "Kharadron Overlords",
        "Sylvaneth", "Daughters of Khaine", "Idoneth Deepkin", "Lumineth Realm-lords",
        "Seraphon", "Beasts of Chaos", "Blades of Khorne", "Disciples of Tzeentch",
        "Hedonites of Slaanesh", "Maggotkin of Nurgle", "Skaven", "Slaves to Darkness",
        "Flesh-eater Courts", "Legions of Nagash", "Nighthaunt", "Ossiarch Bonereapers",
        "Soulblight Gravelords", "Gloomspite Gitz", "Ironjawz", "Bonesplitterz",
        "Sons of Behemat", "Ogor Mawtribes", "Other"
    ],
    GameSystem.WARHAMMER_THE_OLD_WORLD: [
        "Empire", "Bretonnia", "High Elves", "Wood Elves", "Dark Elves", "Dwarfs",
        "Warriors of Chaos", "Daemons of Chaos", "Beastmen", "Orcs & Goblins",
        "Skaven", "Vampire Counts", "Tomb Kings", "Lizardmen", "Ogre Kingdoms",
        "Chaos Dwarfs", "Other"
    ],
    GameSystem.HORUS_HERESY: [
        "Dark Angels", "Emperor's Children", "Iron Warriors", "White Scars", "Space Wolves",
        "Imperial Fists", "Night Lords", "Blood Angels", "Iron Hands", "World Eaters",
        "Ultramarines", "Death Guard", "Thousand Sons", "Sons of Horus", "Word Bearers",
        "Salamanders", "Raven Guard", "Alpha Legion", "Imperial Army", "Mechanicum",
        "Custodes", "Sisters of Silence", "Blackshields", "Other"
    ],
    GameSystem.WARHAMMER_UNDERWORLDS: [
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
    GameSystem.ADEPTUS_TITANICUS: [
        "Legio Gryphonicus", "Legio Astorum", "Legio Atarus", "Legio Crucius", "Legio Defensor",
        "Legio Fureans", "Legio Ignatum", "Legio Metalica", "Legio Mortis", "Legio Tempestus",
        "Legio Vulpa", "Legio Solaria", "Legio Vulcanum", "Legio Honorum", "Legio Lysanda",
        "Legio Magna", "Legio Osedax", "Legio Praesagius", "Legio Krytos", "Legio Audax",
        "Questor Imperialis", "Questor Mechanicus", "Questor Traitoris", "Other"
    ],
    GameSystem.KILL_TEAM: [
        "Space Marines", "Imperial Guard", "Adeptus Mechanicus", "Sisters of Battle",
        "Chaos Space Marines", "Death Guard", "Thousand Sons",
        "Aeldari", "Drukhari", "Harlequins",
        "Orks", "Tyranids", "Genestealer Cults", "Necrons", "T'au Empire",
        "Other"
    ],
    GameSystem.WARCRY: [
        "Stormcast Eternals", "Nighthaunt", "Gloomspite Gitz", "Ironjawz",
        "Slaves to Darkness", "Skaven", "Beasts of Chaos", "Flesh-eater Courts",
        "Daughters of Khaine", "Fyreslayers", "Kharadron Overlords", "Sylvaneth",
        "Other"
    ],
    GameSystem.NECROMUNDA: [
        "House Escher", "House Goliath", "House Van Saar", "House Orlock",
        "House Delaque", "House Cawdor", "Enforcers", "Corpse Grinder Cult",
        "Chaos Cult", "Genestealer Cult", "Other"
    ],
    GameSystem.BLOOD_BOWL: [
        "Human", "Orc", "Dwarf", "Elf", "Skaven", "Chaos", "Undead", "Halfling",
        "Amazon", "Lizardmen", "Norse", "Vampire", "Nurgle", "Khorne", "Other"
    ],
    GameSystem.MIDDLE_EARTH: [
        "Gondor", "Rohan", "The Shire", "Rivendell", "Lothlórien", "The White Council",
        "Mordor", "Isengard", "Haradrim", "Easterlings", "Corsairs of Umbar",
        "The Misty Mountains", "Moria", "Angmar", "Other"
    ],
    GameSystem.BOLT_ACTION: [
        "US Army", "British Army", "Soviet Army", "German Army", "Japanese Army",
        "Italian Army", "French Army", "Partisans", "Resistance", "Other"
    ],
    GameSystem.FLAMES_OF_WAR: [
        "US Forces", "British Forces", "Soviet Forces", "German Forces",
        "Italian Forces", "Finnish Forces", "Romanian Forces", "Hungarian Forces",
        "Other"
    ],
    GameSystem.SAGA: [
        "Vikings", "Anglo-Danes", "Welsh", "Irish", "Scots", "Normans",
        "Anglo-Saxons", "Byzantines", "Moors", "Crusaders", "Other"
    ],
    GameSystem.KINGS_OF_WAR: [
        "Kingdoms of Men", "Elves", "Dwarfs", "Orcs", "Goblins", "Undead",
        "Abyssal Dwarfs", "Ogres", "Basileans", "Nightstalkers", "Other"
    ],
    GameSystem.INFINITY: [
        "PanOceania", "Yu Jing", "Ariadna", "Haqqislam", "Nomads", "Combined Army",
        "ALEPH", "Tohaa", "O-12", "Starco", "Other"
    ],
    GameSystem.MALIFAUX: [
        "Guild", "Resurrectionists", "Arcanists", "Neverborn", "Outcasts",
        "Ten Thunders", "Gremlins", "Other"
    ],
    GameSystem.WARMACHINE_HORDES: [
        "Cygnar", "Khador", "Protectorate of Menoth", "Cryx", "Retribution of Scyrah",
        "Convergence of Cyriss", "Crucible Guard", "Trollbloods", "Circle Orboros",
        "Legion of Everblight", "Skorne", "Grymkin", "Minions", "Other"
    ],
    GameSystem.X_WING: [
        "Rebel Alliance", "Galactic Empire", "Scum and Villainy", "Resistance",
        "First Order", "Galactic Republic", "Separatist Alliance", "Other"
    ],
    GameSystem.STAR_WARS_LEGION: [
        "Rebel Alliance", "Galactic Empire", "Galactic Republic", "Separatist Alliance",
        "Other"
    ],
    GameSystem.BATTLETECH: [
        "Inner Sphere", "Clan", "ComStar", "Word of Blake", "Mercenary", "Other"
    ],
    GameSystem.DROPZONE_COMMANDER: [
        "United Colonies of Mankind", "Post-Human Republic", "Shaltari Tribes",
        "Scourge", "Resistance", "Other"
    ],
    GameSystem.GUILD_BALL: [
        "Alchemists", "Blacksmiths", "Brewers", "Butchers", "Cooks", "Engineers",
        "Farmers", "Fishermen", "Hunters", "Masons", "Morticians", "Navigators",
        "Order", "Ratcatchers", "Smiths", "Union", "Other"
    ],
    GameSystem.DUNGEONS_AND_DRAGONS: [
        "Player Characters", "NPCs", "Undead", "Fiends", "Celestials", "Elementals",
        "Fey", "Giants", "Humanoids", "Monstrosities", "Oozes", "Plants",
        "Beasts", "Dragons", "Constructs", "Aberrations", "Other"
    ],
    GameSystem.PATHFINDER: [
        "Player Characters", "NPCs", "Undead", "Fiends", "Celestials", "Elementals",
        "Fey", "Giants", "Humanoids", "Monstrosities", "Oozes", "Plants",
        "Beasts", "Dragons", "Constructs", "Aberrations", "Other"
    ],
    GameSystem.FROSTGRAVE: [
        "Wizard Warband", "Cultists", "Undead", "Demons", "Constructs", "Animals",
        "Soldiers", "Other"
    ],
    GameSystem.MORDHEIM: [
        "Human Mercenaries", "Reiklanders", "Middenheimers", "Marienburgers",
        "Witch Hunters", "Sisters of Sigmar", "Undead", "Skaven", "Orcs & Goblins",
        "Possessed", "Cult of the Possessed", "Other"
    ],
    GameSystem.GASLANDS: [
        "Mishkin", "Rutherford", "Miyazaki", "Verney", "Idris", "Warden", "Other"
    ],
    GameSystem.ZOMBICIDE: [
        "Survivors", "Zombies", "Abominations", "Other"
    ],
    GameSystem.TRENCH_CRUSADE: [
        "Iron Sultanate", "Heretic Legions", "Court of the Seven-Headed Serpent",
        "New Antioch", "Trench Pilgrims", "Mercenaries", "Other"
    ],
    GameSystem.OTHER: ["Custom"]
}


class StatusLogEntry(BaseModel):
    """Model for status change log entry."""
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    from_status: Optional[PaintingStatus] = None  # None for initial status
    to_status: PaintingStatus
    date: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = Field(None, max_length=500)
    is_manual: bool = False  # True if manually added, False if automatic
    created_at: datetime = Field(default_factory=datetime.now)


class StatusLogEntryCreate(BaseModel):
    """Model for creating a new status log entry."""
    
    from_status: Optional[PaintingStatus] = None
    to_status: PaintingStatus
    date: datetime
    notes: Optional[str] = Field(None, max_length=500)
    is_manual: bool = True


class StatusLogEntryUpdate(BaseModel):
    """Model for updating a status log entry."""
    
    date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)


class PasswordResetToken(BaseModel):
    """Model for password reset token."""
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    token: str = Field(default_factory=lambda: uuid4().hex)
    expires_at: datetime = Field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    used: bool = False
    created_at: datetime = Field(default_factory=datetime.now)


class PasswordResetRequest(BaseModel):
    """Model for requesting a password reset."""
    
    email: EmailStr


class PasswordReset(BaseModel):
    """Model for resetting password with token."""
    
    token: str
    new_password: str = Field(..., min_length=8)


class UnitBase(BaseModel):
    """Base model for unit data."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Unit name")
    game_system: GameSystem = Field(description="Game system this unit belongs to")
    faction: str = Field(..., min_length=1, max_length=100, description="Faction/Army")
    unit_type: UnitType = Field(description="Type of unit")
    quantity: int = Field(default=1, ge=1, description="Number of models in this unit")
    base_dimension: Optional[BaseDimension] = Field(None, description="Base size")
    custom_base_size: Optional[str] = Field(None, max_length=50, description="Custom base size if not standard")
    cost: Optional[Decimal] = Field(None, ge=0, description="Cost in local currency")
    status: PaintingStatus = PaintingStatus.WANT_TO_BUY
    notes: Optional[str] = Field(None, max_length=1000)


class UnitCreate(UnitBase):
    """Model for creating a new unit."""
    pass


class UnitUpdate(BaseModel):
    """Model for updating an existing unit."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    game_system: Optional[GameSystem] = None
    faction: Optional[str] = Field(None, min_length=1, max_length=100)
    unit_type: Optional[UnitType] = None
    quantity: Optional[int] = Field(None, ge=1)
    base_dimension: Optional[BaseDimension] = None
    custom_base_size: Optional[str] = Field(None, max_length=50)
    cost: Optional[Decimal] = Field(None, ge=0)
    status: Optional[PaintingStatus] = None
    notes: Optional[str] = Field(None, max_length=1000)


class Unit(UnitBase):
    """Complete unit model with metadata."""
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            Decimal: lambda v: str(v),
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID  # Owner of this unit
    status_history: List[StatusLogEntry] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# Keep old models for backward compatibility (will be deprecated)
class MiniatureBase(UnitBase):
    """Deprecated: Use UnitBase instead."""
    pass


class MiniatureCreate(UnitCreate):
    """Deprecated: Use UnitCreate instead."""
    pass


class MiniatureUpdate(UnitUpdate):
    """Deprecated: Use UnitUpdate instead."""
    pass


class Miniature(Unit):
    """Deprecated: Use Unit instead."""
    pass


# Player Discovery Models

class GameType(str, Enum):
    """Types of games players are interested in."""
    COMPETITIVE = "competitive"
    NARRATIVE = "narrative"


class Game(BaseModel):
    """Model for a wargame/tabletop game."""
    
    model_config = ConfigDict(
        json_encoders={
            UUID: lambda v: str(v),
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class UserPreferencesCreate(BaseModel):
    """Model for creating user preferences."""
    
    games: List[UUID] = Field(description="List of game IDs the user plays")
    location: str = Field(min_length=3, max_length=100, description="User's location (address, postcode, city, etc.)")
    game_type: GameType = Field(description="Type of games user is interested in")
    bio: Optional[str] = Field(None, max_length=160, description="Short bio about the user")
    show_email: bool = Field(default=False, description="Whether to show email in player discovery")


class UserPreferencesUpdate(BaseModel):
    """Model for updating user preferences."""
    
    games: Optional[List[UUID]] = None
    location: Optional[str] = Field(None, min_length=3, max_length=100)
    game_type: Optional[GameType] = None
    bio: Optional[str] = Field(None, max_length=160)
    show_email: Optional[bool] = None


class UserPreferences(BaseModel):
    """Model for user preferences."""
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    games: List[UUID] = Field(description="List of game IDs the user plays")
    location: str = Field(description="User's location")
    game_type: GameType = Field(description="Type of games user is interested in")
    bio: Optional[str] = Field(description="Short bio about the user")
    show_email: bool = Field(default=False, description="Whether to show email in player discovery")
    latitude: Optional[float] = Field(None, description="Calculated latitude from location")
    longitude: Optional[float] = Field(None, description="Calculated longitude from location")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now) 


class PlayerSearchRequest(BaseModel):
    """Model for player search request."""
    
    games: Optional[List[UUID]] = Field(None, description="Filter by specific games")
    game_type: Optional[GameType] = Field(None, description="Filter by game type")
    max_distance_km: int = Field(default=50, ge=1, le=500, description="Maximum distance in kilometers")


class PlayerSearchResult(BaseModel):
    """Model for player search result."""
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    )
    
    user_id: UUID
    username: str
    email: Optional[str] = Field(None, description="User's email if they opted to show it")
    games: List[Game] = Field(description="Games the player plays")
    game_type: GameType = Field(description="Type of games player is interested in")
    bio: Optional[str]
    distance_km: float = Field(description="Distance from searcher in kilometers")
    location: str = Field(description="Player's location (for privacy, might be partial)")


# Collection Statistics Models
class CollectionStatistics(BaseModel):
    """Model for collection statistics."""
    
    total_units: int = 0
    total_models: int = 0
    total_cost: Optional[Decimal] = None
    status_breakdown: dict[PaintingStatus, int] = Field(default_factory=dict)
    game_system_breakdown: dict[GameSystem, int] = Field(default_factory=dict)
    faction_breakdown: dict[str, int] = Field(default_factory=dict)
    unit_type_breakdown: dict[UnitType, int] = Field(default_factory=dict)
    completion_percentage: float = 0.0  # Percentage of units that are game_ready or parade_ready


class TrendDataPoint(BaseModel):
    """Model for a single data point in trend analysis."""
    
    date: str  # Date in YYYY-MM-DD format
    count: int = 0
    cost: Optional[Decimal] = None


class StatusTrendData(BaseModel):
    """Model for status trend analysis."""
    
    status: PaintingStatus
    data_points: List[TrendDataPoint] = Field(default_factory=list)


class TrendAnalysis(BaseModel):
    """Model for comprehensive trend analysis."""
    
    date_range: dict[str, str]  # {"from": "YYYY-MM-DD", "to": "YYYY-MM-DD"}
    
    # Purchase trends
    purchases_over_time: List[TrendDataPoint] = Field(default_factory=list)
    spending_over_time: List[TrendDataPoint] = Field(default_factory=list)
    
    # Status progression trends
    status_trends: List[StatusTrendData] = Field(default_factory=list)
    
    # Summary statistics for the period
    total_purchased: int = 0
    total_spent: Optional[Decimal] = None
    most_active_month: Optional[str] = None
    average_monthly_purchases: float = 0.0
    average_monthly_spending: Optional[Decimal] = None


class TrendRequest(BaseModel):
    """Model for trend analysis request parameters."""
    
    from_date: Optional[str] = None  # YYYY-MM-DD format
    to_date: Optional[str] = None    # YYYY-MM-DD format
    group_by: str = "month"  # "day", "week", "month", "year"


# Helper function to get factions for a game system
def get_factions_for_game_system(game_system: GameSystem) -> List[str]:
    """Get available factions for a given game system."""
    return GAME_SYSTEM_FACTIONS.get(game_system, ["Other"])


# Project Management Models

class ProjectBase(BaseModel):
    """Base model for project data."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    target_completion_date: Optional[datetime] = Field(None, description="Target completion date")
    color: str = Field(default="#6366f1", description="Project color for UI theming")
    notes: Optional[str] = Field(None, max_length=2000, description="Additional project notes")


class ProjectCreate(ProjectBase):
    """Model for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Model for updating an existing project."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    target_completion_date: Optional[datetime] = None
    color: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=2000)


class Project(ProjectBase):
    """Complete project model with metadata."""
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID  # Owner of this project
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ProjectMiniatureCreate(BaseModel):
    """Model for adding a miniature to a project."""
    
    project_id: UUID
    miniature_id: UUID


class ProjectMiniature(BaseModel):
    """Model for a miniature within a project."""
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    miniature_id: UUID
    added_at: datetime = Field(default_factory=datetime.now)


class ProjectWithMiniatures(Project):
    """Project model with associated miniatures."""
    
    miniatures: List[Miniature] = Field(default_factory=list)


class ProjectStatistics(BaseModel):
    """Model for project statistics."""
    
    total_projects: int = 0
    active_projects: int = 0
    completed_projects: int = 0
    average_completion_rate: float = 0.0 