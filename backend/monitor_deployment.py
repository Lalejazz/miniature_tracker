#!/usr/bin/env python3
"""
Script to monitor deployment success and check for new registrations after DATABASE_URL fix.
"""
import asyncio
import asyncpg
from datetime import datetime, timedelta

async def monitor_deployment():
    """Monitor the deployment and check for new registrations."""
    database_url = "postgresql://miniature_user:QmsugmlRB1TVDBQK9ypcdNQS9DUHXBks@dpg-d0ota50dl3ps73aa03qg-a.frankfurt-postgres.render.com/miniature_tracker"
    
    # Check from the time DATABASE_URL was added (now)
    deployment_time = datetime.utcnow() - timedelta(minutes=5)  # 5 minutes ago to catch any immediate changes
    
    try:
        # Connect to PostgreSQL
        conn = await asyncpg.connect(database_url)
        
        print(f'=== Monitoring Deployment Success ===')
        print(f'Checking for new registrations since: {deployment_time.strftime("%Y-%m-%d %H:%M:%S")} UTC')
        print()
        
        # Get current user count
        total_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        print(f'📊 Current total users in PostgreSQL: {total_count}')
        
        # Check for any new users since deployment
        new_users = await conn.fetch("""
            SELECT id, email, username, is_active, created_at, updated_at 
            FROM users 
            WHERE created_at > $1
            ORDER BY created_at DESC
        """, deployment_time)
        
        if new_users:
            print(f'🎉 NEW REGISTRATIONS DETECTED ({len(new_users)}):')
            for i, user in enumerate(new_users, 1):
                print(f'{i}. Email: {user["email"]}')
                print(f'   Username: {user["username"]}')
                print(f'   Created: {user["created_at"]}')
                print()
        else:
            print('⏳ No new registrations yet (this is normal if deployment just finished)')
            print('   Romano can try registering again now!')
        
        # Show most recent users
        recent_users = await conn.fetch("""
            SELECT id, email, username, is_active, created_at 
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        print(f'=== Most Recent Users in Database ===')
        for i, user in enumerate(recent_users, 1):
            print(f'{i}. {user["email"]} ({user["username"]}) - {user["created_at"]}')
        
        # Database health check
        test_result = await conn.fetchval("SELECT 'PostgreSQL connection working!' as status")
        print(f'\n✅ Database Health: {test_result}')
        
        await conn.close()
        return total_count
        
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        return 0

async def continuous_monitor(interval: int = 30):
    """Continuously monitor for new registrations."""
    print(f"🔄 Starting continuous monitoring every {interval} seconds...")
    print("Press Ctrl+C to stop\n")
    
    last_count = 0
    
    try:
        while True:
            current_count = await monitor_deployment()
            
            if current_count > last_count:
                print(f"\n🚨 USER COUNT INCREASED! From {last_count} to {current_count}")
                print("✅ DATABASE_URL fix is working! New registrations are persisting!")
            
            last_count = current_count
            print(f"\n⏰ Next check in {interval} seconds...\n" + "="*60 + "\n")
            await asyncio.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n✅ Monitoring stopped.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        asyncio.run(continuous_monitor())
    else:
        asyncio.run(monitor_deployment()) 