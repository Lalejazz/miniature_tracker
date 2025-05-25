import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.database import get_database
from app.models import GameSystem, UnitType, PaintingStatus
from app.main import export_collection
from app.crud import MiniatureDB
from uuid import UUID

async def test_export():
    db = get_database()
    await db.initialize()
    
    # Get the specific user by email
    user = await db.get_user_by_email("alexcargnel@gmail.com")
    if user:
        user_id = user.id
        print(f'Testing with user: {user.username} ({user.email})')
        
        # Get miniatures
        miniatures = await db.get_all_miniatures(user_id)
        print(f'Found {len(miniatures)} miniatures')
        
        # Test the actual export endpoint
        try:
            print('\n--- Testing CSV Export Endpoint ---')
            miniature_db = MiniatureDB()
            
            # Test CSV export
            response = await export_collection(
                format="csv",
                db=miniature_db,
                current_user_id=user_id
            )
            
            print(f'CSV Export successful!')
            print(f'Response type: {type(response)}')
            print(f'Media type: {response.media_type}')
            print(f'Headers: {response.headers}')
            print(f'Content length: {len(response.body)} bytes')
            print('First 200 characters of CSV content:')
            print(response.body[:200].decode('utf-8'))
            
        except Exception as e:
            print(f'CSV Export failed: {e}')
            import traceback
            traceback.print_exc()
            
        try:
            print('\n--- Testing JSON Export Endpoint ---')
            
            # Test JSON export
            response = await export_collection(
                format="json",
                db=miniature_db,
                current_user_id=user_id
            )
            
            print(f'JSON Export successful!')
            print(f'Response type: {type(response)}')
            print(f'Media type: {response.media_type}')
            print(f'Headers: {response.headers}')
            print(f'Content length: {len(response.body)} bytes')
            print('First 200 characters of JSON content:')
            print(response.body[:200].decode('utf-8'))
            
        except Exception as e:
            print(f'JSON Export failed: {e}')
            import traceback
            traceback.print_exc()
            
    else:
        print('User alexcargnel@gmail.com not found')
        
        # List all users
        users = await db.get_all_users()
        print(f'Available users ({len(users)}):')
        for u in users:
            print(f'  - {u.username} ({u.email})')

if __name__ == "__main__":
    asyncio.run(test_export()) 