#!/usr/bin/env python3
"""Test script for geocoding service."""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.geocoding import GeocodingService


async def test_geocoding():
    """Test the geocoding service with various addresses."""
    
    test_addresses = [
        "Berlin Mitte, Germany",
        "Berlin Charlottenburg, Germany", 
        "London, UK",
        "New York, NY, USA",
        "Tokyo, Japan"
    ]
    
    print("Testing geocoding service...")
    print("=" * 50)
    
    for address in test_addresses:
        print(f"\nTesting: '{address}'")
        try:
            coordinates = await GeocodingService.get_coordinates_from_address(address)
            if coordinates:
                lat, lon = coordinates
                print(f"✅ Success: {lat:.6f}, {lon:.6f}")
            else:
                print("❌ Failed: No coordinates returned")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_geocoding()) 