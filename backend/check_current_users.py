#!/usr/bin/env python3
"""Check current users in the database."""

import asyncio
from app.database import get_database

async def check_users():
    """Check and display current users."""
    db = get_database()
    await db.initialize()
    users = await db.get_all_users()
    
    print(f'=== CURRENT USERS ({len(users)} total) ===')
    print()
    
    for i, user in enumerate(users, 1):
        print(f'{i}. Username: {user.username}')
        print(f'   Email: {user.email}')
        print(f'   ID: {user.id}')
        print(f'   Created: {user.created_at}')
        print(f'   Active: {user.is_active}')
        print()

if __name__ == "__main__":
    asyncio.run(check_users()) 