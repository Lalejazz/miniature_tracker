#!/usr/bin/env python3
"""Check miniatures for all users in the database."""

import asyncio
from app.database import get_database

async def check_miniatures():
    """Check and display miniatures for all users."""
    db = get_database()
    await db.initialize()
    users = await db.get_all_users()
    
    total_miniatures = 0
    
    print(f'=== MINIATURES BY USER ===')
    print()
    
    for user in users:
        miniatures = await db.get_all_miniatures(user.id)
        total_miniatures += len(miniatures)
        
        print(f'👤 {user.username} ({user.email}):')
        if miniatures:
            for i, mini in enumerate(miniatures, 1):
                print(f'  {i}. {mini.name}')
                print(f'     Status: {mini.status}')
                print(f'     Created: {mini.created_at}')
                if mini.description:
                    print(f'     Description: {mini.description}')
                print()
        else:
            print('  No miniatures')
            print()
    
    print(f'📊 SUMMARY:')
    print(f'   Total users: {len(users)}')
    print(f'   Total miniatures: {total_miniatures}')

if __name__ == "__main__":
    asyncio.run(check_miniatures()) 