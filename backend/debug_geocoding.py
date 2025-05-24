#!/usr/bin/env python3
"""Debug script for geocoding issue."""

import asyncio
import sys
import os
from uuid import UUID

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.geocoding import GeocodingService


async def debug_geocoding_update():
    """Debug the geocoding update issue."""
    
    print("Debugging geocoding update...")
    print("=" * 50)
    
    # Test the geocoding service directly
    test_location = "Berlin Mitte, Germany"
    print(f"\nTesting geocoding for: '{test_location}'")
    
    coordinates = await GeocodingService.get_coordinates_from_address(test_location)
    if coordinates:
        lat, lon = coordinates
        print(f"✅ Geocoding works: {lat:.6f}, {lon:.6f}")
        
        # Now let's manually update the database
        print(f"\nNow let's check the database update logic...")
        
        # Simulate the update_data logic from database.py
        update_data = {'location': test_location}
        
        print(f"Update data: {update_data}")
        print(f"'location' in update_data: {'location' in update_data}")
        print(f"update_data['location'] is not None: {update_data['location'] is not None}")
        
        if 'location' in update_data and update_data['location'] is not None:
            print("✅ Should trigger geocoding!")
            coordinates = await GeocodingService.get_coordinates_from_address(update_data['location'])
            if coordinates:
                update_data['latitude'] = coordinates[0]
                update_data['longitude'] = coordinates[1]
                print(f"✅ Added coordinates to update_data: {update_data}")
            else:
                update_data['latitude'] = None
                update_data['longitude'] = None
                print(f"❌ No coordinates, setting to None: {update_data}")
        else:
            print("❌ Geocoding not triggered!")
        
    else:
        print("❌ Geocoding failed!")


if __name__ == "__main__":
    asyncio.run(debug_geocoding_update()) 