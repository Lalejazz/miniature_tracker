#!/usr/bin/env python3
"""Debug database connection details."""

import asyncio
import os
from app.database import get_database

async def debug_connection():
    """Debug database connection and show details."""
    print("=== DATABASE CONNECTION DEBUG ===")
    print()
    
    # Check environment variable
    database_url = os.getenv("DATABASE_URL")
    print(f"DATABASE_URL environment variable:")
    if database_url:
        # Hide password for security
        safe_url = database_url.replace(database_url.split('@')[0].split('//')[-1], "***HIDDEN***")
        print(f"  {safe_url}")
    else:
        print("  NOT SET (will use file storage)")
    print()
    
    # Check which database implementation we're using
    db = get_database()
    print(f"Database implementation: {type(db).__name__}")
    print()
    
    # If PostgreSQL, get more details
    if hasattr(db, 'database_url'):
        print("PostgreSQL connection details:")
        safe_url = db.database_url.replace(db.database_url.split('@')[0].split('//')[-1], "***HIDDEN***")
        print(f"  URL: {safe_url}")
        print()
    
    # Initialize and test connection
    try:
        await db.initialize()
        print("✅ Database initialization successful")
        
        # Get users to test
        users = await db.get_all_users()
        print(f"✅ Successfully retrieved {len(users)} users")
        
        # If PostgreSQL, check database info
        if hasattr(db, '_pool') and db._pool:
            async with db._pool.acquire() as conn:
                # Check database name
                db_name = await conn.fetchval("SELECT current_database()")
                print(f"✅ Connected to database: {db_name}")
                
                # Check if tables exist
                tables = await conn.fetch("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                print(f"✅ Tables found: {[t['table_name'] for t in tables]}")
                
                # Check users table specifically
                user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
                print(f"✅ Users in database: {user_count}")
                
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_connection()) 