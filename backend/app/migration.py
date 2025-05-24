"""Database migration utilities for transitioning from file to PostgreSQL storage."""

import asyncio
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from uuid import UUID

from app.database import get_database, PostgreSQLDatabase, FileDatabase
from app.auth_models import UserCreate, UserInDB
from app.data_backup import create_emergency_backup


async def migrate_users_to_database() -> bool:
    """Migrate users from JSON file to PostgreSQL database."""
    print("🔄 Starting user migration to database...")
    
    # Create backup first
    backup_path = create_emergency_backup()
    print(f"📦 Created backup at: {backup_path}")
    
    # Initialize databases
    file_db = FileDatabase()
    await file_db.initialize()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url or not database_url.startswith("postgresql"):
        print("❌ DATABASE_URL not set or not PostgreSQL. Migration aborted.")
        return False
    
    pg_db = PostgreSQLDatabase(database_url)
    await pg_db.initialize()
    
    # Load users from file
    users_data = file_db._load_users()
    if not users_data:
        print("📁 No users found in file storage.")
        return True
    
    print(f"👥 Found {len(users_data)} users to migrate")
    
    migrated_count = 0
    failed_count = 0
    
    for user_data in users_data:
        try:
            # Convert to UserInDB model
            user_in_db = UserInDB(**user_data)
            
            # Check if user already exists in database
            existing_user = await pg_db.get_user_by_email(user_in_db.email)
            if existing_user:
                print(f"⚠️  User {user_in_db.email} already exists in database, skipping")
                continue
            
            # Insert user directly into PostgreSQL with existing hashed password
            async with pg_db._pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO users (id, email, username, hashed_password, is_active, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (email) DO NOTHING
                """, 
                user_in_db.id, user_in_db.email, user_in_db.username, 
                user_in_db.hashed_password, user_in_db.is_active,
                user_in_db.created_at, user_in_db.updated_at
                )
            
            migrated_count += 1
            print(f"✅ Migrated user: {user_in_db.email}")
            
        except Exception as e:
            failed_count += 1
            print(f"❌ Failed to migrate user {user_data.get('email', 'unknown')}: {str(e)}")
    
    print(f"\n📊 Migration Summary:")
    print(f"   ✅ Successfully migrated: {migrated_count} users")
    print(f"   ❌ Failed migrations: {failed_count} users")
    print(f"   📦 Backup created at: {backup_path}")
    
    if migrated_count > 0:
        print(f"\n🎉 Migration completed! Users are now stored in PostgreSQL database.")
        print(f"💡 You can now set DATABASE_URL environment variable for persistent storage.")
    
    return failed_count == 0


async def verify_migration() -> bool:
    """Verify that migration was successful by comparing user counts."""
    print("🔍 Verifying migration...")
    
    # Count users in file
    file_db = FileDatabase()
    await file_db.initialize()
    file_users = file_db._load_users()
    file_count = len(file_users)
    
    # Count users in database
    database_url = os.getenv("DATABASE_URL")
    if not database_url or not database_url.startswith("postgresql"):
        print("❌ DATABASE_URL not set or not PostgreSQL")
        return False
    
    pg_db = PostgreSQLDatabase(database_url)
    await pg_db.initialize()
    db_users = await pg_db.get_all_users()
    db_count = len(db_users)
    
    print(f"📊 User count comparison:")
    print(f"   📁 File storage: {file_count} users")
    print(f"   🗄️  Database: {db_count} users")
    
    if db_count >= file_count:
        print("✅ Migration verification successful!")
        return True
    else:
        print("❌ Migration verification failed - database has fewer users than file")
        return False


async def rollback_migration() -> bool:
    """Rollback migration by restoring from the latest backup."""
    print("🔄 Rolling back migration...")
    
    from app.data_backup import DataBackupManager
    backup_manager = DataBackupManager()
    
    # Get latest backup
    backups = backup_manager.list_backups()
    if not backups:
        print("❌ No backups found for rollback")
        return False
    
    latest_backup = backups[0]
    print(f"📦 Restoring from backup: {latest_backup['backup_name']}")
    
    success = backup_manager.restore_backup(latest_backup['backup_name'])
    if success:
        print("✅ Rollback completed successfully")
    else:
        print("❌ Rollback failed")
    
    return success


async def main():
    """CLI interface for migration operations."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migration.py [migrate|verify|rollback]")
        print("Commands:")
        print("  migrate  - Migrate users from file to PostgreSQL database")
        print("  verify   - Verify migration was successful")
        print("  rollback - Restore from latest backup")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "migrate":
        success = await migrate_users_to_database()
        sys.exit(0 if success else 1)
    
    elif command == "verify":
        success = await verify_migration()
        sys.exit(0 if success else 1)
    
    elif command == "rollback":
        success = await rollback_migration()
        sys.exit(0 if success else 1)
    
    else:
        print("Unknown command. Use: migrate, verify, or rollback")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 