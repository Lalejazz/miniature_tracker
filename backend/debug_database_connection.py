#!/usr/bin/env python3
"""
Debug script to understand why production app isn't using PostgreSQL.
"""
import os
import asyncio
from app.database import get_database

async def debug_database_connection():
    """Debug database connection and environment setup."""
    print("=== DATABASE CONNECTION DEBUG ===")
    print()
    
    # Check environment variables
    print("1. Environment Variables:")
    database_url = os.getenv("DATABASE_URL")
    print(f"   DATABASE_URL: {database_url}")
    print(f"   DATABASE_URL exists: {'✅' if database_url else '❌'}")
    print()
    
    # Check which database type is being used
    print("2. Database Type Detection:")
    db = get_database()
    db_type = type(db).__name__
    print(f"   Database class: {db_type}")
    
    if db_type == "PostgreSQLDatabase":
        print("   ✅ Using PostgreSQL (GOOD)")
    elif db_type == "FileDatabase":
        print("   ❌ Using File Storage (BAD - this is the problem!)")
    else:
        print(f"   ❓ Unknown database type: {db_type}")
    print()
    
    # Test connection
    print("3. Connection Test:")
    try:
        await db.initialize()
        users = await db.get_all_users()
        print(f"   ✅ Connection successful")
        print(f"   📊 User count: {len(users)}")
        
        # Show which storage is being used
        if hasattr(db, '_pool'):
            print("   💾 Connected to: PostgreSQL")
        else:
            print("   💾 Connected to: File Storage")
            if hasattr(db, 'data_file'):
                print(f"   📁 File path: {db.data_file}")
        
        # Close properly
        if hasattr(db, '_pool') and db._pool:
            await db._pool.close()
            
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
    
    print()
    print("=== DIAGNOSIS ===")
    if database_url and db_type == "PostgreSQLDatabase":
        print("✅ Configuration looks correct - app should use PostgreSQL")
    elif not database_url:
        print("❌ DATABASE_URL not found - app will default to file storage")
        print("💡 Check Render environment variables!")
    elif database_url and db_type == "FileDatabase":
        print("❌ DATABASE_URL exists but app still uses file storage")
        print("💡 Check app code - DATABASE_URL might not be read correctly")

if __name__ == "__main__":
    asyncio.run(debug_database_connection()) 