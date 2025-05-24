#!/usr/bin/env python3
"""
Script to check for recent registration attempts after PostgreSQL deployment.
"""
import asyncio
import asyncpg
from datetime import datetime, timedelta

async def check_recent_registrations():
    """Check for recent registrations in PostgreSQL database."""
    database_url = "postgresql://miniature_user:QmsugmlRB1TVDBQK9ypcdNQS9DUHXBks@dpg-d0ota50dl3ps73aa03qg-a.frankfurt-postgres.render.com/miniature_tracker"
    
    # Our migration was around May 24, 15:31 (3:31 PM)
    migration_time = datetime(2025, 5, 24, 15, 31, 0)
    
    try:
        # Connect to PostgreSQL
        conn = await asyncpg.connect(database_url)
        
        print(f'=== Checking Registrations After {migration_time} ===')
        
        # Get all users created after migration
        recent_rows = await conn.fetch("""
            SELECT id, email, username, is_active, created_at, updated_at 
            FROM users 
            WHERE created_at > $1
            ORDER BY created_at DESC
        """, migration_time)
        
        print(f'Users registered after PostgreSQL deployment: {len(recent_rows)}')
        print()
        
        if recent_rows:
            for i, row in enumerate(recent_rows, 1):
                print(f'{i}. Email: {row["email"]}')
                print(f'   Username: {row["username"]}')
                print(f'   ID: {row["id"]}')
                print(f'   Created: {row["created_at"]}')
                print(f'   Active: {row["is_active"]}')
                print()
        else:
            print('❌ NO new registrations found after PostgreSQL deployment!')
            print('This suggests the production app might not be using PostgreSQL correctly.')
        
        # Also check total count and most recent user
        total_rows = await conn.fetch("""
            SELECT id, email, username, is_active, created_at, updated_at 
            FROM users 
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        print(f'=== Most Recent 5 Users ===')
        for i, row in enumerate(total_rows, 1):
            print(f'{i}. {row["email"]} ({row["username"]}) - {row["created_at"]}')
        
        # Test database connection health
        test_result = await conn.fetchval("SELECT 'PostgreSQL connection working!' as status")
        print(f'\n✅ Database Connection Test: {test_result}')
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        print("This might indicate the production app can't connect to PostgreSQL!")

if __name__ == "__main__":
    asyncio.run(check_recent_registrations()) 