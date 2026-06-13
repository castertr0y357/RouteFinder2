import logging
from typing import Optional
from django.conf import settings
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError

logger = logging.getLogger(__name__)

def get_zip_from_coords(lat: float, lon: float) -> Optional[str]:
    """
    Reverse geocodes latitude and longitude to find a zip code using Nominatim (OSM).
    Returns the zip code as a string, or None if not found.
    """
    if getattr(settings, 'MOCK_MODE', False):
        logger.info(f"MOCK_MODE: Mocking zip code lookup for coords ({lat}, {lon})")
        return "90210"

    try:
        # User-agent is required by Nominatim's usage policy
        geolocator = Nominatim(user_agent="routefinder_app")
        location = geolocator.reverse((lat, lon), addressdetails=True, timeout=10)
        
        if location and 'address' in location.raw:
            address = location.raw['address']
            # Postal code can be 'postcode' or 'postal-code' depending on the region
            return address.get('postcode') or address.get('postal-code')
            
    except (GeopyError, Exception) as e:
        logger.error(f"Reverse geocoding error: {str(e)}")
        
    return None

def get_address_from_coords(lat: float, lon: float) -> Optional[str]:
    """
    Reverse geocodes latitude and longitude to find a full address using Nominatim (OSM).
    Returns the formatted address as a string, or None if not found.
    """
    if getattr(settings, 'MOCK_MODE', False):
        logger.info(f"MOCK_MODE: Mocking address lookup for coords ({lat}, {lon})")
        return f"123 Mock St, Springfield, {get_zip_from_coords(lat, lon)}"

    try:
        geolocator = Nominatim(user_agent="routefinder_app")
        location = geolocator.reverse((lat, lon), timeout=10)
        
        if location:
            return location.address
            
    except (GeopyError, Exception) as e:
        logger.error(f"Reverse geocoding error: {str(e)}")
        
    return None

