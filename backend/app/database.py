"""Database abstraction layer for miniature tracker."""

import json
import os
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import math

try:
    import asyncpg
except ImportError:
    asyncpg = None

from app.auth_models import User, UserCreate, UserInDB, UserUpdate
from app.models import (
    PasswordResetToken, Miniature, MiniatureCreate, MiniatureUpdate, StatusLogEntry, StatusLogEntryCreate, StatusLogEntryUpdate,
    Unit, UnitCreate, UnitUpdate,
    Game, UserPreferences, UserPreferencesCreate, UserPreferencesUpdate,
    PlayerSearchRequest, PlayerSearchResult, GameType, CollectionStatistics, TrendAnalysis,
    TrendDataPoint, StatusTrendData, TrendRequest,
    Project, ProjectCreate, ProjectUpdate, ProjectWithMiniatures, ProjectMiniature, ProjectMiniatureCreate, ProjectStatistics, ProjectWithStats
)
from app.geocoding import GeocodingService


class DatabaseInterface(ABC):
    """Abstract interface for database operations."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the database."""
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email."""
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def update_user(self, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """Update an existing user."""
        pass
    
    @abstractmethod
    async def get_all_users(self) -> List[User]:
        """Get all users."""
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user and all their associated data."""
        pass
    
    @abstractmethod
    async def get_all_miniatures(self, user_id: UUID) -> List[Miniature]:
        """Get all miniatures for a user."""
        pass
    
    @abstractmethod
    async def get_miniature(self, miniature_id: UUID, user_id: UUID) -> Optional[Miniature]:
        """Get a specific miniature by ID for a user."""
        pass
    
    @abstractmethod
    async def create_miniature(self, miniature: MiniatureCreate, user_id: UUID) -> Miniature:
        """Create a new miniature."""
        pass
    
    @abstractmethod
    async def update_miniature(self, miniature_id: UUID, updates: MiniatureUpdate, user_id: UUID) -> Optional[Miniature]:
        """Update an existing miniature."""
        pass
    
    @abstractmethod
    async def delete_miniature(self, miniature_id: UUID, user_id: UUID) -> bool:
        """Delete a miniature."""
        pass
    
    @abstractmethod
    async def add_status_log_entry(self, miniature_id: UUID, from_status: Optional[str], to_status: str, notes: Optional[str], user_id: UUID) -> Optional[Miniature]:
        """Add a status log entry to a miniature."""
        pass

    @abstractmethod
    async def delete_status_log_entry(self, miniature_id: UUID, log_id: UUID, user_id: UUID) -> Optional[Miniature]:
        """Delete a status log entry."""
        pass

    @abstractmethod
    async def update_status_log_entry(self, miniature_id: UUID, log_id: UUID, updates: StatusLogEntryUpdate, user_id: UUID) -> Optional[Miniature]:
        """Update a status log entry."""
        pass

    @abstractmethod
    async def get_collection_statistics(self, user_id: UUID) -> CollectionStatistics:
        """Get collection statistics for a user."""
        pass

    @abstractmethod
    async def get_trend_analysis(self, user_id: UUID, from_date: Optional[str] = None, to_date: Optional[str] = None, group_by: str = "month") -> TrendAnalysis:
        """Get trend analysis for a user's collection."""
        pass

    # Game management methods
    @abstractmethod
    async def get_all_games(self) -> List[Game]:
        """Get all available games."""
        pass

    @abstractmethod
    async def create_game(self, name: str, description: Optional[str] = None) -> Game:
        """Create a new game."""
        pass

    # User preferences methods
    @abstractmethod
    async def get_user_preferences(self, user_id: UUID) -> Optional[UserPreferences]:
        """Get user preferences by user ID."""
        pass

    @abstractmethod
    async def create_user_preferences(self, user_id: UUID, preferences_create: UserPreferencesCreate) -> UserPreferences:
        """Create user preferences."""
        pass

    @abstractmethod
    async def update_user_preferences(self, user_id: UUID, updates: UserPreferencesUpdate) -> Optional[UserPreferences]:
        """Update user preferences."""
        pass

    @abstractmethod
    async def search_players(self, request: PlayerSearchRequest, user_id: UUID) -> List[PlayerSearchResult]:
        """Search for players based on location and game preferences."""
        pass

    # Project management methods
    @abstractmethod
    async def get_all_projects(self, user_id: UUID) -> List[ProjectWithStats]:
        """Get all projects for a user."""
        pass

    @abstractmethod
    async def get_project_statistics(self, user_id: UUID) -> ProjectStatistics:
        """Get project statistics for a user."""
        pass

    @abstractmethod
    async def get_project(self, project_id: UUID, user_id: UUID) -> Optional[Project]:
        """Get a specific project by ID for a user."""
        pass

    @abstractmethod
    async def get_project_with_miniatures(self, project_id: UUID, user_id: UUID) -> Optional[ProjectWithMiniatures]:
        """Get a project with its associated miniatures."""
        pass

    @abstractmethod
    async def create_project(self, project: ProjectCreate, user_id: UUID) -> Project:
        """Create a new project."""
        pass

    @abstractmethod
    async def update_project(self, project_id: UUID, updates: ProjectUpdate, user_id: UUID) -> Optional[Project]:
        """Update an existing project."""
        pass

    @abstractmethod
    async def delete_project(self, project_id: UUID, user_id: UUID) -> bool:
        """Delete a project."""
        pass

    @abstractmethod
    async def add_miniature_to_project(self, project_miniature: ProjectMiniatureCreate, user_id: UUID) -> bool:
        """Add a miniature to a project."""
        pass

    @abstractmethod
    async def remove_miniature_from_project(self, project_id: UUID, miniature_id: UUID, user_id: UUID) -> bool:
        """Remove a miniature from a project."""
        pass

    @abstractmethod
    async def add_multiple_miniatures_to_project(self, project_id: UUID, miniature_ids: List[UUID], user_id: UUID) -> int:
        """Add multiple miniatures to a project. Returns count of successfully added miniatures."""
        pass


class PostgreSQLDatabase(DatabaseInterface):
    """PostgreSQL database implementation."""
    
    def __init__(self, database_url: str):
        """Initialize PostgreSQL database."""
        if asyncpg is None:
            raise ImportError("asyncpg is required for PostgreSQL support")
        
        self.database_url = database_url
        self._pool: Optional['asyncpg.Pool'] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize PostgreSQL connection and create tables."""
        if self._initialized and self._pool:
            return  # Already initialized
            
        if asyncpg is None:
            raise ImportError("asyncpg is required for PostgreSQL support")
        
        # Create connection pool with limits to prevent exhaustion
        self._pool = await asyncpg.create_pool(
            self.database_url,
            min_size=1,          # Minimum connections in pool
            max_size=10,         # Maximum connections in pool - more conservative
            max_queries=50000,   # Max queries per connection
            max_inactive_connection_lifetime=300.0,  # 5 minutes
        )
        
        # Create users table
        await self._pool.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                full_name VARCHAR(100),
                hashed_password TEXT,
                oauth_provider VARCHAR(50),
                oauth_id VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Add OAuth columns if they don't exist (migration)
        try:
            await self._pool.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(100)")
            await self._pool.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR(50)")
            await self._pool.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS oauth_id VARCHAR(255)")
            await self._pool.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_email_verified BOOLEAN DEFAULT FALSE")
            await self._pool.execute("ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL")
        except Exception as e:
            print(f"OAuth migration warning: {e}")  # Log but don't fail
        
        # Create password reset tokens table
        await self._pool.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id UUID PRIMARY KEY,
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                token VARCHAR(255) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create email verification tokens table
        await self._pool.execute("""
            CREATE TABLE IF NOT EXISTS email_verification_tokens (
                id UUID PRIMARY KEY,
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                token VARCHAR(255) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create miniatures table
        await self._pool.execute("""
            CREATE TABLE IF NOT EXISTS miniatures (
                id UUID PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                status VARCHAR(100) NOT NULL DEFAULT 'want_to_buy',
                user_id UUID NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Migrate miniatures table schema if needed
        try:
            # Check if new columns exist, if not add them
            await self._pool.execute("ALTER TABLE miniatures ADD COLUMN IF NOT EXISTS faction VARCHAR(100)")
            await self._pool.execute("ALTER TABLE miniatures ADD COLUMN IF NOT EXISTS model_type VARCHAR(100)")
            await self._pool.execute("ALTER TABLE miniatures ADD COLUMN IF NOT EXISTS notes TEXT")
            
            # Add new Unit fields
            await self._pool.execute("ALTER TABLE miniatures ADD COLUMN IF NOT EXISTS game_system VARCHAR(50)")
            await self._pool.execute("ALTER TABLE miniatures ADD COLUMN IF NOT EXISTS unit_type VARCHAR(50)")
            await self._pool.execute("ALTER TABLE miniatures ADD COLUMN IF NOT EXISTS quantity INTEGER DEFAULT 1")
            await self._pool.execute("ALTER TABLE miniatures ADD COLUMN IF NOT EXISTS base_dimension VARCHAR(50)")
            await self._pool.execute("ALTER TABLE miniatures ADD COLUMN IF NOT EXISTS custom_base_size VARCHAR(50)")
            await self._pool.execute("ALTER TABLE miniatures ADD COLUMN IF NOT EXISTS cost DECIMAL(10,2)")
            await self._pool.execute("ALTER TABLE miniatures ADD COLUMN IF NOT EXISTS purchase_date TIMESTAMP")
            
            # Copy description to notes if notes is empty and description exists
            await self._pool.execute("""
                UPDATE miniatures 
                SET notes = description 
                WHERE notes IS NULL AND description IS NOT NULL
            """)
            
            # Set default values for required columns if they're NULL
            await self._pool.execute("UPDATE miniatures SET faction = 'Unknown' WHERE faction IS NULL")
            await self._pool.execute("UPDATE miniatures SET model_type = 'Unknown' WHERE model_type IS NULL")
            await self._pool.execute("UPDATE miniatures SET game_system = 'other' WHERE game_system IS NULL")
            await self._pool.execute("UPDATE miniatures SET unit_type = 'other' WHERE unit_type IS NULL")
            await self._pool.execute("UPDATE miniatures SET quantity = 1 WHERE quantity IS NULL")
            
            # Migrate old unit type values to new enum values
            await self._pool.execute("UPDATE miniatures SET model_type = 'character' WHERE model_type = 'HQ'")
            await self._pool.execute("UPDATE miniatures SET unit_type = 'character' WHERE unit_type = 'HQ'")
            
            # Handle other legacy unit types
            await self._pool.execute("UPDATE miniatures SET model_type = 'character' WHERE model_type = 'Legendary Hero'")
            await self._pool.execute("UPDATE miniatures SET unit_type = 'character' WHERE unit_type = 'Legendary Hero'")
            await self._pool.execute("UPDATE miniatures SET model_type = 'character' WHERE model_type = 'Hero'")
            await self._pool.execute("UPDATE miniatures SET unit_type = 'character' WHERE unit_type = 'Hero'")
            await self._pool.execute("UPDATE miniatures SET model_type = 'character' WHERE model_type = 'Lord'")
            await self._pool.execute("UPDATE miniatures SET unit_type = 'character' WHERE unit_type = 'Lord'")
            await self._pool.execute("UPDATE miniatures SET model_type = 'character' WHERE model_type = 'Champion'")
            await self._pool.execute("UPDATE miniatures SET unit_type = 'character' WHERE unit_type = 'Champion'")
            
            # Map any remaining unknown values to 'other'
            await self._pool.execute("""
                UPDATE miniatures SET model_type = 'other' 
                WHERE model_type NOT IN ('infantry', 'cavalry', 'vehicle', 'monster', 'character', 'terrain', 'other')
            """)
            await self._pool.execute("""
                UPDATE miniatures SET unit_type = 'other' 
                WHERE unit_type NOT IN ('infantry', 'cavalry', 'vehicle', 'monster', 'character', 'terrain', 'other')
            """)
            
            # Migrate legacy game system values to valid enum values
            await self._pool.execute("UPDATE miniatures SET game_system = 'dungeons_and_dragons' WHERE game_system = 'DND_RPG'")
            await self._pool.execute("UPDATE miniatures SET game_system = 'dungeons_and_dragons' WHERE game_system = 'dnd_rpg'")
            await self._pool.execute("UPDATE miniatures SET game_system = 'dungeons_and_dragons' WHERE game_system = 'D&D'")
            await self._pool.execute("UPDATE miniatures SET game_system = 'warhammer_40k' WHERE game_system = '40k'")
            await self._pool.execute("UPDATE miniatures SET game_system = 'warhammer_40k' WHERE game_system = 'Warhammer 40k'")
            await self._pool.execute("UPDATE miniatures SET game_system = 'age_of_sigmar' WHERE game_system = 'AoS'")
            await self._pool.execute("UPDATE miniatures SET game_system = 'age_of_sigmar' WHERE game_system = 'Age of Sigmar'")
            
            # Map any remaining unknown game system values to 'other'
            await self._pool.execute("""
                UPDATE miniatures SET game_system = 'other' 
                WHERE game_system NOT IN (
                    'warhammer_40k', 'age_of_sigmar', 'warhammer_the_old_world', 'kill_team', 'warcry', 'necromunda', 'blood_bowl',
                    'middle_earth', 'bolt_action', 'flames_of_war', 'saga', 'kings_of_war', 'infinity',
                    'malifaux', 'warmachine_hordes', 'x_wing', 'star_wars_legion', 'battletech',
                    'dropzone_commander', 'guild_ball', 'dungeons_and_dragons', 'pathfinder',
                    'frostgrave', 'mordheim', 'gaslands', 'zombicide', 'trench_crusade', 'other'
                )
            """)
            
            # Now make required columns NOT NULL
            await self._pool.execute("ALTER TABLE miniatures ALTER COLUMN faction SET NOT NULL")
            await self._pool.execute("ALTER TABLE miniatures ALTER COLUMN model_type SET NOT NULL")
            await self._pool.execute("ALTER TABLE miniatures ALTER COLUMN game_system SET NOT NULL")
            await self._pool.execute("ALTER TABLE miniatures ALTER COLUMN unit_type SET NOT NULL")
            await self._pool.execute("ALTER TABLE miniatures ALTER COLUMN quantity SET NOT NULL")
        
        except Exception as e:
            print(f"Migration warning: {e}")  # Log but don't fail
        
        # Create status log entries table
        await self._pool.execute("""
            CREATE TABLE IF NOT EXISTS status_log_entries (
                id UUID PRIMARY KEY,
                miniature_id UUID REFERENCES miniatures(id) ON DELETE CASCADE,
                user_id UUID NOT NULL,
                from_status VARCHAR(255),
                to_status VARCHAR(255) NOT NULL,
                date TIMESTAMP DEFAULT NOW(),
                notes TEXT,
                is_manual BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Add date column if it doesn't exist (for existing databases)
        try:
            await self._pool.execute("ALTER TABLE status_log_entries ADD COLUMN IF NOT EXISTS date TIMESTAMP DEFAULT NOW()")
        except Exception as e:
            print(f"Migration warning: {e}")  # Log but don't fail
        
        # Create games table
        await self._pool.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Populate default games if table is empty
        await self._populate_default_games()
        
        # Create user preferences table
        await self._pool.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                games UUID[] DEFAULT '{}',
                location VARCHAR(100),
                game_type TEXT,
                bio TEXT CHECK (length(bio) <= 160),
                show_email BOOLEAN DEFAULT FALSE,
                theme VARCHAR(20) DEFAULT 'blue_gradient',
                availability JSONB,
                hosting JSONB,
                latitude DECIMAL(10, 8),
                longitude DECIMAL(11, 8),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Migrate from postcode to location field and add theme column
        try:
            # Add location column if it doesn't exist
            await self._pool.execute("ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS location VARCHAR(100)")
            
            # Add theme column if it doesn't exist
            await self._pool.execute("ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS theme VARCHAR(20) DEFAULT 'blue_gradient'")
            
            # Add availability and hosting columns if they don't exist
            await self._pool.execute("ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS availability JSONB")
            await self._pool.execute("ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS hosting JSONB")
            
            # Copy existing postcode data to location if location is null
            await self._pool.execute("""
                UPDATE user_preferences 
                SET location = postcode 
                WHERE location IS NULL AND postcode IS NOT NULL
            """)
            
            # Make postcode column nullable to avoid constraint violations
            await self._pool.execute("ALTER TABLE user_preferences ALTER COLUMN postcode DROP NOT NULL")
            
            # Make location NOT NULL once data is migrated
            rows_with_null_location = await self._pool.fetchval(
                "SELECT COUNT(*) FROM user_preferences WHERE location IS NULL"
            )
            if rows_with_null_location == 0:
                await self._pool.execute("ALTER TABLE user_preferences ALTER COLUMN location SET NOT NULL")
                
            # Drop the old postcode column after migration (optional, but cleaner)
            await self._pool.execute("ALTER TABLE user_preferences DROP COLUMN IF EXISTS postcode")
            
        except Exception as e:
            print(f"Migration warning: {e}")  # Log but don't fail
        
        # Create projects table
        await self._pool.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                description TEXT,
                target_completion_date DATE,
                color VARCHAR(7),
                notes TEXT,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(name, user_id)
            )
        """)
        
        # Create project_miniatures junction table
        await self._pool.execute("""
            CREATE TABLE IF NOT EXISTS project_miniatures (
                project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
                miniature_id UUID REFERENCES miniatures(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT NOW(),
                PRIMARY KEY (project_id, miniature_id)
            )
        """)
        
        # Create indexes
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_reset_tokens_token ON password_reset_tokens(token)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_miniatures_name ON miniatures(name)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_games_name ON games(name)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_user_preferences_location ON user_preferences(latitude, longitude)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_project_miniatures_project_id ON project_miniatures(project_id)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_project_miniatures_miniature_id ON project_miniatures(miniature_id)")
        
        self._initialized = True
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
            
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE email = $1", email
            )
            if row:
                return UserInDB(**dict(row))
        return None
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
            
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, email, username, full_name, oauth_provider, oauth_id, is_active, created_at, updated_at FROM users WHERE id = $1", 
                user_id
            )
            if row:
                return User(**dict(row))
        return None
    
    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        # Handle password hashing for non-OAuth users
        hashed_password = None
        if user_create.password:
            from app.auth_utils import get_password_hash
            hashed_password = get_password_hash(user_create.password)
        
        user_in_db = UserInDB(
            **user_create.model_dump(exclude={"password"}),
            hashed_password=hashed_password
        )
        
        async with self._pool.acquire() as conn:
            try:
                await conn.execute("""
                    INSERT INTO users (id, email, username, full_name, hashed_password, oauth_provider, oauth_id, is_active, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, 
                user_in_db.id, user_in_db.email, user_in_db.username, user_in_db.full_name,
                user_in_db.hashed_password, user_in_db.oauth_provider, user_in_db.oauth_id,
                user_in_db.is_active, user_in_db.created_at, user_in_db.updated_at
                )
                return User(**user_in_db.model_dump(exclude={"hashed_password"}))
            except Exception as e:
                # Handle unique constraint violations
                if "unique" in str(e).lower():
                    if "email" in str(e).lower():
                        raise ValueError("User with this email already exists")
                    elif "username" in str(e).lower():
                        raise ValueError("User with this username already exists")
                raise
    
    async def update_user(self, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """Update an existing user."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
            
        update_data = user_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_user_by_id(user_id)
        
        # Build dynamic query
        set_clauses = []
        values = []
        for i, (key, value) in enumerate(update_data.items(), 1):
            set_clauses.append(f"{key} = ${i}")
            values.append(value)
        
        values.append(datetime.utcnow())  # updated_at
        values.append(user_id)  # WHERE condition
        
        query = f"""
            UPDATE users 
            SET {', '.join(set_clauses)}, updated_at = ${len(values)-1}
            WHERE id = ${len(values)}
            RETURNING id, email, username, full_name, oauth_provider, oauth_id, is_active, created_at, updated_at
        """
        
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, *values)
            if row:
                return User(**dict(row))
        return None
    
    async def get_all_users(self) -> List[User]:
        """Get all users."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
            
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, email, username, full_name, oauth_provider, oauth_id, is_active, created_at, updated_at FROM users ORDER BY created_at"
            )
            return [User(**dict(row)) for row in rows]
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user and all their associated data."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM users WHERE id = $1",
                user_id
            )
            return result.split()[-1] != '0'  # Check if any rows were affected
    
    async def get_all_miniatures(self, user_id: UUID) -> List[Miniature]:
        """Get all miniatures for a user."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
            
        async with self._pool.acquire() as conn:
            # Get miniatures
            miniature_rows = await conn.fetch(
                """SELECT id, name, faction, model_type, status, notes, user_id, created_at, updated_at,
                   game_system, unit_type, quantity, base_dimension, custom_base_size, cost, purchase_date 
                   FROM miniatures WHERE user_id = $1 ORDER BY created_at""",
                user_id
            )
            
            miniatures = []
            for row in miniature_rows:
                # Get status history for this miniature
                status_rows = await conn.fetch(
                    "SELECT id, from_status, to_status, date, notes, is_manual, created_at FROM status_log_entries WHERE miniature_id = $1 ORDER BY created_at",
                    row['id']
                )
                
                status_history = [
                    StatusLogEntry(
                        id=status_row['id'],
                        from_status=status_row['from_status'],
                        to_status=status_row['to_status'],
                        date=status_row['date'],
                        notes=status_row['notes'],
                        is_manual=status_row['is_manual'],
                        created_at=status_row['created_at']
                    ) for status_row in status_rows
                ]
                
                miniature = Miniature(
                    id=row['id'],
                    name=row['name'],
                    faction=row['faction'],
                    unit_type=row['model_type'],  # Map model_type from DB to unit_type in model
                    status=row['status'],
                    notes=row['notes'],
                    user_id=row['user_id'],
                    status_history=status_history,
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    # New Unit fields
                    game_system=row.get('game_system'),
                    quantity=row.get('quantity', 1),
                    base_dimension=row.get('base_dimension'),
                    custom_base_size=row.get('custom_base_size'),
                    cost=row.get('cost'),
                    purchase_date=row.get('purchase_date')
                )
                miniatures.append(miniature)
            
            return miniatures
    
    async def get_miniature(self, miniature_id: UUID, user_id: UUID) -> Optional[Miniature]:
        """Get a specific miniature by ID for a user."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
            
        async with self._pool.acquire() as conn:
            # Get miniature
            row = await conn.fetchrow(
                "SELECT id, name, faction, model_type, status, notes, user_id, created_at, updated_at, game_system, unit_type, quantity, base_dimension, custom_base_size, cost, purchase_date FROM miniatures WHERE id = $1 AND user_id = $2",
                miniature_id, user_id
            )
            if not row:
                return None
            
            # Get status history
            status_rows = await conn.fetch(
                "SELECT id, from_status, to_status, date, notes, is_manual, created_at FROM status_log_entries WHERE miniature_id = $1 ORDER BY created_at",
                miniature_id
            )
            
            status_history = [
                StatusLogEntry(
                    id=status_row['id'],
                    from_status=status_row['from_status'],
                    to_status=status_row['to_status'],
                    date=status_row['date'],
                    notes=status_row['notes'],
                    is_manual=status_row['is_manual'],
                    created_at=status_row['created_at']
                ) for status_row in status_rows
            ]
            
            return Miniature(
                id=row['id'],
                name=row['name'],
                faction=row['faction'],
                unit_type=row['model_type'],  # Map model_type from DB to unit_type in model
                status=row['status'],
                notes=row['notes'],
                user_id=row['user_id'],
                status_history=status_history,
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                # New Unit fields
                game_system=row.get('game_system'),
                quantity=row.get('quantity', 1),
                base_dimension=row.get('base_dimension'),
                custom_base_size=row.get('custom_base_size'),
                cost=row.get('cost'),
                purchase_date=row.get('purchase_date')
            )
    
    async def create_miniature(self, miniature: MiniatureCreate, user_id: UUID) -> Miniature:
        """Create a new miniature."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        # Generate ID for the miniature
        miniature_id = uuid4()
        
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Insert miniature - use unit_type for both model_type and unit_type for backward compatibility
                miniature_row = await conn.fetchrow(
                    """INSERT INTO miniatures (id, name, faction, model_type, status, notes, user_id, 
                       game_system, unit_type, quantity, base_dimension, custom_base_size, cost, purchase_date) 
                       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14) 
                       RETURNING id, name, faction, model_type, status, notes, user_id, created_at, updated_at,
                       game_system, unit_type, quantity, base_dimension, custom_base_size, cost, purchase_date""",
                    miniature_id, miniature.name, miniature.faction, 
                    miniature.unit_type.value if miniature.unit_type else None,  # Use unit_type for model_type
                    miniature.status.value, miniature.notes, user_id,
                    miniature.game_system.value if miniature.game_system else None,
                    miniature.unit_type.value if miniature.unit_type else None,
                    getattr(miniature, 'quantity', 1),
                    miniature.base_dimension.value if miniature.base_dimension else None,
                    getattr(miniature, 'custom_base_size', None),
                    getattr(miniature, 'cost', None),
                    getattr(miniature, 'purchase_date', None)
                )
                
                # Add initial status log entry
                status_entry = await conn.fetchrow(
                    "INSERT INTO status_log_entries (id, miniature_id, user_id, from_status, to_status, date, notes, is_manual) VALUES ($1, $2, $3, $4, $5, NOW(), $6, $7) RETURNING id, from_status, to_status, date, notes, is_manual, created_at",
                    uuid4(), miniature_id, user_id, None, miniature.status.value, None, False
                )
                
                status_history = [StatusLogEntry(
                    id=status_entry['id'],
                    from_status=status_entry['from_status'],
                    to_status=status_entry['to_status'],
                    date=status_entry['date'],
                    notes=status_entry['notes'],
                    is_manual=status_entry['is_manual'],
                    created_at=status_entry['created_at']
                )]
                
                return Miniature(
                    id=miniature_row['id'],
                    name=miniature_row['name'],
                    faction=miniature_row['faction'],
                    unit_type=miniature_row['model_type'],  # Map model_type from DB to unit_type in model
                    status=miniature_row['status'],
                    notes=miniature_row['notes'],
                    user_id=miniature_row['user_id'],
                    status_history=status_history,
                    created_at=miniature_row['created_at'],
                    updated_at=miniature_row['updated_at'],
                    # New Unit fields
                    game_system=miniature_row.get('game_system'),
                    quantity=miniature_row.get('quantity', 1),
                    base_dimension=miniature_row.get('base_dimension'),
                    custom_base_size=miniature_row.get('custom_base_size'),
                    cost=miniature_row.get('cost'),
                    purchase_date=miniature_row.get('purchase_date')
                )
    
    async def update_miniature(self, miniature_id: UUID, updates: MiniatureUpdate, user_id: UUID) -> Optional[Miniature]:
        """Update an existing miniature."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
            
        update_data = updates.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_miniature(miniature_id, user_id)
        
        # Convert enum status to string if present
        if 'status' in update_data and update_data['status'] is not None:
            update_data['status'] = update_data['status'].value
        
        # Map unit_type to model_type for database compatibility
        if 'unit_type' in update_data:
            if update_data['unit_type'] is not None:
                update_data['model_type'] = update_data['unit_type'].value
            else:
                update_data['model_type'] = None
            # Remove unit_type from update_data since we're using model_type in the database
            del update_data['unit_type']
        
        # Convert other enum fields to strings
        for field in ['game_system', 'base_dimension']:
            if field in update_data and update_data[field] is not None:
                update_data[field] = update_data[field].value
        
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Get current miniature to check for status changes
                current_row = await conn.fetchrow(
                    "SELECT status FROM miniatures WHERE id = $1 AND user_id = $2",
                    miniature_id, user_id
                )
                if not current_row:
                    return None
                
                old_status = current_row['status']
                new_status = update_data.get('status', old_status)
                
                # Build dynamic query for miniature update
                set_clauses = []
                values = []
                for i, (key, value) in enumerate(update_data.items(), 1):
                    set_clauses.append(f"{key} = ${i}")
                    values.append(value)
                
                # Add updated_at, miniature_id, and user_id to values
                updated_at_index = len(values) + 1
                miniature_id_index = len(values) + 2
                user_id_index = len(values) + 3
                
                values.append(datetime.utcnow())  # updated_at
                values.append(miniature_id)      # WHERE condition
                values.append(user_id)           # WHERE condition
                
                query = f"""
                    UPDATE miniatures 
                    SET {', '.join(set_clauses)}, updated_at = ${updated_at_index}
                    WHERE id = ${miniature_id_index} AND user_id = ${user_id_index}
                    RETURNING id, name, faction, model_type, status, notes, user_id, created_at, updated_at,
                    game_system, unit_type, quantity, base_dimension, custom_base_size, cost, purchase_date
                """
                
                miniature_row = await conn.fetchrow(query, *values)
                if not miniature_row:
                    return None
                
                # Add status log entry if status changed
                if old_status != new_status:
                    await conn.execute(
                        "INSERT INTO status_log_entries (id, miniature_id, user_id, from_status, to_status, notes, is_manual) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                        uuid4(), miniature_id, user_id, old_status, new_status, None, False
                    )
                
                # Get status history for the updated miniature
                status_rows = await conn.fetch(
                    "SELECT id, from_status, to_status, date, notes, is_manual, created_at FROM status_log_entries WHERE miniature_id = $1 ORDER BY created_at",
                    miniature_id
                )
                
                status_history = [
                    StatusLogEntry(
                        id=status_row['id'],
                        from_status=status_row['from_status'],
                        to_status=status_row['to_status'],
                        date=status_row['date'],
                        notes=status_row['notes'],
                        is_manual=status_row['is_manual'],
                        created_at=status_row['created_at']
                    ) for status_row in status_rows
                ]
                
                # Return the updated miniature directly from the UPDATE query result
                return Miniature(
                    id=miniature_row['id'],
                    name=miniature_row['name'],
                    faction=miniature_row['faction'],
                    unit_type=miniature_row['model_type'],  # Map model_type from DB to unit_type in model
                    status=miniature_row['status'],
                    notes=miniature_row['notes'],
                    user_id=miniature_row['user_id'],
                    status_history=status_history,
                    created_at=miniature_row['created_at'],
                    updated_at=miniature_row['updated_at'],
                    # New Unit fields
                    game_system=miniature_row.get('game_system'),
                    quantity=miniature_row.get('quantity', 1),
                    base_dimension=miniature_row.get('base_dimension'),
                    custom_base_size=miniature_row.get('custom_base_size'),
                    cost=miniature_row.get('cost'),
                    purchase_date=miniature_row.get('purchase_date')
                )
    
    async def delete_miniature(self, miniature_id: UUID, user_id: UUID) -> bool:
        """Delete a miniature."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
            
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM miniatures WHERE id = $1 AND user_id = $2",
                miniature_id, user_id
            )
            return result.split()[-1] != '0'  # Check if any rows were affected
    
    async def add_status_log_entry(self, miniature_id: UUID, from_status: Optional[str], to_status: str, notes: Optional[str], user_id: UUID) -> Optional[Miniature]:
        """Add a status log entry to a miniature."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Insert the status log entry with current timestamp as date
                await conn.execute("""
                    INSERT INTO status_log_entries (id, miniature_id, user_id, from_status, to_status, date, notes, is_manual, created_at)
                    VALUES ($1, $2, $3, $4, $5, NOW(), $6, $7, NOW())
                """, uuid4(), miniature_id, user_id, from_status, to_status, notes, False)
                
                # Update the miniature's status
                await conn.execute("""
                    UPDATE miniatures SET status = $1, updated_at = NOW()
                    WHERE id = $2 AND user_id = $3
                """, to_status, miniature_id, user_id)
                
                # Return the updated miniature
                return await self.get_miniature(miniature_id, user_id)

    async def delete_status_log_entry(self, miniature_id: UUID, log_id: UUID, user_id: UUID) -> Optional[Miniature]:
        """Delete a status log entry."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Verify the log entry exists and belongs to the user
                log_exists = await conn.fetchval(
                    """SELECT EXISTS(
                        SELECT 1 FROM status_log_entries sle 
                        JOIN miniatures m ON sle.miniature_id = m.id 
                        WHERE sle.id = $1 AND sle.miniature_id = $2 AND m.user_id = $3
                    )""",
                    log_id, miniature_id, user_id
                )
                if not log_exists:
                    return None
                
                # Delete the status log entry
                result = await conn.execute(
                    "DELETE FROM status_log_entries WHERE id = $1 AND miniature_id = $2",
                    log_id, miniature_id
                )
                
                # Check if any rows were affected
                if result.split()[-1] == '0':
                    return None
                
                # Return updated miniature
                return await self.get_miniature(miniature_id, user_id)

    async def update_status_log_entry(self, miniature_id: UUID, log_id: UUID, updates: StatusLogEntryUpdate, user_id: UUID) -> Optional[Miniature]:
        """Update a status log entry."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Verify the log entry exists and belongs to the user
                log_exists = await conn.fetchval(
                    """SELECT EXISTS(
                        SELECT 1 FROM status_log_entries sle 
                        JOIN miniatures m ON sle.miniature_id = m.id 
                        WHERE sle.id = $1 AND sle.miniature_id = $2 AND m.user_id = $3
                    )""",
                    log_id, miniature_id, user_id
                )
                if not log_exists:
                    return None
                
                # Build dynamic update query based on which fields are provided
                update_fields = []
                params = []
                param_count = 1
                
                if updates.to_status is not None:
                    update_fields.append(f"to_status = ${param_count}")
                    params.append(updates.to_status)
                    param_count += 1
                
                if updates.date is not None:
                    update_fields.append(f"date = ${param_count}")
                    params.append(updates.date)
                    param_count += 1
                
                if updates.notes is not None:
                    update_fields.append(f"notes = ${param_count}")
                    params.append(updates.notes)
                    param_count += 1
                
                if not update_fields:
                    # No fields to update
                    return await self.get_miniature(miniature_id, user_id)
                
                # Add updated_at timestamp
                update_fields.append(f"updated_at = NOW()")
                
                # Add WHERE clause parameters
                params.extend([log_id, miniature_id])
                
                # Execute the update
                query = f"UPDATE status_log_entries SET {', '.join(update_fields)} WHERE id = ${param_count} AND miniature_id = ${param_count + 1}"
                result = await conn.execute(query, *params)
                
                # Check if any rows were affected
                if result.split()[-1] == '0':
                    return None
                
                # Return updated miniature
                return await self.get_miniature(miniature_id, user_id)

    async def get_collection_statistics(self, user_id: UUID) -> CollectionStatistics:
        """Get collection statistics for a user."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            # Get all miniatures for the user
            miniatures = await self.get_all_miniatures(user_id)
            
            if not miniatures:
                return CollectionStatistics(
                    total_units=0,
                    total_models=0,
                    total_cost=None,
                    status_breakdown={},
                    game_system_breakdown={},
                    faction_breakdown={},
                    unit_type_breakdown={},
                    completion_percentage=0.0
                )
            
            # Calculate statistics
            total_units = len(miniatures)
            total_models = sum(m.quantity for m in miniatures)
            total_cost = sum(m.cost for m in miniatures if m.cost is not None)
            
            # Status breakdown
            from app.models import PaintingStatus, GameSystem, UnitType
            status_breakdown = {}
            for status in PaintingStatus:
                status_breakdown[status] = sum(1 for m in miniatures if m.status == status)
            
            # Game system breakdown
            game_system_breakdown = {}
            for system in GameSystem:
                game_system_breakdown[system] = sum(1 for m in miniatures if m.game_system == system)
            
            # Faction breakdown
            faction_breakdown = {}
            for miniature in miniatures:
                faction = miniature.faction
                faction_breakdown[faction] = faction_breakdown.get(faction, 0) + 1
            
            # Unit type breakdown
            unit_type_breakdown = {}
            for unit_type in UnitType:
                unit_type_breakdown[unit_type] = sum(1 for m in miniatures if m.unit_type == unit_type)
            
            # Completion percentage (game_ready + parade_ready)
            completed_units = sum(1 for m in miniatures if m.status in [PaintingStatus.GAME_READY, PaintingStatus.PARADE_READY])
            completion_percentage = (completed_units / total_units * 100) if total_units > 0 else 0.0
            
            return CollectionStatistics(
                total_units=total_units,
                total_models=total_models,
                total_cost=total_cost if total_cost > 0 else None,
                status_breakdown=status_breakdown,
                game_system_breakdown=game_system_breakdown,
                faction_breakdown=faction_breakdown,
                unit_type_breakdown=unit_type_breakdown,
                completion_percentage=round(completion_percentage, 1)
            )

    async def get_trend_analysis(self, user_id: UUID, from_date: Optional[str] = None, to_date: Optional[str] = None, group_by: str = "month") -> TrendAnalysis:
        """Get trend analysis for a user's collection."""
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        # Set default date range if not provided
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        if not from_date:
            # Default to 12 months ago
            from_datetime = datetime.now() - timedelta(days=365)
            from_date = from_datetime.strftime("%Y-%m-%d")
        
        # Get all miniatures for the user
        miniatures = await self.get_all_miniatures(user_id)
        
        # Initialize data structures
        purchases_by_period = defaultdict(lambda: {"count": 0, "cost": 0.0})
        status_changes_by_period = defaultdict(lambda: defaultdict(int))
        
        # Helper function to get period key based on group_by
        def get_period_key(date_obj):
            if group_by == "day":
                return date_obj.strftime("%Y-%m-%d")
            elif group_by == "week":
                # Get Monday of the week
                monday = date_obj - timedelta(days=date_obj.weekday())
                return monday.strftime("%Y-%m-%d")
            elif group_by == "month":
                return date_obj.strftime("%Y-%m")
            elif group_by == "year":
                return date_obj.strftime("%Y")
            else:
                return date_obj.strftime("%Y-%m")
        
        # Process each miniature
        for miniature in miniatures:
            # Process status history
            for log_entry in miniature.status_history:
                log_date = log_entry.date if hasattr(log_entry, 'date') else log_entry.created_at
                
                # Check if log entry is within date range
                if from_date <= log_date.strftime("%Y-%m-%d") <= to_date:
                    period_key = get_period_key(log_date)
                    
                    # Track purchases (transitions to "purchased" status)
                    if log_entry.to_status == "purchased":
                        purchases_by_period[period_key]["count"] += 1
                        if miniature.cost:
                            purchases_by_period[period_key]["cost"] += float(miniature.cost)
                    
                    # Track all status changes
                    status_changes_by_period[period_key][log_entry.to_status] += 1
        
        # Generate time series data
        from_datetime = datetime.strptime(from_date, "%Y-%m-%d")
        to_datetime = datetime.strptime(to_date, "%Y-%m-%d")
        
        # Generate all periods in range
        all_periods = []
        current = from_datetime
        while current <= to_datetime:
            period_key = get_period_key(current)
            if period_key not in all_periods:
                all_periods.append(period_key)
            
            # Increment based on group_by
            if group_by == "day":
                current += timedelta(days=1)
            elif group_by == "week":
                current += timedelta(weeks=1)
            elif group_by == "month":
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
            elif group_by == "year":
                current = current.replace(year=current.year + 1)
            else:
                current += timedelta(days=30)  # Default monthly
        
        # Build purchase trend data
        purchases_over_time = []
        spending_over_time = []
        for period in sorted(all_periods):
            data = purchases_by_period[period]
            purchases_over_time.append(TrendDataPoint(
                date=period,
                count=data["count"]
            ))
            spending_over_time.append(TrendDataPoint(
                date=period,
                count=0,  # Not used for spending
                cost=data["cost"] if data["cost"] > 0 else None
            ))
        
        # Build status trend data
        from app.models import PaintingStatus
        status_trends = []
        for status in PaintingStatus:
            data_points = []
            for period in sorted(all_periods):
                count = status_changes_by_period[period].get(status.value, 0)
                data_points.append(TrendDataPoint(
                    date=period,
                    count=count
                ))
            status_trends.append(StatusTrendData(
                status=status,
                data_points=data_points
            ))
        
        # Calculate summary statistics
        total_purchased = sum(data["count"] for data in purchases_by_period.values())
        total_spent = sum(data["cost"] for data in purchases_by_period.values())
        
        # Find most active month
        most_active_month = None
        max_purchases = 0
        for period, data in purchases_by_period.items():
            if data["count"] > max_purchases:
                max_purchases = data["count"]
                most_active_month = period
        
        # Calculate averages
        num_periods = len(all_periods) if all_periods else 1
        average_monthly_purchases = total_purchased / num_periods
        average_monthly_spending = total_spent / num_periods if total_spent > 0 else None
        
        return TrendAnalysis(
            date_range={"from": from_date, "to": to_date},
            purchases_over_time=purchases_over_time,
            spending_over_time=spending_over_time,
            status_trends=status_trends,
            total_purchased=total_purchased,
            total_spent=total_spent if total_spent > 0 else None,
            most_active_month=most_active_month,
            average_monthly_purchases=round(average_monthly_purchases, 1),
            average_monthly_spending=round(average_monthly_spending, 2) if average_monthly_spending else None
        )

    # Game management methods
    async def get_all_games(self) -> List[Game]:
        """Get all available games."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
            
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, name, description, is_active, created_at, updated_at FROM games WHERE is_active = TRUE ORDER BY name"
            )
            return [Game(**dict(row)) for row in rows]
    
    async def create_game(self, name: str, description: Optional[str] = None) -> Game:
        """Create a new game."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        game_id = uuid4()
        async with self._pool.acquire() as conn:
            try:
                row = await conn.fetchrow(
                    "INSERT INTO games (id, name, description) VALUES ($1, $2, $3) RETURNING id, name, description, is_active, created_at, updated_at",
                    game_id, name, description
                )
                return Game(**dict(row))
            except Exception as e:
                if "unique" in str(e).lower():
                    raise ValueError("Game with this name already exists")
                raise

    # User preferences methods
    async def get_user_preferences(self, user_id: UUID) -> Optional[UserPreferences]:
        """Get user preferences by user ID."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
            
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, user_id, games, location, game_type, bio, show_email, theme, availability, hosting, latitude, longitude, created_at, updated_at FROM user_preferences WHERE user_id = $1",
                user_id
            )
            if row:
                return UserPreferences(**dict(row))
        return None
    
    async def create_user_preferences(self, user_id: UUID, preferences_create: UserPreferencesCreate) -> UserPreferences:
        """Create user preferences."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        preferences_id = uuid4()
        
        # Geocode address to get coordinates
        print(f"🔍 Geocoding location: '{preferences_create.location}'")
        try:
            coordinates = await GeocodingService.get_coordinates_from_address(preferences_create.location)
            latitude = coordinates[0] if coordinates else None
            longitude = coordinates[1] if coordinates else None
            print(f"📍 Geocoding result: lat={latitude}, lon={longitude}")
        except Exception as e:
            print(f"❌ Geocoding error: {e}")
            latitude = None
            longitude = None
        
        # Serialize availability and hosting to JSON
        import json
        availability_json = json.dumps([slot.model_dump() for slot in preferences_create.availability]) if preferences_create.availability else None
        hosting_json = json.dumps(preferences_create.hosting.model_dump()) if preferences_create.hosting else None
        
        async with self._pool.acquire() as conn:
            try:
                row = await conn.fetchrow(
                    """INSERT INTO user_preferences (id, user_id, games, location, game_type, bio, show_email, theme, availability, hosting, latitude, longitude) 
                       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12) 
                       RETURNING id, user_id, games, location, game_type, bio, show_email, theme, availability, hosting, latitude, longitude, created_at, updated_at""",
                    preferences_id, user_id, [str(g) for g in preferences_create.games], preferences_create.location, 
                    preferences_create.game_type, preferences_create.bio, preferences_create.show_email,
                    preferences_create.theme, availability_json, hosting_json,
                    latitude, longitude
                )
                print(f"💾 Database saved: lat={row['latitude']}, lon={row['longitude']}")
                return UserPreferences(**dict(row))
            except Exception as e:
                print(f"❌ Database error: {e}")
                if "unique" in str(e).lower():
                    raise ValueError("User preferences already exist")
                raise
    
    async def update_user_preferences(self, user_id: UUID, updates: UserPreferencesUpdate) -> Optional[UserPreferences]:
        """Update user preferences."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
            
        update_data = updates.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_user_preferences(user_id)
        
        # Convert data types for PostgreSQL
        if 'games' in update_data and update_data['games'] is not None:
            update_data['games'] = [str(g) for g in update_data['games']]
        if 'game_type' in update_data and update_data['game_type'] is not None:
            update_data['game_type'] = update_data['game_type']
        
        # Serialize availability and hosting to JSON
        import json
        if 'availability' in update_data and update_data['availability'] is not None:
            update_data['availability'] = json.dumps([slot.model_dump() for slot in update_data['availability']])
        if 'hosting' in update_data and update_data['hosting'] is not None:
            update_data['hosting'] = json.dumps(update_data['hosting'].model_dump())
        
        # Geocode location if it changed
        if 'location' in update_data and update_data['location'] is not None:
            coordinates = await GeocodingService.get_coordinates_from_address(update_data['location'])
            if coordinates:
                update_data['latitude'] = coordinates[0]
                update_data['longitude'] = coordinates[1]
            else:
                update_data['latitude'] = None
                update_data['longitude'] = None
        
        async with self._pool.acquire() as conn:
            # Build dynamic query
            set_clauses = []
            values = []
            for i, (key, value) in enumerate(update_data.items(), 1):
                set_clauses.append(f"{key} = ${i}")
                values.append(value)
            
            values.append(datetime.utcnow())  # updated_at
            values.append(user_id)           # WHERE condition
            
            query = f"""
                UPDATE user_preferences 
                SET {', '.join(set_clauses)}, updated_at = ${len(values)-1}
                WHERE user_id = ${len(values)}
                RETURNING id, user_id, games, location, game_type, bio, show_email, theme, availability, hosting, latitude, longitude, created_at, updated_at
            """
            
            row = await conn.fetchrow(query, *values)
            if row:
                return UserPreferences(**dict(row))
        return None
    
    async def search_players(self, request: PlayerSearchRequest, user_id: UUID) -> List[PlayerSearchResult]:
        """Search for players based on location and game preferences."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        # Get user's location for distance calculation
        user_prefs = await self.get_user_preferences(user_id)
        if not user_prefs or not user_prefs.latitude or not user_prefs.longitude:
            return []
        
        # Build query based on search criteria
        query_conditions = ["up.latitude IS NOT NULL", "up.longitude IS NOT NULL", "up.user_id != $1"]
        query_params = [user_id]
        param_index = 2
        
        # Filter by games if specified
        if request.games:
            game_conditions = []
            for game in request.games:
                game_conditions.append(f"${param_index} = ANY(up.games)")
                query_params.append(str(game))
                param_index += 1
            query_conditions.append(f"({' OR '.join(game_conditions)})")
        
        # Filter by game type if specified
        if request.game_type:
            query_conditions.append(f"up.game_type = ${param_index}")
            query_params.append(request.game_type.value)
            param_index += 1
        
        # Calculate distance using Haversine formula
        distance_formula = f"""
            6371 * acos(
                cos(radians({user_prefs.latitude})) * 
                cos(radians(up.latitude)) * 
                cos(radians(up.longitude) - radians({user_prefs.longitude})) + 
                sin(radians({user_prefs.latitude})) * 
                sin(radians(up.latitude))
            )
        """
        
        # Add distance filter
        query_conditions.append(f"({distance_formula}) <= ${param_index}")
        query_params.append(request.max_distance_km)
        param_index += 1
        
        query = f"""
            SELECT 
                u.id, u.username, u.email, u.created_at,
                up.bio, up.location, up.game_type, up.games, up.show_email, up.theme,
                ({distance_formula}) as distance
            FROM users u
            JOIN user_preferences up ON u.id = up.user_id
            WHERE {' AND '.join(query_conditions)}
            ORDER BY distance
            LIMIT 50
        """
        
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, *query_params)
            
            # Get all games for lookup
            all_games = await self.get_all_games()
            game_lookup = {str(game.id): game for game in all_games}
            
            results = []
            for row in rows:
                # Get user's games
                user_games = []
                for game_id in row['games'] or []:
                    game = game_lookup.get(game_id)
                    if game:
                        user_games.append(game)
                
                # Determine if email should be shown
                email = row['email'] if row['show_email'] else None
                
                result = PlayerSearchResult(
                    user_id=row['id'],
                    username=row['username'],
                    email=email,
                    games=user_games,
                    game_type=GameType(row['game_type']),
                    bio=row['bio'],
                    distance_km=round(row['distance'], 1),
                    location=row['location']
                )
                results.append(result)
            
            return results

    async def _populate_default_games(self) -> None:
        """Populate the games table with default popular wargames."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            # Get game count
            game_count = await conn.fetchval("SELECT COUNT(*) FROM games")
            if game_count > 0:
                return  # Table is not empty
            
            # Insert default games - matching GameSystem enum exactly
            default_games = [
                ("Warhammer 40,000", "The iconic grimdark sci-fi wargame"),
                ("Age of Sigmar", "Fantasy battles in the Mortal Realms"),
                ("Warhammer: The Old World", "Classic fantasy battles in the Old World"),
                ("Horus Heresy", "The galaxy-spanning civil war in the 31st millennium"),
                ("Kill Team", "Small-scale skirmish battles in the 40K universe"),
                ("Warcry", "Fast-paced skirmish combat in Age of Sigmar"),
                ("Warhammer Underworlds", "Competitive deck-based skirmish game"),
                ("Adeptus Titanicus", "Epic-scale Titan warfare"),
                ("Necromunda", "Gang warfare in the underhive"),
                ("Blood Bowl", "Fantasy football with violence"),
                ("Middle-earth SBG", "Battle in Tolkien's world"),
                ("Bolt Action", "World War II historical wargaming"),
                ("Flames of War", "World War II tank combat"),
                ("SAGA", "Dark Age skirmish gaming"),
                ("Kings of War", "Mass fantasy battles"),
                ("Infinity", "Sci-fi skirmish with anime aesthetics"),
                ("Malifaux", "Gothic horror skirmish game"),
                ("Warmachine/Hordes", "Steampunk fantasy battles"),
                ("X-Wing", "Star Wars space combat"),
                ("Star Wars: Legion", "Ground battles in the Star Wars universe"),
                ("BattleTech", "Giant robot combat"),
                ("Dropzone Commander", "10mm sci-fi warfare"),
                ("Guild Ball", "Fantasy sports meets skirmish gaming"),
                ("D&D / RPG", "Dungeons & Dragons and RPG miniatures"),
                ("Pathfinder", "Fantasy RPG miniatures"),
                ("Frostgrave", "Wizard warband skirmish"),
                ("Mordheim", "Skirmish in the City of the Damned"),
                ("Gaslands", "Post-apocalyptic vehicular combat"),
                ("Zombicide", "Cooperative zombie survival"),
                ("Trench Crusade", "Grimdark alternate history warfare"),
                ("Other Game System", "Custom or unlisted game systems")
            ]
            
            for name, description in default_games:
                await conn.execute(
                    "INSERT INTO games (name, description) VALUES ($1, $2) ON CONFLICT (name) DO NOTHING",
                    name, description
                )

    # Project management methods - PostgreSQL implementation
    async def get_all_projects(self, user_id: UUID) -> List[ProjectWithStats]:
        """Get all projects for a user."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT id, name, description, target_completion_date, color, notes, user_id, created_at, updated_at 
                   FROM projects WHERE user_id = $1 ORDER BY created_at DESC""",
                user_id
            )
            
            projects = []
            for row in rows:
                try:
                    # Get miniatures count and status breakdown for this project
                    miniature_rows = await conn.fetch(
                        """SELECT m.status, COUNT(*) as count
                           FROM miniatures m
                           JOIN project_miniatures pm ON m.id = pm.miniature_id
                           WHERE pm.project_id = $1 AND m.user_id = $2
                           GROUP BY m.status""",
                        row['id'], user_id
                    )
                    
                    # Calculate stats
                    miniature_count = 0
                    status_breakdown = {}
                    completed_count = 0
                    
                    for mini_row in miniature_rows:
                        status = mini_row['status']
                        count = mini_row['count']
                        miniature_count += count
                        status_breakdown[status] = count
                        
                        # Count completed miniatures (game_ready or parade_ready)
                        if status in ['game_ready', 'parade_ready']:
                            completed_count += count
                    
                    # Calculate completion percentage
                    completion_percentage = (completed_count / miniature_count * 100) if miniature_count > 0 else 0.0
                    
                    projects.append(ProjectWithStats(
                        id=row['id'],
                        name=row['name'],
                        description=row['description'],
                        target_completion_date=row['target_completion_date'],
                        color=row['color'],
                        notes=row['notes'],
                        user_id=row['user_id'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        miniature_count=miniature_count,
                        completion_percentage=round(completion_percentage, 1),
                        status_breakdown=status_breakdown
                    ))
                except Exception as e:
                    print(f"Error loading project {row.get('id', 'unknown')}: {e}")
                    continue
            
            return projects

    async def get_project_statistics(self, user_id: UUID) -> ProjectStatistics:
        """Get project statistics for a user."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            # Get project count
            project_count = await conn.fetchval(
                "SELECT COUNT(*) FROM projects WHERE user_id = $1",
                user_id
            )
            
            # Get miniatures in projects count
            miniatures_in_projects = await conn.fetchval(
                """SELECT COUNT(DISTINCT pm.miniature_id) 
                   FROM project_miniatures pm 
                   JOIN projects p ON pm.project_id = p.id 
                   WHERE p.user_id = $1""",
                user_id
            )
            
            # Get completion stats (projects with target dates)
            completed_projects = await conn.fetchval(
                """SELECT COUNT(*) FROM projects 
                   WHERE user_id = $1 AND target_completion_date < NOW()""",
                user_id
            )
            
            return ProjectStatistics(
                total_projects=project_count or 0,
                total_miniatures_in_projects=miniatures_in_projects or 0,
                completed_projects=completed_projects or 0,
                average_completion_rate=0.0  # Can be calculated later if needed
            )

    async def get_project(self, project_id: UUID, user_id: UUID) -> Optional[Project]:
        """Get a specific project by ID for a user."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """SELECT id, name, description, target_completion_date, color, notes, user_id, created_at, updated_at 
                   FROM projects WHERE id = $1 AND user_id = $2""",
                project_id, user_id
            )
            
            if row:
                return Project(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    target_completion_date=row['target_completion_date'],
                    color=row['color'],
                    notes=row['notes'],
                    user_id=row['user_id'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
            return None

    async def get_project_with_miniatures(self, project_id: UUID, user_id: UUID) -> Optional[ProjectWithMiniatures]:
        """Get a project with its associated miniatures."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        project = await self.get_project(project_id, user_id)
        if not project:
            return None
        
        async with self._pool.acquire() as conn:
            # Get miniatures in this project
            miniature_rows = await conn.fetch(
                """SELECT m.id, m.name, m.faction, m.model_type, m.status, m.notes, m.user_id, 
                          m.created_at, m.updated_at, m.game_system, m.quantity, m.base_dimension, 
                          m.custom_base_size, m.cost
                   FROM miniatures m
                   JOIN project_miniatures pm ON m.id = pm.miniature_id
                   WHERE pm.project_id = $1 AND m.user_id = $2
                   ORDER BY m.created_at""",
                project_id, user_id
            )
            
            miniatures = []
            for row in miniature_rows:
                try:
                    # Get status history for each miniature
                    status_rows = await conn.fetch(
                        "SELECT id, from_status, to_status, date, notes, is_manual, created_at FROM status_log_entries WHERE miniature_id = $1 ORDER BY created_at",
                        row['id']
                    )
                    
                    status_history = [
                        StatusLogEntry(
                            id=status_row['id'],
                            from_status=status_row['from_status'],
                            to_status=status_row['to_status'],
                            date=status_row['date'],
                            notes=status_row['notes'],
                            is_manual=status_row['is_manual'],
                            created_at=status_row['created_at']
                        ) for status_row in status_rows
                    ]
                    
                    miniature = Miniature(
                        id=row['id'],
                        name=row['name'],
                        faction=row['faction'],
                        unit_type=row['model_type'],
                        status=row['status'],
                        notes=row['notes'],
                        user_id=row['user_id'],
                        status_history=status_history,
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        game_system=row.get('game_system'),
                        quantity=row.get('quantity', 1),
                        base_dimension=row.get('base_dimension'),
                        custom_base_size=row.get('custom_base_size'),
                        cost=row.get('cost')
                    )
                    miniatures.append(miniature)
                except Exception as e:
                    print(f"Error loading miniature {row.get('id', 'unknown')}: {e}")
                    continue
            
            return ProjectWithMiniatures(
                **project.model_dump(),
                miniatures=miniatures
            )

    async def create_project(self, project: ProjectCreate, user_id: UUID) -> Project:
        """Create a new project."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            # Check for duplicate names
            existing = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM projects WHERE name = $1 AND user_id = $2)",
                project.name, user_id
            )
            if existing:
                raise ValueError("Project with this name already exists")
            
            # Create new project
            project_id = uuid4()
            row = await conn.fetchrow(
                """INSERT INTO projects (id, name, description, target_completion_date, color, notes, user_id)
                   VALUES ($1, $2, $3, $4, $5, $6, $7)
                   RETURNING id, name, description, target_completion_date, color, notes, user_id, created_at, updated_at""",
                project_id, project.name, project.description, project.target_completion_date,
                project.color, project.notes, user_id
            )
            
            return Project(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                target_completion_date=row['target_completion_date'],
                color=row['color'],
                notes=row['notes'],
                user_id=row['user_id'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )

    async def update_project(self, project_id: UUID, updates: ProjectUpdate, user_id: UUID) -> Optional[Project]:
        """Update an existing project."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        update_data = updates.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_project(project_id, user_id)
        
        async with self._pool.acquire() as conn:
            # Check for duplicate names if name is being updated
            if "name" in update_data:
                existing = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM projects WHERE name = $1 AND user_id = $2 AND id != $3)",
                    update_data["name"], user_id, project_id
                )
                if existing:
                    raise ValueError("Project with this name already exists")
            
            # Build dynamic update query
            set_clauses = []
            values = []
            param_count = 1
            
            for field, value in update_data.items():
                set_clauses.append(f"{field} = ${param_count}")
                values.append(value)
                param_count += 1
            
            set_clauses.append(f"updated_at = NOW()")
            
            query = f"""UPDATE projects SET {', '.join(set_clauses)}
                       WHERE id = ${param_count} AND user_id = ${param_count + 1}
                       RETURNING id, name, description, target_completion_date, color, notes, user_id, created_at, updated_at"""
            
            values.extend([project_id, user_id])
            
            row = await conn.fetchrow(query, *values)
            if row:
                return Project(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    target_completion_date=row['target_completion_date'],
                    color=row['color'],
                    notes=row['notes'],
                    user_id=row['user_id'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
            return None

    async def delete_project(self, project_id: UUID, user_id: UUID) -> bool:
        """Delete a project."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Delete project_miniature associations first
                await conn.execute(
                    """DELETE FROM project_miniatures 
                       WHERE project_id = $1 AND project_id IN (
                           SELECT id FROM projects WHERE user_id = $2
                       )""",
                    project_id, user_id
                )
                
                # Delete the project
                result = await conn.execute(
                    "DELETE FROM projects WHERE id = $1 AND user_id = $2",
                    project_id, user_id
                )
                return result.split()[-1] != '0'

    async def add_miniature_to_project(self, project_miniature: ProjectMiniatureCreate, user_id: UUID) -> bool:
        """Add a miniature to a project."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            # Verify project and miniature belong to user
            project_exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM projects WHERE id = $1 AND user_id = $2)",
                project_miniature.project_id, user_id
            )
            miniature_exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM miniatures WHERE id = $1 AND user_id = $2)",
                project_miniature.miniature_id, user_id
            )
            
            if not project_exists or not miniature_exists:
                return False
            
            # Check if already exists
            existing = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM project_miniatures WHERE project_id = $1 AND miniature_id = $2)",
                project_miniature.project_id, project_miniature.miniature_id
            )
            if existing:
                raise ValueError("Miniature already exists in project")
            
            # Add the association
            await conn.execute(
                "INSERT INTO project_miniatures (project_id, miniature_id) VALUES ($1, $2)",
                project_miniature.project_id, project_miniature.miniature_id
            )
            return True

    async def remove_miniature_from_project(self, project_id: UUID, miniature_id: UUID, user_id: UUID) -> bool:
        """Remove a miniature from a project."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                """DELETE FROM project_miniatures 
                   WHERE project_id = $1 AND miniature_id = $2 
                   AND project_id IN (SELECT id FROM projects WHERE user_id = $3)""",
                project_id, miniature_id, user_id
            )
            return result.split()[-1] != '0'

    async def add_multiple_miniatures_to_project(self, project_id: UUID, miniature_ids: List[UUID], user_id: UUID) -> int:
        """Add multiple miniatures to a project. Returns count of successfully added miniatures."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Verify project belongs to user
                project_exists = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM projects WHERE id = $1 AND user_id = $2)",
                    project_id, user_id
                )
                if not project_exists:
                    return 0
                
                added_count = 0
                for miniature_id in miniature_ids:
                    # Check if already exists
                    already_exists = await conn.fetchval(
                        "SELECT EXISTS(SELECT 1 FROM project_miniatures WHERE project_id = $1 AND miniature_id = $2)",
                        project_id, miniature_id
                    )
                    if already_exists:
                        continue
                    
                    # Add the association
                    try:
                        await conn.execute(
                            "INSERT INTO project_miniatures (project_id, miniature_id) VALUES ($1, $2)",
                            project_id, miniature_id
                        )
                        added_count += 1
                    except Exception:
                        # Skip if there's an error (e.g., constraint violation)
                        continue
                
                return added_count


class FileDatabase(DatabaseInterface):
    """File-based database implementation (for development)."""
    
    def __init__(self, data_file: str = "data/users.json"):
        """Initialize file database."""
        self.data_file = os.path.join(os.path.dirname(__file__), "..", data_file)
        self.games_file = os.path.join(os.path.dirname(__file__), "..", "data/games.json")
        self.preferences_file = os.path.join(os.path.dirname(__file__), "..", "data/preferences.json")
    
    async def initialize(self) -> None:
        """Initialize file database."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Initialize users file
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f)
        
        # Initialize games file with default games
        if not os.path.exists(self.games_file):
            default_games = [
                {"id": str(uuid4()), "name": "Warhammer 40,000", "description": "The iconic grimdark sci-fi wargame", "is_active": True},
                {"id": str(uuid4()), "name": "Age of Sigmar", "description": "Fantasy battles in the Mortal Realms", "is_active": True},
                {"id": str(uuid4()), "name": "Warhammer: The Old World", "description": "Classic fantasy battles in the Old World", "is_active": True},
                {"id": str(uuid4()), "name": "Horus Heresy", "description": "The galaxy-spanning civil war in the 31st millennium", "is_active": True},
                {"id": str(uuid4()), "name": "Kill Team", "description": "Small-scale skirmish battles in the 40K universe", "is_active": True},
                {"id": str(uuid4()), "name": "Warcry", "description": "Fast-paced skirmish combat in Age of Sigmar", "is_active": True},
                {"id": str(uuid4()), "name": "Warhammer Underworlds", "description": "Competitive deck-based skirmish game", "is_active": True},
                {"id": str(uuid4()), "name": "Adeptus Titanicus", "description": "Epic-scale Titan warfare", "is_active": True},
                {"id": str(uuid4()), "name": "Necromunda", "description": "Gang warfare in the underhive", "is_active": True},
                {"id": str(uuid4()), "name": "Blood Bowl", "description": "Fantasy football with violence", "is_active": True},
                {"id": str(uuid4()), "name": "Middle-earth SBG", "description": "Battle in Tolkien's world", "is_active": True},
                {"id": str(uuid4()), "name": "Bolt Action", "description": "World War II historical wargaming", "is_active": True},
                {"id": str(uuid4()), "name": "Flames of War", "description": "World War II tank combat", "is_active": True},
                {"id": str(uuid4()), "name": "SAGA", "description": "Dark Age skirmish gaming", "is_active": True},
                {"id": str(uuid4()), "name": "Kings of War", "description": "Mass fantasy battles", "is_active": True},
                {"id": str(uuid4()), "name": "Infinity", "description": "Sci-fi skirmish with anime aesthetics", "is_active": True},
                {"id": str(uuid4()), "name": "Malifaux", "description": "Gothic horror skirmish game", "is_active": True},
                {"id": str(uuid4()), "name": "Warmachine/Hordes", "description": "Steampunk fantasy battles", "is_active": True},
                {"id": str(uuid4()), "name": "X-Wing", "description": "Star Wars space combat", "is_active": True},
                {"id": str(uuid4()), "name": "Star Wars: Legion", "description": "Ground battles in the Star Wars universe", "is_active": True},
                {"id": str(uuid4()), "name": "BattleTech", "description": "Giant robot combat", "is_active": True},
                {"id": str(uuid4()), "name": "Dropzone Commander", "description": "10mm sci-fi warfare", "is_active": True},
                {"id": str(uuid4()), "name": "Guild Ball", "description": "Fantasy sports meets skirmish gaming", "is_active": True},
                {"id": str(uuid4()), "name": "D&D / RPG", "description": "Dungeons & Dragons and RPG miniatures", "is_active": True},
                {"id": str(uuid4()), "name": "Pathfinder", "description": "Fantasy RPG miniatures", "is_active": True},
                {"id": str(uuid4()), "name": "Frostgrave", "description": "Wizard warband skirmish", "is_active": True},
                {"id": str(uuid4()), "name": "Mordheim", "description": "Skirmish in the City of the Damned", "is_active": True},
                {"id": str(uuid4()), "name": "Gaslands", "description": "Post-apocalyptic vehicular combat", "is_active": True},
                {"id": str(uuid4()), "name": "Zombicide", "description": "Cooperative zombie survival", "is_active": True},
                {"id": str(uuid4()), "name": "Trench Crusade", "description": "Grimdark alternate history warfare", "is_active": True},
                {"id": str(uuid4()), "name": "Other Game System", "description": "Custom or unlisted game systems", "is_active": True}
            ]
            with open(self.games_file, 'w') as f:
                json.dump(default_games, f, indent=2)
        
        # Initialize preferences file
        if not os.path.exists(self.preferences_file):
            with open(self.preferences_file, 'w') as f:
                json.dump([], f)
    
    def _load_users(self) -> List[dict]:
        """Load users from JSON file."""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_users(self, users: List[dict]) -> None:
        """Save users to JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump(users, f, indent=2, default=str)
    
    def _load_games(self) -> List[dict]:
        """Load games from JSON file."""
        try:
            with open(self.games_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_games(self, games: List[dict]) -> None:
        """Save games to JSON file."""
        with open(self.games_file, 'w') as f:
            json.dump(games, f, indent=2, default=str)
    
    def _load_preferences(self) -> List[dict]:
        """Load preferences from JSON file."""
        try:
            with open(self.preferences_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_preferences(self, preferences: List[dict]) -> None:
        """Save preferences to JSON file."""
        with open(self.preferences_file, 'w') as f:
            json.dump(preferences, f, indent=2, default=str)
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email."""
        users = self._load_users()
        for user_data in users:
            if user_data.get("email") == email:
                return UserInDB(**user_data)
        return None
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        users = self._load_users()
        for user_data in users:
            if user_data.get("id") == str(user_id):
                user_dict = user_data.copy()
                user_dict.pop("hashed_password", None)
                return User(**user_dict)
        return None
    
    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        # Handle password hashing for non-OAuth users
        hashed_password = None
        if user_create.password:
            from app.auth_utils import get_password_hash
            hashed_password = get_password_hash(user_create.password)
        
        user_in_db = UserInDB(
            **user_create.model_dump(exclude={"password"}),
            hashed_password=hashed_password
        )
        
        users = self._load_users()
        
        # Check if user already exists
        if any(u.get("email") == user_create.email for u in users):
            raise ValueError("User with this email already exists")
        
        if any(u.get("username") == user_create.username for u in users):
            raise ValueError("User with this username already exists")
        
        users.append(user_in_db.model_dump())
        self._save_users(users)
        
        return User(**user_in_db.model_dump(exclude={"hashed_password"}))
    
    async def update_user(self, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """Update an existing user."""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == str(user_id):
                update_data = user_update.model_dump(exclude_unset=True)
                if update_data:
                    user_data.update(update_data)
                    user_data["updated_at"] = datetime.utcnow().isoformat()
                    users[i] = user_data
                    self._save_users(users)
                
                user_dict = user_data.copy()
                user_dict.pop("hashed_password", None)
                return User(**user_dict)
        return None
    
    async def get_all_users(self) -> List[User]:
        """Get all users."""
        users = self._load_users()
        user_list = []
        for user_data in users:
            user_dict = user_data.copy()
            user_dict.pop("hashed_password", None)
            user_list.append(User(**user_dict))
        return user_list
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user and all their associated data."""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == str(user_id):
                del users[i]
                self._save_users(users)
                return True
        return False
    
    async def get_all_miniatures(self, user_id: UUID) -> List[Miniature]:
        """Get all miniatures for a user."""
        users = self._load_users()
        miniature_list = []
        for user_data in users:
            if user_data.get("id") == str(user_id):
                miniature_data = user_data.get("miniatures", [])
                miniature_list.extend(miniature_data)
        return [Miniature(**data) for data in miniature_list]
    
    async def get_miniature(self, miniature_id: UUID, user_id: UUID) -> Optional[Miniature]:
        """Get a specific miniature by ID for a user."""
        users = self._load_users()
        for user_data in users:
            if user_data.get("id") == str(user_id):
                miniature_data = user_data.get("miniatures", [])
                for data in miniature_data:
                    if data.get("id") == str(miniature_id):
                        return Miniature(**data)
        return None
    
    async def create_miniature(self, miniature: MiniatureCreate, user_id: UUID) -> Miniature:
        """Create a new miniature."""
        users = self._load_users()
        
        # Check if user exists
        if any(u.get("id") == str(user_id) for u in users):
            miniature_data = {
                "id": str(miniature.id),
                "name": miniature.name,
                "description": miniature.description,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            user_data = next(u for u in users if u.get("id") == str(user_id))
            if user_data.get("miniatures"):
                user_data["miniatures"].append(miniature_data)
            else:
                user_data["miniatures"] = [miniature_data]
            self._save_users(users)
            return Miniature(**miniature_data)
        raise ValueError("User not found")
    
    async def update_miniature(self, miniature_id: UUID, updates: MiniatureUpdate, user_id: UUID) -> Optional[Miniature]:
        """Update an existing miniature."""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == str(user_id):
                miniature_data = user_data.get("miniatures", [])
                for j, data in enumerate(miniature_data):
                    if data.get("id") == str(miniature_id):
                        update_data = updates.model_dump(exclude_unset=True)
                        print(f"🔍 [FileDB] Raw update_data: {update_data}")
                        
                        if update_data:
                            # Convert enum fields to their string values for file storage
                            for field in ['status', 'game_system', 'unit_type', 'base_dimension']:
                                if field in update_data and update_data[field] is not None:
                                    if hasattr(update_data[field], 'value'):
                                        update_data[field] = update_data[field].value
                                        print(f"🔄 [FileDB] Converted {field} to: {update_data[field]}")
                            
                            # Ensure quantity is an integer
                            if 'quantity' in update_data and update_data['quantity'] is not None:
                                update_data['quantity'] = int(update_data['quantity'])
                                print(f"🔢 [FileDB] Converted quantity to int: {update_data['quantity']}")
                            
                            # Update the data
                            data.update(update_data)
                            data["updated_at"] = datetime.utcnow().isoformat()
                            miniature_data[j] = data
                            user_data["updated_at"] = datetime.utcnow().isoformat()
                            users[i] = user_data
                            self._save_users(users)
                            
                            print(f"💾 [FileDB] Saved data: {data}")
                        
                        return Miniature(**data)
        return None
    
    async def delete_miniature(self, miniature_id: UUID, user_id: UUID) -> bool:
        """Delete a miniature."""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == str(user_id):
                miniature_data = user_data.get("miniatures", [])
                for j, data in enumerate(miniature_data):
                    if data.get("id") == str(miniature_id):
                        del miniature_data[j]
                        user_data["updated_at"] = datetime.utcnow().isoformat()
                        users[i] = user_data
                        self._save_users(users)
                        return True
        return False
    
    async def add_status_log_entry(self, miniature_id: UUID, from_status: Optional[str], to_status: str, notes: Optional[str], user_id: UUID) -> Optional[Miniature]:
        """Add a status log entry to a miniature."""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == str(user_id):
                status_log_entries = user_data.get("status_log_entries", [])
                status_log_entry = {
                    "id": str(uuid4()),
                    "from_status": from_status,
                    "to_status": to_status,
                    "notes": notes,
                    "created_at": datetime.utcnow().isoformat()
                }
                status_log_entries.append(status_log_entry)
                user_data["status_log_entries"] = status_log_entries
                user_data["updated_at"] = datetime.utcnow().isoformat()
                users[i] = user_data
                self._save_users(users)
                return Miniature(**status_log_entry)
        return None

    async def delete_status_log_entry(self, miniature_id: UUID, log_id: UUID, user_id: UUID) -> Optional[Miniature]:
        """Delete a status log entry."""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == str(user_id):
                miniature_data = user_data.get("miniatures", [])
                for miniature in miniature_data:
                    if miniature.get("id") == str(miniature_id):
                        status_history = miniature.get("status_history", [])
                        for j, log_entry in enumerate(status_history):
                            if log_entry.get("id") == str(log_id):
                                del status_history[j]
                                miniature["status_history"] = status_history
                                miniature["updated_at"] = datetime.utcnow().isoformat()
                                user_data["updated_at"] = datetime.utcnow().isoformat()
                                users[i] = user_data
                                self._save_users(users)
                                return Miniature(**miniature)
        return None

    async def update_status_log_entry(self, miniature_id: UUID, log_id: UUID, updates: StatusLogEntryUpdate, user_id: UUID) -> Optional[Miniature]:
        """Update a status log entry."""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == str(user_id):
                miniature_data = user_data.get("miniatures", [])
                for j, data in enumerate(miniature_data):
                    if data.get("id") == str(miniature_id):
                        status_history = data.get("status_history", [])
                        for k, log_entry in enumerate(status_history):
                            if log_entry.get("id") == str(log_id):
                                # Update the log entry with new values
                                if updates.to_status is not None:
                                    log_entry["to_status"] = updates.to_status
                                if updates.date is not None:
                                    log_entry["date"] = updates.date.isoformat()
                                if updates.notes is not None:
                                    log_entry["notes"] = updates.notes
                                
                                # Update timestamps
                                data["updated_at"] = datetime.utcnow().isoformat()
                                user_data["updated_at"] = datetime.utcnow().isoformat()
                                users[i] = user_data
                                self._save_users(users)
                                return Miniature(**data)
        return None

    async def get_collection_statistics(self, user_id: UUID) -> CollectionStatistics:
        """Get collection statistics for a user."""
        miniatures = await self.get_all_miniatures(user_id)
        
        if not miniatures:
            return CollectionStatistics(
                total_units=0,
                total_models=0,
                total_cost=None,
                status_breakdown={},
                game_system_breakdown={},
                faction_breakdown={},
                unit_type_breakdown={},
                completion_percentage=0.0
            )
        
        # Calculate statistics
        total_units = len(miniatures)
        total_models = sum(getattr(m, 'quantity', 1) for m in miniatures)
        total_cost = sum(getattr(m, 'cost', 0) or 0 for m in miniatures)
        
        # Status breakdown
        status_breakdown = {}
        for miniature in miniatures:
            status = miniature.status.value if hasattr(miniature.status, 'value') else str(miniature.status)
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
        
        # Game system breakdown
        game_system_breakdown = {}
        for miniature in miniatures:
            game_system = getattr(miniature, 'game_system', None)
            if game_system:
                system_key = game_system.value if hasattr(game_system, 'value') else str(game_system)
                game_system_breakdown[system_key] = game_system_breakdown.get(system_key, 0) + 1
        
        # Faction breakdown
        faction_breakdown = {}
        for miniature in miniatures:
            faction = miniature.faction
            faction_breakdown[faction] = faction_breakdown.get(faction, 0) + 1
        
        # Unit type breakdown
        unit_type_breakdown = {}
        for miniature in miniatures:
            unit_type = getattr(miniature, 'unit_type', None)
            if unit_type:
                type_key = unit_type.value if hasattr(unit_type, 'value') else str(unit_type)
                unit_type_breakdown[type_key] = unit_type_breakdown.get(type_key, 0) + 1
        
        # Calculate completion percentage (painted vs total)
        completed_statuses = ['painted', 'completed', 'finished']
        completed_units = sum(
            count for status, count in status_breakdown.items() 
            if status.lower() in completed_statuses
        )
        completion_percentage = (completed_units / total_units * 100) if total_units > 0 else 0.0
        
        return CollectionStatistics(
            total_units=total_units,
            total_models=total_models,
            total_cost=total_cost if total_cost > 0 else None,
            status_breakdown=status_breakdown,
            game_system_breakdown=game_system_breakdown,
            faction_breakdown=faction_breakdown,
            unit_type_breakdown=unit_type_breakdown,
            completion_percentage=round(completion_percentage, 1)
        )

    # Game management methods
    async def get_all_games(self) -> List[Game]:
        """Get all available games."""
        games = self._load_games()
        return [Game(**game) for game in games]
    
    async def create_game(self, name: str, description: Optional[str] = None) -> Game:
        """Create a new game."""
        games = self._load_games()
        game_id = str(uuid4())
        game = Game(
            id=game_id,
            name=name,
            description=description,
            is_active=True
        )
        games.append(game.model_dump())
        self._save_games(games)
        return game

    # User preferences methods
    async def get_user_preferences(self, user_id: UUID) -> Optional[UserPreferences]:
        """Get user preferences by user ID."""
        preferences = self._load_preferences()
        for preference in preferences:
            if preference.get("user_id") == str(user_id):
                return UserPreferences(**preference)
        return None
    
    async def create_user_preferences(self, user_id: UUID, preferences_create: UserPreferencesCreate) -> UserPreferences:
        """Create user preferences."""
        preferences_list = self._load_preferences()
        preference_id = str(uuid4())
        
        # Geocode address to get coordinates
        print(f"🔍 [FileDB] Geocoding location: '{preferences_create.location}'")
        try:
            coordinates = await GeocodingService.get_coordinates_from_address(preferences_create.location)
            latitude = coordinates[0] if coordinates else None
            longitude = coordinates[1] if coordinates else None
            print(f"📍 [FileDB] Geocoding result: lat={latitude}, lon={longitude}")
        except Exception as e:
            print(f"❌ [FileDB] Geocoding error: {e}")
            latitude = None
            longitude = None
        
        preference = UserPreferences(
            id=preference_id,
            user_id=user_id,
            games=preferences_create.games,
            location=preferences_create.location,
            game_type=preferences_create.game_type,
            bio=preferences_create.bio,
            show_email=preferences_create.show_email,
            theme=preferences_create.theme,
            latitude=latitude,
            longitude=longitude
        )
        preferences_list.append(preference.model_dump())
        self._save_preferences(preferences_list)
        print(f"💾 [FileDB] Saved with coordinates: lat={latitude}, lon={longitude}")
        return preference
    
    async def update_user_preferences(self, user_id: UUID, updates: UserPreferencesUpdate) -> Optional[UserPreferences]:
        """Update user preferences."""
        preferences = self._load_preferences()
        for i, preference in enumerate(preferences):
            if preference.get("user_id") == str(user_id):
                update_data = updates.model_dump(exclude_unset=True)
                if update_data:
                    # Geocode location if it changed
                    if 'location' in update_data and update_data['location'] is not None:
                        print(f"🔍 [FileDB] Geocoding updated location: '{update_data['location']}'")
                        try:
                            coordinates = await GeocodingService.get_coordinates_from_address(update_data['location'])
                            if coordinates:
                                update_data['latitude'] = coordinates[0]
                                update_data['longitude'] = coordinates[1]
                                print(f"📍 [FileDB] Updated geocoding result: lat={coordinates[0]}, lon={coordinates[1]}")
                            else:
                                update_data['latitude'] = None
                                update_data['longitude'] = None
                                print(f"❌ [FileDB] No coordinates found for location")
                        except Exception as e:
                            print(f"❌ [FileDB] Geocoding error: {e}")
                            update_data['latitude'] = None
                            update_data['longitude'] = None
                    
                    for key, value in update_data.items():
                        if key in preference:
                            preference[key] = value
                    preference["updated_at"] = datetime.utcnow().isoformat()
                    preferences[i] = preference
                    self._save_preferences(preferences)
                
                return UserPreferences(**preference)
        return None
    
    async def search_players(self, request: PlayerSearchRequest, user_id: UUID) -> List[PlayerSearchResult]:
        """Search for players based on location and game preferences."""
        # Get searcher's preferences to find their location
        searcher_prefs = await self.get_user_preferences(user_id)
        if not searcher_prefs or not searcher_prefs.latitude or not searcher_prefs.longitude:
            return []  # Searcher has no location set
        
        searcher_lat = float(searcher_prefs.latitude)
        searcher_lon = float(searcher_prefs.longitude)
        
        # Load all preferences and users
        preferences = self._load_preferences()
        users = self._load_users()
        games = self._load_games()
        
        # Create user lookup
        user_lookup = {user['id']: user for user in users}
        game_lookup = {game['id']: game for game in games}
        
        results = []
        
        for pref in preferences:
            # Skip searcher themselves
            if pref.get('user_id') == str(user_id):
                continue
                
            # Skip if no coordinates
            if not pref.get('latitude') or not pref.get('longitude'):
                continue
            
            pref_lat = float(pref['latitude'])
            pref_lon = float(pref['longitude'])
            
            # Calculate distance using Haversine formula
            def haversine_distance(lat1, lon1, lat2, lon2):
                R = 6371  # Earth's radius in kilometers
                
                lat1_rad = math.radians(lat1)
                lon1_rad = math.radians(lon1)
                lat2_rad = math.radians(lat2)
                lon2_rad = math.radians(lon2)
                
                dlat = lat2_rad - lat1_rad
                dlon = lon2_rad - lon1_rad
                
                a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
                c = 2 * math.asin(math.sqrt(a))
                
                return R * c
            
            distance_km = haversine_distance(searcher_lat, searcher_lon, pref_lat, pref_lon)
            
            # Filter by distance
            if distance_km > request.max_distance_km:
                continue
            
            # Filter by games if specified
            if request.games:
                pref_games = set(pref.get('games', []))
                search_games = set(str(g) for g in request.games)
                if not pref_games.intersection(search_games):
                    continue
            
            # Filter by game type if specified
            if request.game_type and pref.get('game_type') != request.game_type.value:
                continue
            
            # Get user details
            user = user_lookup.get(pref['user_id'])
            if not user:
                continue
            
            # Get game details
            user_games = []
            for game_id in pref.get('games', []):
                game = game_lookup.get(game_id)
                if game:
                    user_games.append(game)
            
            # Create result
            result = PlayerSearchResult(
                user_id=pref['user_id'],
                username=user['username'],
                email=user['email'] if pref.get('show_email') else None,
                games=user_games,
                game_type=GameType(pref.get('game_type', 'competitive')),
                bio=pref.get('bio'),
                distance_km=round(distance_km, 2),
                location=pref['location'][:10] + "***" if len(pref['location']) > 10 else pref['location']
            )
            results.append(result)
        
        # Sort by distance
        results.sort(key=lambda x: x.distance_km)
        
        return results[:50]  # Limit to 50 results

    async def get_trend_analysis(self, user_id: UUID, from_date: Optional[str] = None, to_date: Optional[str] = None, group_by: str = "month") -> TrendAnalysis:
        """Get trend analysis for a user's collection."""
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        # Set default date range if not provided
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        if not from_date:
            # Default to 12 months ago
            from_datetime = datetime.now() - timedelta(days=365)
            from_date = from_datetime.strftime("%Y-%m-%d")
        
        # Get all miniatures for the user
        miniatures = await self.get_all_miniatures(user_id)
        
        # Initialize data structures
        purchases_by_period = defaultdict(lambda: {"count": 0, "cost": 0.0})
        status_changes_by_period = defaultdict(lambda: defaultdict(int))
        
        # Helper function to get period key based on group_by
        def get_period_key(date_obj):
            if group_by == "day":
                return date_obj.strftime("%Y-%m-%d")
            elif group_by == "week":
                # Get Monday of the week
                monday = date_obj - timedelta(days=date_obj.weekday())
                return monday.strftime("%Y-%m-%d")
            elif group_by == "month":
                return date_obj.strftime("%Y-%m")
            elif group_by == "year":
                return date_obj.strftime("%Y")
            else:
                return date_obj.strftime("%Y-%m")
        
        # Process each miniature
        for miniature in miniatures:
            # Process status history
            for log_entry in miniature.status_history:
                log_date = log_entry.date if hasattr(log_entry, 'date') else log_entry.created_at
                
                # Check if log entry is within date range
                if from_date <= log_date.strftime("%Y-%m-%d") <= to_date:
                    period_key = get_period_key(log_date)
                    
                    # Track purchases (transitions to "purchased" status)
                    if log_entry.to_status == "purchased":
                        purchases_by_period[period_key]["count"] += 1
                        if miniature.cost:
                            purchases_by_period[period_key]["cost"] += float(miniature.cost)
                    
                    # Track all status changes
                    status_changes_by_period[period_key][log_entry.to_status] += 1
        
        # Generate time series data
        from_datetime = datetime.strptime(from_date, "%Y-%m-%d")
        to_datetime = datetime.strptime(to_date, "%Y-%m-%d")
        
        # Generate all periods in range
        all_periods = []
        current = from_datetime
        while current <= to_datetime:
            period_key = get_period_key(current)
            if period_key not in all_periods:
                all_periods.append(period_key)
            
            # Increment based on group_by
            if group_by == "day":
                current += timedelta(days=1)
            elif group_by == "week":
                current += timedelta(weeks=1)
            elif group_by == "month":
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
            elif group_by == "year":
                current = current.replace(year=current.year + 1)
            else:
                current += timedelta(days=30)  # Default monthly
        
        # Build purchase trend data
        purchases_over_time = []
        spending_over_time = []
        for period in sorted(all_periods):
            data = purchases_by_period[period]
            purchases_over_time.append(TrendDataPoint(
                date=period,
                count=data["count"]
            ))
            spending_over_time.append(TrendDataPoint(
                date=period,
                count=0,  # Not used for spending
                cost=data["cost"] if data["cost"] > 0 else None
            ))
        
        # Build status trend data
        from app.models import PaintingStatus
        status_trends = []
        for status in PaintingStatus:
            data_points = []
            for period in sorted(all_periods):
                count = status_changes_by_period[period].get(status.value, 0)
                data_points.append(TrendDataPoint(
                    date=period,
                    count=count
                ))
            status_trends.append(StatusTrendData(
                status=status,
                data_points=data_points
            ))
        
        # Calculate summary statistics
        total_purchased = sum(data["count"] for data in purchases_by_period.values())
        total_spent = sum(data["cost"] for data in purchases_by_period.values())
        
        # Find most active month
        most_active_month = None
        max_purchases = 0
        for period, data in purchases_by_period.items():
            if data["count"] > max_purchases:
                max_purchases = data["count"]
                most_active_month = period
        
        # Calculate averages
        num_periods = len(all_periods) if all_periods else 1
        average_monthly_purchases = total_purchased / num_periods
        average_monthly_spending = total_spent / num_periods if total_spent > 0 else None
        
        return TrendAnalysis(
            date_range={"from": from_date, "to": to_date},
            purchases_over_time=purchases_over_time,
            spending_over_time=spending_over_time,
            status_trends=status_trends,
            total_purchased=total_purchased,
            total_spent=total_spent if total_spent > 0 else None,
            most_active_month=most_active_month,
            average_monthly_purchases=round(average_monthly_purchases, 1),
            average_monthly_spending=round(average_monthly_spending, 2) if average_monthly_spending else None
        )

    # Project management methods
    async def get_all_projects(self, user_id: UUID) -> List[ProjectWithStats]:
        """Get all projects for a user."""
        users = self._load_users()
        
        for user_data in users:
            if user_data.get("id") == str(user_id):
                projects_data = user_data.get("projects", [])
                projects = []
                for data in projects_data:
                    try:
                        # Get miniatures for this project to calculate stats
                        project_miniatures = await self._get_project_miniatures(UUID(data["id"]), user_id)
                        
                        # Calculate stats
                        miniature_count = len(project_miniatures)
                        status_breakdown = {}
                        completed_count = 0
                        
                        for miniature in project_miniatures:
                            status = miniature.status.value
                            status_breakdown[status] = status_breakdown.get(status, 0) + 1
                            
                            # Count completed miniatures (game_ready or parade_ready)
                            if status in ['game_ready', 'parade_ready']:
                                completed_count += 1
                        
                        # Calculate completion percentage
                        completion_percentage = (completed_count / miniature_count * 100) if miniature_count > 0 else 0.0
                        
                        project = ProjectWithStats(
                            **data,
                            miniature_count=miniature_count,
                            completion_percentage=round(completion_percentage, 1),
                            status_breakdown=status_breakdown
                        )
                        projects.append(project)
                    except Exception as e:
                        print(f"Error loading project {data.get('id', 'unknown')}: {e}")
                        continue
                return projects
        return []
    
    async def get_project_statistics(self, user_id: UUID) -> ProjectStatistics:
        """Get project statistics for a user."""
        projects = await self.get_all_projects(user_id)
        miniatures = await self.get_all_miniatures(user_id)
        
        total_projects = len(projects)
        active_projects = len([p for p in projects if hasattr(p, 'target_date') and p.target_date])
        completed_projects = 0  # We'll calculate this based on project completion
        
        # Calculate completion rates for projects with miniatures
        completion_rates = []
        for project in projects:
            project_miniatures = await self._get_project_miniatures(project.id, user_id)
            if project_miniatures:
                completed_count = len([m for m in project_miniatures if m.status.value in ['game_ready', 'parade_ready']])
                completion_rate = (completed_count / len(project_miniatures)) * 100
                completion_rates.append(completion_rate)
                if completion_rate == 100:
                    completed_projects += 1
        
        average_completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 0.0
        
        return ProjectStatistics(
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            average_completion_rate=round(average_completion_rate, 1)
        )
    
    async def get_project(self, project_id: UUID, user_id: UUID) -> Optional[Project]:
        """Get a specific project by ID for a user."""
        users = self._load_users()
        
        for user_data in users:
            if user_data.get("id") == str(user_id):
                projects_data = user_data.get("projects", [])
                for data in projects_data:
                    if data.get("id") == str(project_id):
                        try:
                            return Project(**data)
                        except Exception as e:
                            print(f"Error loading project {project_id}: {e}")
                            return None
        return None
    
    async def get_project_with_miniatures(self, project_id: UUID, user_id: UUID) -> Optional[ProjectWithMiniatures]:
        """Get a project with its associated miniatures."""
        project = await self.get_project(project_id, user_id)
        if not project:
            return None
        
        project_miniatures = await self._get_project_miniatures(project_id, user_id)
        
        return ProjectWithMiniatures(
            **project.model_dump(),
            miniatures=project_miniatures
        )
    
    async def _get_project_miniatures(self, project_id: UUID, user_id: UUID) -> List[Miniature]:
        """Helper method to get miniatures for a project."""
        users = self._load_users()
        
        for user_data in users:
            if user_data.get("id") == str(user_id):
                project_miniatures_data = user_data.get("project_miniatures", [])
                miniature_ids = [
                    pm["miniature_id"] for pm in project_miniatures_data 
                    if pm.get("project_id") == str(project_id)
                ]
                
                # Get the actual miniature objects
                miniatures_data = user_data.get("miniatures", [])
                project_miniatures = []
                for data in miniatures_data:
                    if data.get("id") in miniature_ids:
                        try:
                            miniature = Miniature(**data)
                            project_miniatures.append(miniature)
                        except Exception as e:
                            print(f"Error loading miniature {data.get('id', 'unknown')}: {e}")
                            continue
                return project_miniatures
        return []
    
    async def create_project(self, project: ProjectCreate, user_id: UUID) -> Project:
        """Create a new project."""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == str(user_id):
                projects_data = user_data.get("projects", [])
                
                # Check for duplicate names
                for existing_project in projects_data:
                    if existing_project.get("name") == project.name:
                        raise ValueError("Project with this name already exists")
                
                # Create new project
                new_project = Project(
                    **project.model_dump(),
                    user_id=user_id
                )
                
                projects_data.append(new_project.model_dump())
                user_data["projects"] = projects_data
                users[i] = user_data
                self._save_users(users)
                
                return new_project
        
        raise ValueError("User not found")
    
    async def update_project(self, project_id: UUID, updates: ProjectUpdate, user_id: UUID) -> Optional[Project]:
        """Update an existing project."""
        users = self._load_users()
        
        update_data = updates.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_project(project_id, user_id)
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == str(user_id):
                projects_data = user_data.get("projects", [])
                for j, data in enumerate(projects_data):
                    if data.get("id") == str(project_id):
                        # Check for duplicate names if name is being updated
                        if "name" in update_data:
                            for other_project in projects_data:
                                if (other_project.get("id") != str(project_id) and 
                                    other_project.get("name") == update_data["name"]):
                                    raise ValueError("Project with this name already exists")
                        
                        # Update the project data
                        data.update(update_data)
                        data["updated_at"] = datetime.now().isoformat()
                        
                        projects_data[j] = data
                        user_data["projects"] = projects_data
                        users[i] = user_data
                        self._save_users(users)
                        
                        return Project(**data)
        return None
    
    async def delete_project(self, project_id: UUID, user_id: UUID) -> bool:
        """Delete a project."""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == str(user_id):
                projects_data = user_data.get("projects", [])
                original_length = len(projects_data)
                
                # Remove the project
                projects_data = [p for p in projects_data if p.get("id") != str(project_id)]
                
                if len(projects_data) < original_length:
                    # Also remove all project_miniature associations
                    project_miniatures_data = user_data.get("project_miniatures", [])
                    project_miniatures_data = [
                        pm for pm in project_miniatures_data 
                        if pm.get("project_id") != str(project_id)
                    ]
                    
                    user_data["projects"] = projects_data
                    user_data["project_miniatures"] = project_miniatures_data
                    users[i] = user_data
                    self._save_users(users)
                    return True
        return False
    
    async def add_miniature_to_project(self, project_miniature: ProjectMiniatureCreate, user_id: UUID) -> bool:
        """Add a miniature to a project."""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == str(user_id):
                project_miniatures_data = user_data.get("project_miniatures", [])
                
                # Check if already exists
                for pm in project_miniatures_data:
                    if (pm.get("project_id") == str(project_miniature.project_id) and 
                        pm.get("miniature_id") == str(project_miniature.miniature_id)):
                        raise ValueError("Miniature already exists in project")
                
                # Add the association
                new_association = ProjectMiniature(
                    project_id=project_miniature.project_id,
                    miniature_id=project_miniature.miniature_id
                )
                
                project_miniatures_data.append(new_association.model_dump())
                user_data["project_miniatures"] = project_miniatures_data
                users[i] = user_data
                self._save_users(users)
                return True
        return False
    
    async def remove_miniature_from_project(self, project_id: UUID, miniature_id: UUID, user_id: UUID) -> bool:
        """Remove a miniature from a project."""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == str(user_id):
                project_miniatures_data = user_data.get("project_miniatures", [])
                original_length = len(project_miniatures_data)
                
                # Remove the association
                project_miniatures_data = [
                    pm for pm in project_miniatures_data 
                    if not (pm.get("project_id") == str(project_id) and 
                           pm.get("miniature_id") == str(miniature_id))
                ]
                
                if len(project_miniatures_data) < original_length:
                    user_data["project_miniatures"] = project_miniatures_data
                    users[i] = user_data
                    self._save_users(users)
                    return True
        return False
    
    async def add_multiple_miniatures_to_project(self, project_id: UUID, miniature_ids: List[UUID], user_id: UUID) -> int:
        """Add multiple miniatures to a project. Returns count of successfully added miniatures."""
        users = self._load_users()
        added_count = 0
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == str(user_id):
                project_miniatures_data = user_data.get("project_miniatures", [])
                
                for miniature_id in miniature_ids:
                    # Check if already exists
                    already_exists = any(
                        pm.get("project_id") == str(project_id) and 
                        pm.get("miniature_id") == str(miniature_id)
                        for pm in project_miniatures_data
                    )
                    
                    if not already_exists:
                        # Add the association
                        new_association = ProjectMiniature(
                            project_id=project_id,
                            miniature_id=miniature_id
                        )
                        project_miniatures_data.append(new_association.model_dump())
                        added_count += 1
                
                if added_count > 0:
                    user_data["project_miniatures"] = project_miniatures_data
                    users[i] = user_data
                    self._save_users(users)
                break
        
        return added_count


# Global database instance to ensure singleton pattern
_database_instance: Optional[DatabaseInterface] = None

def get_database() -> DatabaseInterface:
    """Get database instance based on environment (singleton pattern)."""
    global _database_instance
    
    if _database_instance is not None:
        return _database_instance
    
    database_url = os.getenv("DATABASE_URL")
    
    if database_url and database_url.startswith("postgresql"):
        _database_instance = PostgreSQLDatabase(database_url)
    else:
        _database_instance = FileDatabase()
    
    return _database_instance 