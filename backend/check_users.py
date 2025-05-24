#!/usr/bin/env python3
"""
Script to check current user count and list all users for monitoring new registrations.
"""
import asyncio
from app.database import get_database

async def check_users():
    """Check and display current user count and user list."""
    db = get_database()
    await db.initialize()
    
    print('=== Current User Count and List ===')
    users = await db.get_all_users()
    print(f'Total users: {len(users)}')
    print()
    
    if users:
        for i, user in enumerate(users, 1):
            print(f'{i}. Email: {user.email}')
            print(f'   Username: {user.username}')
            print(f'   Created: {user.created_at}')
            print(f'   Verified: {user.is_active}')
            print()
    else:
        print('No users found.')
    
    # Close connection if it's PostgreSQL
    if hasattr(db, '_pool') and db._pool:
        await db._pool.close()

if __name__ == "__main__":
    asyncio.run(check_users()) 