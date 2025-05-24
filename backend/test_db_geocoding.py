#!/usr/bin/env python3
"""Test script for database geocoding integration."""

import asyncio
import sys
import os
from uuid import UUID

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import get_database
from app.models import UserPreferencesUpdate


async def test_db_geocoding():
    """Test the database geocoding integration."""
    
    print("Testing database geocoding integration...")
    print("=" * 50)
    
    # Get database instance
    db = get_database()
    await db.initialize()
    
    # Test user ID (first Berlin user)
    user_id = UUID("9f11ac2e-7770-437a-a41f-dcf6e4526db0")
    
    print(f"\nTesting with user ID: {user_id}")
    
    # Get current preferences
    current_prefs = await db.get_user_preferences(user_id)
    if current_prefs:
        print(f"Current location: {current_prefs.location}")
        print(f"Current latitude: {current_prefs.latitude}")
        print(f"Current longitude: {current_prefs.longitude}")
    else:
        print("No preferences found!")
        return
    
    # Try updating with geocoding
    print(f"\nUpdating location to 'Berlin Mitte, Germany'...")
    update = UserPreferencesUpdate(location="Berlin Mitte, Germany")
    
    try:
        updated_prefs = await db.update_user_preferences(user_id, update)
        if updated_prefs:
            print(f"✅ Updated location: {updated_prefs.location}")
            print(f"✅ Updated latitude: {updated_prefs.latitude}")
            print(f"✅ Updated longitude: {updated_prefs.longitude}")
        else:
            print("❌ Update failed!")
    except Exception as e:
        print(f"❌ Error during update: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_db_geocoding()) 