#!/usr/bin/env python3
"""
Script to search for missing user romano.deltin@gmail.com.
"""
import asyncio
import asyncpg
import json

async def find_missing_user():
    """Search for romano.deltin@gmail.com in PostgreSQL database."""
    database_url = "postgresql://miniature_user:QmsugmlRB1TVDBQK9ypcdNQS9DUHXBks@dpg-d0ota50dl3ps73aa03qg-a.frankfurt-postgres.render.com/miniature_tracker"
    target_email = "romano.deltin@gmail.com"
    
    try:
        # Connect to PostgreSQL
        conn = await asyncpg.connect(database_url)
        
        print(f'=== Searching for {target_email} ===')
        
        # Search for the specific user
        row = await conn.fetchrow("""
            SELECT id, email, username, is_active, created_at, updated_at 
            FROM users 
            WHERE email = $1
        """, target_email)
        
        if row:
            print(f'✅ FOUND USER in PostgreSQL:')
            print(f'   Email: {row["email"]}')
            print(f'   Username: {row["username"]}')
            print(f'   ID: {row["id"]}')
            print(f'   Created: {row["created_at"]}')
            print(f'   Active: {row["is_active"]}')
        else:
            print(f'❌ User {target_email} NOT FOUND in PostgreSQL database')
        
        # Also search for any similar emails (case variations, etc.)
        similar_rows = await conn.fetch("""
            SELECT id, email, username, is_active, created_at, updated_at 
            FROM users 
            WHERE LOWER(email) LIKE LOWER($1)
        """, f'%{target_email.split("@")[0]}%')
        
        if similar_rows:
            print(f'\n🔍 Similar emails found:')
            for row in similar_rows:
                print(f'   {row["email"]} ({row["username"]})')
        
        await conn.close()
        
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")

def check_file_storage():
    """Check file storage for the missing user."""
    target_email = "romano.deltin@gmail.com"
    
    try:
        with open('data/users.json', 'r') as f:
            users = json.load(f)
        
        print(f'\n=== Searching in File Storage ===')
        found = False
        for user in users:
            if user["email"].lower() == target_email.lower():
                print(f'✅ FOUND USER in file storage:')
                print(f'   Email: {user["email"]}')
                print(f'   Username: {user["username"]}')
                print(f'   Created: {user["created_at"]}')
                found = True
                break
        
        if not found:
            print(f'❌ User {target_email} NOT FOUND in file storage')
            
    except Exception as e:
        print(f"Error reading file storage: {e}")

def check_backups():
    """Check backup files for the missing user."""
    target_email = "romano.deltin@gmail.com"
    backup_dirs = [
        'backup/data_backup_20250524_151523/users.json',
        'backup/data_backup_20250524_153046/users.json', 
        'backup/data_backup_20250524_153114/users.json'
    ]
    
    print(f'\n=== Searching in Backups ===')
    
    for backup_file in backup_dirs:
        try:
            with open(backup_file, 'r') as f:
                users = json.load(f)
            
            found = False
            for user in users:
                if user["email"].lower() == target_email.lower():
                    print(f'✅ FOUND USER in {backup_file}:')
                    print(f'   Email: {user["email"]}')
                    print(f'   Username: {user["username"]}')
                    print(f'   Created: {user["created_at"]}')
                    found = True
                    break
            
            if not found:
                print(f'❌ Not found in {backup_file} ({len(users)} users)')
                
        except Exception as e:
            print(f"Error reading {backup_file}: {e}")

if __name__ == "__main__":
    asyncio.run(find_missing_user())
    check_file_storage()
    check_backups() 