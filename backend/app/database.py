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
from app.models import PasswordResetToken, Miniature, MiniatureCreate, MiniatureUpdate, StatusLogEntry


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


class PostgreSQLDatabase(DatabaseInterface):
    """PostgreSQL database implementation."""
    
    def __init__(self, database_url: str):
        """Initialize PostgreSQL database."""
        if asyncpg is None:
            raise ImportError("asyncpg is required for PostgreSQL support")
        
        self.database_url = database_url
        self._pool: Optional['asyncpg.Pool'] = None
    
    async def initialize(self) -> None:
        """Initialize PostgreSQL connection and create tables."""
        if asyncpg is None:
            raise ImportError("asyncpg is required for PostgreSQL support")
            
        self._pool = await asyncpg.create_pool(self.database_url)
        
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
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create status log entries table
        await self._pool.execute("""
            CREATE TABLE IF NOT EXISTS status_log_entries (
                id UUID PRIMARY KEY,
                miniature_id UUID REFERENCES miniatures(id) ON DELETE CASCADE,
                from_status VARCHAR(255),
                to_status VARCHAR(255) NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create indexes
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_reset_tokens_token ON password_reset_tokens(token)")
        await self._pool.execute("CREATE INDEX IF NOT EXISTS idx_miniatures_name ON miniatures(name)")
    
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
            rows = await conn.fetch(
                "SELECT id, name, description, created_at, updated_at FROM miniatures WHERE user_id = $1 ORDER BY created_at",
                user_id
            )
            return [Miniature(**dict(row)) for row in rows]
    
    async def get_miniature(self, miniature_id: UUID, user_id: UUID) -> Optional[Miniature]:
        """Get a specific miniature by ID for a user."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
            
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, name, description, created_at, updated_at FROM miniatures WHERE id = $1 AND user_id = $2",
                miniature_id, user_id
            )
            if row:
                return Miniature(**dict(row))
        return None
    
    async def create_miniature(self, miniature: MiniatureCreate, user_id: UUID) -> Miniature:
        """Create a new miniature."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO miniatures (name, description, user_id) VALUES ($1, $2, $3) RETURNING id, name, description, created_at, updated_at",
                miniature.name, miniature.description, user_id
            )
            if row:
                return Miniature(**dict(row))
        return None
    
    async def update_miniature(self, miniature_id: UUID, updates: MiniatureUpdate, user_id: UUID) -> Optional[Miniature]:
        """Update an existing miniature."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
            
        update_data = updates.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_miniature(miniature_id, user_id)
        
        # Build dynamic query
        set_clauses = []
        values = []
        for i, (key, value) in enumerate(update_data.items(), 1):
            set_clauses.append(f"{key} = ${i}")
            values.append(value)
        
        values.append(datetime.utcnow())  # updated_at
        values.append(miniature_id)  # WHERE condition
        values.append(user_id)  # WHERE condition
        
        query = f"""
            UPDATE miniatures 
            SET {', '.join(set_clauses)}, updated_at = ${len(values)-1}
            WHERE id = ${len(values)} AND user_id = ${len(values)-1}
            RETURNING id, name, description, created_at, updated_at
        """
        
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, *values)
            if row:
                return Miniature(**dict(row))
        return None
    
    async def delete_miniature(self, miniature_id: UUID, user_id: UUID) -> bool:
        """Delete a miniature."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
            
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM miniatures WHERE id = $1 AND user_id = $2",
                miniature_id, user_id
            )
            return result.rowcount > 0
    
    async def add_status_log_entry(self, miniature_id: UUID, from_status: Optional[str], to_status: str, notes: Optional[str], user_id: UUID) -> Optional[Miniature]:
        """Add a status log entry to a miniature."""
        if self._pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO status_log_entries (miniature_id, from_status, to_status, notes, user_id) VALUES ($1, $2, $3, $4, $5) RETURNING id, miniature_id, from_status, to_status, notes, created_at",
                miniature_id, from_status, to_status, notes, user_id
            )
            if row:
                return Miniature(**dict(row))
        return None


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


def get_database() -> DatabaseInterface:
    """Get database instance based on environment."""
    database_url = os.getenv("DATABASE_URL")
    
    if database_url and database_url.startswith("postgresql"):
        return PostgreSQLDatabase(database_url)
    else:
        return FileDatabase() 