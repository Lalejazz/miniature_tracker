#!/usr/bin/env python3
"""
Simple persistent storage solution for miniatures data.
Stores miniatures as JSON blobs in PostgreSQL to prevent data loss.
"""
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.database import get_database


class PersistentMiniatureStorage:
    """Simple persistent storage that backs up miniatures to PostgreSQL as JSON."""
    
    def __init__(self):
        self.db = get_database()
    
    async def _ensure_table_exists(self):
        """Ensure the miniatures_backup table exists."""
        await self.db.initialize()
        
        # Only create table if we're using PostgreSQL
        if hasattr(self.db, '_pool') and self.db._pool:
            async with self.db._pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS miniatures_backup (
                        user_id UUID NOT NULL,
                        miniatures_json TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW(),
                        PRIMARY KEY (user_id)
                    )
                """)
    
    async def backup_user_miniatures(self, user_id: UUID, miniatures_data: List[Dict[str, Any]]):
        """Backup user's miniatures to PostgreSQL as JSON."""
        await self._ensure_table_exists()
        
        # Only backup if we're using PostgreSQL
        if hasattr(self.db, '_pool') and self.db._pool:
            miniatures_json = json.dumps(miniatures_data, default=str)
            
            async with self.db._pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO miniatures_backup (user_id, miniatures_json, updated_at)
                    VALUES ($1, $2, NOW())
                    ON CONFLICT (user_id) 
                    DO UPDATE SET 
                        miniatures_json = EXCLUDED.miniatures_json,
                        updated_at = NOW()
                """, user_id, miniatures_json)
    
    async def restore_user_miniatures(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Restore user's miniatures from PostgreSQL backup."""
        await self._ensure_table_exists()
        
        # Only restore if we're using PostgreSQL
        if hasattr(self.db, '_pool') and self.db._pool:
            async with self.db._pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT miniatures_json FROM miniatures_backup WHERE user_id = $1",
                    user_id
                )
                if row:
                    return json.loads(row['miniatures_json'])
        
        return []
    
    async def get_all_backed_up_users(self) -> List[UUID]:
        """Get all user IDs that have backed up miniatures."""
        await self._ensure_table_exists()
        
        # Only check if we're using PostgreSQL
        if hasattr(self.db, '_pool') and self.db._pool:
            async with self.db._pool.acquire() as conn:
                rows = await conn.fetch("SELECT user_id FROM miniatures_backup")
                return [UUID(row['user_id']) for row in rows]
        
        return []


# Global instance
persistent_storage = PersistentMiniatureStorage()


async def backup_miniatures_for_user(user_id: UUID, miniatures_data: List[Dict[str, Any]]):
    """Convenience function to backup miniatures for a user."""
    await persistent_storage.backup_user_miniatures(user_id, miniatures_data)


async def restore_miniatures_for_user(user_id: UUID) -> List[Dict[str, Any]]:
    """Convenience function to restore miniatures for a user."""
    return await persistent_storage.restore_user_miniatures(user_id) 