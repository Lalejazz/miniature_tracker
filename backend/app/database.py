"""Database abstraction layer for miniature tracker."""

import json
import os
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

try:
    import asyncpg
except ImportError:
    asyncpg = None

from app.auth_models import User, UserCreate, UserInDB, UserUpdate
from app.models import (
    PasswordResetToken, Miniature, MiniatureCreate, MiniatureUpdate, StatusLogEntry,
    Game, UserPreferences, UserPreferencesCreate, UserPreferencesUpdate,
    PlayerSearchRequest, PlayerSearchResult, GameType
)


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
    async def create_user_preferences(self, user_id: UUID, preferences: UserPreferencesCreate) -> UserPreferences:
        """Create user preferences."""
        pass

    @abstractmethod
    async def update_user_preferences(self, user_id: UUID, updates: UserPreferencesUpdate) -> Optional[UserPreferences]:
        """Update user preferences."""
        pass

    @abstractmethod
    async def search_players(self, searcher_user_id: UUID, search_request: PlayerSearchRequest) -> List[PlayerSearchResult]:
        """Search for players based on criteria."""
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
                hashed_password TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
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
            
            # Copy description to notes if notes is empty and description exists
            await self._pool.execute("""
                UPDATE miniatures 
                SET notes = description 
                WHERE notes IS NULL AND description IS NOT NULL
            """)
            
            # Set default values for required columns if they're NULL
            await self._pool.execute("UPDATE miniatures SET faction = 'Unknown' WHERE faction IS NULL")
            await self._pool.execute("UPDATE miniatures SET model_type = 'Unknown' WHERE model_type IS NULL")
            
            # Now make faction and model_type NOT NULL
            await self._pool.execute("ALTER TABLE miniatures ALTER COLUMN faction SET NOT NULL")
            await self._pool.execute("ALTER TABLE miniatures ALTER COLUMN model_type SET NOT NULL")
            
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
                notes TEXT,
                is_manual BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
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
                postcode VARCHAR(20) NOT NULL,
                game_types TEXT[] DEFAULT '{}',
                bio TEXT NOT NULL CHECK (length(bio) <= 160),
                latitude DECIMAL(10, 8),
                longitude DECIMAL(11, 8),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create indexes
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_reset_tokens_token ON password_reset_tokens(token)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_miniatures_name ON miniatures(name)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_games_name ON games(name)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_user_preferences_postcode ON user_preferences(postcode)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_user_preferences_location ON user_preferences(latitude, longitude)")
        
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
                "SELECT id, email, username, is_active, created_at, updated_at FROM users WHERE id = $1", 
                user_id
            )
            if row:
                return User(**dict(row))
        return None
    
    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user."""
        from app.auth_utils import get_password_hash
        
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        user_in_db = UserInDB(
            **user_create.model_dump(exclude={"password"}),
            hashed_password=get_password_hash(user_create.password)
        )
        
        async with self._pool.acquire() as conn:
            try:
                await conn.execute("""
                    INSERT INTO users (id, email, username, hashed_password, is_active, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, 
                user_in_db.id, user_in_db.email, user_in_db.username, 
                user_in_db.hashed_password, user_in_db.is_active,
                user_in_db.created_at, user_in_db.updated_at
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
            RETURNING id, email, username, is_active, created_at, updated_at
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
                "SELECT id, email, username, is_active, created_at, updated_at FROM users ORDER BY created_at"
            )
            return [User(**dict(row)) for row in rows]
    
    async def get_all_miniatures(self, user_id: UUID) -> List[Miniature]:
        """Get all miniatures for a user."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
            
        async with self._pool.acquire() as conn:
            # Get miniatures
            miniature_rows = await conn.fetch(
                "SELECT id, name, faction, model_type, status, notes, user_id, created_at, updated_at FROM miniatures WHERE user_id = $1 ORDER BY created_at",
                user_id
            )
            
            miniatures = []
            for row in miniature_rows:
                # Get status history for this miniature
                status_rows = await conn.fetch(
                    "SELECT id, from_status, to_status, notes, is_manual, created_at FROM status_log_entries WHERE miniature_id = $1 ORDER BY created_at",
                    row['id']
                )
                
                status_history = [
                    StatusLogEntry(
                        id=status_row['id'],
                        from_status=status_row['from_status'],
                        to_status=status_row['to_status'],
                        notes=status_row['notes'],
                        is_manual=status_row['is_manual'],
                        created_at=status_row['created_at']
                    ) for status_row in status_rows
                ]
                
                miniature = Miniature(
                    id=row['id'],
                    name=row['name'],
                    faction=row['faction'],
                    model_type=row['model_type'],
                    status=row['status'],
                    notes=row['notes'],
                    user_id=row['user_id'],
                    status_history=status_history,
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
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
                "SELECT id, name, faction, model_type, status, notes, user_id, created_at, updated_at FROM miniatures WHERE id = $1 AND user_id = $2",
                miniature_id, user_id
            )
            if not row:
                return None
            
            # Get status history
            status_rows = await conn.fetch(
                "SELECT id, from_status, to_status, notes, is_manual, created_at FROM status_log_entries WHERE miniature_id = $1 ORDER BY created_at",
                miniature_id
            )
            
            status_history = [
                StatusLogEntry(
                    id=status_row['id'],
                    from_status=status_row['from_status'],
                    to_status=status_row['to_status'],
                    notes=status_row['notes'],
                    is_manual=status_row['is_manual'],
                    created_at=status_row['created_at']
                ) for status_row in status_rows
            ]
            
            return Miniature(
                id=row['id'],
                name=row['name'],
                faction=row['faction'],
                model_type=row['model_type'],
                status=row['status'],
                notes=row['notes'],
                user_id=row['user_id'],
                status_history=status_history,
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
    
    async def create_miniature(self, miniature: MiniatureCreate, user_id: UUID) -> Miniature:
        """Create a new miniature."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        # Generate ID for the miniature
        miniature_id = uuid4()
        
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Insert miniature
                miniature_row = await conn.fetchrow(
                    "INSERT INTO miniatures (id, name, faction, model_type, status, notes, user_id) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id, name, faction, model_type, status, notes, user_id, created_at, updated_at",
                    miniature_id, miniature.name, miniature.faction, miniature.model_type, miniature.status.value, miniature.notes, user_id
                )
                
                # Add initial status log entry
                status_entry = await conn.fetchrow(
                    "INSERT INTO status_log_entries (id, miniature_id, user_id, from_status, to_status, notes, is_manual) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id, from_status, to_status, notes, is_manual, created_at",
                    uuid4(), miniature_id, user_id, None, miniature.status.value, None, False
                )
                
                status_history = [StatusLogEntry(
                    id=status_entry['id'],
                    from_status=status_entry['from_status'],
                    to_status=status_entry['to_status'],
                    notes=status_entry['notes'],
                    is_manual=status_entry['is_manual'],
                    created_at=status_entry['created_at']
                )]
                
                return Miniature(
                    id=miniature_row['id'],
                    name=miniature_row['name'],
                    faction=miniature_row['faction'],
                    model_type=miniature_row['model_type'],
                    status=miniature_row['status'],
                    notes=miniature_row['notes'],
                    user_id=miniature_row['user_id'],
                    status_history=status_history,
                    created_at=miniature_row['created_at'],
                    updated_at=miniature_row['updated_at']
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
                    RETURNING id, name, faction, model_type, status, notes, user_id, created_at, updated_at
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
                
                # Get updated miniature with status history
                return await self.get_miniature(miniature_id, user_id)
    
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
                # Verify miniature exists
                exists = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM miniatures WHERE id = $1 AND user_id = $2)",
                    miniature_id, user_id
                )
                if not exists:
                    return None
                
                # Add status log entry
                await conn.execute(
                    "INSERT INTO status_log_entries (id, miniature_id, user_id, from_status, to_status, notes, is_manual) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                    uuid4(), miniature_id, user_id, from_status, to_status, notes, True
                )
                
                # Update miniature status
                await conn.execute(
                    "UPDATE miniatures SET status = $1, updated_at = NOW() WHERE id = $2 AND user_id = $3",
                    to_status, miniature_id, user_id
                )
                
                # Return updated miniature
                return await self.get_miniature(miniature_id, user_id)

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
                "SELECT id, user_id, games, postcode, game_types, bio, latitude, longitude, created_at, updated_at FROM user_preferences WHERE user_id = $1",
                user_id
            )
            if row:
                return UserPreferences(**dict(row))
        return None
    
    async def create_user_preferences(self, user_id: UUID, preferences: UserPreferencesCreate) -> UserPreferences:
        """Create user preferences."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        preferences_id = uuid4()
        async with self._pool.acquire() as conn:
            try:
                row = await conn.fetchrow(
                    """INSERT INTO user_preferences (id, user_id, games, postcode, game_types, bio) 
                       VALUES ($1, $2, $3, $4, $5, $6) 
                       RETURNING id, user_id, games, postcode, game_types, bio, latitude, longitude, created_at, updated_at""",
                    preferences_id, user_id, [str(g) for g in preferences.games], preferences.postcode, 
                    [gt.value for gt in preferences.game_types], preferences.bio
                )
                return UserPreferences(**dict(row))
            except Exception as e:
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
        if 'game_types' in update_data and update_data['game_types'] is not None:
            update_data['game_types'] = [gt.value for gt in update_data['game_types']]
        
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
                RETURNING id, user_id, games, postcode, game_types, bio, latitude, longitude, created_at, updated_at
            """
            
            row = await conn.fetchrow(query, *values)
            if row:
                return UserPreferences(**dict(row))
        return None
    
    async def search_players(self, searcher_user_id: UUID, search_request: PlayerSearchRequest) -> List[PlayerSearchResult]:
        """Search for players based on criteria."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        # Get searcher's location for distance calculation
        async with self._pool.acquire() as conn:
            searcher_row = await conn.fetchrow(
                "SELECT latitude, longitude FROM user_preferences WHERE user_id = $1",
                searcher_user_id
            )
            if not searcher_row or not searcher_row['latitude'] or not searcher_row['longitude']:
                return []  # Searcher has no location set
            
            searcher_lat = float(searcher_row['latitude'])
            searcher_lon = float(searcher_row['longitude'])
            
            # Build search query with filters
            where_clauses = ["up.user_id != $1", "up.latitude IS NOT NULL", "up.longitude IS NOT NULL"]
            params = [searcher_user_id]
            param_count = 1
            
            # Filter by games if specified
            if search_request.games:
                param_count += 1
                where_clauses.append(f"up.games && ${param_count}")
                params.append([str(g) for g in search_request.games])
            
            # Filter by game types if specified
            if search_request.game_types:
                param_count += 1
                where_clauses.append(f"up.game_types && ${param_count}")
                params.append([gt.value for gt in search_request.game_types])
            
            # Distance calculation using Haversine formula
            distance_formula = f"""
                (6371 * acos(
                    cos(radians({searcher_lat})) * cos(radians(up.latitude)) *
                    cos(radians(up.longitude) - radians({searcher_lon})) +
                    sin(radians({searcher_lat})) * sin(radians(up.latitude))
                ))
            """
            
            query = f"""
                SELECT u.id as user_id, u.username, up.games, up.game_types, up.bio, up.postcode,
                       {distance_formula} as distance_km
                FROM user_preferences up
                JOIN users u ON up.user_id = u.id
                WHERE {' AND '.join(where_clauses)}
                  AND {distance_formula} <= {search_request.max_distance_km}
                ORDER BY distance_km
                LIMIT 50
            """
            
            rows = await conn.fetch(query, *params)
            
            # Convert to results
            results = []
            for row in rows:
                # Get game details
                game_rows = await conn.fetch(
                    "SELECT id, name, description, is_active FROM games WHERE id = ANY($1)",
                    row['games'] if row['games'] else []
                )
                games = [Game(**dict(game_row)) for game_row in game_rows]
                
                results.append(PlayerSearchResult(
                    user_id=row['user_id'],
                    username=row['username'],
                    games=games,
                    game_types=[GameType(gt) for gt in row['game_types']] if row['game_types'] else [],
                    bio=row['bio'],
                    distance_km=round(float(row['distance_km']), 2),
                    postcode=row['postcode'][:4] + "***"  # Partial postcode for privacy
                ))
            
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
            
            # Insert default games
            default_games = [
                ("Warhammer 40,000", "The iconic grimdark sci-fi wargame"),
                ("Age of Sigmar", "Fantasy battles in the Mortal Realms"),
                ("Kill Team", "Small-scale skirmish battles in the 40K universe"),
                ("Warcry", "Fast-paced skirmish combat in Age of Sigmar"),
                ("Bolt Action", "World War II historical wargaming"),
                ("SAGA", "Dark Age skirmish gaming"),
                ("Art de la Guerre", "Ancient and medieval warfare"),
                ("Kings of War", "Mass fantasy battles"),
                ("Flames of War", "World War II tank combat"),
                ("X-Wing", "Star Wars space combat"),
                ("Star Wars Legion", "Ground battles in the Star Wars universe"),
                ("Infinity", "Sci-fi skirmish with anime aesthetics"),
                ("Malifaux", "Gothic horror skirmish game"),
                ("Guild Ball", "Fantasy sports meets skirmish gaming"),
                ("Blood Bowl", "Fantasy football with violence"),
                ("Necromunda", "Gang warfare in the underhive"),
                ("Middle-earth Strategy Battle Game", "Battle in Tolkien's world"),
                ("Battletech", "Giant robot combat"),
                ("Dropzone Commander", "10mm sci-fi warfare"),
                ("Warmachine/Hordes", "Steampunk fantasy battles")
            ]
            
            for name, description in default_games:
                await conn.execute(
                    "INSERT INTO games (name, description) VALUES ($1, $2) ON CONFLICT (name) DO NOTHING",
                    name, description
                )


class FileDatabase(DatabaseInterface):
    """File-based database implementation (for development)."""
    
    def __init__(self, data_file: str = "data/users.json"):
        """Initialize file database."""
        self.data_file = os.path.join(os.path.dirname(__file__), "..", data_file)
    
    async def initialize(self) -> None:
        """Initialize file database."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
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
        from app.auth_utils import get_password_hash
        
        users = self._load_users()
        
        # Check if user already exists
        if any(u.get("email") == user_create.email for u in users):
            raise ValueError("User with this email already exists")
        
        if any(u.get("username") == user_create.username for u in users):
            raise ValueError("User with this username already exists")
        
        # Create user with hashed password
        user_in_db = UserInDB(
            **user_create.model_dump(exclude={"password"}),
            hashed_password=get_password_hash(user_create.password)
        )
        
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
                        if update_data:
                            data.update(update_data)
                            data["updated_at"] = datetime.utcnow().isoformat()
                            miniature_data[j] = data
                            user_data["updated_at"] = datetime.utcnow().isoformat()
                            users[i] = user_data
                            self._save_users(users)
                        
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

    # Game management methods
    async def get_all_games(self) -> List[Game]:
        """Get all available games."""
        # For file database, return empty list or hardcoded games
        return []
    
    async def create_game(self, name: str, description: Optional[str] = None) -> Game:
        """Create a new game."""
        # For file database, create a simple game object
        game = Game(
            id=uuid4(),
            name=name,
            description=description,
            is_active=True
        )
        return game

    # User preferences methods
    async def get_user_preferences(self, user_id: UUID) -> Optional[UserPreferences]:
        """Get user preferences by user ID."""
        # For file database, return None (not implemented)
        return None
    
    async def create_user_preferences(self, user_id: UUID, preferences: UserPreferencesCreate) -> UserPreferences:
        """Create user preferences."""
        # For file database, return a simple UserPreferences object
        return UserPreferences(
            id=uuid4(),
            user_id=user_id,
            games=preferences.games,
            postcode=preferences.postcode,
            game_types=preferences.game_types,
            bio=preferences.bio
        )
    
    async def update_user_preferences(self, user_id: UUID, updates: UserPreferencesUpdate) -> Optional[UserPreferences]:
        """Update user preferences."""
        # For file database, return None (not implemented)
        return None
    
    async def search_players(self, searcher_user_id: UUID, search_request: PlayerSearchRequest) -> List[PlayerSearchResult]:
        """Search for players based on criteria."""
        # For file database, return empty list
        return []


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