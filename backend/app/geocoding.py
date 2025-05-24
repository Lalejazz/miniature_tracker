"""Geocoding service for converting addresses to coordinates."""

import httpx
import logging
from typing import Optional, Tuple, Dict, Union

logger = logging.getLogger(__name__)


class GeocodingService:
    """Service for converting addresses to coordinates."""
    
    @staticmethod
    async def get_coordinates_from_address(address: str) -> Optional[Tuple[float, float]]:
        """
        Convert an address to latitude/longitude coordinates using OpenStreetMap Nominatim.
        
        This service is free and supports worldwide addresses including:
        - Full addresses: "123 Main St, New York, NY, USA"
        - Cities: "London, UK" or "Tokyo, Japan"
        - Postcodes: "SW1A 1AA, UK" or "10001, USA"
        - Regions: "California, USA" or "Bayern, Germany"
        
        Args:
            address: Address to geocode (can be postcode, city, full address, etc.)
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            # Clean the address
            clean_address = address.strip()
            if not clean_address:
                return None
            
            # Use OpenStreetMap Nominatim - free worldwide geocoding service
            url = "https://nominatim.openstreetmap.org/search"
            
            params: Dict[str, Union[str, int]] = {
                "q": clean_address,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }
            
            headers = {
                "User-Agent": "MiniatureTracker/1.0 (https://github.com/alexcargnel/miniature_tracker)"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers, timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        result = data[0]
                        latitude = result.get("lat")
                        longitude = result.get("lon")
                        
                        if latitude and longitude:
                            lat_float = float(latitude)
                            lon_float = float(longitude)
                            logger.info(f"Geocoded address '{address}' to {lat_float}, {lon_float}")
                            return (lat_float, lon_float)
                
                logger.warning(f"Could not geocode address '{address}': No results found")
                return None
                
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {e}")
            return None 