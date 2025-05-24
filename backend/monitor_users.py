#!/usr/bin/env python3
"""
Script to monitor user registrations with optional watch mode.
"""
import asyncio
import argparse
from datetime import datetime
from app.database import get_database

async def check_users(show_timestamp: bool = True):
    """Check and display current user count and user list."""
    db = get_database()
    await db.initialize()
    
    if show_timestamp:
        print(f'=== User Check at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ===')
    else:
        print('=== Current User Count and List ===')
    
    users = await db.get_all_users()
    print(f'Total users: {len(users)}')
    print()
    
    if users:
        for i, user in enumerate(users, 1):
            print(f'{i}. Email: {user.email}')
            print(f'   Username: {user.username}')
            print(f'   Created: {user.created_at}')
            print(f'   Active: {user.is_active}')
            print()
    else:
        print('No users found.')
    
    # Close connection if it's PostgreSQL
    if hasattr(db, '_pool') and db._pool:
        await db._pool.close()
    
    return len(users)

async def monitor_users(interval: int = 30):
    """Monitor users continuously with specified interval (seconds)."""
    print(f"Monitoring user registrations every {interval} seconds...")
    print("Press Ctrl+C to stop monitoring\n")
    
    last_count = 0
    
    try:
        while True:
            current_count = await check_users(show_timestamp=True)
            
            if current_count > last_count:
                print(f"🎉 NEW USER(S) DETECTED! Count increased from {last_count} to {current_count}")
            
            last_count = current_count
            print(f"Next check in {interval} seconds...\n")
            await asyncio.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n✅ Monitoring stopped.")

def main():
    parser = argparse.ArgumentParser(description="Monitor user registrations")
    parser.add_argument("--watch", "-w", action="store_true", 
                       help="Continuous monitoring mode")
    parser.add_argument("--interval", "-i", type=int, default=30,
                       help="Monitoring interval in seconds (default: 30)")
    
    args = parser.parse_args()
    
    if args.watch:
        asyncio.run(monitor_users(args.interval))
    else:
        asyncio.run(check_users(show_timestamp=False))

if __name__ == "__main__":
    main() 