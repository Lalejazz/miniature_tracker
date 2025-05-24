#!/usr/bin/env python3
"""
Script to check users directly in PostgreSQL database.
"""
import asyncio
import os
try:
    import asyncpg
except ImportError:
    print("asyncpg not installed. Installing...")
    os.system("pip install asyncpg")
    import asyncpg

async def check_postgres_users():
    """Check users directly in PostgreSQL database."""
    database_url = "postgresql://miniature_user:QmsugmlRB1TVDBQK9ypcdNQS9DUHXBks@dpg-d0ota50dl3ps73aa03qg-a.frankfurt-postgres.render.com/miniature_tracker"
    
    try:
        # Connect to PostgreSQL
        conn = await asyncpg.connect(database_url)
        
        print('=== Users in PostgreSQL Database ===')
        
        # Get all users
        rows = await conn.fetch("""
            SELECT id, email, username, is_active, created_at, updated_at 
            FROM users 
            ORDER BY created_at
        """)
        
        print(f'Total users in PostgreSQL: {len(rows)}')
        print()
        
        if rows:
            for i, row in enumerate(rows, 1):
                print(f'{i}. Email: {row["email"]}')
                print(f'   Username: {row["username"]}')
                print(f'   ID: {row["id"]}')
                print(f'   Created: {row["created_at"]}')
                print(f'   Active: {row["is_active"]}')
                print()
        else:
            print('No users found in PostgreSQL database.')
        
        await conn.close()
        return len(rows)
        
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return 0

if __name__ == "__main__":
    asyncio.run(check_postgres_users()) 