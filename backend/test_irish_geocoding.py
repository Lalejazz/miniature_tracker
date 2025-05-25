#!/usr/bin/env python3
"""Test script for Irish Eircode geocoding."""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.geocoding import GeocodingService


async def test_irish_geocoding():
    """Test the geocoding service with Irish Eircodes."""
    
    test_eircodes = [
        "T12 ABC1",  # Dublin area
        "T12 ABC2",  # Dublin area (close to above)
        "T12 XYZ1",  # Dublin area
        "T23 DEF1",  # Cork area
        "T23 DEF2",  # Cork area (close to above)
        "Cork, Ireland",
        "Dublin, Ireland",
        "T12 ABC1, Dublin, Ireland",
        "T23 DEF1, Cork, Ireland"
    ]
    
    print("Testing Irish Eircode geocoding...")
    print("=" * 50)
    
    for eircode in test_eircodes:
        print(f"\nTesting: '{eircode}'")
        try:
            coordinates = await GeocodingService.get_coordinates_from_address(eircode)
            if coordinates:
                lat, lon = coordinates
                print(f"✅ Success: {lat:.6f}, {lon:.6f}")
            else:
                print("❌ Failed: No coordinates returned")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_irish_geocoding()) 